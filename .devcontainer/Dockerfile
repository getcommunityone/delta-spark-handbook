FROM apache/spark-py:v3.4.0

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip
ENV PATH=$PATH:$SPARK_HOME/bin

# Install Apache Iceberg dependencies
RUN wget https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.4.2/iceberg-spark-runtime-3.4_2.12-1.4.2.jar \
    -O $SPARK_HOME/jars/iceberg-spark-runtime-3.4_2.12-1.4.2.jar

# Install AWS SDK for S3 compatibility
RUN wget https://repo1.maven.org/maven2/software/amazon/awssdk/bundle/2.17.178/bundle-2.17.178.jar \
    -O $SPARK_HOME/jars/bundle-2.17.178.jar

# Install AWS URL connection handler
RUN wget https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar \
    -O $SPARK_HOME/jars/hadoop-aws-3.3.4.jar

# Create workspace directory
WORKDIR /workspace