# Kyuubi version to download
KYUUBI_VERSION := 1.10.0
KYUUBI_FILE := apache-kyuubi-$(KYUUBI_VERSION)-bin.tgz
HIVE_VERSION := 3.1.3
HIVE_JDBC_URL="https://repo1.maven.org/maven2/org/apache/hive/hive-jdbc/3.1.3/hive-jdbc-3.1.3.jar"

# Directory setup
DELTAJARS_DIR := delta-jars
DOWNLOAD_DIR := $(DELTAJARS_DIR)/downloads
KYUUBI_DIR := $(DELTAJARS_DIR)/kyuubi

# URLs for JARs
KYUUBI_BINARY_URL := https://dlcdn.apache.org/kyuubi/kyuubi-$(KYUUBI_VERSION)/$(KYUUBI_FILE)
KYUUBI_ENGINE_JAR_URL := https://repo1.maven.org/maven2/org/apache/kyuubi/kyuubi-spark-sql-engine_2.12/$(KYUUBI_VERSION)/kyuubi-spark-sql-engine_2.12-$(KYUUBI_VERSION).jar
KYUUBI_COMMON_JAR_URL := https://repo1.maven.org/maven2/org/apache/kyuubi/kyuubi-common_2.12/$(KYUUBI_VERSION)/kyuubi-common_2.12-$(KYUUBI_VERSION).jar
KYUUBI_SERVER_PLUGIN_JAR_URL := https://repo1.maven.org/maven2/org/apache/kyuubi/kyuubi-server-plugin/$(KYUUBI_VERSION)/kyuubi-server-plugin-$(KYUUBI_VERSION).jar

# Main target
.PHONY: kyu-all
kyu-all: kyu-download-jars kyu-download-additional-jars

# Create necessary directories
$(DELTAJARS_DIR):
	mkdir -p $(DELTAJARS_DIR)

$(DOWNLOAD_DIR):
	mkdir -p $(DOWNLOAD_DIR)

$(HOME_KYUUBI):
	mkdir -p $(HOME_KYUUBI)

# Download and setup Kyuubi, overwriting if it exists
.PHONY: kyu-download-jars
kyu-download-all-jars: $(DELTAJARS_DIR) $(DOWNLOAD_DIR)   $(HOME_KYUUBI)
	echo "Downloading Kyuubi $(KYUUBI_VERSION)..."
	cd $(DOWNLOAD_DIR) && wget -O $(KYUUBI_FILE) $(KYUUBI_BINARY_URL)
	echo "Extracting Kyuubi..."
	rm -rf $(KYUUBI_DIR) && mkdir -p $(KYUUBI_DIR)
	tar -xzf $(DOWNLOAD_DIR)/$(KYUUBI_FILE) -C $(KYUUBI_DIR) --strip-components=1
	echo "Kyuubi setup complete. JARs are available in $(DELTAJARS_DIR)"

# Download all additional JARs (engine, common, server plugin), overwriting existing files
.PHONY: kyu-download-additional-jars
kyu-download-jars: $(DELTAJARS_DIR)
	echo "Downloading additional Kyuubi JARs..."
	wget -O $(DELTAJARS_DIR)/kyuubi-spark-sql-engine_2.12-$(KYUUBI_VERSION).jar $(KYUUBI_ENGINE_JAR_URL)
	wget -O $(DELTAJARS_DIR)/kyuubi-common_2.12-$(KYUUBI_VERSION).jar $(KYUUBI_COMMON_JAR_URL)
	wget -O $(DELTAJARS_DIR)/kyuubi-server-plugin-$(KYUUBI_VERSION).jar $(KYUUBI_SERVER_PLUGIN_JAR_URL)
	wget -O $(DELTAJARS_DIR)/hive-jdbc-$(HIVE_VERSION).jar $(HIVE_JDBC_URL) || { echo "Failed to download Hive JDBC driver"; exit 1; }
	echo "Additional JAR downloads complete."

# Clean 

.PHONY: kyu-clean
kyu-clean:
	rm -rf $(DELTAJARS_DIR)
	rm -rf $(HOME_KYUUBI)
	echo "Cleaned up Kyuubi installation"

# Help target
.PHONY: kyu-help
kyu-help:
	echo "Available targets:"
	echo "  kyu-all                  : Sets up Kyuubi (default)"
	echo "  kyu-download-jars        : Downloads and sets up Kyuubi JARs"
	echo "  kyu-download-additional-jars  : Downloads Kyuubi Engine, Common, and Server Plugin JARs"
	echo "  kyu-clean                : Removes all downloaded files and directories"
	echo "  kyu-help                 : Shows this help message"
