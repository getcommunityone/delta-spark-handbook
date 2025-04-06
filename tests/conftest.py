import pytest
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from botocore import UNSIGNED
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
S3_LOCAL_BUCKET = "omop531"
S3_BUCKET = "hls-eng-data-public"  # Public S3 bucket to read from
MINIO_BUCKET = "ehr"  # MinIO bucket to write to
TEST_PREFIX = "data/synthea"  # Removed leading slash
TEST_DATA = b"test content"

@pytest.fixture(scope="session")
def s3_client():
    """Create a real S3 client for testing."""
    config = Config(
        signature_version=UNSIGNED,
        retries={'max_attempts': 3},
        connect_timeout=5,
        read_timeout=10
    )
    return boto3.client('s3', config=config)

@pytest.fixture(scope="session")
def minio_client():
    """Create a real MinIO client for testing."""
    client = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin"
    )
    
    # Create test bucket if it doesn't exist
    try:
        client.create_bucket(Bucket=MINIO_BUCKET)
        logger.info(f"Created MinIO bucket: {MINIO_BUCKET}")
    except ClientError as e:
        if e.response['Error']['Code'] != 'BucketAlreadyExists':
            raise
        logger.info(f"MinIO bucket {MINIO_BUCKET} already exists")
    
    return client

@pytest.fixture(scope="session")
def test_files(s3_client):
    """Get list of test files from public S3 bucket."""
    try:
        logger.info(f"Listing files from S3 bucket {S3_BUCKET} with prefix {TEST_PREFIX}")
        response = s3_client.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=TEST_PREFIX
        )
        test_files = [obj['Key'] for obj in response.get('Contents', [])]
        logger.info(f"Found {len(test_files)} files in S3")
        return test_files
    except ClientError as e:
        logger.error(f"Error listing files from S3: {e}")
        raise 