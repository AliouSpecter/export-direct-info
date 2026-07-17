# Infrastructure & Outils — exportdirectinfo.com

_Mis à jour : 2026-05-16_

---

## Stack actuelle

| Couche | Outil | Détail |
|--------|-------|--------|
| Site | WordPress | Hetzner (docker) |
| Hébergement VPS principal | Hetzner CPX22 | IP : 91.98.130.53 — Nuremberg |
| Automatisation | n8n | Opérationnel sur Hetzner (docker) |
| DNS | Cloudflare | Zone active — migré le 2026-05-01 |
| Domaine | o2switch | Registrar conservé |
| Email | o2switch | mail.exportdirectinfo.com — IP 109.234.167.40 |
| Newsletter | Brevo | Code de vérification DNS en place |
| Contenu | Bilingue FR + EN | ✅ Polylang 3.8.3 configuré — traduction automatique active |

---

## Serveur Hetzner CPX22

| Paramètre | Valeur |
|-----------|--------|
| IP publique | `91.98.130.53` |
| IPv6 | `2a01:4f8:1c1e:a3fb::/64` |
| OS | Ubuntu 24.04 LTS |
| Type | CPX22 — 2 vCPU AMD / 4GB RAM / 80GB SSD |
| Datacenter | Nuremberg (NBG1) |
| Accès SSH | `ssh root@91.98.130.53` (clé : `~/.ssh/id_ed25519`) |

---

## Containers Docker sur Hetzner

| Container | Image | Rôle | Statut |
|-----------|-------|------|--------|
| `n8n-traefik-1` | `traefik:v2.11` | Reverse proxy + SSL | ✅ Running |
| `n8n-n8n-1` | `docker.n8n.io/n8nio/n8n` | Automatisations | ✅ Running |
| `wordpress` | `wordpress:latest` | Site exportdirectinfo.com | ✅ Running |
| `wordpress-db` | `mysql:8.0` | Base de données WordPress | ✅ Running |

Fichiers de config :
- `/root/n8n/docker-compose.yml` — Traefik + n8n
- `/root/wordpress/docker-compose.yml` — WordPress + MySQL
- `/root/wordpress/.env` — mot de passe MySQL

---

## Domaines & DNS (Cloudflare)

| Type | Nom | Contenu | Proxy | Rôle |
|------|-----|---------|-------|------|
| A | `exportdirectinfo.com` | `91.98.130.53` | DNS only | WordPress Hetzner |
| CNAME | `www.exportdirectinfo.com` | `exportdirectinfo.com` | DNS only | Redirect www |
| A | `mail.exportdirectinfo.com` | `109.234.167.40` | DNS only | Email o2switch |
| A | `n8n.automationact.com` | `91.98.130.53` | DNS only | n8n Hetzner |

---

## WordPress — Plugins actifs

### Polylang (bilingue FR + EN, gratuit 3.8.3)

| Paramètre | Valeur |
|-----------|--------|
| Langue par défaut | Français (fr) — URLs sans préfixe |
| Langue secondaire | English (en) — URLs préfixées `/en/` |
| Préfixe tables WP | `wpdp_` (pas `wp_`) |

### Catégories FR/EN liées (Polylang)

| Catégorie FR | slug FR | Catégorie EN | slug EN |
|---|---|---|---|
| Agroalimentaire | `agroalimentaire` | Agri-food | `agri-food` |
| Certifications | `certifications` | Certifications | `certifications-en` |
| Financements | `financements` | Financing | `financing` |
| Logistique & Douanes | `logistique-douanes` | Logistics & Customs | `logistics-customs` |
| Opportunités d'export | `opportunites-dexport` | Export Opportunities | `export-opportunities` |

---

### Mu-plugin custom : `edi-translation-api.php`

Fichier : `/var/www/html/wp-content/mu-plugins/edi-translation-api.php`

**Endpoints REST :**

| Endpoint | Méthode | Rôle |
|---|---|---|
| `/wp-json/edi/v1/pending-translations?limit=1` | GET | Retourne le prochain item FR sans traduction EN |
| `/wp-json/edi/v1/link-translations` | POST | Lie FR↔EN dans Polylang + copie la featured image |

Auth : Basic Auth — valeur réelle stockée dans n8n (credential HTTP Basic Auth) et dans `.env`, jamais en clair dans ce fichier.

---

### Workflow n8n Traduction FR→EN

| Paramètre | Valeur |
|---|---|
| ID workflow | `SFFYVdV7rb5dC8X6` |
| Nom | Traduction automatique FR-EN (pages puis articles, 1/12h) |
| Modèle Claude | `claude-sonnet-4-6`, max_tokens 32000 |
| Statut | Actif ✅ |

**Flux (10 nodes) :**
1. Schedule trigger → `GET /wp-json/edi/v1/pending-translations?limit=1`
2. Extrait l'item (pages prioritaires, puis articles)
3. `GET /wp/v2/pages/{id}` ou `/wp/v2/posts/{id}`
4. Construit le prompt Claude (system prompt détaillé avec règles HTML)
5. `POST api.anthropic.com/v1/messages` — traduit via Claude
6. Parse la réponse par balises XML `<en_title>`, `<en_excerpt>`, `<en_content>`
7. `POST /wp/v2/posts` ou `/wp/v2/pages` — crée brouillon EN
8. `POST /wp-json/edi/v1/link-translations` — lie FR↔EN + copie featured image

---

### Thème enfant Astra — Code custom

Thème actif : **Astra Child** (parent : Astra 4.11.0)

**`functions.php`** :
1. Correctif routing Polylang EN : filtre `request` (name vs pagename)
2. Sélecteur de langue : filtre `wp_nav_menu_items`

**Attention :** ne jamais modifier `_elementor_data` via l'API WordPress meta (corrompt le JSON). Toujours passer par MySQL direct.

---

## Roadmap infrastructure

| Étape | Action | Statut |
|-------|--------|--------|
| A | Migration DNS → Cloudflare | ✅ Fait |
| B | Création serveur Hetzner CPX22 | ✅ Fait |
| C | Migration n8n → Hetzner | ✅ Fait |
| D | Migration WordPress → Hetzner | ✅ Fait |
| F | Plugin bilingue FR/EN — Polylang configuré | ✅ Fait |
| G | Workflow n8n traduction FR→EN | ✅ Actif |
| J | Publier brouillons EN au fil des traductions | 🔄 En cours |

---

## Accès SSH — Connexion rapide

```powershell
ssh root@91.98.130.53
```

Clé SSH : `C:\Users\mamad\.ssh\id_ed25519`

---

## Automatisations prévues

### Pipeline 1 — Génération & Publication WordPress
1. Sujet depuis le backlog
2. Recherche + rédaction (routine Claude Code Deep Research)
3. QC structure/SEO/GEO
4. Traduction FR→EN (workflow n8n existant)
5. n8n pousse l'article en **brouillon** sur WordPress via API REST
6. Validation manuelle → publication

### Pipeline 2 — Distribution réseaux sociaux
Déclenché après publication WordPress : LinkedIn, Instagram, X, Facebook, Brevo.
