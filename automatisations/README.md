# Automatisations — Export Direct Info

_Mis à jour : 2026-05-01_

> Périmètre : **création et publication de contenu sur WordPress**.
> Pipeline basé sur l'automatisation n8n existante, à adapter.

---

## Infrastructure

- **Orchestration** : n8n
- **IA** : API Anthropic (Claude), Perplexity Sonar
- **Publication** : WordPress REST API (exportdirectinfo.com)
- **Images** : Automatisation existante (brief → génération image)

---

## Pipeline

```
Sujet article
      │
      ▼
Automatisation n8n existante
(génération plan + article + image)
      │
      ▼
Publication WordPress via API REST   ←  voir wordpress-api.md
      │  POST /wp-json/wp/v2/media   (image)
      │  POST /wp-json/wp/v2/posts   (article FR — statut: draft)
      │  POST /wp-json/wp/v2/posts   (article EN — statut: draft)
      │
      ▼
⏸ Relecture manuelle dans WP Admin
      │
      ▼
Publication
```

---

## Fichiers

| Fichier | Contenu |
|---------|---------|
| `wordpress-api.md` | Guide complet : compte WP, Application Password, endpoints, erreurs |
| `n8n-api.md` | API REST n8n : PUT vs PATCH, corps filtré, JSON (Python), rate limit |
| `workflow-brief-edi-partie1.md` | Workflow **Brief_EDI** : partie 1 (Telegram → plan → validation) |
| `workflows/` | JSONs n8n exportés |
| `../ops/n8n_api_put_smoke_test.py` | Test GET + PUT + restauration (charge `.env`) |

---

## Prochaines étapes

1. Auditer et consolider les workflows EDI existants (Brief_EDI, Redaction_EDI, Create content for EDI)
2. Remplacer la validation Telegram par un statut Notion
3. Construire la routine Claude Code de rédaction Deep Research (validée manuellement, à automatiser)
