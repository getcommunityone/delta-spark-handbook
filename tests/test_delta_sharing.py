import os
import json
import pytest
import tempfile
import pandas as pd
import delta_sharing
from pyspark.sql import SparkSession
import requests
import time
import shutil


class TestDeltaSharing:
    """Test suite for Delta Sharing functionality."""

    @classmethod
    def setup_class(cls):
        """Set up test environment before running tests."""
        # Create a temporary profile file
        cls.temp_dir = tempfile.mkdtemp()
        cls.profile_path = os.path.join(
            cls.temp_dir, "delta_sharing_profile.json")

        # Write profile information to file
        profile_data = {
            "shareCredentialsVersion": 1,
            "endpoint": "http://localhost:7777",
            "bearerToken": "dapi0123456789"
        }

        # Define the base directory
        jars_home = '/workspace/delta-spark-handbook/delta-jars'

        # Required core JARs
        jars_list = [
            # Delta Lake
            f"{jars_home}/delta-spark_2.12-3.3.0.jar",
            f"{jars_home}/delta-storage-3.3.0.jar",
            # AWS
            f"{jars_home}/hadoop-aws-3.3.2.jar",
            f"{jars_home}/aws-java-sdk-bundle-1.12.610.jar",
            # Kyuubi
            f"{jars_home}/kyuubi/externals/engines/spark/kyuubi-spark-sql-engine_2.12-1.10.0.jar",
            f"{jars_home}/kyuubi/externals/engines/spark/kyuubi-common_2.12-1.10.0.jar"
        ]

        # Convert to comma-separated string
        jars = ",".join(jars_list)

        with open(cls.profile_path, "w") as f:
            json.dump(profile_data, f)

        # Initialize Spark session
        cls.spark = (SparkSession.builder
                     .appName("DeltaSharingTest")
                     # Add jars directly
                     .config("spark.jars", jars)
                     .config("spark.driver.extraClassPath", jars)
                     .config("spark.executor.extraClassPath", jars)
                     .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                     .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
                     .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")
                     .config("spark.hadoop.fs.s3a.access.key", "minioadmin")
                     .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")
                     .config("spark.hadoop.fs.s3a.path.style.access", "true")
                     .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
                     .getOrCreate())

        # Create test Delta table
        cls._create_test_delta_table()

        # Wait for Delta Sharing server to detect the new table
        time.sleep(2)

    @classmethod
    def teardown_class(cls):
        """Clean up after tests."""
        # Stop Spark session
        cls.spark.stop()

        # Remove temporary directory
        shutil.rmtree(cls.temp_dir)

    @classmethod
    def _create_test_delta_table(cls):
        """Create a test Delta table to share."""
        # Create a test dataframe
        test_data = [
            (1, "Alice", "Engineering", 90000.0),
            (2, "Bob", "Marketing", 85000.0),
            (3, "Charlie", "Sales", 75000.0),
            (4, "Diana", "Engineering", 95000.0),
            (5, "Eva", "HR", 70000.0)
        ]

        columns = ["id", "name", "department", "salary"]
        df = cls.spark.createDataFrame(test_data, columns)

        # Write to Delta format in MinIO bucket (wba)
        df.write.format("delta").mode("overwrite").save(
            "s3a://wba/warehouse/test_table")

        # Also create as a table in Spark catalog
        df.write.format("delta").mode(
            "overwrite").saveAsTable("test_employees")

    def test_server_health(self):
        """Test that the Delta Sharing server is healthy."""
        response = requests.get("http://localhost:7777/health")
        assert response.status_code == 200

    def test_list_shares(self):
        """Test listing of shares from the Delta Sharing server."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()

        # Verify we have at least one share
        assert len(shares) > 0

        # Check the first share has the expected structure
        first_share = shares[0]
        assert hasattr(first_share, "name")
        assert isinstance(first_share.name, str)

    def test_list_schemas(self):
        """Test listing schemas within a share."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()

        # Get the first share
        first_share = shares[0]

        # List schemas in the share
        schemas = client.list_schemas(first_share)

        # Verify we have at least one schema
        assert len(schemas) > 0

        # Check the schema has the expected structure
        first_schema = schemas[0]
        assert hasattr(first_schema, "name")
        assert isinstance(first_schema.name, str)

    def test_list_tables(self):
        """Test listing tables within a schema."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()
        schemas = client.list_schemas(shares[0])

        # List tables in the first schema
        tables = client.list_tables(schemas[0])

        # Verify we have at least one table
        assert len(tables) > 0

        # Check the table has the expected structure
        first_table = tables[0]
        assert hasattr(first_table, "name")
        assert isinstance(first_table.name, str)

    def test_read_table(self):
        """Test reading a table using Delta Sharing."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()
        schemas = client.list_schemas(shares[0])
        tables = client.list_tables(schemas[0])

        # Check if test_table exists among tables
        test_table = next(
            (t for t in tables if t.name == "test_employees"), None)
        if not test_table:
            pytest.skip("test_employees table not found in shared tables")

        # Read the table as pandas DataFrame
        table_url = f"{self.profile_path}#{shares[0].name}.{schemas[0].name}.{test_table.name}"
        df = delta_sharing.load_as_pandas(table_url)

        # Verify the dataframe structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "id" in df.columns
        assert "name" in df.columns
        assert "department" in df.columns
        assert "salary" in df.columns

        # Verify specific values
        assert 1 in df["id"].values

    def test_query_table(self):
        """Test querying a table with filtering."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()
        schemas = client.list_schemas(shares[0])
        tables = client.list_tables(schemas[0])

        table = tables[0]
        table_url = f"{self.profile_path}#{shares[0].name}.{schemas[0].name}.{table.name}"

        # Define a query with filtering
        query = "SELECT * FROM delta_sharing_table WHERE department = 'Engineering'"

        # Load with query
        df = delta_sharing.load_as_pandas(table_url, query=query)

        # Verify filtered results
        assert all(row["department"] == "Engineering" for _,
                   row in df.iterrows())

    def test_table_metadata(self):
        """Test retrieving metadata for a shared table."""
        client = delta_sharing.SharingClient(self.profile_path)
        shares = client.list_shares()
        schemas = client.list_schemas(shares[0])
        tables = client.list_tables(schemas[0])

        table = tables[0]
        table_url = f"{self.profile_path}#{shares[0].name}.{schemas[0].name}.{table.name}"

        # Get table metadata
        table_metadata = client.get_table_metadata(table)

        # Verify metadata structure
        assert hasattr(table_metadata, "protocol")
        assert hasattr(table_metadata, "metadata")

    def test_api_direct_access(self):
        """Test direct REST API access to Delta Sharing server."""
        headers = {"Authorization": f"Bearer dapi0123456789"}

        # List shares via REST API
        response = requests.get(
            "http://localhost:7777/shares", headers=headers)
        assert response.status_code == 200

        shares_data = response.json()
        assert "items" in shares_data
        assert len(shares_data["items"]) > 0

        # Get first share name
        share_name = shares_data["items"][0]["name"]

        # List schemas in that share
        response = requests.get(
            f"http://localhost:7777/shares/{share_name}/schemas", headers=headers)
        assert response.status_code == 200

        schemas_data = response.json()
        assert "items" in schemas_data

        # Check if we have schemas
        if len(schemas_data["items"]) > 0:
            schema_name = schemas_data["items"][0]["name"]

            # List tables in that schema
            response = requests.get(
                f"http://localhost:7777/shares/{share_name}/schemas/{schema_name}/tables",
                headers=headers
            )
            assert response.status_code == 200
