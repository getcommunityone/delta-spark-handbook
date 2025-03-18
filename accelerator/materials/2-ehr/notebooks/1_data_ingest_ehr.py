from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType, TimestampType, DoubleType
import os
from datetime import datetime
from pyspark.sql import functions as F


<<<<<<< HEAD
def create_spark_session():
    """Create a Spark session configured for Delta Lake with S3 access."""
    # Stop any existing Spark session
    try:
        spark.stop()
    except:
        pass

    # Define JAR locations
    jars_home = os.path.join(os.getcwd(), 'delta-jars')
    required_jars = [
        'delta-spark_2.12-3.3.0.jar',
        'delta-storage-3.3.0.jar',
        'hadoop-aws-3.3.4.jar',
        'aws-java-sdk-bundle-1.12.782.jar',
        'postgresql-42.7.3.jar'  # Added PostgreSQL JDBC driver
    ]

    # Verify all required JARs exist
    for jar in required_jars:
        jar_path = os.path.join(jars_home, jar)
        if not os.path.exists(jar_path):
            raise Exception(f"Required JAR not found: {jar_path}")

    # Create Hadoop configuration directory
    hadoop_conf_dir = os.path.join(os.getcwd(), 'hadoop-conf')
    os.makedirs(hadoop_conf_dir, exist_ok=True)

    # Write core-site.xml with S3 configuration
    core_site_xml = os.path.join(hadoop_conf_dir, 'core-site.xml')
    with open(core_site_xml, 'w') as f:
        f.write('''<?xml version="1.0"?>
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
        <value>minioadmin</value>
    </property>
    <property>
        <name>fs.s3a.secret.key</name>
        <value>minioadmin</value>
    </property>
    <property>
        <name>fs.s3a.path.style.access</name>
        <value>true</value>
    </property>
</configuration>''')

    # Set environment variables
    os.environ['HADOOP_CONF_DIR'] = hadoop_conf_dir
    os.environ['SPARK_HOME'] = '/opt/spark'
    os.environ['SPARK_CLASSPATH'] = os.pathsep.join([os.path.join(jars_home, jar) for jar in required_jars])
    os.environ['HADOOP_CLASSPATH'] = os.environ['SPARK_CLASSPATH']

    # Create Spark session
    spark = SparkSession.builder \
        .appName("Delta Lake EHR Data Ingestion") \
        .master("local[*]") \
        .config("spark.jars", ",".join([os.path.join(jars_home, jar) for jar in required_jars])) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.delta.logStore.class", "io.delta.storage.S3SingleDriverLogStore") \
        .config("spark.hadoop.fs.s3a.fast.upload", "true") \
        .config("spark.hadoop.fs.s3a.multipart.size", "104857600") \
        .config("spark.sql.warehouse.dir", "s3a://wba/warehouse") \
        .config("spark.sql.catalogImplementation", "hive") \
        .config("spark.hadoop.javax.jdo.option.ConnectionURL", "jdbc:postgresql://localhost:5432/metastore_db") \
        .config("spark.hadoop.javax.jdo.option.ConnectionDriverName", "org.postgresql.Driver") \
        .config("spark.hadoop.javax.jdo.option.ConnectionUserName", "admin") \
        .config("spark.hadoop.javax.jdo.option.ConnectionPassword", "admin") \
        .config("spark.driver.extraClassPath", os.pathsep.join([os.path.join(jars_home, jar) for jar in required_jars])) \
        .config("spark.executor.extraClassPath", os.pathsep.join([os.path.join(jars_home, jar) for jar in required_jars])) \
        .getOrCreate()

    return spark
=======
def create_spark_session(app_name="EHR Data Loader", aws_access_key=None, aws_secret_key=None):
    """
    Create and return a Spark session configured for Delta Lake with S3 access.
    """

    try:
        SparkSession.builder.getOrCreate().stop()
        print("Stopped existing Spark session")
    except:
        print("No existing Spark session to stop")

    # Define the base directory
    # First try to find JAR files in various locations
    possible_jar_locations = [
        os.path.join(os.getcwd(), 'delta-jars'),  # Current directory
        os.path.join(os.path.dirname(os.getcwd()), 'delta-jars'),  # Parent directory
        '/workspace/delta-jars',              # Inside Docker
        '/workspace/delta-spark-handbook/delta-jars'  # Inside Docker

    ]
    
    # Try to find the jars directory
    jars_home = None
    for location in possible_jar_locations:
        if os.path.exists(location):
            print(f"Found JAR directory at: {location}")
            jars_home = location
            break

    # Required core JARs
    jars_list = [
        # Delta Lake
        f"{jars_home}/delta-spark_2.12-3.3.0.jar",
        f"{jars_home}/delta-storage-3.3.0.jar",
        # AWS
        f"{jars_home}/hadoop-aws-3.3.4.jar",
        f"{jars_home}/aws-java-sdk-bundle-1.12.782.jar",
        # Kyuubi
        f"{jars_home}/kyuubi-spark-sql-engine_2.12-1.10.0.jar",
        f"{jars_home}/kyuubi-common_2.12-1.10.0.jar"
    ]

    # Convert to comma-separated string
    jars = ",".join(jars_list)

    builder = (SparkSession.builder
               .appName(app_name)
               .master("local[*]")
               # .config("spark.jars.packages", packages_string)
               .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
               .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
               .config("spark.jars.excludes", "org.slf4j:slf4j-log4j12")
               .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
               .config("spark.jars", jars)
               .config("spark.driver.extraClassPath", jars)
               .config("spark.executor.extraClassPath", jars)
               .config("spark.sql.warehouse.dir", "s3a://delta")
               .config("spark.hadoop.hive.metastore.uris", "thrift://hive-metastore:9083")
               .enableHiveSupport()
               )

    # Configure S3 access if credentials are provided
    if aws_access_key and aws_secret_key:
        builder = (builder
                   .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000")
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
>>>>>>> origin/dev-r1


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
<<<<<<< HEAD
    """
    full_table_name = "unknown"

    try:
        # Ensure the database exists
        spark.sql(f"CREATE DATABASE IF NOT EXISTS {database_name}")
=======

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

        # Ensure the database exists
        spark.sql(
            f"CREATE DATABASE IF NOT EXISTS {database_name} LOCATION 's3a://delta/{database_name}/{database_name}.db'")

        table_path = f"s3a://delta/{database_name}/{table_name}"
>>>>>>> origin/dev-r1

        # Infer schema from file
        schema = infer_schema_from_file(spark, file_path)

        # Read the CSV file with the inferred schema
        df = spark.read.option("header", "true").schema(schema).csv(file_path)

        # Convert all column names to lowercase
        for col_name in df.columns:
            df = df.withColumnRenamed(col_name, col_name.lower())

        if "start" in df.columns:
<<<<<<< HEAD
            df = df.withColumn("start_date", F.to_date(F.col("start"), "yyyy-MM-dd"))
=======
            df = df.withColumn("start_date", F.to_date(
                F.col("start"), "yyyy-MM-dd"))
>>>>>>> origin/dev-r1
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
<<<<<<< HEAD
        writer = df.write.format("delta").mode(mode).option("overwriteSchema", "true")
=======
        writer = df.write.format("delta").mode(
            mode).option("overwriteSchema", "true").option("delta.compatibility.symlinkFormatManifest.enabled", "false")
>>>>>>> origin/dev-r1

        if partition_by:
            writer = writer.partitionBy(partition_by)

<<<<<<< HEAD
        writer.saveAsTable(full_table_name)
=======
        # writer.saveAsTable(full_table_name)
        writer.save(table_path)

        # Then create/refresh the table definition pointing to that location
        spark.sql(f"""
            CREATE TABLE IF NOT EXISTS {database_name}.{table_name}
            USING DELTA
            LOCATION '{table_path}'
        """)
>>>>>>> origin/dev-r1

        print(f"Successfully loaded {file_path} into table {full_table_name}")
        return True
    except Exception as e:
<<<<<<< HEAD
        print(f"Error loading {file_path} into table {full_table_name}: {str(e)}")
=======
        print(
            f"Error loading {file_path} into table {full_table_name}: {str(e)}")
>>>>>>> origin/dev-r1
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
<<<<<<< HEAD
    spark = create_spark_session()
=======
    spark = create_spark_session(
        aws_access_key=aws_access_key, aws_secret_key=aws_secret_key)
>>>>>>> origin/dev-r1

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
 
    load_ehr_data_to_delta(ehr_s3_path, database_name,
                           aws_access_key, aws_secret_key)

    # Option 2: Using instance profile or environment variables
    # load_ehr_data_to_delta(ehr_s3_path, delta_s3_path)
