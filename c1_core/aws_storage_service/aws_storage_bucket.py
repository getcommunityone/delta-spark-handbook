"""
AwsStorageBucket.download_file_from_s3_to_local(
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
    AwsStorageBucket.download_file_from_s3(bucket_name, s3_object_key, local_file_path)

Note:
    The module requires the installation of boto3 packages.
    Ensure that AWS credentials are configured properly for boto3 to access the specified S3 bucket.
"""

import os
import sys
import time
from urllib.parse import urlparse
import boto3
import botocore
from botocore.config import Config
from botocore import UNSIGNED
        
from c1_core.c1_log_service.environment_logging import LoggerSingleton

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


class AwsStorageBucket:
    """
    This module provides a class for downloading files from an S3 bucket.

    Usage:
        bucket_name = 'my-bucket'  # Replace with your S3 bucket name
        s3_object_key = 'path/to/s3/object'  # Replace with the path to your S3 object
        local_file_path = 'path/to/local/file'  # Replace with the desired local path for the downloaded file

        AwsStorageBucket.download_file_from_s3(bucket_name, s3_object_key, local_file_path)
    """

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
    def download_files_from_s3_to_minio(
        minio_bucket_name: str,
        s3_dir_path: str,
        data_product_id: str,
        environment: str,
        minio_endpoint: str = "http://localhost:9000",
        minio_access_key: str = "minioadmin",
        minio_secret_key: str = "minioadmin"
    ):
        """
        Download multiple files from S3 public bucket to MinIO.
        
        Args:
            minio_bucket_name (str): Name of bucket to output 
            s3_dir_path (str): S3 path to the directory containing files
            data_product_id (str): The ID of the data product
            environment (str): The environment in which the operation is performed
            minio_endpoint (str): MinIO endpoint URL
            minio_access_key (str): MinIO access key
            minio_secret_key (str): MinIO secret key
            
        Returns:
            dict: Summary of the operation including success count and total files
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("download_files_from_s3_to_minio"):
            start_time = time.time()
            try:
                # Parse S3 URL
                parsed = urlparse(s3_dir_path)
                bucket = parsed.netloc
                
                # Handle both s3:// and https:// URLs
                if parsed.scheme == 's3':
                    prefix = parsed.path.lstrip('/')
                else:
                    # For https:// URLs, remove the bucket name from the path
                    path_parts = parsed.path.lstrip('/').split('/')
                    if path_parts[0] == bucket:
                        prefix = '/'.join(path_parts[1:])
                    else:
                        prefix = parsed.path.lstrip('/')
                
                # Remove any trailing slash from the key
                prefix = prefix.rstrip('/')
                
                logger.info(f"Starting download from S3: bucket={bucket}, prefix={prefix}")
                
                # Setup S3 client for public access
                s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
                
                try:
                    # List all objects in the prefix
                    logger.info(f"Listing objects in bucket {bucket} with prefix {prefix}")
                    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
                    if 'Contents' not in response or len(response['Contents']) == 0:
                        error_msg = f"No files found in S3: {prefix}"
                        logger.error(error_msg)
                        return {"success": False, "message": error_msg, "files_processed": 0}
                    
                    available_keys = [obj['Key'] for obj in response.get('Contents', [])]
                    logger.info(f"Found {len(available_keys)} files to process")
                    
                    # Setup MinIO client
                    logger.info(f"Setting up MinIO client with endpoint {minio_endpoint}")
                    s3_minio = boto3.client(
                        "s3",
                        endpoint_url=minio_endpoint,
                        aws_access_key_id=minio_access_key,
                        aws_secret_access_key=minio_secret_key,
                        config=Config(
                            retries={'max_attempts': 3},
                            connect_timeout=5,
                            read_timeout=10
                        )
                    )
                    
                    # Test MinIO connection
                    try:
                        logger.info("Testing MinIO connection...")
                        s3_minio.list_buckets()
                        logger.info("Successfully connected to MinIO")
                    except Exception as e:
                        logger.error(f"Failed to connect to MinIO: {str(e)}", exc_info=True)
                        raise
                    
                    success_count = 0
                    for key in available_keys:
                        try:
                            logger.info(f"⏳ Downloading from S3: {key}")
                            response = s3.get_object(Bucket=bucket, Key=key)
                            content = response['Body'].read()
                            download_time = time.time()
                            logger.info(f"✅ Download complete in {download_time - start_time:.2f}s")

                            # Save to MinIO
                            logger.info(f"📤 Saving {key} to MinIO: {minio_bucket_name}")
                            s3_minio.put_object(
                                Bucket=minio_bucket_name,
                                Key=key,
                                Body=content
                            )
                            logger.info(f"✅ File {key} saved to MinIO: {minio_bucket_name} successfully")
                            success_count += 1
                            
                        except Exception as file_error:
                            error_msg = f"Failed to process file {key}: {file_error}"
                            logger.error(error_msg)
                            continue
                    
                    total_time = time.time() - start_time
                    summary = {
                        "success": True,
                        "total_files": len(available_keys),
                        "successful_files": success_count,
                        "failed_files": len(available_keys) - success_count,
                        "total_time": f"{total_time:.2f}s"
                    }
                    logger.info(f"Operation completed: {summary}")
                    return summary
                        
                except Exception as s3_error:
                    error_msg = f"Error during S3 operations: {s3_error}"
                    logger.error(error_msg)
                    raise s3_error
                    
            except Exception as ex:
                error_msg = f"Error in download_files_from_s3_to_minio: {ex}"
                exc_info = sys.exc_info()
                LoggerSingleton.instance(
                    NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
                ).error_with_exception(error_msg, exc_info)
                return {"success": False, "message": error_msg, "files_processed": 0}

    @staticmethod
    def list_s3_files_boto(
        s3_dir_path: str,
        file_extension: str = None,
        data_product_id: str = None,
        environment: str = None,
        max_retries: int = 15,
        timeout: int = 60,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        region_name: str = None,
        endpoint_url: str = None,
        public_access: bool = False,
        use_fallback_strategies: bool = True
    ):
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("list_s3_files_boto"):
            try:
                logger.info(f"Listing files in MinIO path: {s3_dir_path} with extension: {file_extension}")

                parsed = urlparse(s3_dir_path)
                bucket = parsed.netloc
                prefix = parsed.path.lstrip('/')

                config = Config(
                    retries={'max_attempts': max_retries, 'mode': 'adaptive'},
                    connect_timeout=timeout,
                    read_timeout=timeout,
                    s3={'addressing_style': 'path'}
                )

                client_kwargs = {'config': config}
                if endpoint_url is not None:
                    client_kwargs['endpoint_url'] = endpoint_url

                # For public access or when no credentials are provided
                if public_access or (not aws_access_key_id and not aws_secret_access_key):
                    config.signature_version = UNSIGNED
                    s3 = boto3.client('s3', **client_kwargs)
                else:
                    client_kwargs.update({
                        'aws_access_key_id': aws_access_key_id,
                        'aws_secret_access_key': aws_secret_access_key,
                    })
                    if aws_session_token:
                        client_kwargs['aws_session_token'] = aws_session_token
                    s3 = boto3.client('s3', **client_kwargs)

                try:
                    # First check if bucket exists
                    try:
                        s3.head_bucket(Bucket=bucket)
                    except Exception as ex:
                        if "NoSuchBucket" in str(ex):
                            logger.error(f"Bucket {bucket} does not exist")
                            return []
                        raise

                    paginator = s3.get_paginator('list_objects_v2')
                    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

                    all_files = []
                    for page in page_iterator:
                        if 'Contents' in page:
                            page_files = [
                                f"s3://{bucket}/{obj['Key']}"
                                for obj in page['Contents']
                                if file_extension is None or obj['Key'].endswith(file_extension)
                            ]
                            all_files.extend(page_files)

                    if not all_files:
                        logger.warning("No files found.")

                    logger.info(f"Found {len(all_files)} files.")
                    return all_files

                except Exception as ex:
                    if "AccessDenied" in str(ex):
                        logger.warning("Access denied. Attempting with public access...")
                        config.signature_version = UNSIGNED
                        s3 = boto3.client('s3', **client_kwargs)
                        return AwsStorageBucket.list_s3_files_boto(
                            s3_dir_path=s3_dir_path,
                            file_extension=file_extension,
                            data_product_id=data_product_id,
                            environment=environment,
                            public_access=True
                        )
                    raise ex

            except Exception as ex:
                error_msg = f"Error listing files from s3: {ex}"
                logger.error(error_msg, exc_info=True)
                raise ex

    @classmethod
    def list_s3_files_minio(cls,
        s3_dir_path: str,
        file_extension: str = None,
        data_product_id: str = None,
        environment: str = None,
        max_retries: int = 15,
        timeout: int = 60,
        aws_access_key_id: str = None,
        aws_secret_access_key: str = None,
        aws_session_token: str = None,
        region_name: str = None,
        endpoint_url: str = "http://localhost:9000",  # Use WSL2 IP
        public_access: bool = False,
        use_fallback_strategies: bool = True
    ):
        """
        List files in an S3 bucket using boto3 client.
        """
        from urllib.parse import urlparse
        import boto3
        from botocore.config import Config
        from botocore import UNSIGNED
        import requests
        import os
        
        # Initialize logging first
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()
        
        # Disable SSL verification for local development
        os.environ['AWS_CA_BUNDLE'] = '/dev/null'

        with tracer.start_as_current_span("list_s3_files_minio"):
            try:
                logger.info(f"Listing files in MinIO path: {s3_dir_path} with extension: {file_extension}")
                logger.info(f"Using endpoint: {endpoint_url}")

                # Parse S3 URL
                parsed = urlparse(s3_dir_path)
                bucket = parsed.netloc
                prefix = parsed.path.lstrip('/')
                
                logger.info(f"Using bucket: {bucket}, prefix: {prefix}")
                
                # Configure boto3 client with WSL2-specific settings
                config = Config(
                    retries={'max_attempts': 3, 'mode': 'adaptive'},
                    connect_timeout=5,
                    read_timeout=10,
                    s3={'addressing_style': 'path'},
                    tcp_keepalive=True
                )

                client_kwargs = {
                    'config': config,
                    'endpoint_url': endpoint_url,
                    'verify': False,  # Disable SSL verification for local development
                    'region_name': 'us-east-1'  # Required for S3 compatibility
                }

                if public_access:
                    config.signature_version = UNSIGNED
                else:
                    if aws_access_key_id and aws_secret_access_key:
                        client_kwargs.update({
                            'aws_access_key_id': aws_access_key_id,
                            'aws_secret_access_key': aws_secret_access_key,
                        })
                        if aws_session_token:
                            client_kwargs['aws_session_token'] = aws_session_token

                logger.info(f"Initializing boto3 client with kwargs: {client_kwargs}")
                
                # Initialize boto3 client
                s3 = boto3.client('s3', **client_kwargs)
                
                try:
                    # List objects in the bucket
                    logger.info("Starting to list objects...")
                    all_files = []
                    paginator = s3.get_paginator('list_objects_v2')
                    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)
                    
                    for page in page_iterator:
                        if 'Contents' in page:
                            page_files = [
                                f"s3://{bucket}/{obj['Key']}"
                                for obj in page['Contents']
                                if file_extension is None or obj['Key'].endswith(file_extension)
                            ]
                            all_files.extend(page_files)
                            logger.info(f"Found {len(page_files)} files in current page")
                    
                    if not all_files:
                        logger.warning("No files found.")
                    
                    logger.info(f"Found {len(all_files)} files total.")
                    return all_files
                    
                except Exception as ex:
                    error_msg = f"Error listing files from MinIO: {ex}"
                    logger.error(error_msg, exc_info=True)
                    raise ex
                
            except Exception as ex:
                error_msg = f"Error in list_s3_files_minio: {ex}"
                logger.error(error_msg, exc_info=True)
                raise ex

    @staticmethod
    def list_s3_files_spark(
        spark,
        s3_dir_path: str,
        file_extension: str = None,
        data_product_id: str = None,
        environment: str = None
    ):
        """
        List files in an S3 bucket using Spark.

        Args:
            spark: SparkSession object
            s3_dir_path (str): S3 directory path (e.g., s3a://bucket-name/path/)
            file_extension (str, optional): File extension to filter by
            data_product_id (str, optional): The ID of the data product
            environment (str, optional): The environment in which the operation is performed

        Returns:
            List[str]: List of file paths matching the criteria
        """
        tracer, logger = LoggerSingleton.instance(
            NAMESPACE_NAME, SERVICE_NAME, data_product_id, environment
        ).initialize_logging_and_tracing()

        with tracer.start_as_current_span("list_s3_files_spark"):
            try:
                logger.info(f"Starting list_s3_files_spark with path: {s3_dir_path}")
                logger.info(f"File extension filter: {file_extension}")

       
                # Create a DataFrame representing the files
                logger.info("Starting to read files using binaryFile format...")
                start_time = time.time()
                
                try:
                    files_df = spark.read.format("binaryFile").load(s3_dir_path)
                    read_time = time.time() - start_time
                    logger.info(f"Successfully read files in {read_time:.2f} seconds")
                    logger.info(f"Number of partitions: {files_df.rdd.getNumPartitions()}")
                except Exception as e:
                    logger.error(f"Failed to read files: {str(e)}", exc_info=True)
                    raise

                # Filter files by extension if specified
                if file_extension:
                    logger.info(f"Filtering files by extension: {file_extension}")
                    files_df = files_df.filter(files_df.path.endswith(file_extension))
                    logger.info(f"Number of files after filtering: {files_df.count()}")

                # Collect the file paths
                logger.info("Collecting file paths...")
                start_time = time.time()
                files = [row.path for row in files_df.select("path").collect()]
                collect_time = time.time() - start_time
                logger.info(f"Collected {len(files)} files in {collect_time:.2f} seconds")

                if not files:
                    logger.warning("No files found.")

                logger.info(f"Found {len(files)} files total.")
                return files

            except Exception as ex:
                error_msg = f"Error listing files from S3 using Spark: {ex}"
                logger.error(error_msg, exc_info=True)
                raise ex