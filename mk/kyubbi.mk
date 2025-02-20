# Kyuubi version to download
KYUUBI_VERSION := 1.9.0
KYUUBI_FILE := apache-kyuubi-$(KYUUBI_VERSION)-bin.tgz

# Directory setup
DELTAJARS_DIR := delta-jars
DOWNLOAD_DIR := $(DELTAJARS_DIR)/downloads
KYUUBI_DIR := $(DELTAJARS_DIR)/kyuubi
HOME_KYUUBI := $(HOME)/.kyuubi-sqltools

# URLs - Note: correct URL structure for Kyuubi
KYUUBI_BINARY_URL := https://dlcdn.apache.org/kyuubi/kyuubi-$(KYUUBI_VERSION)/$(KYUUBI_FILE)

# Main target
.PHONY: kyu-all
kyu-all: kyu-download-jars

# Create necessary directories
$(DELTAJARS_DIR):
	mkdir -p $(DELTAJARS_DIR)

$(DOWNLOAD_DIR):
	mkdir -p $(DOWNLOAD_DIR)

$(KYUUBI_DIR):
	mkdir -p $(KYUUBI_DIR)

$(HOME_KYUUBI):
	mkdir -p $(HOME_KYUUBI)

# Download and setup Kyuubi
.PHONY: kyu-download-jars
kyu-download-jars: $(DELTAJARS_DIR) $(DOWNLOAD_DIR) $(KYUUBI_DIR) $(HOME_KYUUBI)
	echo "Downloading Kyuubi $(KYUUBI_VERSION)..."
	cd $(DOWNLOAD_DIR) && wget $(KYUUBI_BINARY_URL)
	echo "Extracting Kyuubi..."
	tar -xzf $(DOWNLOAD_DIR)/$(KYUUBI_FILE) -C $(KYUUBI_DIR) --strip-components=1
	echo "Copying required JARs..."
	cp $(KYUUBI_DIR)/jars/*.jar $(DELTAJARS_DIR)/
	cp $(KYUUBI_DIR)/jars/*.jar $(HOME_KYUUBI)/
	echo "Cleaning up..."
	rm -rf $(DOWNLOAD_DIR)
	echo "Kyuubi setup complete. JARs are available in $(DELTAJARS_DIR) and $(HOME_KYUUBI)"

# Clean target
.PHONY: kyu-clean
kyu-clean:
	rm -rf $(DELTAJARS_DIR)
	rm -rf $(HOME_KYUUBI)
	echo "Cleaned up Kyuubi installation"

# Help target
.PHONY: kyu-help
kyu-help:
	echo "Available targets:"
	echo "  kyu-all           : Sets up Kyuubi (default)"
	echo "  kyu-download-jars : Downloads and sets up Kyuubi JARs"
	echo "  kyu-clean         : Removes all downloaded files and directories"
	echo "  kyu-help          : Shows this help message"