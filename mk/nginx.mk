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
SPARK_DOMAIN = spark.communityone.com
JDBC_DOMAIN = jdbc.communityone.com
DELTASHARING_DOMAIN = deltasharing.communityone.com
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
	@if [ -f $(NGINX_CONF) ]; then \
		sudo cp $(NGINX_CONF) $(NGINX_CONF).bak; \
	fi

	# Create Spark domain configuration file
	@sudo rm -f $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@sudo touch $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@sudo chmod 644 $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)

	@echo "server {" > $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "    listen 80;" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "    listen [::]:80;" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "    server_name $(SPARK_DOMAIN);" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "    location / {" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "        proxy_pass http://localhost:8080/;" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "    }" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)
	@echo "}" >> $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN)

	@sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(SPARK_DOMAIN) $(NGINX_SITES_ENABLED)/$(SPARK_DOMAIN)

	# Create MinIO domain configuration file (Including WebSockets)
	@if [ -n "$(MINIO_DOMAIN)" ]; then \
		sudo rm -f $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		sudo touch $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		sudo chmod 644 $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "server {" > $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    listen 80;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    listen [::]:80;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    server_name $(MINIO_DOMAIN);" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    # Global proxy settings" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    proxy_http_version 1.1;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header Upgrade $$http_upgrade;' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header Connection "Upgrade";' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header Host $$host;' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header X-Real-IP $$remote_addr;' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header X-Forwarded-For $$proxy_add_x_forwarded_for;' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo '    proxy_set_header X-Forwarded-Proto $$scheme;' >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    location / {" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "        proxy_pass http://localhost:$(MINIO_PORT_1)/;" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "    }" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		echo "}" >> $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN); \
		sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(MINIO_DOMAIN) $(NGINX_SITES_ENABLED)/$(MINIO_DOMAIN); \
	else \
		echo "Error: MINIO_DOMAIN is not set. Skipping MinIO configuration."; \
	fi

	# Create JDBC domain configuration file
	@if [ -n "$(JDBC_DOMAIN)" ]; then \
		sudo rm -f $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		sudo touch $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		sudo chmod 644 $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "server {" > $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "    listen 80;" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "    listen [::]:80;" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "    server_name $(JDBC_DOMAIN);" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "    location / {" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "        proxy_pass http://localhost:10009/;" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "    }" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		echo "}" >> $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN); \
		sudo ln -sf $(NGINX_SITES_AVAILABLE)/$(JDBC_DOMAIN) $(NGINX_SITES_ENABLED)/$(JDBC_DOMAIN); \
	else \
		echo "Error: JDBC_DOMAIN is not set. Skipping JDBC configuration."; \
	fi

	# Validate Nginx configuration and reload
	@sudo nginx -t && sudo systemctl reload nginx && echo "Nginx configuration updated and reloaded successfully" || echo "Nginx configuration has errors. Please check the syntax."

nginx-restart:
	sudo systemctl restart nginx

# Clean the build directory
nginx-clean:
	rm -rf $(BUILD_DIR)/*

# Obtain SSL certificate using Certbot
nginx-certbot-setup:
	sudo certbot --nginx -d $(DOMAIN) -d www.$(DOMAIN) -d $(MINIO_DOMAIN) -d $(SPARK_DOMAIN) -d $(JDBC_DOMAIN) -d $(DELTASHARING_DOMAIN) --expand --non-interactive --agree-tos -m $(ADMIN_EMAIL) --redirect

# Set up automatic certificate renewal
nginx-certbot-renew:
	echo "0 0,12 * * * root certbot renew --quiet" | sudo tee -a /etc/crontab > /dev/null
