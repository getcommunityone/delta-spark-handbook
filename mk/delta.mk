# Makefile for Delta Spark Handbook setup

# Variables
SHELL = /bin/bash
HADOOP_AWS_VERSION := 3.3.2
AWS_SDK_VERSION := 1.12.261

delta-create-dirs:
	@echo "Creating directories..."
	@mkdir -p $(DIRS)
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) spark-conf/
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 spark-conf/
	@sudo chmod -R 755 delta-jars/

delta-download-jars: create-dirs
	@echo "Downloading Delta Lake and AWS JARs..."
	@mkdir -p delta-jars
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 delta-jars/
	@rm -f delta-jars/delta-spark_2.12-3.2.1.jar
	@rm -f delta-jars/delta-storage-3.2.1.jar
	@rm -f delta-jars/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	@rm -f delta-jars/aws-java-sdk-bundle-$(AWS_SDK_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.2.1/delta-spark_2.12-3.2.1.jar
	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-storage/3.2.1/delta-storage-3.2.1.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$(HADOOP_AWS_VERSION)/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/$(AWS_SDK_VERSION)/aws-java-sdk-bundle-$(AWS_SDK_VERSION).jar
	@echo "JARs downloaded successfully"
