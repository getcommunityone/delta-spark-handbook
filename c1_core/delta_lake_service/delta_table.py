from pyspark.sql import functions as F

class DeltaTable:

    @staticmethod
    def infer_schema_from_file(spark, file_path, sample_size=1000):
        """
        Infer schema from a CSV file by reading a sample.
        """
        # Read a sample of the CSV file to infer schema
        sample_df = spark.read.option("header", "true").option(
            "inferSchema", "true").csv(file_path).limit(sample_size)
        return sample_df.schema

    @classmethod
    def load_file_to_delta(cls, spark, file_path, database_name, table_name, mode="overwrite", partition_by=None):
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
            schema = cls.infer_schema_from_file(spark, file_path)

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

