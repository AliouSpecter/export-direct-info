# Workflow n8n **Brief_EDI** — Partie 1 : plan de recherche & validation

> ⚠️ **Document historique, non à jour.** Décrit une version antérieure de `Brief_EDI` (déclencheur Telegram, validation via Telegram *Send and wait*). Depuis mai/juin 2026, `Brief_EDI` poll directement Notion (statut "Brief") et n'utilise plus Telegram. Voir **`infrastructure/infrastructure.md`, section 3** pour la description à jour du workflow (déclencheur, flux, images compressées et uploadées sur WordPress). Conservé ici uniquement pour mémoire historique de la conception initiale.

_Rédigé : 2026-05-01_

**ID workflow** : `o5tsXNCUXy65mmQb`  
Cette section décrit uniquement la **chaîne « sujet Telegram → plan → validation / correction »** (sticky note « Ecriture et validation du plan de recherche »), telle qu'elle existait avant la bascule vers Notion. Les branches **images Gemini** et **rédaction (agent maître + planning)** décrites plus bas ont également été refondues depuis (voir `infrastructure.md`).

---

## Schéma d’enchaînement (partie 1, version historique)

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

## Rôle de chaque nœud (à l'époque de ce schéma)

| Nœud | Type | Rôle |
|------|------|------|
| **Telegram Trigger** | Déclencheur Telegram | Écoute les **messages** (et callbacks). Démarre le flux quand quelqu’un envoie le **sujet** d’article dans le chat configuré. *Remplacé depuis par un poll sur le statut Notion "Brief".* |
| **Sonar Pro - Construire plan de recherche** | Perplexity (Sonar Pro) | Prend le texte du message comme sujet. Applique le prompt système « expert agro / SEO / GEO » et produit un **plan en 3 blocs** (axes, objectif, bénéfices). Ce nœud existe toujours dans la version actuelle. |
| **Extraire le plan de recherche** | Code (JavaScript) | Parse la réponse texte du modèle : extrait les sections **Axes**, **Objectif**, **Bénéfices** via expressions régulières et les met dans `axes`, `objectif`, `benefices`. |
| **Fixer les variables** | Set | Construit le champ unique **`Plan de recherche`**. |
| **Nettoyer le texte** | Code (JavaScript) | Post‑traitement du plan : enlève les références type `[1]`, les `**`, la numérotation en début de ligne. Sortie : **`plan_clean`**. |
| **Valider le plan de recherche** | Telegram *Send and wait* | *Remplacé depuis par le déplacement manuel de la carte Notion vers "Brief validé".* |
| **Text Classifier** | LangChain Text Classifier | Classe la réponse en **Validé** ou **À corriger**. |
| **Claude Opus 4 - Correcteur du plan de recherche** | Anthropic | Branche **À corriger** : applique le prompt « assistant éditorial », renvoie uniquement la version révisée du plan. |
| **set_build_prompts_request** | Set | Branche **Validé** : prépare le champ **`prompt_for_prompts`** pour la génération des prompts d’images. |

---

## Notes utiles

- **Lancer la rédaction** (déclencheur planifié) et **The master agent** constituaient une autre entrée du workflow à l'époque : rédaction longue (chercheur de sources, rédacteur, image agent). Cette approche a été abandonnée au profit de la routine Claude Code "EDI — Rédaction Deep Research" (voir `infrastructure.md` section 4).
- Voir `automatisations/workflows/Brief_EDI.pre-notion-backup.json` pour l'export complet du canvas de l'époque.
