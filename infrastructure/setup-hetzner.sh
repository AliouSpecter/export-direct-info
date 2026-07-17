#!/bin/bash
# Script installation Hetzner — Docker + Traefik + n8n + WordPress
# À exécuter SUR le serveur Hetzner : ssh root@91.98.130.53

set -e

DOMAIN_N8N="n8n.exportdirectinfo.com"
DOMAIN_WP="exportdirectinfo.com"
EMAIL="mamadou90ba@gmail.com"

echo "=== Installation Hetzner ==="

# 1. Mise à jour système
apt-get update -q && apt-get upgrade -y -q

# 2. Installation Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# 3. Création structure dossiers
mkdir -p /root/n8n
mkdir -p /root/wordpress
mkdir -p /root/traefik/data
touch /root/traefik/data/acme.json
chmod 600 /root/traefik/data/acme.json

# 4. Création réseau Docker
docker network create web 2>/dev/null || echo "Réseau web déjà existant"

# 5. Docker compose Traefik + n8n
cat > /root/n8n/docker-compose.yml << EOF
version: "3.8"

services:
  traefik:
    image: traefik:v3.0
    container_name: traefik
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /root/traefik/data:/data
    command:
      - "--api=false"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--certificatesresolvers.letsencrypt.acme.email=\${EMAIL}"
      - "--certificatesresolvers.letsencrypt.acme.storage=/data/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    networks:
      - web

  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n
    restart: always
    environment:
      - N8N_HOST=\${DOMAIN_N8N}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://\${DOMAIN_N8N}/
      - GENERIC_TIMEZONE=Europe/Paris
    volumes:
      - n8n_data:/home/node/.n8n
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.n8n.rule=Host(\`\${DOMAIN_N8N}\`)"
      - "traefik.http.routers.n8n.entrypoints=websecure"
      - "traefik.http.routers.n8n.tls.certresolver=letsencrypt"
      - "traefik.http.services.n8n.loadbalancer.server.port=5678"
    networks:
      - web

volumes:
  n8n_data:

networks:
  web:
    external: true
EOF

# 6. Docker compose WordPress
WP_DB_PASS=$(openssl rand -base64 16)
cat > /root/wordpress/docker-compose.yml << EOF
version: "3.8"

services:
  db:
    image: mysql:8.0
    container_name: wordpress-db
    restart: always
    environment:
      MYSQL_DATABASE: wordpress
      MYSQL_USER: wordpress
      MYSQL_PASSWORD: \${WP_DB_PASS}
      MYSQL_ROOT_PASSWORD: \${WP_DB_PASS}root
    volumes:
      - db_data:/var/lib/mysql
    networks:
      - web

  wordpress:
    image: wordpress:latest
    container_name: wordpress
    restart: always
    depends_on:
      - db
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: \${WP_DB_PASS}
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - wp_data:/var/www/html
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.wordpress.rule=Host(\`\${DOMAIN_WP}\`) || Host(\`www.\${DOMAIN_WP}\`)"
      - "traefik.http.routers.wordpress.entrypoints=websecure"
      - "traefik.http.routers.wordpress.tls.certresolver=letsencrypt"
      - "traefik.http.services.wordpress.loadbalancer.server.port=80"
    networks:
      - web

volumes:
  db_data:
  wp_data:

networks:
  web:
    external: true
EOF

# 7. Sauvegarde mot de passe DB
echo "WORDPRESS_DB_PASSWORD=\${WP_DB_PASS}" > /root/wordpress/.env
echo "✅ Mot de passe DB sauvegardé dans /root/wordpress/.env"

# 8. Démarrage Traefik + n8n
cd /root/n8n && docker compose up -d

echo "=== Installation terminée ==="
echo "n8n sera accessible sur : https://\${DOMAIN_N8N}"
echo "WordPress sera accessible sur : https://\${DOMAIN_WP}"
