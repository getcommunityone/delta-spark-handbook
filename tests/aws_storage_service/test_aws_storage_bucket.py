import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
import sys
import os
import boto3
import logging
import time
from botocore.config import Config
from botocore import UNSIGNED

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from c1_core.aws_storage_service.aws_storage_bucket import AwsStorageBucket

# Import test configuration from conftest.py
from tests.conftest import S3_LOCAL_BUCKET, MINIO_BUCKET, TEST_PREFIX, TEST_DATA

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_s3_access():
    """Verify S3 bucket and prefix accessibility."""
    try:
        # Setup S3 client for public access
        s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
        
        # Try to list objects with the prefix
        logger.info(f"Verifying access to S3 bucket: {S3_LOCAL_BUCKET} and prefix: {TEST_PREFIX}")
        response = s3.list_objects_v2(
            Bucket=S3_LOCAL_BUCKET,
            Prefix=TEST_PREFIX
        )
        
        if 'Contents' not in response or len(response['Contents']) == 0:
            logger.error(f"No files found in prefix {TEST_PREFIX}")
            return False
            
        logger.info(f"Found {len(response['Contents'])} files in prefix {TEST_PREFIX}")
        for obj in response['Contents']:
            logger.info(f"Found file: {obj['Key']}")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying S3 access: {str(e)}", exc_info=True)
        return False

def setup_minio():
    """Setup MinIO client and bucket."""
    try:
        # Create MinIO client with proper configuration
        logger.info("Setting up MinIO client...")
        minio_endpoint = "http://localhost:9000"  # Use localhost since running on host
        logger.info(f"Using endpoint: {minio_endpoint}")
        logger.info(f"Using bucket: {MINIO_BUCKET}")
        
        # Configure the client with more robust settings
        config = Config(
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            },
            connect_timeout=10,
            read_timeout=20,
            s3={
                'addressing_style': 'path',
                'payload_signing_enabled': False,
                'use_accelerate_endpoint': False
            }
        )
        
        client = boto3.client(
            "s3",
            endpoint_url=minio_endpoint,  # Use localhost since running on host
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=config,
            region_name="us-east-1"  # Required for MinIO
        )
        
        # Test connection with retry
        logger.info("Testing MinIO connection...")
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Connection attempt {attempt + 1}/{max_retries}")
                response = client.list_buckets()
                buckets = [b['Name'] for b in response.get('Buckets', [])]
                logger.info(f"Successfully connected to MinIO. Found buckets: {buckets}")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to MinIO after {max_retries} attempts: {str(e)}", exc_info=True)
                    logger.error(f"Error type: {type(e).__name__}")
                    if hasattr(e, 'response'):
                        logger.error(f"Error response: {e.response}")
                    return None
                logger.warning(f"Connection attempt {attempt + 1} failed, retrying...")
                time.sleep(2)  # Wait before retrying
        
        # Check if bucket exists first
        try:
            logger.info(f"Checking if MinIO bucket exists: {MINIO_BUCKET}")
            client.head_bucket(Bucket=MINIO_BUCKET)
            logger.info(f"MinIO bucket {MINIO_BUCKET} already exists")
            return client
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    logger.info(f"Creating MinIO bucket: {MINIO_BUCKET}")
                    client.create_bucket(
                        Bucket=MINIO_BUCKET,
                        CreateBucketConfiguration={
                            'LocationConstraint': 'us-east-1'  # Required for MinIO
                        }
                    )
                    logger.info(f"Successfully created MinIO bucket: {MINIO_BUCKET}")
                except ClientError as create_error:
                    if create_error.response['Error']['Code'] != 'BucketAlreadyExists':
                        logger.error(f"Error creating bucket: {str(create_error)}", exc_info=True)
                        logger.error(f"Error response: {create_error.response}")
                        return None
                    logger.info(f"MinIO bucket {MINIO_BUCKET} already exists")
            else:
                logger.error(f"Error checking bucket: {str(e)}", exc_info=True)
                logger.error(f"Error response: {e.response}")
                return None
            
            return client
            
        except Exception as e:
            logger.error(f"Error checking/creating bucket: {str(e)}", exc_info=True)
            logger.error(f"Error type: {type(e).__name__}")
            if hasattr(e, 'response'):
                logger.error(f"Error response: {e.response}")
            return None
            
    except Exception as e:
        logger.error(f"Error setting up MinIO: {str(e)}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        if hasattr(e, 'response'):
            logger.error(f"Error response: {e.response}")
        return None

@pytest.fixture(scope="session")
def minio_client():
    """Create a real MinIO client for testing."""
    logger.info("Initializing MinIO client fixture...")
    client = setup_minio()
    if client is None:
        logger.error("Failed to setup MinIO client")
        pytest.skip("Failed to setup MinIO. Skipping tests.")
    logger.info("Successfully initialized MinIO client")
    return client


@pytest.mark.integration
def test_successful_download():
    """Test successful download of multiple files from S3 to MinIO."""
    logger.info("Starting successful download test")
    
    # Verify S3 access first
    if not verify_s3_access():
        pytest.skip("S3 bucket or prefix not accessible. Skipping test.")
    
    # Log test configuration
    logger.info(f"Using S3 bucket: {S3_LOCAL_BUCKET}")
    logger.info(f"Using MinIO bucket: {MINIO_BUCKET}")
    logger.info(f"Using test prefix: {TEST_PREFIX}")
    
    # Execute the method
    try:
        logger.info("Starting download from S3 to MinIO...")
        result = AwsStorageBucket.download_files_from_s3_to_minio(
            minio_bucket_name=MINIO_BUCKET,
            s3_path=f"s3://{S3_LOCAL_BUCKET}/{TEST_PREFIX}/",
            data_product_id="test-product",
            environment="test",
            minio_endpoint="http://localhost:9000",  # Use localhost since running on host
            minio_access_key="minioadmin",
            minio_secret_key="minioadmin"
        )
        
        logger.info(f"Download result: {result}")
        
        # Verify the result
        assert result is not None, "Result is None. Ensure the method returns a valid dictionary."
        assert isinstance(result, dict), f"Expected result to be a dictionary, got {type(result)}"
        assert result.get("success") is True, f"Expected success=True, got {result.get('success')}"
        assert "total_files" in result, f"Missing 'total_files' in result: {result}"
        assert "successful_files" in result, f"Missing 'successful_files' in result: {result}"
        assert "failed_files" in result, f"Missing 'failed_files' in result: {result}"
        assert result["failed_files"] == 0, f"Expected failed_files=0, got {result.get('failed_files')}"
        assert result["successful_files"] > 0, f"Expected successful_files>0, got {result.get('successful_files')}"
        assert "total_time" in result, f"Missing 'total_time' in result: {result}"
        assert isinstance(result["total_time"], str), f"Expected total_time to be string, got {type(result.get('total_time'))}"
        assert result["total_time"].endswith("s"), f"Expected total_time to end with 's', got {result.get('total_time')}"
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise

@pytest.mark.integration
def test_no_files_found(minio_client):
    """Test when no files are found in the S3 bucket."""
    # Execute the method with non-existent prefix
    result = AwsStorageBucket.download_files_from_s3_to_minio(
        minio_bucket_name=MINIO_BUCKET,
        s3_path=f"s3://{S3_LOCAL_BUCKET}/non-existent-prefix/",
        data_product_id="test-product",
        environment="test",
        minio_endpoint="http://localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadmin"
    )

    # Verify the result
    assert result["success"] is False
    assert result["files_processed"] == 0
    assert "No files found" in result["message"]
    
@pytest.mark.integration
def test_list_s3_files_boto_success():
    """Test successful listing of files in S3 bucket using list_s3_files_boto."""
    logger.info("Starting test for list_s3_files_boto with valid S3 path")

    # Execute the method
    try:
        logger.info("Listing files in S3 bucket...")
        files = AwsStorageBucket.list_s3_files_boto(
            s3_dir_path=f"s3://{S3_LOCAL_BUCKET}/{TEST_PREFIX}/",
            file_extension=".csv",
            data_product_id="test-product",
            environment="test",
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin"
        )

        logger.info(f"Files listed: {files}")

        # Verify the result
        assert isinstance(files, list), f"Expected list, got {type(files)}"
        assert len(files) > 0, "Expected at least one file, but found none"
        for file in files:
            assert file.endswith(".csv"), f"File {file} does not have the expected .csv extension"

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


@pytest.mark.integration
def test_list_s3_files_boto_no_files_found(minio_client):
    """Test list_s3_files_boto when no files are found in the S3 bucket."""
    logger.info("Starting test for list_s3_files_boto with non-existent prefix")

    # Execute the method with non-existent prefix
    try:
        files = AwsStorageBucket.list_s3_files_boto(
            s3_dir_path=f"s3://{S3_LOCAL_BUCKET}/non-existent-prefix/",
            file_extension=".csv",
            data_product_id="test-product",
            environment="test",
            public_access=True
        )

        logger.info(f"Files listed: {files}")

        # Verify the result
        assert isinstance(files, list), f"Expected list, got {type(files)}"
        assert len(files) == 0, f"Expected no files, but found {len(files)}"

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


@pytest.mark.integration
def test_list_s3_files_boto_invalid_path(minio_client):
    """Test list_s3_files_boto with an invalid S3 path."""
    logger.info("Starting test for list_s3_files_boto with invalid S3 path")

    # Execute the method with an invalid S3 path
    invalid_path = "invalid-s3-path"
    try:
        with pytest.raises(ValueError, match="Invalid S3 path"):
            AwsStorageBucket.list_s3_files_boto(
                s3_dir_path=invalid_path,
                file_extension=".csv",
                data_product_id="test-product",
                environment="test",
                public_access=True
            )

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


@pytest.mark.integration
def test_list_s3_files_boto_invalid_credentials(minio_client):
    """Test list_s3_files_boto with invalid AWS credentials."""
    logger.info("Starting test for list_s3_files_boto with invalid AWS credentials")

    # Execute the method with invalid credentials
    try:
        with pytest.raises(Exception, match="InvalidAccessKeyId|SignatureDoesNotMatch"):
            AwsStorageBucket.list_s3_files_boto(
                s3_dir_path=f"s3://{S3_LOCAL_BUCKET}/{TEST_PREFIX}/",
                file_extension=".csv",
                data_product_id="test-product",
                environment="test",
                aws_access_key_id="invalid_key",
                aws_secret_access_key="invalid_secret",
                public_access=False
            )

    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}", exc_info=True)
        raise


