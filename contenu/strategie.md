# Stratégie Éditoriale — Export Direct Info

_Mis à jour : 2026-05-01_

---

## Positionnement éditorial

**Cible** : Dirigeants et managers de TPE/micro-entreprises agroalimentaires africaines.

**Angle** : Contenu pratique, concret, orienté solutions et gains commerciaux. Pas de théorie, pas de définitions — des mécanismes, des leviers, des coûts, du ROI, des accès marché.

**Ton** : Expert terrain, direct, actionnable. Ni condescendant ni académique.

**Format dominant** : Articles longs (1 500–3 000 mots), structurés pour le SEO classique et le GEO (moteurs IA).

---

## Domaines de contenu

| # | Domaine | Exemples de sujets |
|---|---------|-------------------|
| 1 | **Export & Commerce international** | Trouver des acheteurs, Incoterms pratiques, accès marché UE |
| 2 | **Certifications & Normes** | ISO, BIO, Fair Trade, HACCP, normes UE pour agroalimentaire |
| 3 | **Financement** | Accéder aux financements, microcrédits, fonds agricoles, BPI Afrique |
| 4 | **Logistique** | Transport, froid, douanes, incoterms, prestataires fiables |
| 5 | **Filières & Marchés** | Cacao, karité, café, mangue, noix de cajou — accès et prix |
| 6 | **Compétitivité & Outils** | Outils de gestion, réduction coûts, amélioration qualité produit |

---

## Objectifs SEO + GEO

### SEO classique
- Cibler les intentions informationnelles ET transactionnelles
- Répondre à une question précise dès l'introduction
- Titres H2/H3 autonomes (chaque section lisible indépendamment)
- Données chiffrées, tableaux comparatifs, listes actionnables

### GEO (Generative Engine Optimization)
Optimiser pour que le contenu soit extrait et cité par Perplexity, ChatGPT, Gemini :
- Informations actionnables à forte valeur ajoutée en premier
- Structurer les réponses comme des "blocs de connaissance" autonomes
- Inclure : chiffres, coûts, délais, noms d'organismes, étapes concrètes
- GEO est un **critère d'évaluation du plan**, pas un axe de contenu en soi

---

## Pipeline de production d'un article

```
Sujet fourni
     │
     ▼
[Étape 1] Agent Plan de recherche (Claude)
     │    → 3 blocs : Axes à traiter / Objectif / Bénéfices cibles
     │
     ▼
[Étape 2] Révision manuelle du plan (10 min)
     │    → Retour utilisateur si ajustements nécessaires
     │
     ▼
[Étape 3] Agent Révision plan (Claude) — si modifications demandées
     │
     ▼
[Étape 4] Plan validé → Rédaction article (Claude)
     │    → Article complet FR (HTML propre)
     │
     ▼
[Étape 5] Génération image de couverture (automatisation existante)
     │
     ▼
[Étape 6] Publication brouillon WordPress (via n8n + API REST WP)
     │
     ▼
[Étape 7] Relecture manuelle (10-15 min) → Publication
```

---

## Volume cible

- **Phase 1** : 3–5 articles / semaine
- **Langues** : FR + EN (deux versions par article)
- **Longueur** : 1 500 à 3 000 mots selon la profondeur du sujet

---

## Mots-clés prioritaires (à enrichir)

- export agroalimentaire afrique
- certification bio produits africains
- norme haccp petite entreprise agroalimentaire
- financement tpe agroalimentaire afrique
- trouver acheteurs europe produits africains
- logistique export afrique europe
- noix de cajou export côte d'ivoire
- karité burkina faso exportation
