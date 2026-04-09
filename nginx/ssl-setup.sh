#!/usr/bin/env bash
set -euo pipefail

# SSL/HTTPS setup script using Let's Encrypt with certbot
# Usage: ./nginx/ssl-setup.sh <domain>
#
# Prerequisites:
#   - certbot installed (apt install certbot python3-certbot-nginx)
#   - DNS A record pointing to the server
#   - Port 80 and 443 open

DOMAIN="${1:-}"

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>"
    echo "Example: $0 democratia.example.com"
    exit 1
fi

NGINX_CONF="$(dirname "$0")/nginx.conf"
SSL_CONF="$(dirname "$0")/nginx-ssl.conf"

echo "=== DemocratIA HTTPS Setup ==="
echo "Domain: $DOMAIN"
echo ""

# Step 1: Obtain certificate
echo "[1/3] Obtaining SSL certificate for $DOMAIN..."
certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email admin@"$DOMAIN" \
    --domain "$DOMAIN" \
    --preferred-challenges http

CERT_PATH="/etc/letsencrypt/live/$DOMAIN"

if [ ! -f "$CERT_PATH/fullchain.pem" ]; then
    echo "ERROR: Certificate not found at $CERT_PATH"
    exit 1
fi

echo "[2/3] Generating HTTPS nginx configuration..."
cat > "$SSL_CONF" << NGINX_EOF
events {
    worker_connections 1024;
}

http {
    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name $DOMAIN;
        return 301 https://\$host\$request_uri;
    }

    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 443 ssl http2;
        server_name $DOMAIN;

        ssl_certificate $CERT_PATH/fullchain.pem;
        ssl_certificate_key $CERT_PATH/privkey.pem;

        # SSL security settings
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # HSTS
        add_header Strict-Transport-Security "max-age=63072000" always;

        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        location /docs {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
        }

        location /openapi.json {
            proxy_pass http://backend;
            proxy_set_header Host \$host;
        }

        location / {
            proxy_pass http://frontend;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
NGINX_EOF

echo "[3/3] Setting up auto-renewal cron..."
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet --post-hook 'docker compose -f $(pwd)/docker-compose.yml restart nginx'") | sort -u | crontab -

echo ""
echo "=== HTTPS setup complete ==="
echo "SSL config written to: $SSL_CONF"
echo ""
echo "To activate HTTPS, update docker-compose.yml nginx volumes:"
echo "  - ./nginx/nginx-ssl.conf:/etc/nginx/nginx.conf:ro"
echo "  - /etc/letsencrypt:/etc/letsencrypt:ro"
echo "And expose port 443:"
echo "  ports:"
echo "    - '80:80'"
echo "    - '443:443'"
