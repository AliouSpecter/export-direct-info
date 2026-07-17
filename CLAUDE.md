# Export Direct Info — Contexte Claude Code

## Serveur

| Paramètre | Valeur |
|-----------|--------|
| Hébergeur | Hetzner CPX22 — Nuremberg |
| IP | `91.98.130.53` |
| OS | Ubuntu 24.04 LTS |
| Accès SSH | `ssh -i ~/.ssh/id_ed25519 root@91.98.130.53` |

Claude peut exécuter des commandes sur ce serveur directement via SSH sans demander de mot de passe.

## Stack

| Couche | Outil |
|--------|-------|
| Site | WordPress (container Docker) |
| Base de données | MySQL 8.0 (container Docker) |
| Automatisation | n8n (container Docker) |
| Reverse proxy / SSL | Traefik (container Docker) |
| DNS | Cloudflare |
| Email | o2switch (mail.exportdirectinfo.com) |
| Newsletter | Brevo |

## Commandes SSH directes (Claude les exécute automatiquement)

```bash
# Connexion
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@91.98.130.53 "COMMANDE"

# Etat des containers
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@91.98.130.53 "docker ps"

# Corriger permissions WordPress
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@91.98.130.53 "docker exec wordpress chown -R www-data:www-data /var/www/html/wp-content/"

# Redémarrer WordPress
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@91.98.130.53 "docker restart wordpress"
```

## Fichiers de référence

- `infrastructure/infrastructure.md` — stack complète, DNS, migration
- `infrastructure/ops-commands.md` — toutes les commandes opérationnelles
- `infrastructure/setup-hetzner.sh` — script de setup serveur
- `.env` — variables d'environnement (ne pas committer)
- `tasks.md` — tâches en cours
