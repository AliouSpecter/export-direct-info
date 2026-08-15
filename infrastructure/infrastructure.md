# Infrastructure & Outils — exportdirectinfo.com

_Mis à jour : 2026-08-15_

> Note : ce fichier peut être renommé plus tard si son contenu (pipeline de contenu) mérite un fichier dédié séparé de l'infrastructure serveur pure. Pour l'instant tout est ici.

---

## Stack actuelle

| Couche | Outil | Détail |
|--------|-------|--------|
| Site | WordPress | Hetzner (docker) |
| Hébergement VPS principal | Hetzner CPX22 | IP : 91.98.130.53 — Nuremberg |
| Automatisation "plomberie" | n8n | Opérationnel sur Hetzner (docker), URL `https://n8n.automationact.com` |
| Automatisation "intelligence" | Routines Claude Code (cloud) | Recherche + rédaction, alimentation du backlog |
| Pilotage éditorial | Notion | Base "Article EDI" — tableau de bord unique du pipeline |
| Code / mémoire du pipeline | GitHub | Repo privé `AliouSpecter/export-direct-info` |
| DNS | Cloudflare | Zone active |
| Domaine | o2switch | Registrar conservé |
| Email | o2switch | mail.exportdirectinfo.com |
| Newsletter | Brevo | Code de vérification DNS en place |
| Contenu | Bilingue FR + EN | Polylang 3.8.3 — traduction automatique active |

---

## Serveur Hetzner CPX22

| Paramètre | Valeur |
|-----------|--------|
| IP publique | `91.98.130.53` |
| IPv6 | `2a01:4f8:1c1e:a3fb::/64` |
| OS | Ubuntu 24.04 LTS |
| Type | CPX22 — 2 vCPU AMD / 4GB RAM / 80GB SSD |
| Datacenter | Nuremberg (NBG1) |
| Accès SSH | `ssh -i ~/.ssh/id_ed25519 root@91.98.130.53` |

## Containers Docker sur Hetzner

| Container | Image | Rôle |
|-----------|-------|------|
| `n8n-traefik-1` | `traefik:v2.11` | Reverse proxy + SSL |
| `n8n-n8n-1` | `docker.n8n.io/n8nio/n8n` | Automatisations |
| `wordpress` | `wordpress:latest` | Site exportdirectinfo.com |
| `wordpress-db` | `mysql:8.0` | Base de données WordPress (préfixe tables `wpdp_`) |

## Domaines & DNS (Cloudflare)

| Type | Nom | Contenu | Rôle |
|------|-----|---------|------|
| A | `exportdirectinfo.com` | `91.98.130.53` | WordPress |
| CNAME | `www.exportdirectinfo.com` | `exportdirectinfo.com` | Redirect www |
| A | `mail.exportdirectinfo.com` | `109.234.167.40` | Email o2switch |
| A | `n8n.automationact.com` | `91.98.130.53` | n8n |

---

# Pipeline de production de contenu automatisé

Construit en plusieurs sessions à partir de juillet 2026. Objectif : produire des articles calibrés sur la qualité "Deep Research" (recherche multi-passes, tableaux et chiffres sourcés, structure SEO+GEO) de façon automatisée, avec validation humaine à des points de contrôle précis, du choix du sujet jusqu'à la publication et sa traduction.

## Vue d'ensemble

```
[EDI — Alimentation Backlog]  (routine, lundi, 2 sujets/semaine)
        │  écrit des sujets dans Notion, État = "Projet d'articles"
        ▼
 Notion : État = "Projet d'articles"
        │  ← VALIDATION HUMAINE : tu déplaces vers "Brief"
        ▼
[Brief_EDI]  (n8n, poll quotidien 9h)
        │  Perplexity Sonar Pro → plan de recherche
        │  Gemini → 3 images, uploadées directement dans la médiathèque WordPress
        │  écrit plan + références images dans Notion, État = "Brief validé"
        ▼
 Notion : État = "Brief validé"
        │  ← VALIDATION HUMAINE : tu relis le plan + images, déplaces vers "Rédaction"
        ▼
[EDI — Rédaction Deep Research]  (routine cloud, toutes les 2h)
        │  Recherche web multi-passes (une recherche par donnée précise)
        │  Rédige l'article HTML complet (méthodologie détaillée dans
        │  automatisations/methodologie-redaction-deep-research.md)
        │  écrit bloc JSON (titre/catégorie/image) + HTML dans Notion,
        │  État = "Article validé"
        ▼
 Notion : État = "Article validé", "Résumé" encore vide
        ▼
[Publier_EDI]  (n8n, poll toutes les 3h)
        │  Lit le JSON + HTML depuis Notion
        │  Crée le brouillon WordPress (catégorie + image à la une)
        │  Écrit le lien du brouillon dans "Résumé" (visible en haut de la carte)
        ▼
 Notion : "Résumé" = lien vers le brouillon WordPress
        │  ← VALIDATION HUMAINE FINALE : tu relis sur WordPress, tu publies
        ▼
 Article FR publié
        │
        ▼
[Traduction automatique FR→EN]  (n8n, toutes les heures)
        │  Traduit via Claude, localise les liens internes vers leurs
        │  équivalents EN (voir mu-plugin edi-translation-api.php)
        │  Crée le brouillon EN, le lie au FR via Polylang, copie l'image à la une
        ▼
 Brouillon EN prêt
        │  ← VALIDATION HUMAINE : tu publies la version EN
        ▼
 Article EN publié
```

Deux points de validation humaine sur le contenu (Brief validé → Rédaction, Article validé → Publication) + un troisième optionnel côté traduction (publier ou non la version EN). Le reste tourne seul.

---

## 1. Notion — tableau de bord ("Article EDI")

- URL : https://www.notion.so/3548e6c9f9d480d8918add48a51f9198
- Propriété clé : **"État"** (status) — pilote tout le pipeline
- Chaîne de statuts :
  ```
  Projet d'articles → Brief → Brief validé → Rédaction → Article validé → Publication → Archivé
  ```
- Propriété **"Résumé"** (rich_text) : contient le lien cliquable vers le brouillon WordPress une fois `Publier_EDI` passé — c'est le seul endroit à regarder pour aller relire un article.
- Propriété **"Nom de la tâche"** (title) : le sujet/titre de l'article.
- Les propriétés `Lancer rédaction`, `Brief généré`, `Article rédigé`, `Lancer brief`, `Autre tâches` sont des restes d'anciennes versions du pipeline (Gmail/Sheets) — plus utilisées, ignorer.

---

## 2. Idéation — routine `EDI — Alimentation Backlog`

| Paramètre | Valeur |
|---|---|
| Type | Routine Claude Code (cloud, `claude.ai/code/routines`) |
| ID | `trig_01C5TwvB51zh35GezvLCpssr` |
| Fréquence | Hebdomadaire, lundi 8h UTC (`0 8 * * 1`) |
| Volume | 2 sujets par exécution |

**Logique** : liste les titres déjà présents dans Notion (tous statuts), lit `contenu/sujets/backlog.md` dans le repo, choisit 2 sujets pas encore utilisés (dans des domaines différents si possible). Si le backlog est presque épuisé, fait une recherche web légère pour proposer de nouveaux sujets d'actualité alignés sur `contenu/strategie.md`. Crée les cartes Notion avec État = **"Projet d'articles"** (pas directement "Brief" — c'est volontaire : le déplacement manuel vers "Brief" sert de validation de l'idée par l'humain).

---

## 3. Plan de recherche + images — workflow n8n `Brief_EDI`

| Paramètre | Valeur |
|---|---|
| ID workflow | `o5tsXNCUXy65mmQb` |
| Déclencheur | Schedule, quotidien 9h (`triggerAtHour: 9`) |
| Statut | Actif |

**Flux** :
1. Poll Notion → cartes État = "Brief"
2. Perplexity Sonar Pro → plan de recherche en 3 blocs (axes / objectif / bénéfices), écrit dans le corps de la page Notion
3. Gemini (`gemini-2.5-flash` pour les prompts, `gemini-3-pro-image-preview` pour les images) → génère 3 images
4. **Chaque image est uploadée directement dans la médiathèque WordPress** (`POST /wp-json/wp/v2/media`, credential manuel `bot-redaction`, pas via Notion — voir "bug corrigé" plus bas) puis une ligne texte cliquable `Image WordPress generee (id=<id>) : voir l'image` est ajoutée à la page Notion
5. État → "Brief validé"

**Bug corrigé (août 2026)** : le nœud d'ajout d'image dans Notion avait un bug de bibliothèque HTTP interne à n8n (voir historique plus bas) — la solution a été de sortir complètement Notion du circuit image et d'uploader directement vers WordPress.

---

## 4. Rédaction — routine `EDI — Rédaction Deep Research`

| Paramètre | Valeur |
|---|---|
| Type | Routine Claude Code (cloud) |
| ID | `trig_01YGR8hPvk3KJLF7U8LrYLZb` |
| Fréquence | Toutes les 2h (`9 */2 * * *`) |
| Modèle | `claude-sonnet-5` |
| Repo attaché | `https://github.com/AliouSpecter/export-direct-info` |
| Connecteur | Notion |

**Logique** : cherche une carte Notion État = "Rédaction" (la plus ancienne si plusieurs). Lit `automatisations/methodologie-redaction-deep-research.md` dans le repo (méthode complète : recherche multi-passes, structure attendue, règles de liens, ponctuation) et l'applique à la lettre. Recherche web ciblée par donnée précise (pas une requête large), rédige l'article HTML complet.

**Écrit dans Notion, jamais directement dans WordPress** (l'environnement cloud de la routine bloque les connexions sortantes vers `exportdirectinfo.com` — voir historique) :
1. Un bloc `code` (langage `json`) : `{"titre_wp": "...", "categorie_wp": <id>, "image_couverture_id": <id ou null>}`
2. Le HTML complet en blocs `code` (langage `html`, tranches ≤1900 caractères)
3. État → "Article validé"

Détail complet de la méthode : voir `automatisations/methodologie-redaction-deep-research.md`.

---

## 5. Publication WordPress — workflow n8n `Publier_EDI`

| Paramètre | Valeur |
|---|---|
| ID workflow | `zH7FiUaqmHMWYPin` |
| Déclencheur | Schedule, toutes les 3h (`0 */3 * * *`) |
| Statut | Actif |

**Flux** : cherche les pages Notion État = "Article validé" **ET** "Résumé" vide (c'est ce couple de conditions qui évite de retraiter une page déjà publiée). Lit les blocs Notion, reconstruit le JSON de métadonnées + le HTML complet, crée le brouillon WordPress (`POST /wp-json/wp/v2/posts`, `status: draft`, catégorie + `featured_media`), construit le lien d'édition, l'écrit dans la propriété "Résumé" de la page Notion.

---

## 6. Catégories WordPress

Voir `ops/wp-ids.md` pour les IDs exacts et la règle de correspondance sujet → catégorie. Catégories réelles du site (différentes des 6 prévues à l'origine dans `contenu/strategie.md`) : Agroalimentaire (4), Certifications (6), Financements (19), Logistique & Douanes (2), Opportunités d'export (5).

---

## 7. Comptes WordPress utilisés par le pipeline

| Compte | Login | Rôle | Nom d'affichage | Usage |
|---|---|---|---|---|
| Rédaction automatique | `bot-redaction` | Auteur | **Aliou BA** (changé août 2026, initialement "Redaction Bot") | `Brief_EDI` (upload images), `Publier_EDI` (création brouillons) |
| Admin | `Aliou90b@` | Administrateur | — | Workflow de traduction FR→EN, édition des quelques articles antérieurs à la création de `bot-redaction` |

**Piège connu** : `bot-redaction` ne peut pas éditer un article dont il n'est pas l'auteur (erreur `rest_forbidden_context`). Les tout premiers articles du pipeline (créés avant l'existence de ce compte) appartiennent au compte admin — utiliser les identifiants admin pour les modifier.

Identifiants stockés dans `.env` local (`WP_BOT_USER`, `WP_BOT_APP_PASSWORD`, `WP_ADMIN_BASIC_AUTH`) — jamais commités.

---

## 8. Traduction automatique FR→EN

| Paramètre | Valeur |
|---|---|
| ID workflow | `SFFYVdV7rb5dC8X6` |
| Nom | Traduction automatique FR-EN (pages puis articles) |
| Fréquence | Toutes les heures (`0 * * * *`) |
| Modèle | `claude-sonnet-4-6`, max_tokens 32000 |
| Statut | Actif |

**Flux** :
1. `GET /wp-json/edi/v1/pending-translations?limit=1` — priorité pages, puis articles FR publiés sans traduction EN
2. `GET` contenu complet FR
3. Claude traduit (system prompt strict : sentence case, expressions interdites qui trahissent une traduction machine, préserve tout le HTML/tableaux/images tel quel)
4. **`POST /wp-json/edi/v1/localize-links`** (ajouté août 2026) : réécrit les liens internes du contenu traduit vers leur équivalent EN quand une traduction publiée existe (sinon laisse le lien FR, jamais de lien cassé)
5. `POST /wp/v2/posts` — crée le brouillon EN
6. `POST /wp-json/edi/v1/link-translations` — lie FR↔EN dans Polylang, copie l'image à la une FR → EN si l'EN n'en a pas déjà une

Le brouillon EN reste en `draft` — publication manuelle, comme côté FR.

---

## 9. Mu-plugin custom `edi-translation-api.php`

Fichier : `/var/www/html/wp-content/mu-plugins/edi-translation-api.php` (charge sur **chaque page** du site — toute modification doit être vérifiée avec `php -l` avant déploiement, et sauvegardée avant écrasement).

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/wp-json/edi/v1/pending-translations?limit=N` | GET | Prochain(s) item(s) FR sans traduction EN |
| `/wp-json/edi/v1/link-translations` | POST | Lie FR↔EN dans Polylang + copie l'image à la une |
| `/wp-json/edi/v1/localize-links` | POST | Réécrit les liens internes d'un contenu vers leurs équivalents EN quand ils existent (ajouté août 2026) |

---

## 10. Historique des bugs corrigés (pour référence)

- **Nœud Notion "Append image bloc" (Brief_EDI)** : erreur `Invalid request URL` systématique. Cause réelle découverte après plusieurs itérations : un bug interne à la bibliothèque HTTP historique utilisée par le nœud HTTP Request de n8n, indépendant de l'URL/des en-têtes/du contenu (vérifié en reproduisant la requête à l'identique avec succès en dehors de n8n). **Solution retenue** : sortir Notion du circuit image, uploader directement vers WordPress depuis `Brief_EDI`.
- **Réseau bloqué dans la routine de rédaction** : l'environnement cloud des routines Claude Code bloque les connexions sortantes vers des domaines externes (dont `exportdirectinfo.com`), seul le connecteur Notion (infra Anthropic) passe. **Solution** : séparation stricte — la routine écrit uniquement dans Notion, `Publier_EDI` (n8n, réseau normal) s'occupe de WordPress.
- **Code node n8n multi-items** : un nœud `Code` traitant 3 images en une seule exécution perdait 2 items sur 3 par défaut (mode `runOnceForAllItems` implicite). **Solution** : mode explicite `runOnceForEachItem` + format de retour adapté (objet simple, pas de tableau).
- **Tirets cadratins (—)** : présents dans les premiers articles générés, retirés a posteriori. Règle ajoutée à la méthodologie : jamais de `—` dans le texte des articles.
- **Elementor accidentel** : un article ouvert manuellement dans WP Admin a été marqué `_elementor_edit_mode: builder` sans contenu Elementor réel, alourdissant inutilement la page. Les articles créés par le pipeline (`Publier_EDI`) restent en édition classique par défaut ; éviter de cliquer "Modifier avec Elementor" sur un article du pipeline.

---

## Ce qui reste manuel / non construit

- Publication finale (FR et EN) : toujours un clic manuel dans WP Admin, par choix.
- Distribution réseaux sociaux (LinkedIn, Instagram, X, Facebook, Brevo) : mise de côté pour l'instant, à construire après stabilisation complète du pipeline de contenu.

---

## Thème enfant Astra — Code custom

Thème actif : **Astra Child** (parent : Astra 4.11.0)

**`functions.php`** :
1. Correctif routing Polylang EN : filtre `request` (name vs pagename)
2. Sélecteur de langue : filtre `wp_nav_menu_items`

**Attention :** ne jamais modifier `_elementor_data` via l'API WordPress meta (corrompt le JSON). Toujours passer par MySQL direct.

---

## Accès SSH — Connexion rapide

```powershell
ssh -i ~/.ssh/id_ed25519 root@91.98.130.53
```
