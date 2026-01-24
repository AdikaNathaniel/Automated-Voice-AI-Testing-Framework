#!/bin/bash
# Generate self-signed SSL certificates for development
# Usage: ./generate-dev-certs.sh

set -e

# Configuration
domains="voiceai-testing.local,api.voiceai-testing.local,localhost"
cert_path="./nginx/ssl"
days_valid=365

echo "### Generating Self-Signed SSL Certificates for Development ###"
echo ""

# Create directories
mkdir -p "$cert_path"
mkdir -p "./certbot/conf"
mkdir -p "./certbot/www"

# Generate private key and certificate
echo "### Creating self-signed certificate..."
openssl req -x509 \
    -nodes \
    -newkey rsa:4096 \
    -days $days_valid \
    -keyout "$cert_path/privkey.pem" \
    -out "$cert_path/fullchain.pem" \
    -subj "/CN=voiceai-testing.local" \
    -addext "subjectAltName=DNS:voiceai-testing.local,DNS:api.voiceai-testing.local,DNS:localhost"

# Set permissions
chmod 600 "$cert_path/privkey.pem"
chmod 644 "$cert_path/fullchain.pem"

echo ""
echo "### Development SSL certificates generated! ###"
echo "Location: $cert_path"
echo "  - fullchain.pem (certificate)"
echo "  - privkey.pem (private key)"
echo ""
echo "Valid for: $days_valid days"
echo "Domains: $domains"
echo ""
echo "Note: Browsers will show security warnings for self-signed certs."
echo "Add an exception or import the certificate to your trusted store."
echo ""
echo "For macOS: sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain $cert_path/fullchain.pem"
echo "For Linux: sudo cp $cert_path/fullchain.pem /usr/local/share/ca-certificates/voiceai.crt && sudo update-ca-certificates"
