# Makefile for setting up a web server with Nginx to serve a Docusaurus site

# Variables
SERVER_IP = your_server_ip
DOMAIN = your_domain.com
DOCUSAURUS_DIR = mk-docs/
NGINX_SITES_AVAILABLE = /etc/nginx/sites-available
NGINX_SITES_ENABLED = /etc/nginx/sites-enabled
BUILD_DIR = $(DOCUSAURUS_DIR)/build
NGINX_CONF = $(NGINX_SITES_AVAILABLE)/docusaurus

# Default rule to build and deploy everything
all: nginx-install docusaurus.nginx nginx-configure nginx-build nginx-deploy nginx-restart

# Install Nginx
nginx-install:
	sudo apt update
	sudo apt install -y nginx

# Configure Nginx to serve the Docusaurus site
nginx-configure: docusaurus.nginx
	sudo ln -sf $(NGINX_CONF) $(NGINX_SITES_ENABLED)
	sudo nginx -t

# Build the Docusaurus site
nginx-build:
	cd $(DOCUSAURUS_DIR) && npm install && npm run build

# Deploy the Docusaurus build to the serving directory
nginx-deploy:
	sudo rsync -av --delete $(BUILD_DIR)/ /var/www/docusaurus/

# Restart Nginx to apply configuration changes
nginx-restart:
	sudo systemctl restart nginx

# Clean the build directory
nginx-clean:
	rm -rf $(BUILD_DIR)/*

# Nginx site configuration for Docusaurus
define NGINX_SITE_CONFIG
server {
    listen 80;
    server_name $(DOMAIN) $(SERVER_IP);

    location / {
        root /var/www/docusaurus;
        index index.html;
        try_files $$uri $$uri/ =404;
    }
}
endef
export NGINX_SITE_CONFIG

# Generate the Nginx configuration file
docusaurus.nginx:
	sudo sh -c 'echo "$$NGINX_SITE_CONFIG" > $(NGINX_CONF)'
