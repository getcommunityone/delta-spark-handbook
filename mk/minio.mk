# MinIO Configuration
MINIO_SERVER=http://minio:9000
ACCESS_KEY=minioadmin
SECRET_KEY=minioadmin
BUCKET_NAME=ehr
TEST_FILE=testfile.txt
DOWNLOADED_FILE=downloaded.txt

# Set AWS CLI configuration for MinIO
minio-configure:
	@echo "Configuring AWS CLI for MinIO..."
	aws configure set aws_access_key_id $(ACCESS_KEY)
	aws configure set aws_secret_access_key $(SECRET_KEY)
	aws configure set region us-east-1
	aws configure set s3.endpoint_url $(MINIO_SERVER)

# List MinIO buckets
minio-list-buckets:
	@echo "Listing MinIO buckets..."
	aws s3 ls --endpoint-url $(MINIO_SERVER)

# Create a test bucket
minio-create-bucket:
	@echo "Creating bucket: $(BUCKET_NAME)..."
	aws s3 mb s3://$(BUCKET_NAME) --endpoint-url $(MINIO_SERVER)

# Upload a test file
minio-upload:
	@echo "Uploading test file to MinIO..."
	echo "Hello MinIO" > $(TEST_FILE)
	aws s3 cp $(TEST_FILE) s3://$(BUCKET_NAME)/ --endpoint-url $(MINIO_SERVER)

# List files in the bucket
minio-list-files:
	@echo "Listing files in bucket: $(BUCKET_NAME)..."
	aws s3 ls s3://$(BUCKET_NAME)/ --endpoint-url $(MINIO_SERVER)

# Download the file
minio-download:
	@echo "Downloading test file from MinIO..."
	aws s3 cp s3://$(BUCKET_NAME)/$(TEST_FILE) $(DOWNLOADED_FILE) --endpoint-url $(MINIO_SERVER)
	@echo "Downloaded content:"
	cat $(DOWNLOADED_FILE)

# Remove the test file
minio-delete-file:
	@echo "Deleting test file from MinIO..."
	aws s3 rm s3://$(BUCKET_NAME)/$(TEST_FILE) --endpoint-url $(MINIO_SERVER)

# Delete the bucket
minio-delete-bucket:
	@echo "Deleting bucket: $(BUCKET_NAME)..."
	aws s3 rb s3://$(BUCKET_NAME) --force --endpoint-url $(MINIO_SERVER)

# Clean up local files
minio-clean:
	@echo "Cleaning up local files..."
	rm -f $(
