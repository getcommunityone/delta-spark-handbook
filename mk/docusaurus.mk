	# Docusaurus Management Makefile

DOCS_DIR := $(shell pwd)/mk-docs
NODE_IMAGE := node:18
DOCKER_COMPOSE := docker-compose

# Install Docusaurus dependencies
docu-install:
	@echo "Installing Docusaurus..."
	cd $(DOCS_DIR) && npm install

# Start Docusaurus in Development Mode
docu-serve:
	@echo "Starting Docusaurus..."
	cd $(DOCS_DIR) && npm run start

# Build Static Documentation
docu-build:
	@echo "Building Docusaurus..."
	cd $(DOCS_DIR) && npm run build

# Clean built files
docu-clean:
	@echo "Cleaning Docusaurus build..."
	rm -rf $(DOCS_DIR)/build

# Run Docusaurus in Docker
docu-docker-serve:
	@echo "Running Docusaurus in Docker..."
	docker run --rm -it -v $(DOCS_DIR):/app -w /app -p 3000:3000 $(NODE_IMAGE) npm run start

# Rebuild and Restart Services
docu-restart:
	@echo "Restarting all services..."
	$(DOCKER_COMPOSE) down && $(DOCKER_COMPOSE) up -d --build

# Deploy Documentation (Optional, for GitHub Pages)
docu-deploy:
	@echo "Deploying Docusaurus..."
	cd $(DOCS_DIR) && GIT_USER=${GIT_USER} npm run deploy
