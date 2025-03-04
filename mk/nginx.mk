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
	if [ -f $(NGINX_CONF) ]; then \
		sudo cp $(NGINX_CONF) $(NGINX_CONF).bak; \
	fi
	sudo bash -c 'echo "server { \
		listen 80; \
		listen [::]:80; \
		server_name $(DOMAIN) www.$(DOMAIN); \
		location / { \
			root /var/www/$(DOMAIN); \
			index index.html index.htm; \
			try_files \$$uri \$$uri/ =404; \
		} \
		location /minio/ { \
			proxy_set_header Host \$$host; \
			proxy_pass http://localhost:9001; \
		} \
		location /minio-storage/ { \
			proxy_set_header Host \$$host; \
			proxy_pass http://localhost:9000; \
		} \
	}" > $(NGINX_CONF)'
	sudo ln -sf $(NGINX_CONF) $(NGINX_SITES_ENABLED)/$(DOMAIN)

# Restart Nginx to apply configuration changes
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
