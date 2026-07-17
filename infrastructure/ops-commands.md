# Commandes opérationnelles — exportdirectinfo.com

_Toutes les actions ci-dessous se font depuis PowerShell Windows, sans ouvrir le navigateur._

---

## CONNEXION AU SERVEUR (toujours en premier)

```powershell
ssh root@91.98.130.53
```

---

## WORDPRESS — Santé & redémarrage

```bash
docker ps
docker stats --no-stream
docker restart wordpress
cd /root/wordpress && docker compose restart
docker logs wordpress -f
docker logs wordpress --tail 50
docker logs wordpress-db --tail 50
```

---

## WORDPRESS — Fichiers & permissions

```bash
docker exec wordpress chown -R www-data:www-data /var/www/html/wp-content/
docker exec -it wordpress bash
```

---

## WORDPRESS — Plugins & mises à jour via WP-CLI

```bash
docker exec wordpress wp plugin list --allow-root
docker exec wordpress wp plugin update --all --allow-root
docker exec wordpress wp core update --allow-root
docker exec wordpress wp cache flush --allow-root
docker exec wordpress wp rewrite flush --allow-root
```

---

## BASE DE DONNÉES

```bash
docker exec wordpress-db mysqldump \
  -u root -p$(grep MYSQL_ROOT_PASSWORD /root/wordpress/.env | cut -d= -f2) \
  wordpress > /root/backup-$(date +%Y%m%d).sql

docker exec wordpress wp db optimize --allow-root
docker exec wordpress wp db repair --allow-root
```

---

## N8N — Actions courantes

```bash
docker ps | grep n8n
docker logs n8n-n8n-1 -f
cd /root/n8n && docker compose restart
```

---

## SERVEUR — Santé générale

```bash
htop
df -h
free -h
uptime
journalctl -n 50 --no-pager
```

---

## POLYLANG / BILINGUE FR-EN

```bash
docker exec wordpress wp term list category --fields=term_id,name,slug,count --allow-root
docker exec wordpress-db mysql -u wordpress -p$(cat /root/wordpress/.env | cut -d= -f2) \
  -e "SELECT p.ID, p.post_title, p.post_status FROM wpdp_posts p
      JOIN wpdp_term_relationships tr ON p.ID=tr.object_id
      JOIN wpdp_term_taxonomy tt ON tr.term_taxonomy_id=tt.term_taxonomy_id AND tt.taxonomy='language'
      JOIN wpdp_terms t ON tt.term_id=t.term_id AND t.slug='en'
      WHERE p.post_type='post' ORDER BY p.ID;" wordpress

# Voir les articles FR sans traduction EN (prochains dans la file n8n)
# Identifiants réels dans .env / credential n8n WP_BOT — ne jamais les coller ici en clair
curl -s -u 'UTILISATEUR:APP_PASSWORD' \
  'https://exportdirectinfo.com/wp-json/edi/v1/pending-translations?limit=5'

docker exec wordpress wp post update POST_ID --post_status=publish --allow-root
```

---

## MU-PLUGIN edi-translation-api.php

```bash
docker exec wordpress cat /var/www/html/wp-content/mu-plugins/edi-translation-api.php
docker exec wordpress php -l /var/www/html/wp-content/mu-plugins/edi-translation-api.php
```

---

## HOMEPAGE EN — Maintenance

```bash
# ⚠️ IMPORTANT : ne jamais modifier _elementor_data via WP meta API (corrompt le JSON)
# Toujours passer par MySQL direct
docker exec wordpress-db mysql -u wordpress -pMOT_DE_PASSE -e "UPDATE wpdp_postmeta SET meta_value='...' WHERE post_id=3119 AND meta_key='_elementor_data'" wordpress
```

---

## QUITTER LE SERVEUR

```bash
exit
```
