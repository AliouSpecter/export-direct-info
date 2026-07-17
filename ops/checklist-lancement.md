# Checklist Lancement — Export Direct Info

*Mis à jour : 2026-05-01*

> Périmètre : création et publication de contenu sur WordPress.

---

## Phase 1 — WordPress (prérequis)

- Créer le compte utilisateur `bot-redaction` dans WP Admin (rôle : Auteur)
- Générer un Application Password pour ce compte
- Tester l'API REST : `GET https://exportdirectinfo.com/wp-json/wp/v2/posts`
- Créer les catégories WordPress (Export, Certifications, Financement, Logistique, Filières, Compétitivité)
- Vérifier le plugin bilingue FR/EN (Polylang)

---

## Phase 2 — n8n : WF-04 Publication WordPress

*Commencer par ce workflow : c'est le plus simple, pas d'IA impliquée.*

- Créer le credential `WP_BOT` dans n8n (HTTP Basic Auth)
- Construire le nœud HTTP → `POST /wp-json/wp/v2/posts` avec statut `draft`
- Tester avec un article factice
- Tester l'upload d'une image : `POST /wp-json/wp/v2/media`
- Tester la création article avec image de couverture attachée

---

## Phase 3 — n8n : WF-01 Plan de recherche

- Créer le credential `ANTHROPIC_API_KEY` dans n8n
- Construire le nœud HTTP vers l'API Anthropic
- Tester avec un sujet simple
- Vérifier le format de sortie (3 blocs attendus)

---

## Phase 4 — n8n : WF-03 Rédaction article

- Documenter le prompt de rédaction
- Construire le nœud rédaction (FR + EN)
- Connecter à l'automatisation image existante
- Chaîner WF-01 → WF-03 → WF-04 (pipeline complet)
- Test end-to-end : sujet → brouillon WP en moins de 3 minutes

---

## Phase 5 — n8n : WF-02 Révision plan *(optionnel)*

- Construire le nœud conditionnel de révision
- Tester le cas avec et sans retour utilisateur

---

## Sécurité & Maintenance

- Export JSON des workflows n8n sauvegardé (dans `automatisations/workflows/`)
- Monitoring VPS activé
- Logs des workflows activés dans n8n
- Rotation Application Password WP planifiée (tous les 6 mois)
