# Main Makefile
# Include all makefiles from the mk directory
include mk/*.mk

# Default target
.PHONY: all
all: install-extensions setup download-jars

# Common variables used across included makefiles
DOWNLOAD_DIR := $(HOME)/.kyuubi-sqltools
JDBC_DIR := $(DOWNLOAD_DIR)/jdbc

# Basic setup target
setup:
	mkdir -p $(DOWNLOAD_DIR)
	mkdir -p $(JDBC_DIR)

# Show help
help:
	@echo "Available targets:"
	@echo "  all              - Run all targets"
	@echo "  setup            - Create necessary directories"
	@echo "  install-deps     - Install dependencies"
	@echo "  clean            - Clean all build artifacts"

# Clean everything
clean:
	rm -rf $(DOWNLOAD_DIR)