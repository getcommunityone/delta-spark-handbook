SPARK_VERSION=3.5.4
DELTA_JARS_DIR=delta-jars
CONTAINER_NAME=temp-spark-container

spark-all: spark-download-jars

spark-download-jars:
	mkdir -p $(DELTA_JARS_DIR)
	# Create temporary container
	docker create --name $(CONTAINER_NAME) bitnami/spark:$(SPARK_VERSION)
	# Copy jars from container
	docker cp $(CONTAINER_NAME):/opt/bitnami/spark/jars/. $(DELTA_JARS_DIR)/
	# Remove temporary container
	docker rm $(CONTAINER_NAME)
 
spark-verify:
	@echo "Verifying copied JARs..."
	@ls -l $(DELTA_JARS_DIR)
	@echo "JAR count:"
	@ls -1 $(DELTA_JARS_DIR) | wc -l