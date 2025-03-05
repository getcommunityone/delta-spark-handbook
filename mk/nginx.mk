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
# Back up the existing Nginx configuration if it exists
	if [ -f $(NGINX_CONF) ]; then \
		sudo cp $(NGINX_CONF) $(NGINX_CONF).bak; \
	fi
	
	# Create main domain configuration file
	sudo rm -f $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	sudo touch $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	sudo chmod 666 $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	
	echo "server {" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	listen 80;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	listen [::]:80;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	server_name $(DOMAIN) www.$(DOMAIN);" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_http_version 1.1;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header Upgrade \$$http_upgrade;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header Connection \"upgrade\";" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header Host \$$host;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header X-Real-IP \$$remote_addr;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header X-Forwarded-For \$$proxy_add_x_forwarded_for;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_set_header X-Forwarded-Proto \$$scheme;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	real_ip_header X-Real-IP;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	proxy_connect_timeout 300;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	location / {" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "		root $(WEB_ROOT);" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "		index index.html index.htm;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "		try_files \$$uri \$$uri/ =404;" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "	}" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	echo "}" >> $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	
	sudo chmod 644 $(NGINX_SITES_AVAILABLE)/$(DOMAIN)
	
	# Create MinIO domain configuration file
	sudo rm -f $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	sudo touch $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	sudo chmod 666 $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	
	echo "server {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	listen 80;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	listen [::]:80;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	server_name $(MINIO_DOMAIN);" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	ignore_invalid_headers off;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	client_max_body_size 0;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_buffering off;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_request_buffering off;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	# Global proxy settings for all locations" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_http_version 1.1;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header Host \$$host;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header X-Real-IP \$$remote_addr;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header X-Forwarded-For \$$proxy_add_x_forwarded_for;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header X-Forwarded-Proto \$$scheme;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	# WebSocket specific headers" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header Upgrade \$$http_upgrade;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	proxy_set_header Connection \"upgrade\";" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	# Root location" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	location / {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "		chunked_transfer_encoding off;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "		proxy_pass http://localhost:$(MINIO_PORT_1)/;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	# WebSocket specific location" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	location /ws/ {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "		proxy_pass http://localhost:$(MINIO_PORT_1)/ws/;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	location /minio/ {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "		proxy_pass http://localhost:$(MINIO_PORT_1)/;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	location /minio-storage/ {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "		proxy_pass http://localhost:$(MINIO_PORT_2)/;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "	}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	echo "}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	
	sudo chmod 644 $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN)
	
	# Enable the site configurations by creating symlinks in sites-enabled
	sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(DOMAIN) $(NGINX_SITES_ENABLED)/$(DOMAIN)
	sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN) $(NGINX_SITES_ENABLED)/$(MINIO_DOMAIN)
	
	# Verify nginx configuration and reload if valid
	sudo nginx -t && sudo systemctl reload nginx && echo "Nginx configuration updated and reloaded successfully" || echo "Nginx configuration has errors. Please check the syntax."
	
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
