#!/bin/bash
# Ensure the script exits on error
set -e

# Change ownership inside the container
chown -R 1001:1001 /opt/bitnami/spark/conf
chmod -R u+rwX,g+rX,o+rX /opt/bitnami/spark/conf

# Start Spark Master process
if [ "$SPARK_MODE" = "master" ]; then
    echo "Starting Spark Master..."
    exec /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.master.Master
elif [ "$SPARK_MODE" = "worker" ]; then
    echo "Starting Spark Worker..."
    exec /opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker "$SPARK_MASTER_URL"
else
    echo "Unknown SPARK_MODE: $SPARK_MODE"
    exit 1
fi
