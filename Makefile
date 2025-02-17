# Makefile for Delta Spark Handbook setup

# Variables
SHELL = /bin/bash
DELTA_VERSION = 2.4.0
DELTA_STORAGE_VERSION = 2.4.0
HADOOP_AWS_VERSION = 3.3.2
AWS_SDK_VERSION = 1.12.261

# Directories
DIRS = .devcontainer kyuubi-conf spark-conf accelerator/materials/1-getting-started delta-jars warehouse

# JAR files
# JAR files
DELTA_JARS = delta-jars/delta-core_2.12-$(DELTA_VERSION).jar \
    delta-jars/delta-storage-$(DELTA_STORAGE_VERSION).jar \
    delta-jars/hadoop-aws-$(HADOOP_AWS_VERSION).jar \
    delta-jars/aws-java-sdk-bundle-$(AWS_SDK_VERSION).jar

# Configuration files
CONFIG_FILES = kyuubi-conf/kyuubi-defaults.conf spark-conf/spark-defaults.conf requirements.txt

.PHONY: all clean setup download-jars create-dirs create-configs help verify

all: help

help:
	@echo "Available targets:"
	@echo "  make setup         - Complete setup (create dirs, download JARs, create configs)"
	@echo "  make clean         - Remove all generated files and directories"
	@echo "  make download-jars - Download required JARs only"
	@echo "  make create-dirs   - Create required directories only"
	@echo "  make create-configs - Create configuration files only"
	@echo "  make verify        - Verify the setup"

setup: create-dirs download-jars create-configs
	@echo "Setup completed successfully!"

create-dirs:
	@echo "Creating directories..."
	@mkdir -p $(DIRS)
	@sudo chown -R 1001:1001 spark-conf/
	@sudo chown -R 1001:1001 delta-jars/
	@sudo chmod -R 755 spark-conf/
	@sudo chmod -R 755 delta-jars/
	
download-jars: create-dirs
	@echo "Downloading Delta Lake and AWS JARs..."
	@wget -q -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-core_2.12/$(DELTA_VERSION)/delta-core_2.12-$(DELTA_VERSION).jar
    @wget -q -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-storage/$(DELTA_STORAGE_VERSION)/delta-storage-$(DELTA_STORAGE_VERSION).jar
	@wget -q -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$(HADOOP_AWS_VERSION)/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	@wget -q -P delta-jars https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/$(AWS_SDK_VERSION)/aws-java-sdk-bundle-$(AWS_SDK_VERSION).jar
	@echo "JARs downloaded successfully"

create-configs: create-dirs
	@echo "Creating Kyuubi configuration..."
	@echo "kyuubi.authentication=NONE" > kyuubi-conf/kyuubi-defaults.conf
	@echo "kyuubi.frontend.protocols=THRIFT,REST" >> kyuubi-conf/kyuubi-defaults.conf
	@echo "kyuubi.metrics.enabled=true" >> kyuubi-conf/kyuubi-defaults.conf
	@echo "kyuubi.engine.type=SPARK_SQL" >> kyuubi-conf/kyuubi-defaults.conf
	@echo "kyuubi.engine.share.level=USER" >> kyuubi-conf/kyuubi-defaults.conf
	@echo "kyuubi.engine.pool.size=1" >> kyuubi-conf/kyuubi-defaults.conf
	@echo "Creating Spark configuration..."
	@echo "spark.master=spark://spark-master:7077" > spark-conf/spark-defaults.conf
	@echo "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" >> spark-conf/spark-defaults.conf
	@echo "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.impl=org.apache.hadoop.fs.s3a.S3AFileSystem" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.endpoint=http://minio:9000" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.access.key=minioadmin" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.secret.key=minioadmin" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.path.style.access=true" >> spark-conf/spark-defaults.conf
	@echo "spark.hadoop.fs.s3a.connection.ssl.enabled=false" >> spark-conf/spark-defaults.conf
	@echo "spark.jars=./delta-jars/*" >> spark-conf/spark-defaults.conf
	@echo "Creating requirements.txt..."
	@echo "delta-spark==${DELTA_VERSION}" > requirements.txt
	@echo "pyspark==3.4.4" >> requirements.txt
	@echo "pandas==2.0.3" >> requirements.txt
	@echo "pyarrow==12.0.1" >> requirements.txt
	@echo "pytest==7.4.0" >> requirements.txt
	@echo "black==23.7.0" >> requirements.txt
	@echo "jupyter==1.0.0" >> requirements.txt
	@echo "python-dotenv==1.0.0" >> requirements.txt
	@echo "pyhive==0.7.0" >> requirements.txt
	@echo "thrift==0.16.0" >> requirements.txt
	@echo "thrift-sasl==0.4.3" >> requirements.txt
	@echo "Configuration files created successfully"

clean:
	@echo "Cleaning up..."
	@rm -rf $(DIRS)
	@rm -f $(CONFIG_FILES)
	@echo "Cleanup completed"

verify: setup
	@echo "Verifying setup..."
	@for dir in $(DIRS); do \
		if [ ! -d "$$dir" ]; then \
			echo "Directory $$dir is missing!"; \
			exit 1; \
		fi; \
	done
	@for jar in $(DELTA_JARS); do \
		if [ ! -f "$$jar" ]; then \
			echo "JAR file $$jar is missing!"; \
			exit 1; \
		fi; \
	done
	@for config in $(CONFIG_FILES); do \
		if [ ! -f "$$config" ]; then \
			echo "Configuration file $$config is missing!"; \
			exit 1; \
		fi; \
	done
	@echo "Setup verification completed successfully"