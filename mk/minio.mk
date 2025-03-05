# MinIO settings
MINIO_ALIAS=myminio
MINIO_ENDPOINT=http://127.0.0.1:9000
MINIO_CONSOLE=http://127.0.0.1:9001
ACCESS_KEY=minioadmin
SECRET_KEY=minioadmin

# File upload limits
BODY_SIZE_LIMIT=1G
MIN_PART_SIZE=64M

.PHONY: minio-config minio-restart minio-test minio-upload minio-quota minio-setup

# Configure MinIO for large file uploads
minio-config:
	@echo "🔧 Setting MinIO HTTP limits..."
	@echo "export MINIO_HTTP_BODY_SIZE_LIMIT=$(BODY_SIZE_LIMIT)" | sudo tee -a /etc/environment
	@echo "export MINIO_HTTP_MIN_PART_SIZE=$(MIN_PART_SIZE)" | sudo tee -a /etc/environment
	@echo "✅ Configuration updated."

# Restart MinIO to apply changes
minio-restart:
	@echo "🔄 Restarting MinIO..."
	sudo systemctl restart minio || (pkill minio && nohup minio server /data > minio.log 2>&1 &)
	@echo "✅ MinIO restarted."

# Test MinIO connection
minio-test:
	@echo "🛠️  Checking MinIO status..."
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(ACCESS_KEY) $(SECRET_KEY)
	mc admin info $(MINIO_ALIAS)
	@echo "✅ MinIO is running."

# Upload a test file using mc
minio-upload:
	@echo "📂 Uploading a test file..."
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(ACCESS_KEY) $(SECRET_KEY)
	mc cp --storage-class STANDARD large_file.zip $(MINIO_ALIAS)/my-bucket/
	@echo "✅ Upload complete."

# Set bucket quota (200GB limit)
minio-quota:
	@echo "📏 Setting bucket quota..."
	mc alias set $(MINIO_ALIAS) $(MINIO_ENDPOINT) $(ACCESS_KEY) $(SECRET_KEY)
	mc admin bucket quota set $(MINIO_ALIAS)/my-bucket --hard 200G
	@echo "✅ Bucket quota set."

# Full setup (configure, restart, test)
minio-setup: minio-config minio-restart minio-test
	@echo "🚀 MinIO is ready with new settings!"
