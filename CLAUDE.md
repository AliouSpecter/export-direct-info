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

## Renforcement SEO (pages existantes) — ne passe jamais par le pipeline de rédaction

Depuis 2026-10-09, la routine Claude **"EDI — Alimentation Backlog"** (cron hebdo, lundi 10h Europe/Paris) propose **toujours 2 sujets par exécution** :
1. Un sujet neuf trouvé par recherche web (remplace l'ancienne logique qui puisait dans `contenu/sujets/backlog.md` — ce fichier ne contient plus de listes de sujets statiques).
2. Un sujet de **renforcement**, tiré de `contenu/sujets/backlog.md` section "## Renforcement (positions à consolider)" (alimentée manuellement par Claude à partir de Google Search Console — pas d'automatisation de cette collecte pour l'instant). La carte Notion créée est préfixée `[RENFORCEMENT]` et son champ "Résumé" contient l'URL de la page existante à améliorer.

**Important — confirmé techniquement (2026-10-09)** : une carte `[RENFORCEMENT]` ne doit **jamais** avancer vers "Brief" → "Rédaction" dans Notion. Le pipeline automatisé ne sait créer que des articles neufs :
- `Publier_EDI` ne détecte que les pages où le champ "Résumé" est vide — or il est pré-rempli par l'URL cible dès la création de la carte, donc son déclencheur ne matchera jamais une carte renforcement (blocage silencieux).
- La routine "EDI — Rédaction Deep Research" rédige toujours un article neuf complet (`<h1>` + contenu from scratch) et ne peut de toute façon pas lire la page existante (réseau sortant bloqué vers exportdirectinfo.com depuis cet environnement — testé et confirmé via `getaddrinfo ENOTFOUND`).
- Même en forçant, `Publier_EDI` ferait un `POST /wp-json/wp/v2/posts` (toujours un nouveau post), jamais une édition de l'existant.

Les cartes `[RENFORCEMENT]` se traitent uniquement **en session Claude Code locale**, avec le skill `.claude/skills/renforcement-edi/SKILL.md` (accès SSH/WordPress direct). Une fois traité : retirer la ligne de `backlog.md` (et pousser sur GitHub), archiver la carte Notion (État = "Archivé", **jamais de suppression définitive** — la déduplication de la routine se fait en comparant aux titres Notion existants, archivés inclus).

## Note technique — contenu Elementor vs `post_content`

Certaines pages du site (au moins les articles plus anciens) sont construites avec **Elementor** : leur contenu visible n'est PAS dans le champ standard `content`/`post_content` de WordPress mais dans la meta `_elementor_data` (JSON de widgets). **Éditer `post_content` via l'API REST sur une page Elementor est silencieusement sans effet** — la donnée est enregistrée mais jamais affichée.

Avant d'éditer le corps d'un article existant, toujours vérifier lequel des deux mécanismes est utilisé (ex : chercher si le texte de l'article apparaît dans le HTML rendu de la page en le comparant à `post_content`, ou vérifier la présence de `_elementor_data` en postmeta). Pour modifier du contenu Elementor, ne pas créer d'endpoint REST générique exposé publiquement (risque de sécurité) — utiliser un script PHP à usage unique exécuté directement dans le conteneur via `docker exec wordpress php /chemin/script.php` (SSH), jamais via HTTP.

## Pipeline éditorial automatisé — état actuel (2026-10-09)

Voir `automatisations/methodologie-redaction-deep-research.md` pour le détail complet de la rédaction. En résumé :

- **Routine Claude "EDI — Alimentation Backlog"** (cron hebdo, lundi 10h) : propose 2 sujets par run (1 recherche web + 1 renforcement, voir section dédiée ci-dessus). Écrit les cartes dans Notion avec État = "Projet d'articles" — jamais "Brief" directement, c'est à l'humain de valider en déplaçant la carte.
- **Routine Claude "EDI — Rédaction Deep Research"** (cron horaire) : traite les cartes à l'État "Rédaction", fait la recherche approfondie et rédige l'article complet (HTML) directement dans Notion. Ne touche jamais WordPress (restriction réseau sortant de son environnement, confirmée).
- **`Brief_EDI`** (n8n, actif, poll 15 min) : génère le plan de recherche (Brief) et les images de couverture, les upload sur WordPress, écrit les métadonnées en texte dans Notion.
- **`Publier_EDI`** (n8n, actif, poll 15 min) : lit les pages `Article validé` prêtes (Résumé vide), crée le brouillon WordPress, marque la page comme traitée. Ne gère que la création de nouveaux posts (voir section Renforcement ci-dessus).
- **`Redaction_EDI`** (n8n) : désactivé — résidu non documenté qui faisait doublon avec la routine sur l'étape de rédaction (risque de collision/duplication de contenu). Conservé désactivé pour historique.

## Fichiers de référence

- `infrastructure/infrastructure.md` — stack complète, DNS, migration
- `infrastructure/ops-commands.md` — toutes les commandes opérationnelles
- `infrastructure/setup-hetzner.sh` — script de setup serveur
- `automatisations/methodologie-redaction-deep-research.md` — pipeline éditorial à jour (rédaction d'articles neufs)
- `.claude/skills/renforcement-edi/SKILL.md` — méthode complète pour traiter une tâche de renforcement SEO (page existante)
- `contenu/sujets/backlog.md` — section "Renforcement" : opportunités GSC en attente de traitement
- `.env` — variables d'environnement (ne pas committer)
- `tasks.md` — tâches en cours
