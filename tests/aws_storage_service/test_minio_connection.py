from minio import Minio
import logging
import urllib3
from urllib3.exceptions import MaxRetryError, ProtocolError
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import time
import urllib3
from minio import Minio
from minio.error import S3Error
from requests.exceptions import ConnectionError
from urllib3.exceptions import MaxRetryError, ProtocolError
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def test_minio_connection():
    """Test direct connection to MinIO using the MinIO client."""
    try:
        urllib3.disable_warnings()

        # Create MinIO client
        logger.info("Creating MinIO client...")
        client = Minio(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False,  # HTTP
            region="us-east-1"
        )

        # Test connection with retries
        max_retries = 3
        retry_delay = 2
        for attempt in range(max_retries):
            try:
                logger.info(f"Testing connection (attempt {attempt + 1}/{max_retries})...")
                buckets = client.list_buckets()
                bucket_names = [b.name for b in buckets]
                logger.info(f"Success! Found buckets: {bucket_names}")
                break
            except (S3Error, MaxRetryError, ProtocolError, ConnectionError) as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("All retry attempts failed.")
                    raise

        # Create test bucket if it doesn’t exist
        test_bucket = "test-bucket"
        if not client.bucket_exists(test_bucket):
            client.make_bucket(test_bucket)
            logger.info(f"Bucket '{test_bucket}' created.")
        else:
            logger.info(f"Bucket '{test_bucket}' already exists.")

        # List objects in the bucket
        logger.info(f"Listing objects in bucket: {test_bucket}")
        objects = client.list_objects(test_bucket)
        object_names = [obj.object_name for obj in objects]
        logger.info(f"Bucket contents: {object_names}")

        assert len(object_names) == 0, "Bucket should be empty after creation"

    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    test_minio_connection() 