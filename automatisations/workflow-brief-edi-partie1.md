# Workflow n8n **Brief_EDI** — Partie 1 : plan de recherche & validation

_Mis à jour : 2026-05-01_

**ID workflow** : `o5tsXNCUXy65mmQb`  
Cette section décrit uniquement la **chaîne « sujet Telegram → plan → validation / correction »** (sticky note « Ecriture et validation du plan de recherche »). Les branches **images Gemini** et **rédaction (agent maître + planning)** sont traitées ailleurs dans le même canvas.

---

## Schéma d’enchaînement (partie 1)

```text
[Telegram Trigger]
        │
        ▼
[Sonar Pro - Construire plan de recherche]
        │
        ▼
[Extraire le plan de recherche]
        │
        ▼
[Fixer les variables]
        │
        ▼
[Nettoyer le texte]
        │
        ▼
[Valider le plan de recherche]  ← Telegram : message d’attente utilisateur
        │
        ▼
[Text Classifier]
    ┌───┴───┐
    │       │
 Validé   À corriger
    │       │
    │       ▼
    │   [Claude Opus 4 - Correcteur du plan de recherche]
    │       │
    │       └──► retour vers [Fixer les variables]
    │
    ▼
[set_build_prompts_request]  ← suite : branche prompts / images (hors « partie 1 » stricte)
```

---

## Rôle de chaque nœud

| Nœud | Type | Rôle |
|------|------|------|
| **Telegram Trigger** | Déclencheur Telegram | Écoute les **messages** (et callbacks). Démarre le flux quand quelqu’un envoie le **sujet** d’article dans le chat configuré. **À remplacer par un déclencheur basé sur un statut Notion.** |
| **Sonar Pro - Construire plan de recherche** | Perplexity (Sonar Pro) | Prend le texte du message comme sujet. Applique le prompt système « expert agro / SEO / GEO » et produit un **plan en 3 blocs** (axes, objectif, bénéfices). |
| **Extraire le plan de recherche** | Code (JavaScript) | Parse la réponse texte du modèle : extrait les sections **Axes**, **Objectif**, **Bénéfices** via expressions régulières et les met dans `axes`, `objectif`, `benefices`. |
| **Fixer les variables** | Set | Construit le champ unique **`Plan de recherche`**. |
| **Nettoyer le texte** | Code (JavaScript) | Post‑traitement du plan : enlève les références type `[1]`, les `**`, la numérotation en début de ligne. Sortie : **`plan_clean`**. |
| **Valider le plan de recherche** | Telegram *Send and wait* | Étape à remplacer par un statut Notion (à valider / validé). |
| **Text Classifier** | LangChain Text Classifier | Classe la réponse en **Validé** ou **À corriger**. |
| **Claude Opus 4 - Correcteur du plan de recherche** | Anthropic | Branche **À corriger** : applique le prompt « assistant éditorial », renvoie uniquement la version révisée du plan. |
| **set_build_prompts_request** | Set | Branche **Validé** : prépare le champ **`prompt_for_prompts`** pour la génération des prompts d’images. |

---

## Notes utiles

- **Lancer la rédaction** (déclencheur planifié) et **The master agent** constituent une autre entrée du workflow : rédaction longue (chercheur de sources, rédacteur, image agent).
- Voir `automatisations/workflows/Brief_EDI.pre-notion-backup.json` pour l'export complet du canvas.
