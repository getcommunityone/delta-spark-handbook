# Makefile for setting up a web server with Nginx to serve a Docusaurus site

# Variables
SERVER_IP = 136.239.110.18
DOMAIN = communityone.com
ADMIN_EMAIL = jcbowyer@hotmail.com
DOCUSAURUS_DIR = mk-docs
NGINX_SITES_AVAILABLE = /etc/nginx/sites-available
NGINX_SITES_ENABLED = /etc/nginx/sites-enabled
BUILD_DIR = $(DOCUSAURUS_DIR)/build
NGINX_CONF = $(NGINX_SITES_AVAILABLE)/default

# Default rule to build and deploy everything
all: nginx-install nginx-build nginx-deploy nginx-restart

# Install Nginx
nginx-install:
	sudo apt install -y nginx python3 python3-venv libaugeas0 certbot python3-certbot-nginx

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

# Obtain SSL certificate using Certbot
nginx-certbot-setup:
	sudo certbot --nginx -d $(DOMAIN) -d www.$(DOMAIN) --non-interactive --agree-tos -m $(ADMIN_EMAIL)

# Set up automatic certificate renewal
nginx-certbot-renew:
	echo "0 0,12 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab > /dev/null




