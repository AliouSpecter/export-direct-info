#!/bin/bash
# Script export Hostinger → sauvegarde n8n complète (migration historique)
# À exécuter SUR l'ancien serveur Hostinger

set -e

BACKUP_DIR="/root/migration-backup"
DATE=$(date +%Y%m%d-%H%M%S)

echo "=== Démarrage export n8n ==="
mkdir -p $BACKUP_DIR

# 1. Trouver et sauvegarder le docker-compose
find /root -name "docker-compose.yml" -o -name "docker-compose.yaml" 2>/dev/null | while read f; do
  cp "$f" "$BACKUP_DIR/docker-compose.yml"
  echo "✅ docker-compose trouvé : $f"
done

# 2. Sauvegarder les volumes Docker n8n
docker run --rm \
  --volumes-from root-n8n-1 \
  -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/n8n-data.tar.gz /home/node/.n8n 2>/dev/null || \
docker run --rm \
  --volumes-from root-n8n-1 \
  -v $BACKUP_DIR:/backup \
  ubuntu bash -c "tar czf /backup/n8n-data.tar.gz \$(docker inspect root-n8n-1 --format='{{range .Mounts}}{{.Destination}} {{end}}')" 2>/dev/null || \
echo "⚠️  Tentative alternative..."

# 3. Inspecter et sauvegarder les volumes montés
docker inspect root-n8n-1 --format='{{json .Mounts}}' > $BACKUP_DIR/n8n-volumes.json
cat $BACKUP_DIR/n8n-volumes.json

# 4. Trouver le volume source et le compresser directement
N8N_SOURCE=$(docker inspect root-n8n-1 --format='{{range .Mounts}}{{if eq .Type "volume"}}{{.Source}}{{end}}{{end}}')
if [ -n "$N8N_SOURCE" ]; then
  tar czf $BACKUP_DIR/n8n-data.tar.gz -C $(dirname $N8N_SOURCE) $(basename $N8N_SOURCE)
  echo "✅ Données n8n sauvegardées"
fi

# 5. Sauvegarder config Traefik
TRAEFIK_SOURCE=$(docker inspect root-traefik-1 --format='{{range .Mounts}}{{if eq .Type "bind"}}{{.Source}} {{end}}{{end}}' 2>/dev/null)
if [ -n "$TRAEFIK_SOURCE" ]; then
  tar czf $BACKUP_DIR/traefik-data.tar.gz $TRAEFIK_SOURCE 2>/dev/null && echo "✅ Traefik sauvegardé"
fi

echo "=== Export terminé ==="
ls -lh $BACKUP_DIR/
