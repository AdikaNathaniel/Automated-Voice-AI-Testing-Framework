#!/bin/bash
# Initialize Let's Encrypt certificates for Voice AI Testing Framework
# Usage: ./init-letsencrypt.sh [staging|production]

set -e

# Configuration
domains=(voiceai-testing.local api.voiceai-testing.local)
email="admin@voiceai-testing.local"  # Change to your email
rsa_key_size=4096
data_path="./certbot"
nginx_path="./nginx"

# Use staging Let's Encrypt for testing (remove --staging for production)
staging_arg=""
if [ "$1" == "staging" ]; then
    staging_arg="--staging"
    echo "Using Let's Encrypt staging environment..."
fi

echo "### Voice AI Testing Framework - Let's Encrypt SSL Setup ###"
echo ""

# Check for existing certificates
if [ -d "$data_path/conf/live/${domains[0]}" ]; then
    read -p "Existing certificates found. Replace them? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
        echo "Keeping existing certificates."
        exit 0
    fi
fi

# Create required directories
echo "### Creating directories..."
mkdir -p "$data_path/conf"
mkdir -p "$data_path/www"
mkdir -p "$nginx_path/ssl"

# Download recommended TLS parameters
if [ ! -f "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -f "$data_path/conf/ssl-dhparams.pem" ]; then
    echo "### Downloading recommended TLS parameters..."
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$data_path/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$data_path/conf/ssl-dhparams.pem"
    echo ""
fi

# Create temporary self-signed certificate for initial nginx startup
echo "### Creating temporary self-signed certificate..."
path="/etc/letsencrypt/live/${domains[0]}"
mkdir -p "$data_path/conf/live/${domains[0]}"
docker compose run --rm --entrypoint "\
    openssl req -x509 -nodes -newkey rsa:$rsa_key_size -days 1\
        -keyout '$path/privkey.pem' \
        -out '$path/fullchain.pem' \
        -subj '/CN=localhost'" certbot
echo ""

# Copy temporary certs to nginx ssl directory
cp "$data_path/conf/live/${domains[0]}/fullchain.pem" "$nginx_path/ssl/fullchain.pem"
cp "$data_path/conf/live/${domains[0]}/privkey.pem" "$nginx_path/ssl/privkey.pem"

# Start nginx
echo "### Starting nginx..."
docker compose up --force-recreate -d nginx
echo ""

# Wait for nginx to be ready
echo "### Waiting for nginx..."
sleep 5

# Delete temporary certificate
echo "### Deleting temporary certificate..."
docker compose run --rm --entrypoint "\
    rm -Rf /etc/letsencrypt/live/${domains[0]} && \
    rm -Rf /etc/letsencrypt/archive/${domains[0]} && \
    rm -Rf /etc/letsencrypt/renewal/${domains[0]}.conf" certbot
echo ""

# Request Let's Encrypt certificate
echo "### Requesting Let's Encrypt certificate for ${domains[@]}..."
domain_args=""
for domain in "${domains[@]}"; do
    domain_args="$domain_args -d $domain"
done

# Enable this for actual cert request
docker compose run --rm --entrypoint "\
    certbot certonly --webroot -w /var/www/certbot \
        $staging_arg \
        $domain_args \
        --email $email \
        --rsa-key-size $rsa_key_size \
        --agree-tos \
        --force-renewal \
        --non-interactive" certbot
echo ""

# Copy certificates to nginx ssl directory
echo "### Copying certificates to nginx..."
cp "$data_path/conf/live/${domains[0]}/fullchain.pem" "$nginx_path/ssl/fullchain.pem"
cp "$data_path/conf/live/${domains[0]}/privkey.pem" "$nginx_path/ssl/privkey.pem"

# Reload nginx
echo "### Reloading nginx..."
docker compose exec nginx nginx -s reload

echo ""
echo "### SSL setup complete! ###"
echo "Certificates installed for: ${domains[@]}"
echo ""
echo "Certificate renewal is automatic via the certbot container."
echo "To manually renew: docker compose run --rm certbot renew"
