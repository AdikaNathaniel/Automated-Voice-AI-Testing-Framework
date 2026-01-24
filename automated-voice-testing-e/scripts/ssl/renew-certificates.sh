#!/bin/bash
# Renew Let's Encrypt certificates manually
# Usage: ./renew-certificates.sh [--force]

set -e

nginx_path="./nginx/ssl"
certbot_path="./certbot/conf"
domains=(voiceai-testing.local)

echo "### Voice AI Testing Framework - Certificate Renewal ###"
echo ""

# Check if force renewal requested
force_arg=""
if [ "$1" == "--force" ]; then
    force_arg="--force-renewal"
    echo "Forcing certificate renewal..."
fi

# Check for docker compose
if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed"
    exit 1
fi

# Check if certbot container exists
if ! docker compose ps | grep -q certbot; then
    echo "Warning: Certbot container not running. Starting it..."
    docker compose up -d certbot
    sleep 2
fi

# Renew certificates
echo "### Attempting certificate renewal..."
docker compose run --rm --entrypoint "\
    certbot renew $force_arg" certbot

# Check if renewal was successful
if [ $? -eq 0 ]; then
    echo ""
    echo "### Updating nginx certificates..."

    # Copy renewed certificates
    if [ -f "$certbot_path/live/${domains[0]}/fullchain.pem" ]; then
        cp "$certbot_path/live/${domains[0]}/fullchain.pem" "$nginx_path/fullchain.pem"
        cp "$certbot_path/live/${domains[0]}/privkey.pem" "$nginx_path/privkey.pem"

        # Set permissions
        chmod 644 "$nginx_path/fullchain.pem"
        chmod 600 "$nginx_path/privkey.pem"

        echo "Certificates copied to nginx."
    fi

    # Reload nginx
    echo "### Reloading nginx..."
    docker compose exec nginx nginx -s reload

    echo ""
    echo "### Certificate renewal complete! ###"
else
    echo ""
    echo "### Certificate renewal failed! ###"
    echo "Check certbot logs: docker compose logs certbot"
    exit 1
fi

# Show certificate expiry
echo ""
echo "### Certificate Status ###"
docker compose run --rm --entrypoint "\
    certbot certificates" certbot
