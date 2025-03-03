# Makefile to install Node.js

# Define the version of Node.js you want to install
NODE_VERSION=22.x

# Update package list and install prerequisites
node-install-prerequisites:
	@echo "Updating package list and installing prerequisites..."
	sudo apt update
	sudo apt install -y curl gnupg2 lsb-release

# Install Node.js
node-install:
	@echo "Installing Node.js version $(NODE_VERSION)..."
	curl -fsSL https://deb.nodesource.com/setup_$(NODE_VERSION) | sudo -E bash -
	sudo apt install -y nodejs

# Check Node.js version
node-check-version:
	@echo "Node.js version:"
	node -v
	@echo "npm version:"
	npm -v

# Full install process
node-install-all: node-install-prerequisites node-install node-check-version

# Clean up (if necessary)
clean:
	@echo "Cleaning up..."
	sudo apt autoremove -y

