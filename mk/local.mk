# Makefile to setup local development environment similar to devcontainer
# Update

SPARK_VERSION=3.5.5
SPARK_HOME=/opt/spark
DELTA_VERSION=3.3.0
KYUUBI_VERSION=1.10.0
AWS_CLI_ZIP=awscliv2.zip
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=minioadmin
AWS_S3_ENDPOINT=http://minio:9000

local-setup: local-install-dependencies local-install-spark local-install-delta local-install-kyuubi local-install-awscli

local-install-dependencies:
	sudo apt-get update && sudo apt-get install -y openjdk-17-jdk curl wget make unzip gnupg lsb-release ca-certificates

local-install-spark:
	curl -L -O https://downloads.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz
	tar xvf spark-${SPARK_VERSION}-bin-hadoop3.tgz
	sudo mv spark-${SPARK_VERSION}-bin-hadoop3 ${SPARK_HOME}
	rm spark-${SPARK_VERSION}-bin-hadoop3.tgz
	echo 'export SPARK_HOME=${SPARK_HOME}' >> ~/.bashrc
	echo 'export PATH=$$PATH:$$SPARK_HOME/bin' >> ~/.bashrc
	echo 'export PYTHONPATH=$$SPARK_HOME/python:$$SPARK_HOME/python/lib/py4j-0.10.9.5-src.zip:$$PYTHONPATH' >> ~/.bashrc

local-install-delta:
	wget https://repo1.maven.org/maven2/io/delta/delta-spark_2.12/${DELTA_VERSION}/delta-spark_2.12-${DELTA_VERSION}.jar -P ${SPARK_HOME}/jars/
	wget https://repo1.maven.org/maven2/io/delta/delta-storage/${DELTA_VERSION}/delta-storage-${DELTA_VERSION}.jar -P ${SPARK_HOME}/jars/
	wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.2/hadoop-aws-3.3.2.jar -P ${SPARK_HOME}/jars/
	wget https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.782/aws-java-sdk-bundle-1.12.782.jar -P ${SPARK_HOME}/jars/

local-install-kyuubi:
	wget https://repository.apache.org/content/groups/public/org/apache/kyuubi/kyuubi-spark-sql-engine_2.12/${KYUUBI_VERSION}/kyuubi-spark-sql-engine_2.12-${KYUUBI_VERSION}.jar \
		-O ${SPARK_HOME}/jars/kyuubi-spark-sql-engine_2.12-${KYUUBI_VERSION}.jar

local-install-awscli:
	curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "${AWS_CLI_ZIP}"
	unzip ${AWS_CLI_ZIP}
	sudo ./aws/install
	rm -rf aws ${AWS_CLI_ZIP}
	echo 'export AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}' >> ~/.bashrc
	echo 'export AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}' >> ~/.bashrc
	echo 'export AWS_REGION=${AWS_REGION}' >> ~/.bashrc
	echo 'export AWS_S3_ENDPOINT=${AWS_S3_ENDPOINT}' >> ~/.bashrc

local-clean:
	sudo rm -rf ${SPARK_HOME}
	sudo apt-get remove -y  openjdk-17-jdk
	sudo apt-get autoremove -y
	sed -i '/SPARK_HOME/d' ~/.bashrc
	sed -i '/AWS_/d' ~/.bashrc

.PHONY: setup install-dependencies  install-spark install-delta install-kyuubi install-awscli clean
