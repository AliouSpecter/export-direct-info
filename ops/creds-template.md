# Credentials & Clés API — Template

*Mis à jour : 2026-05-01*

> ⚠️ **Ce fichier ne contient JAMAIS les valeurs réelles.**
> Il sert de référence pour savoir quelles clés configurer dans n8n.
> Les vraies valeurs sont stockées dans n8n → Settings → Credentials.

---

## WordPress

| Clé | Où la créer | Nom credential n8n |
| -------------------- | -------------------------------------------------------------------- | ------------------ |
| URL API | `https://exportdirectinfo.com/wp-json/wp/v2` | `WP_BOT` |
| Nom utilisateur | WP Admin → Utilisateurs → `bot-redaction` | `WP_BOT` |
| Application Password | WP Admin → Profil de `bot-redaction` → "Mots de passe d'application" | `WP_BOT` |

**Étapes** :

1. WP Admin → Utilisateurs → Ajouter → rôle **Auteur**, login `bot-redaction`
2. Ouvrir le profil de ce compte → section "Mots de passe d'application"
3. Générer → copier immédiatement (affiché une seule fois)
4. Créer dans n8n : Credentials → HTTP Basic Auth → `WP_BOT`

---

## Anthropic (Claude API)

| Clé | Où la créer | Nom credential n8n |
| ------- | ------------------------------------------------------------------- | ------------------- |
| API Key | [console.anthropic.com](https://console.anthropic.com) → API Keys | `ANTHROPIC_API_KEY` |

**Étapes** :

1. console.anthropic.com → API Keys → Create Key
2. Créer dans n8n : Credentials → Header Auth → Name: `x-api-key`, Value: la clé

---

## Notion (fichier `/.env` à la racine du projet)

| Variable | Rôle |
| ------------------------- | --------------------------------------------------------------- |
| `NOTION_API_KEY` | Secret d’intégration (My integrations → Internal integration) |
| `NOTION_DATABASE_ID` | ID de la **base** Kanban Export Direct Info (32 car. de l’URL) |
| `NOTION_PARENT_PAGE_ID` | Optionnel : page parente pour créer des pages hors base |

**Où trouver `NOTION_DATABASE_ID`** : dans l’URL de la base, segment avant `?`.

**Script** (schéma statuts + cases à cocher) : `python ops/notion_update_edi_schema.py` (lit `.env`).

---

## Checklist configuration n8n

- Credential `WP_BOT` créé et testé (test : GET /wp-json/wp/v2/users/me)
- Credential `ANTHROPIC_API_KEY` créé et testé (test : appel simple à l'API)
