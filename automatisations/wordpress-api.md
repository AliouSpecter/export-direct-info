# Connexion WordPress — Publication via API REST

_Mis à jour : 2026-05-01_

---

## 1. Préparer WordPress

### Créer un compte dédié à l'automatisation

1. WP Admin → **Utilisateurs → Ajouter**
2. Login : `bot-redaction`
3. Rôle : **Auteur** (peut créer des brouillons, pas supprimer)
4. Définir un mot de passe fort (peu importe, il ne sera pas utilisé directement)

### Générer un Application Password

1. WP Admin → **Utilisateurs → bot-redaction → Modifier**
2. Descendre jusqu'à la section **"Mots de passe d'application"**
3. Nom : `n8n-auto` → cliquer **Ajouter**
4. Copier le mot de passe généré immédiatement (affiché une seule fois)
5. Format : `xxxx xxxx xxxx xxxx xxxx xxxx`

> Les Application Passwords sont disponibles nativement depuis WordPress 5.6.

---

## 2. Tester la connexion

```bash
curl -X GET https://exportdirectinfo.com/wp-json/wp/v2/users/me \
  -u "bot-redaction:xxxx xxxx xxxx xxxx xxxx xxxx"
```

Si l'API retourne 401 → vérifier que l'Application Password est bien activé et que l'API REST n'est pas bloquée par un plugin de sécurité.

---

## 3. Récupérer les IDs utiles

**Catégories :** `GET https://exportdirectinfo.com/wp-json/wp/v2/categories?per_page=100`
**Tags :** `GET https://exportdirectinfo.com/wp-json/wp/v2/tags?per_page=100`

Noter les IDs dans `ops/wp-ids.md`.

---

## 4. Uploader une image de couverture

```
POST https://exportdirectinfo.com/wp-json/wp/v2/media
```
Headers : `Authorization: Basic base64(bot-redaction:app_password)`, `Content-Type: image/jpeg`, `Content-Disposition: attachment; filename="nom-image.jpg"`

---

## 5. Créer un article en brouillon

```
POST https://exportdirectinfo.com/wp-json/wp/v2/posts
```

```json
{
  "title": "Titre de l'article",
  "content": "<h2>Section 1</h2><p>Contenu HTML...</p>",
  "excerpt": "Résumé court de l'article (150-160 caractères).",
  "status": "draft",
  "categories": [12],
  "tags": [34, 56],
  "featured_media": 789,
  "slug": "titre-article-url",
  "meta": { "_yoast_wpseo_metadesc": "Meta description SEO (150-160 caractères)." }
}
```

---

## 6. Dans n8n — Configuration du nœud HTTP

| Champ | Valeur |
|-------|--------|
| Method | POST |
| URL | `https://exportdirectinfo.com/wp-json/wp/v2/posts` |
| Authentication | Basic Auth |
| Username | `bot-redaction` |
| Password | *(Application Password généré)* |
| Body Content Type | JSON |

---

## 7. Ordre des appels dans le workflow n8n

```
1. POST /wp-json/wp/v2/media        → récupérer media_id
        ↓
2. POST /wp-json/wp/v2/posts (FR)   → brouillon FR avec featured_media = media_id
        ↓
3. POST /wp-json/wp/v2/posts (EN)   → brouillon EN
```

---

## Erreurs courantes

| Code | Cause probable | Solution |
|------|---------------|----------|
| 401 | Application Password incorrect ou API bloquée | Vérifier le plugin sécurité WP |
| 403 | Compte `bot-redaction` sans permission | Vérifier le rôle (Auteur minimum) |
| 404 | URL de l'API incorrecte | Vérifier les permaliens WP |
| 500 | Problème serveur | Vérifier les logs WP |
