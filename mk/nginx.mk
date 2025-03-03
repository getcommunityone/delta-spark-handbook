# Makefile for setting up a web server with Nginx to serve a Docusaurus site

# Variables
SERVER_IP = 0.0.0.0
DOMAIN = your_domain.com
DOCUSAURUS_DIR = mk-docs
NGINX_SITES_AVAILABLE = /etc/nginx/sites-available
NGINX_SITES_ENABLED = /etc/nginx/sites-enabled
BUILD_DIR = $(DOCUSAURUS_DIR)/build
NGINX_CONF = $(NGINX_SITES_AVAILABLE)/default

# Default rule to build and deploy everything
all: nginx-install nginx-build nginx-deploy nginx-restart

# Install Nginx
nginx-install:
	sudo apt update
	sudo apt install -y nginx

# Build the Docusaurus site
nginx-build:
	cd $(DOCUSAURUS_DIR) && npm install && npm run build

# Deploy the Docusaurus build to the serving directory
nginx-deploy:
	sudo rsync -av --delete $(BUILD_DIR)/ /var/www/html/

# Restart Nginx to apply configuration changes
nginx-restart:
	sudo systemctl restart nginx

# Clean the build directory
nginx-clean:
	rm -rf $(BUILD_DIR)/*



