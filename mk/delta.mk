# Makefile for Delta Spark Handbook setup

# Variables
SHELL = /bin/bash
HADOOP_AWS_VERSION := 3.4.1
AWS_SDK_VERSION := 2.20.159
DELTA_JARS_DIR=:= delta-jars

delta-create-dirs:
	@echo "Creating directories..."
	@mkdir -p $(DELTA_JARS_DIR)
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) spark-conf/
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 spark-conf/
	@sudo chmod -R 755 delta-jars/

delta-download-jars: delta-create-dirs
	@echo "Downloading Delta Lake, AWS, and Stax2 JARs..."
	@mkdir -p delta-jars
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 delta-jars/
	@rm -f delta-jars/delta-spark_2.12-3.3.0.jar
	@rm -f delta-jars/delta-storage-3.3.0.jar
	@rm -f delta-jars/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	@rm -f delta-jars/aws-java-sdk-bundle-2.20.159.jar
	@rm -f delta-jars/hive-jdbc-3.1.3.jar
	@rm -f delta-jars/hadoop-common-3.4.1.jar
	@rm -f delta-jars/hadoop-client-3.4.1.jar
	@rm -f delta-jars/hadoop-auth-3.4.1.jar
	@rm -f delta-jars/woodstox-core-6.2.6.jar
	@rm -f delta-jars/stax2-api-4.2.1.jar  # Remove old stax2-api if it exists
	@rm -f delta-jars/commons-configuration2-2.7.jar

	# Download Delta Lake JARs
	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.3.0/delta-spark_2.12-3.3.0.jar
	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-storage/3.3.0/delta-storage-3.3.0.jar

	# Download Hadoop AWS and AWS SDK JARs
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$(HADOOP_AWS_VERSION)/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/aws-sdk-java/2.20.159/aws-sdk-java-2.20.159.jar

	# Download Hive JDBC JAR
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3.jar

	# Download Hadoop Common, Client, Auth JARs
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.4.1/hadoop-common-3.4.1.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.4.1/hadoop-client-3.4.1.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-auth/3.4.1/hadoop-auth-3.4.1.jar

	# Download Woodstox core JAR
	wget -P delta-jars https://repo1.maven.org/maven2/com/fasterxml/woodstox/woodstox-core/6.2.6/woodstox-core-6.2.6.jar

	# Download Stax2 API JAR (fix for XMLInputFactory2)
	wget -P delta-jars https://repo1.maven.org/maven2/org/codehaus/woodstox/stax2-api/4.2.1/stax2-api-4.2.1.jar

	@echo "Downloading commons-configuration2 JAR..."
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/commons/commons-configuration2/2.7/commons-configuration2-2.7.jar


	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/kinesis/amazon-kinesis-client/3.0.0/amazon-kinesis-client-3.0.0.jar

	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/auth/2.20.159/auth-2.20.159.jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/s3/2.20.159/s3-2.20.159.jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/utils/2.20.159/utils-2.20.159.jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/regions/2.20.159/regions-2.20.159.jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/aws-core/2.20.159/aws-core-2.20.159.jar
