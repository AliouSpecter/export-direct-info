# Automatisations — Export Direct Info

_Mis à jour : 2026-08-15_

> Périmètre : **création et publication de contenu sur WordPress**, de l'idéation à la publication FR + traduction EN.
> Pour la documentation complète et à jour du pipeline (schéma détaillé, IDs de workflows, statuts Notion, comptes, historique des bugs), voir **`infrastructure/infrastructure.md`** — ce README n'en est qu'un résumé d'orientation.

---

## Infrastructure

- **Pilotage éditorial** : Notion (base "Article EDI", propriété "État" = statut du pipeline)
- **Orchestration "plomberie"** : n8n (self-hosted, `https://n8n.automationact.com`)
- **Intelligence / recherche + rédaction** : Routines Claude Code (cloud)
- **IA** : Claude (rédaction, traduction), Perplexity Sonar Pro (plan de recherche), Gemini (images)
- **Publication** : WordPress REST API (exportdirectinfo.com), bilingue FR/EN via Polylang
- **Images** : générées par Gemini, compressées (GraphicsMagick, nœud `Edit Image` n8n) puis uploadées dans la médiathèque WordPress

---

## Pipeline (résumé — schéma complet dans `infrastructure/infrastructure.md`)

```
Idée de sujet (routine hebdo ou saisie manuelle)
      │  Notion : État = "Projet d'articles"
      ▼  [validation humaine → "Brief"]
Brief_EDI (n8n)
      │  plan de recherche + 3 images compressées uploadées sur WordPress
      │  Notion : État = "Brief validé"
      ▼  [validation humaine → "Rédaction"]
Routine "EDI — Rédaction Deep Research" (Claude Code cloud)
      │  recherche multi-passes + rédaction HTML complète, écrite dans Notion
      │  Notion : État = "Article validé"
      ▼
Publier_EDI (n8n)
      │  crée le brouillon WordPress FR, lien écrit dans "Résumé"
      ▼  [validation humaine finale → publication FR]
Article FR publié
      ▼
Traduction automatique FR→EN (n8n)
      │  traduit, localise les liens internes, publie directement en EN
      ▼
Article EN publié automatiquement
```

---

## Fichiers

| Fichier | Contenu |
|---------|---------|
| `../infrastructure/infrastructure.md` | **Documentation de référence** : schéma complet, IDs de workflows, statuts Notion, comptes WP, historique des bugs corrigés |
| `methodologie-redaction-deep-research.md` | Règles de qualité éditoriale appliquées par la routine de rédaction (lu à chaque exécution) |
| `wordpress-api.md` | Guide WordPress REST API : compte WP, Application Password, endpoints, erreurs |
| `n8n-api.md` | API REST n8n : PUT vs PATCH, corps filtré, JSON (Python), rate limit |
| `workflow-brief-edi-partie1.md` | ⚠️ Historique — décrit une version antérieure de `Brief_EDI` (déclencheur Telegram), remplacée depuis par le poll Notion. Conservé pour mémoire, voir `infrastructure.md` section 3 pour l'état actuel |
| `workflows/` | JSONs n8n exportés |
