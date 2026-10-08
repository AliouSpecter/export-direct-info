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

## Éditorial — stratégie de contenu SEO (règle obligatoire)

Avant de proposer ou rédiger un nouvel article sur exportdirectinfo.com, **vérifier systématiquement** :

1. Existe-t-il déjà une page EDI sur ce sujet ?
2. Quelle requête / intention de recherche principale cette page cible-t-elle déjà ?
3. Le nouvel article répond-il à une **intention différente** (pas juste un angle légèrement reformulé) ?
4. Quel est le mot-clé principal visé, précisément ?
5. Quelle(s) page(s) existante(s) doit-il compléter par un lien interne (et réciproquement) ?

**Si la réponse à la question 3 est non → ne pas créer l'article.** Améliorer/étendre la page existante à la place.

Raison : plusieurs pages ciblant la même intention se cannibalisent dans les résultats Google (vu concrètement sur le cluster "certifications PME agroalimentaires" — 4 pages coincées en position 20-29 au lieu qu'une seule ne domine). Organiser le contenu en **clusters** : une page pilier générale + des pages filles sur des angles réellement distincts (coût, labels, étude de cas, financement...), reliées entre elles par des liens internes bidirectionnels.

Cette règle s'applique à toute génération de contenu, y compris via l'automatisation (routine de rédaction + n8n).

## Note technique — contenu Elementor vs `post_content`

Certaines pages du site (au moins les articles plus anciens) sont construites avec **Elementor** : leur contenu visible n'est PAS dans le champ standard `content`/`post_content` de WordPress mais dans la meta `_elementor_data` (JSON de widgets). **Éditer `post_content` via l'API REST sur une page Elementor est silencieusement sans effet** — la donnée est enregistrée mais jamais affichée.

Avant d'éditer le corps d'un article existant, toujours vérifier lequel des deux mécanismes est utilisé (ex : chercher si le texte de l'article apparaît dans le HTML rendu de la page en le comparant à `post_content`, ou vérifier la présence de `_elementor_data` en postmeta). Pour modifier du contenu Elementor, ne pas créer d'endpoint REST générique exposé publiquement (risque de sécurité) — utiliser un script PHP à usage unique exécuté directement dans le conteneur via `docker exec wordpress php /chemin/script.php` (SSH), jamais via HTTP.

## Pipeline éditorial automatisé — état actuel (2026-10-08)

Voir `automatisations/methodologie-redaction-deep-research.md` pour le détail complet. En résumé :

- **Routine Claude "EDI — Rédaction Deep Research"** : propose les sujets, fait la recherche approfondie et rédige l'article complet (HTML) directement dans Notion. Ne touche jamais WordPress (restriction réseau sortant de son environnement).
- **`Brief_EDI`** (n8n, actif, poll 15 min) : génère le plan de recherche (Brief) et les images de couverture, les upload sur WordPress, écrit les métadonnées en texte dans Notion.
- **`Publier_EDI`** (n8n, actif, poll 15 min) : lit les pages `Article validé` prêtes (Résumé vide), crée le brouillon WordPress, marque la page comme traitée.
- **`Redaction_EDI`** (n8n) : désactivé — résidu non documenté qui faisait doublon avec la routine sur l'étape de rédaction (risque de collision/duplication de contenu). Conservé désactivé pour historique.

## Fichiers de référence

- `infrastructure/infrastructure.md` — stack complète, DNS, migration
- `infrastructure/ops-commands.md` — toutes les commandes opérationnelles
- `infrastructure/setup-hetzner.sh` — script de setup serveur
- `automatisations/methodologie-redaction-deep-research.md` — pipeline éditorial à jour
- `.env` — variables d'environnement (ne pas committer)
- `tasks.md` — tâches en cours
