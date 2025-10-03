#!/bin/bash

# SSL Setup Script using Let's Encrypt
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <domain-name>${NC}"
    echo -e "${YELLOW}Example: $0 yourdomain.com${NC}"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo -e "${GREEN}Setting up SSL for domain: $DOMAIN${NC}"

# Create necessary directories
mkdir -p nginx/conf.d
mkdir -p certbot/conf
mkdir -p certbot/www

# Create initial nginx config without SSL
cat > nginx/conf.d/default.conf << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF

echo -e "${YELLOW}Starting nginx for certificate generation...${NC}"
docker-compose -f docker-compose.prod.yml up -d nginx

echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
docker-compose -f docker-compose.prod.yml run --rm certbot \
    certonly --webroot --webroot-path /var/www/certbot \
    --email $EMAIL --agree-tos --no-eff-email \
    -d $DOMAIN -d www.$DOMAIN

# Create final nginx config with SSL
cat > nginx/conf.d/default.conf << EOF
upstream backend {
    server backend:8080;
}

upstream frontend {
    server frontend:80;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location /api/ {
        proxy_pass http://backend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /actuator/ {
        proxy_pass http://backend/actuator/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location / {
        proxy_pass http://frontend/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo -e "${YELLOW}Restarting nginx with SSL configuration...${NC}"
docker-compose -f docker-compose.prod.yml restart nginx

echo -e "${GREEN}SSL setup completed successfully!${NC}"
echo -e "${GREEN}Your site should now be accessible at: https://$DOMAIN${NC}"