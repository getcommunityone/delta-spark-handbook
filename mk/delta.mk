# Makefile for Delta Spark Handbook setup

# Variables
SHELL = /bin/bash
HADOOP_AWS_VERSION := 3.4.1
AWS_SDK_VERSION := 2.24.12
DELTA_JARS_DIR=:= delta-jars

delta-create-dirs:
	@echo "Creating directories..."
	@mkdir -p $(DELTA_JARS_DIR)
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) spark-conf/
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 spark-conf/
	@sudo chmod -R 755 delta-jars/

delta-download-jars: delta-create-dirs
	@echo "Downloading Delta Lake and AWS JARs..."
	@mkdir -p delta-jars
	@sudo chown -R $(CURRENT_USER):$(CURRENT_USER) delta-jars/
	@sudo chmod -R 755 delta-jars/
	@rm -f delta-jars/delta-spark_2.12-3.3.0.jar
	@rm -f delta-jars/delta-storage-3.3.0.jar
	@rm -f delta-jars/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	@rm -f delta-jars/aws-java-sdk-bundle-$(AWS_SDK_VERSION).jar
	@rm -f delta-jars/postgresql-42.7.3.jar
	@rm -f delta-jars/hadoop-client-api-$(HADOOP_AWS_VERSION).jar
	@rm -f delta-jars/hadoop-client-runtime-$(HADOOP_AWS_VERSION).jar
	@rm -f delta-jars/hadoop-client-$(HADOOP_AWS_VERSION).jar

	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/3.3.0/delta-spark_2.12-3.3.0.jar
	wget -P delta-jars https://repo1.maven.org/maven2/io/delta/delta-storage/3.3.0/delta-storage-3.3.0.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/$(HADOOP_AWS_VERSION)/hadoop-aws-$(HADOOP_AWS_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/$(AWS_SDK_VERSION)/bundle-$(AWS_SDK_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/software/amazon/awssdk/url-connection-client/$(AWS_SDK_VERSION)/url-connection-client-$(AWS_SDK_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.4.1/hadoop-common-3.4.1.jar
	wget -P delta-jars https://repo1.maven.org/maven2/com/fasterxml/woodstox/woodstox-core/6.2.4/woodstox-core-6.2.4.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/codehaus/woodstox/stax2-api/4.2/stax2-api-4.2.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/commons/commons-configuration2/2.8.0/commons-configuration2-2.8.0.jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/$(HADOOP_AWS_VERSION)/hadoop-client-api-$(HADOOP_AWS_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/$(HADOOP_AWS_VERSION)/hadoop-client-runtime-$(HADOOP_AWS_VERSION).jar
	wget -P delta-jars https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/$(HADOOP_AWS_VERSION)/hadoop-client-$(HADOOP_AWS_VERSION).jar

	@echo "JARs downloaded successfully"
