from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType, DoubleType
import os
from datetime import datetime


def create_spark_session(app_name="EHR Data Loader", aws_access_key=None, aws_secret_key=None):
    """
    Create and return a Spark session configured for Delta Lake with S3 access.
    """

    try:
        SparkSession.builder.getOrCreate().stop()
        print("Stopped existing Spark session")
    except:
        print("No existing Spark session to stop")

    builder = (SparkSession.builder
               .appName(app_name)
               .master("local[*]")
               .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0,org.apache.hadoop:hadoop-aws:3.3.1")
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog"))

    # Configure S3 access if credentials are provided
    if aws_access_key and aws_secret_key:
        builder = (builder
                   .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
                   .config("spark.hadoop.fs.s3a.access.key", aws_access_key)
                   .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key)
                   .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
                   .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
                   # IMPORTANT for MinIO
                   .config("spark.hadoop.fs.s3a.path.style.access", "true")
                   # Disable SSL for local MinIO
                   .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
                   )
    else:
        # Use instance profile or environment variables for authentication
        builder = builder.config("spark.hadoop.fs.s3a.aws.credentials.provider",
                                 "com.amazonaws.auth.DefaultAWSCredentialsProviderChain")

    # Additional S3 optimizations
    builder = (builder
               .config("spark.hadoop.fs.s3a.virtual.hosted.style", "false")
               .config("spark.hadoop.fs.s3a.signing-algorithm", "S3SignerType")
               .config("spark.hadoop.fs.s3a.connection.maximum", 100)
               .config("spark.hadoop.fs.s3a.experimental.input.fadvise", "sequential")
               .config("spark.hadoop.fs.s3a.fast.upload", "true")
               .config("spark.hadoop.fs.s3a.block.size", 128 * 1024 * 1024))

    return builder.getOrCreate()


def infer_schema_from_file(spark, file_path, sample_size=1000):
    """
    Infer schema from a CSV file by reading a sample.
    """
    # Read a sample of the CSV file to infer schema
    sample_df = spark.read.option("header", "true").option(
        "inferSchema", "true").csv(file_path).limit(sample_size)
    return sample_df.schema


def load_file_to_delta(spark, file_path, database_name, table_name, mode="overwrite", partition_by=None):
    """
    Load a CSV file into a Delta table using a database name.

    Args:
        spark: SparkSession object.
        file_path: Path to the CSV file (can be S3 URI).
        database_name: Name of the database to store the Delta table.
        table_name: Name of the table to create.
        mode: Write mode (overwrite, append, etc.).
        partition_by: Column(s) to partition the data by.
    """
    try:
        # Ensure the database exists
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")

        # Infer schema from file
        schema = infer_schema_from_file(spark, file_path)

        # Read the CSV file with the inferred schema
        df = spark.read.option("header", "true").schema(schema).csv(file_path)

        # Add metadata columns
        df = df.withColumn("ingestion_timestamp",
                           spark.sql("current_timestamp()"))
        df = df.withColumn("source_file", spark.sql(
            f"'{file_path.split('/')[-1]}'"))

        # Define the full table name
        full_table_name = f"{database_name}.{table_name}"

        # Write to Delta Lake using saveAsTable
        writer = df.write.format("delta").mode(
            mode).option("overwriteSchema", "true")

        if partition_by:
            writer = writer.partitionBy(partition_by)

        writer.saveAsTable(full_table_name)

        print(f"Successfully loaded {file_path} into table {full_table_name}")
        return True
    except Exception as e:
        print(
            f"Error loading {file_path} into table {full_table_name}: {str(e)}")
        return False


def list_s3_files(spark, s3_dir_path, file_extension=".csv"):
    """
    List files in an S3 directory with a specific extension.

    Args:
        spark: SparkSession object
        s3_dir_path: S3 directory path (e.g., s3a://bucket-name/path/)
        file_extension: File extension to filter by

    Returns:
        List of file paths
    """
    # Create a DataFrame representing the files
    files_df = spark.read.format("binaryFile").load(s3_dir_path)

    # Filter files by extension and collect their paths
    csv_files = files_df.filter(files_df.path.endswith(
        file_extension)).select("path").collect()

    return [row.path for row in csv_files]


def load_ehr_data_to_delta(ehr_s3_path, database_name, aws_access_key=None, aws_secret_key=None):
    """
    Load all EHR CSV files from S3 into Delta tables using a database.

    Args:
        ehr_s3_path: S3 URI to directory containing EHR CSV files.
        database_name: Database name where tables will be stored.
        aws_access_key: AWS access key (optional).
        aws_secret_key: AWS secret key (optional).
    """
    # Create Spark session
    spark = create_spark_session(
        aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)

    # Define partition strategies for specific tables
    partition_config = {
        "patients.csv": ["gender"],
        "encounters.csv": ["year", "month"],
        "medications.csv": ["year"],
        "observations.csv": ["year", "month"],
        "procedures.csv": ["year"],
        "imaging_studies.csv": ["year"],
        "conditions.csv": ["year"],
        "immunizations.csv": ["year"],
        "allergies.csv": None,
        "careplans.csv": None,
        "organizations.csv": None,
        "providers.csv": None
    }

    # List all CSV files in the S3 directory
    s3_files = list_s3_files(spark, ehr_s3_path, ".csv")

    # Process each file
    results = {}

    for file_path in s3_files:
        file_name = file_path.split('/')[-1]
        if file_name.endswith(".csv"):
            table_name = file_name.split('.')[0]

            # Get partition columns if defined
            partition_by = partition_config.get(file_name)

            # Load file to Delta table in the database
            success = load_file_to_delta(
                spark, file_path, database_name, table_name, partition_by=partition_by)
            results[file_name] = success

    # Print summary
    print("\nSummary of Delta Lake table loading:")
    for file_name, success in results.items():
        status = "Success" if success else "Failed"
        print(f"{file_name}: {status}")

    return results


# Example usage
if __name__ == "__main__":
    # S3 paths
    database_name = "ehr"

    # Option 1: Using AWS credentials
    aws_access_key = "minioadmin"  # Replace with your key or use None
    aws_secret_key = "minioadmin"  # Replace with your key or use None

    # Update S3 path to use s3a protocol
    ehr_s3_path = "s3a://ehr/"
    # Configure additional S3 settings for MinIO
    spark = create_spark_session(
        aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)

    load_ehr_data_to_delta(ehr_s3_path, database_name,
                           aws_access_key, aws_secret_key)

    # Option 2: Using instance profile or environment variables
    # load_ehr_data_to_delta(ehr_s3_path, delta_s3_path)
