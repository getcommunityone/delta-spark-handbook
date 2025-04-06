"""
AwsStorageFile.download_file_from_s3_to_local(
    bucket_name='my-bucket',
    s3_object_key='path/to/s3/object',
    local_file_path='path/to/local/file',
    data_product_id='your-data-product-id'
)
Usage Example:
    # Specify the S3 bucket details and local file path
    bucket_name = 'my-bucket'  # Replace with your S3 bucket name
    s3_object_key = 'path/to/s3/object'  # Replace with the path to your S3 object
    local_file_path = 'path/to/local/file'  # Replace with the desired local path for the downloaded file

    # Call the static method to download the file
    AwsStorageFile.download_file_from_s3(bucket_name, s3_object_key, local_file_path)

Note:
    The module requires the installation of boto3 packages.
    Ensure that AWS credentials are configured properly for boto3 to access the specified S3 bucket.
"""

import gzip
import io
import os
import sys
import tempfile
import time
from urllib.parse import urlparse
import boto3
import botocore
from botocore.config import Config
from botocore import UNSIGNED

from c1_core.c1_log_service.environment_logging import LoggerSingleton
from azure.storage.filedatalake import DataLakeServiceClient

OS_NAME = os.name
sys.path.append("../..")

if OS_NAME.lower() == "nt":
    print("environment_logging: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("environment_logging: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


# Get the currently running file name
NAMESPACE_NAME = os.path.basename(os.path.dirname(__file__))
# Get the parent folder name of the running file
SERVICE_NAME = os.path.basename(__file__)


class AwsStorageFile:
    """
    This module provides a class for downloading files from an S3 bucket.

    Usage:
        bucket_name = 'my-bucket'  # Replace with your S3 bucket name
        s3_object_key = 'path/to/s3/object'  # Replace with the path to your S3 object
        local_file_path = 'path/to/local/file'  # Replace with the desired local path for the downloaded file

        AwsStorageFile.download_file_from_s3(bucket_name, s3_object_key, local_file_path)
    """

    @staticmethod
    def download_file_from_s3_to_adls(
        s3_bucket,
        s3_key,
        adls_account_name,
        adls_file_system,
        adls_directory,
        adls_file_name,
        azure_storage_sas_token,
    ):
        """
        Downloads a file from Amazon S3 and uploads it to Azure Data Lake Storage.

        Args:
            s3_bucket (str): The name of the Amazon S3 bucket.
            s3_key (str): The key of the object in the Amazon S3 bucket.
            adls_account_name (str): The name of the Azure Data Lake Storage account.
            adls_file_system (str): The name of the Azure Data Lake Storage file system.
            adls_directory (str): The directory path in Azure Data Lake Storage.
            adls_file_name (str): The name of the file in Azure Data Lake Storage.
            azure_storage_sas_token (str): The SAS token for accessing Azure Storage.

        Returns:
            str: The success message indicating that the file was uploaded successfully.
        """

        # Initialize S3 client
        s3_client = boto3.client("s3")

        # Get the object from S3
        s3_object = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        data_stream = s3_object["Body"].read()

        # Initialize ADLS client
        service_client = DataLakeServiceClient(
            account_url=f"https://{adls_account_name}.dfs.core.windows.net",
            credential=azure_storage_sas_token,
        )

        # Get ADLS file system client
        file_system_client = service_client.get_file_system_client(
            file_system=adls_file_system
        )

        # Get directory client
        directory_client = file_system_client.get_directory_client(adls_directory)

        # Get file client
        file_client = directory_client.get_file_client(adls_file_name)

        # Upload data to ADLS
        file_client.upload_data(data_stream, overwrite=True)

        return "Success"

    @staticmethod
    def download_file_from_s3_to_local(
        bucket_name: str,
        s3_object_key: str,
        local_file_path: str,
        data_product_id: str,
        environment: str,
    ):
        """
        Downloads a file from an S3 bucket to the local file system.

        Args:
            bucket_name (str): The name of the S3 bucket.
            s3_object_key (str): The key of the object in the S3 bucket.
            local_file_path (str): The path where the file will be downloaded to on the local file system.
            aws_access_key_id (str): The AWS access key ID.
            aws_secret_access_key (str): The AWS secret access key.
            data_product_id (str): The ID of the data product.
            environment (str): The environment in which the operation is performed.

        Raises:
            Exception: If there is an error during the file download.

        """

        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_file_from_s3_to_local"):
            try:
                # Create a botocore session
                session = botocore.session.get_session()

                region_name = "us-east-1"

                # Create a client for the S3 service
                s3 = session.create_client(
                    "s3", region_name=region_name
                )  # Replace 'your-region' with the appropriate region

                # Download the file
                try:
                    response = s3.get_object(Bucket=bucket_name, Key=s3_object_key)
                    total_downloaded = 0
                    with open(local_file_path, "wb") as f:
                        # Stream the content to file
                        for chunk in response["Body"].iter_chunks():
                            f.write(chunk)
                            total_downloaded += len(chunk)
                            logger.info(f"Downloaded {total_downloaded} bytes")
                    logger.info(f"File downloaded successfully: {local_file_path}")

                except Exception as e:
                    error_message = f"Error downloading file: {e}"
                    error_message = (
                        error_message
                        + f"Failed to download file from S3 bucket {bucket_name} to local file path {local_file_path}"
                    )
                    logger.error(error_message)
                    raise e

            except Exception as ex:
                error_msg = "Error: %s", ex
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                raise

    @staticmethod
    def download_file_from_s3_to_minio(minio_bucket_name: str, s3_path: str, data_product_id: str, environment: str):
        """
        Download and prepare data from S3 public bucket.
        
        Args:
            minio_bucket_name (str): Name of bucket to output 
            s3_path (str): S3 path to the vocabulary files
            data_product_id (str): The ID of the data product
            environment (str): The environment in which the operation is performed
            
        Returns:
            tuple: (temp_file_path, download_time) or (None, None) if failed
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_file_from_s3_to_minio"):
            start_time = time.time()
            try:
                # Parse S3 URL
                parsed = urlparse(s3_path)
                bucket = parsed.netloc
                
                # Handle both s3:// and https:// URLs
                if parsed.scheme == 's3':
                    key = parsed.path.lstrip('/')
                else:
                    # For https:// URLs, remove the bucket name from the path
                    path_parts = parsed.path.lstrip('/').split('/')
                    if path_parts[0] == bucket:
                        key = '/'.join(path_parts[1:])
                    else:
                        key = parsed.path.lstrip('/')
                
                logger.info(f"Starting download from S3: bucket={bucket}, key={key}")
                
                # Setup S3 client for public access
                s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
                
                try:
                    # Check if file exists
                    response = s3.list_objects_v2(Bucket=bucket, Prefix=key)
                    if 'Contents' not in response or len(response['Contents']) == 0:
                        error_msg = f"File not found in S3: {key}"
                        logger.error(error_msg)
                        return None, None
                        
                    logger.info("Downloading from S3...")
                    response = s3.get_object(Bucket=bucket, Key=key)
                    gz_content = response['Body'].read()
                    download_time = time.time()
                    logger.info(f"Download complete in {download_time - start_time:.2f}s")

                    # Save raw .csv.gz file to MinIO
                    logger.info(f"Saving raw .csv.gz to MinIO: {key}")
                    try:
                        s3_minio = boto3.client(
                            "s3",
                            endpoint_url="http://localhost:9000",  # adjust to your MinIO endpoint
                            aws_access_key_id="minioadmin",
                            aws_secret_access_key="minioadmin"
                        )
                        s3_minio.put_object(
                            Bucket=f"{minio_bucket_name}",
                            Key=key,
                            Body=gz_content
                        )
                        logger.info("Raw .csv.gz saved to MinIO successfully")
                    except Exception as minio_error:
                        error_msg = f"Failed to save file to MinIO: {minio_error}"
                        logger.error(error_msg)
                        raise minio_error
                    
                    # Decompress and save to temporary file
                    try:
                        with gzip.GzipFile(fileobj=io.BytesIO(gz_content)) as gz:
                            content = gz.read().decode('utf-8')

                        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode='w', encoding='utf-8') as tmp_file:
                            tmp_file.write(content)
                            tmp_path = tmp_file.name
                            logger.info(f"Temporary file created at: {tmp_path}")
                            
                        return tmp_path, download_time
                    except Exception as decompress_error:
                        error_msg = f"Failed to decompress and save file: {decompress_error}"
                        logger.error(error_msg)
                        raise decompress_error
                        
                except Exception as s3_error:
                    error_msg = f"Error during S3 operations: {s3_error}"
                    logger.error(error_msg)
                    raise s3_error
                    
            except Exception as ex:
                error_msg = f"Error in download_file_from_s3_to_minio: {ex}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return None, None
        