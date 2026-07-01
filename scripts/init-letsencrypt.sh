#!/bin/bash
# Obtain a Let's Encrypt certificate via certbot standalone mode.
#
# Usage:
#   bash scripts/init-letsencrypt.sh example.com admin@example.com [--staging]
#
# After success:
#   1. Edit nginx/conf.d/ssl/coremarket-ssl.conf — replace YOUR_DOMAIN with your domain.
#   2. Uncomment the SSL conf mount in docker-compose.prod.yml.
#   3. docker compose -f docker-compose.prod.yml exec nginx nginx -s reload

set -euo pipefail

DOMAIN="${1:?Usage: $0 <domain> <email> [--staging]}"
EMAIL="${2:?Usage: $0 <domain> <email> [--staging]}"
STAGING=""
[ "${3:-}" = "--staging" ] && STAGING="--staging"

CERTBOT_CONF="$(pwd)/certbot/conf"
CERTBOT_WWW="$(pwd)/certbot/www"

mkdir -p "$CERTBOT_CONF" "$CERTBOT_WWW"

echo "==> Stopping nginx to free port 80 ..."
docker compose -f docker-compose.prod.yml stop nginx 2>/dev/null || true

echo "==> Requesting certificate for $DOMAIN ..."
docker run --rm \
  -v "$CERTBOT_CONF:/etc/letsencrypt" \
  -v "$CERTBOT_WWW:/var/www/certbot" \
  -p 80:80 \
  certbot/certbot certonly \
  --standalone \
  --email "$EMAIL" \
  -d "$DOMAIN" \
  --agree-tos \
  --no-eff-email \
  --rsa-key-size 4096 \
  $STAGING

echo ""
echo "==> Certificate obtained at $CERTBOT_CONF/live/$DOMAIN/"
echo ""
echo "Next steps:"
echo "  1. Replace YOUR_DOMAIN in nginx/conf.d/ssl/coremarket-ssl.conf with: $DOMAIN"
echo "  2. In docker-compose.prod.yml, swap the nginx conf.d mount to coremarket-ssl.conf"
echo "  3. Restart: docker compose -f docker-compose.prod.yml up -d nginx"
echo ""
echo "Auto-renewal (add to crontab):"
echo "  0 3 1 * * cd $(pwd) && docker run --rm \\"
echo "    -v $(pwd)/certbot/conf:/etc/letsencrypt \\"
echo "    -v $(pwd)/certbot/www:/var/www/certbot \\"
echo "    certbot/certbot renew --quiet \\"
echo "  && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload"
