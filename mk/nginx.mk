# Makefile for setting up a web server with Nginx to serve a Docusaurus site and MinIO object storage

# Variables
SERVER_IP = 136.239.110.18
DOMAIN = communityone.com
ADMIN_EMAIL = jcbowyer@hotmail.com
DOCUSAURUS_DIR = mk-docs
NGINX_SITES_AVAILABLE = /etc/nginx/sites-available
NGINX_SITES_ENABLED = /etc/nginx/sites-enabled
BUILD_DIR = $(DOCUSAURUS_DIR)/build
NGINX_CONF = $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
MINIO_DOMAIN = minio.communityone.com
WEB_ROOT=/var/www/$(DOMAIN)
SUBDOMAIN=minio
MINIO_CONF_DIR=/var/www/minio
MINIO_PORT_1=9001
MINIO_PORT_2=9000

# Install Nginx
nginx-install:
	sudo apt install -y nginx python3 python3-venv libaugeas0 certbot python3-certbot-nginx

# Build the Docusaurus site
nginx-build:
	cd $(DOCUSAURUS_DIR) && npm install && npm run build


# Deploy the Docusaurus build to the serving directory
nginx-deploy:
	sudo rsync -av --delete $(BUILD_DIR)/ /var/www/$(DOMAIN)/

nginx-config:
	if [ -f $(NGINX_SITES_AVAILABLE)/$(DOMAIN) ]; then \
		sudo cp $(NGINX_SITES_AVAILABLE)/$(DOMAIN) $(NGINX_SITES_AVAILABLE)/$(DOMAIN).bak; \
	fi
	# Main domain and www configuration
	sudo bash -c 'echo "server { \
		listen 80; \
		listen [::]:80; \
		server_name $(DOMAIN) www.$(DOMAIN); \
		location / { \
			root $(WEB_ROOT); \
			index index.html index.htm; \
			try_files \$$uri \$$uri/ =404; \
		} \
	}" > $(NGINX_SITES_AVAILABLE)/$(DOMAIN)'

	# Minio subdomain configuration
	sudo bash -c 'echo "server { \
		listen 80; \
		listen [::]:80; \
		server_name $(MINIO_DOMAIN); \
		location / { \
      		proxy_set_header Host \$$host; \
        	proxy_pass http://localhost:$(MINIO_PORT_1)/; \
		} \
		location /minio/ { \
			proxy_set_header Host \$$host; \
			proxy_pass http://localhost:$(MINIO_PORT_1)/; \
		} \
		location /minio-storage/ { \
			proxy_set_header Host \$$host; \
			proxy_pass http://localhost:$(MINIO_PORT_2)/; \
		} \
	}" > $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)'

	# Enable the site configurations by creating symlinks in sites-enabled
	sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(DOMAIN) $(NGINX_SITES_ENABLED)/$(DOMAIN)
	sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN) $(NGINX_SITES_ENABLED)/$(MINIO_DOMAIN)

## Restart Nginx to apply configuration changes
nginx-restart:
	sudo systemctl restart nginx

# Clean the build directory
nginx-clean:
	rm -rf $(BUILD_DIR)/*

# Obtain SSL certificate using Certbot
nginx-certbot-setup:
	sudo certbot --nginx -d $(DOMAIN) -d www.$(DOMAIN) -d $(MINIO_DOMAIN) --expand --non-interactive --agree-tos -m $(ADMIN_EMAIL) --redirect

# Set up automatic certificate renewal
nginx-certbot-renew:
	echo "0 0,12 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab > /dev/null
