from pyspark.sql import SparkSession

class DeltaSession:
    @staticmethod
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

        # Define the base directory
        jars_home = '/home/developer/projects/delta-spark-handbook/delta-jars'

        # Required core JARs
        jars_list = [
            # Delta Lake
            f"{jars_home}/delta-spark_2.12-3.3.0.jar",
            f"{jars_home}/delta-storage-3.3.0.jar",
            # AWS
            f"{jars_home}/hadoop-aws-3.3.4.jar",
            f"{jars_home}/bundle-2.24.12.jar",
            # Kyuubi
            f"{jars_home}/kyuubi-spark-sql-engine_2.12-1.10.0.jar",
            f"{jars_home}/kyuubi-common_2.12-1.10.0.jar"
        ]

        # Convert to comma-separated string
        jars = ",".join(jars_list)

        # Create SparkSession using the builder pattern
        builder = (SparkSession.builder
                .appName(app_name)
                .master("local[*]")
                # Add debug configurations
                .config("spark.hadoop.fs.s3a.connection.maximum", "1")
                .config("spark.hadoop.fs.s3a.attempts.maximum", "1")
                .config("spark.hadoop.fs.s3a.connection.timeout", "5000")
                .config("spark.hadoop.fs.s3a.impl.disable.cache", "true")
                .config("spark.hadoop.fs.s3a.debug.detailed.exceptions", "true")
                
                # Add jars directly
                .config("spark.jars", jars)
                .config("spark.driver.extraClassPath", jars)
                .config("spark.executor.extraClassPath", jars)
                # Delta Lake configurations
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                # S3/MinIO configurations
                .config("spark.hadoop.fs.s3a.access.key", aws_access_key)
                .config("spark.hadoop.fs.s3a.secret.key", aws_secret_key)
                .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
                .config("spark.hadoop.fs.s3a.path.style.access", "true")
                .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
                .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
                .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
                # Additional Delta Lake configurations
                .config("spark.delta.logStore.class", "io.delta.storage.S3SingleDriverLogStore")
                .config("spark.hadoop.fs.s3a.fast.upload", "true")
                .config("spark.hadoop.fs.s3a.multipart.size", "104857600")
                .config("spark.sql.warehouse.dir", "s3a://wba/warehouse")
                .enableHiveSupport()
                .config("hive.metastore.uris", "thrift://localhost:9083")
                # Disable Derby
                .config("spark.hadoop.javax.jdo.option.ConnectionURL", "")  # Empty to prevent Derby initialization
                )

        spark = builder.getOrCreate()
    
        return spark
