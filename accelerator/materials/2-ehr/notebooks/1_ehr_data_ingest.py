from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType, DoubleType
import os
from datetime import datetime
from pyspark.sql import functions as F
from urllib.parse import urlparse

import boto3
from botocore import UNSIGNED
from botocore.config import Config
import time

def create_spark_session(app_name="EHR Data Loader", aws_access_key=None, aws_secret_key=None):
    """
    Create and return a Spark session configured for Delta Lake with S3 access.
    """
    # Stop any existing Spark session
    try:
        SparkSession.builder.getOrCreate().stop()
        print("Stopped existing Spark session")
    except:
        print("No existing Spark session to stop")

    # Define the base directory for JAR files
    jars_home = os.path.join(os.getcwd(), 'delta-jars')
    if not os.path.exists(jars_home):
        raise Exception(f"JAR directory not found at: {jars_home}")

    # Required JARs
    jar_locations = [
        f"{jars_home}/delta-spark_2.12-3.3.0.jar",
        f"{jars_home}/delta-storage-3.3.0.jar",
        f"{jars_home}/hadoop-aws-3.3.4.jar",
        f"{jars_home}/bundle-2.24.12.jar",
        # Add Hadoop client JARs
        f"{jars_home}/hadoop-client-3.4.1.jar",
        f"{jars_home}/hadoop-client-runtime-3.4.1.jar",
        f"{jars_home}/hadoop-client-api-3.4.1.jar"
    ]

    # Verify all JARs exist
    for jar in jar_locations:
        if not os.path.exists(jar):
            raise Exception(f"Required JAR not found: {jar}")

    # Create Hadoop configuration directory
    hadoop_conf_dir = "hadoop-conf"
    os.makedirs(hadoop_conf_dir, exist_ok=True)

    # Write core-site.xml with S3 configuration
    core_site_xml = f"""<?xml version="1.0"?>
<configuration>
    <property>
        <name>fs.s3a.impl</name>
        <value>org.apache.hadoop.fs.s3a.S3AFileSystem</value>
    </property>
    <property>
        <name>fs.s3a.endpoint</name>
        <value>http://localhost:9000</value>
    </property>
    <property>
        <name>fs.s3a.access.key</name>
        <value>{aws_access_key or 'minioadmin'}</value>
    </property>
    <property>
        <name>fs.s3a.secret.key</name>
        <value>{aws_secret_key or 'minioadmin'}</value>
    </property>
    <property>
        <name>fs.s3a.path.style.access</name>
        <value>true</value>
    </property>
    <property>
        <name>fs.s3a.connection.ssl.enabled</name>
        <value>false</value>
    </property>
</configuration>"""

    with open(f"{hadoop_conf_dir}/core-site.xml", "w") as f:
        f.write(core_site_xml)

    # Set environment variables
    os.environ["HADOOP_CONF_DIR"] = os.path.abspath(hadoop_conf_dir)
    os.environ["SPARK_HOME"] = "/opt/spark"
    os.environ["SPARK_CLASSPATH"] = ":".join(
        [os.path.abspath(jar) for jar in jar_locations])
    os.environ["HADOOP_CLASSPATH"] = os.environ["SPARK_CLASSPATH"]

    # Create Spark session with comprehensive configuration
    builder = (SparkSession.builder
               .appName(app_name)
               .master("local[*]")
               #.master("spark://localhost:7077") 
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
               .config("spark.sql.catalogImplementation", "hive")
               .config("spark.hadoop.javax.jdo.option.ConnectionURL", "jdbc:postgresql://localhost:5432/metastore_db")
               .config("spark.hadoop.javax.jdo.option.ConnectionDriverName", "org.postgresql.Driver")
               .config("spark.hadoop.javax.jdo.option.ConnectionUserName", "admin")
               .config("spark.hadoop.javax.jdo.option.ConnectionPassword", "admin")
               .config("spark.hadoop.hive.metastore.uris", "thrift://localhost:9083")
               .config("spark.sql.warehouse.dir", "s3a://wba/warehouse")
               .config("spark.driver.extraClassPath", ":".join([os.path.abspath(jar) for jar in jar_locations]))
               .config("spark.executor.extraClassPath", ":".join([os.path.abspath(jar) for jar in jar_locations]))
               .config("spark.jars.excludes", "org.slf4j:slf4j-log4j12,org.slf4j:slf4j-reload4j,org.slf4j:log4j-slf4j-impl")
               .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
               .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
               .config("spark.hadoop.fs.s3a.access.key", aws_access_key or "minioadmin")
               .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key or "minioadmin")
               .config("spark.hadoop.fs.s3a.path.style.access", "true")
               .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
               .config("spark.hadoop.fs.s3a.fast.upload", "true")
               .config("spark.hadoop.fs.s3a.multipart.size", "5242880")
               .config("spark.hadoop.fs.s3a.block.size", "5242880")
               .config("spark.hadoop.fs.s3a.multipart.threshold", "5242880")
               .config("spark.hadoop.fs.s3a.threads.core", "10")
               .config("spark.hadoop.fs.s3a.threads.max", "20")
               .config("spark.hadoop.fs.s3a.max.total.tasks", "50")
               .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
               .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
               .config("spark.hadoop.fs.s3a.socket.timeout", "60000")
               .config("spark.hadoop.fs.s3a.connection.maximum", "50")
               .config("spark.hadoop.fs.s3a.fast.upload.buffer", "bytebuffer")
               .config("spark.hadoop.fs.s3a.fast.upload.active.blocks", "2")
               .config("spark.hadoop.fs.s3a.multipart.purge", "false")
               .config("spark.hadoop.fs.s3a.multipart.purge.age", "86400000")
               .config("spark.hadoop.fs.s3a.retry.limit", "10")
               .config("spark.hadoop.fs.s3a.retry.interval", "1000")
               .config("spark.hadoop.fs.s3a.attempts.maximum", "10")
               .config("spark.hadoop.fs.s3a.connection.request.timeout", "60000")
               .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60000")
               .enableHiveSupport())

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

    full_table_name = "unknown"

    try:



        # Infer schema from file
        schema = infer_schema_from_file(spark, file_path)

        # Read the CSV file with the inferred schema
        df = spark.read.option("header", "true").schema(schema).csv(file_path)

        # Convert all column names to lowercase
        for col_name in df.columns:
            df = df.withColumnRenamed(col_name, col_name.lower())

        if "start" in df.columns:

            df = df.withColumn("start_date", F.to_date(
                F.col("start"), "yyyy-MM-dd"))

            df = df.withColumn("year", F.year(F.col("start_date")))
            df = df.withColumn("month", F.month(F.col("start_date")))

        # Ensure DATE is properly converted to a date type
        if "date" in df.columns:
            df = df.withColumn("date", F.to_date(F.col("date"), "yyyy-MM-dd"))
            df = df.withColumn("year", F.year(F.col("date")))
            df = df.withColumn("month", F.month(F.col("date")))

        # Add metadata columns
        df = df.withColumn("ingestion_timestamp", F.current_timestamp())
        df = df.withColumn("source_file", F.lit(file_path.split('/')[-1]))

        # Define the full table name
        full_table_name = f"{database_name}.{table_name}"

        # Write to Delta Lake using saveAsTable

        writer = df.write.format("delta").mode(
            mode).option("overwriteSchema", "true").option("delta.compatibility.symlinkFormatManifest.enabled", "false")

        if partition_by:
            writer = writer.partitionBy(partition_by)

        # Get warehouse dir from Spark config
        warehouse_dir = spark.conf.get("spark.sql.warehouse.dir").rstrip("/")

        # Format: {warehouse_dir}/{database}.db/{table}
        table_path = f"{warehouse_dir}/{database_name}.db/{table_name}"

        print(f"📁 Calculated table path: {table_path}")


        # writer.saveAsTable(full_table_name)
        writer.save(table_path)

        # Then create/refresh the table definition pointing to that location
        spark.sql(f"""
         CREATE TABLE IF NOT EXISTS {database_name}.{table_name}
            USING DELTA
             LOCATION '{table_path}'
         """)

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
        "providers.csv": None,
        "devices.csv": None,
        "supplies.csv": None,
        "payer_transitions.csv": None,
        "payers.csv": None
    }
    
    # Download Files
    vocab_s3_path = "s3://hls-eng-data-public/data/synthea/"

    parsed = urlparse(vocab_s3_path)
    bucket = parsed.netloc
    prefix = parsed.path.lstrip('/').rstrip('/')

    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    available_keys = [obj['Key'] for obj in response.get('Contents', [])]

    start_time = time.time()
    for key in available_keys:
        print("⏳ Downloading from S3...")
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_content = response['Body'].read()
        download_time = time.time()
        print(f"✅ Download complete in {download_time - start_time:.2f}s")

        # Save raw .csv.gz file to MinIO
        raw_key = key
        print(f"📤 Saving raw .csv to MinIO: {raw_key}...")
        s3_minio = boto3.client(
            "s3",
            endpoint_url="http://localhost:9000",  # adjust to your MinIO endpoint
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin"
        )
        s3_minio.put_object(
            Bucket=f"{database_name}",
            Key=raw_key,
            Body=csv_content
        )
        print("✅ Raw .csv saved to MinIO.")
        
        
    # List all CSV files in the S3 directory
    s3_files = list_s3_files(spark, ehr_s3_path, ".csv")

    
    # Process each file
    results = {}

    spark.sql(f"DROP DATABASE IF EXISTS {database_name} CASCADE")
    
    # Ensure the database exists
    spark.sql(
        f"CREATE DATABASE IF NOT EXISTS {database_name} ")
    
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

    load_ehr_data_to_delta(ehr_s3_path, database_name,
                           aws_access_key, aws_secret_key)

    # Option 2: Using instance profile or environment variables
    # load_ehr_data_to_delta(ehr_s3_path, delta_s3_path)
