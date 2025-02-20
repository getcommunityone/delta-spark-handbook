# mk/hive.mk
# Configuration variables
HIVE_VERSION := 3.1.3
HADOOP_VERSION := 3.3.6
DOWNLOAD_DIR := /app/kyuubi-sqltools
JDBC_DIR := $(DOWNLOAD_DIR)/jdbc

# URLs for downloading JARs
HIVE_JDBC_URL := https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/$(HIVE_VERSION)/hive-jdbc-$(HIVE_VERSION)-standalone.jar
HADOOP_COMMON_URL := https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/$(HADOOP_VERSION)/hadoop-common-$(HADOOP_VERSION).jar

.PHONY: hive-all hive-clean hive-setup-dirs hive-download-jars

# Main target without VSCode-specific tasks
hive-all: hive-setup-dirs hive-download-jars

hive-setup-dirs:
	@echo "Creating necessary directories..."
	mkdir -p $(JDBC_DIR)

hive-download-jars:
	@echo "Downloading JDBC drivers..."
	@if [ ! -f $(JDBC_DIR)/hive-jdbc-$(HIVE_VERSION)-standalone.jar ]; then \
		wget -P $(JDBC_DIR) $(HIVE_JDBC_URL); \
	fi
	@if [ ! -f $(JDBC_DIR)/hadoop-common-$(HADOOP_VERSION).jar ]; then \
		wget -P $(JDBC_DIR) $(HADOOP_COMMON_URL); \
	fi

hive-clean:
	@echo "Cleaning up..."
	rm -rf $(DOWNLOAD_DIR)