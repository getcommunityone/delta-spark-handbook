# Makefile for Delta Spark Handbook setup

# Variables
SHELL = /bin/bash
DELTA_VERSION = 3.2.1
DELTA_STORAGE_VERSION = 3.2.1
HADOOP_AWS_VERSION = 3.3.2
AWS_SDK_VERSION = 1.12.261
GIT_USER_NAME ?= "John Bowyer"
GIT_USER_EMAIL ?= "jcbowyer@hotmail.com"

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

kyu-all: help

kyu-help:
	@echo "Available targets:"
	@echo "  make setup         - Complete setup (create dirs, download JARs, create configs)"
	@echo "  make clean         - Remove all generated files and directories"
	@echo "  make download-jars - Download required JARs only"
	@echo "  make create-dirs   - Create required directories only"
	@echo "  make create-configs - Create configuration files only"
	@echo "  make verify        - Verify the setup"

kyu-setup: create-dirs download-jars create-configs git-config
	@echo "Setup completed successfully!"

CURRENT_USER := $(shell whoami)

kyu-git-config:
	@echo "Configuring git..."
	$(call check_defined,GIT_USER_NAME)
	$(call check_defined,GIT_USER_EMAIL)
	@git config --global --replace-all user.name '$(GIT_USER_NAME)'
	@git config --global --replace-all user.email '$(GIT_USER_EMAIL)'
	@echo "Current git configuration:"
	@git config --list | grep user
	@echo "Git configuration completed successfully"

	


kyu-create-configs: create-dirs
	@echo "Creating requirements.txt..."
	@echo "delta-spark==${DELTA_VERSION}" > requirements.txt
	@echo "pyspark==3.5.4  >> requirements.txt
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

kyu-clean:
	@echo "Cleaning up..."
	@rm -rf $(DIRS)
	@rm -f $(CONFIG_FILES)
	@echo "Cleanup completed"
  