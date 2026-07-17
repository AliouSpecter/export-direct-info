# API REST n8n — Bonnes pratiques (instance self‑hosted)

_Mis à jour : 2026-05-01_

Contexte : Export Direct Info utilise n8n (`N8N_BASE_URL` + `N8N_API_KEY` dans `.env` à la racine du projet).

---

## Authentification

- En-tête obligatoire : `X-N8N-API-KEY: <clé>` (créée dans **Réglages → n8n API**).
- Ne pas committer la clé ; `.env` est dans `.gitignore`.

---

## Méthodes HTTP

| Opération | Méthode | Sur cette instance |
|-----------|---------|-------------------|
| Lire un workflow | `GET /api/v1/workflows/:id` | OK |
| Mettre à jour | `PATCH` | **405** — non supporté |
| Remplacer | `PUT /api/v1/workflows/:id` | OK, corps **strictement** conforme au schéma |

---

## Corps du `PUT`

Le `GET` renvoie des champs **refusés** par le `PUT`. Ne conserver que : `name`, `nodes`, `connections`, `settings` (filtré : `executionOrder`, `callerPolicy`, `errorWorkflow`).

---

## JSON : Python plutôt que PowerShell

`ConvertFrom-Json` en PowerShell fusionne les clés **sans respecter la casse** → JSON corrompu si deux nœuds ne diffèrent que par la casse. Toujours utiliser Python pour lire/modifier le JSON d'un workflow.

---

## Limite de débit (`429`)

Attendre **1–2 secondes** entre deux écritures successives.

---

## Script de smoke test

`ops/n8n_api_put_smoke_test.py` — charge `.env`, `GET` du workflow, `PUT` test de renommage, pause, `PUT` de restauration.

---

## Référence

- [Authentification API n8n](https://docs.n8n.io/api/authentication/)
- [API Workflows](https://docs.n8n.io/api/api-reference/)
