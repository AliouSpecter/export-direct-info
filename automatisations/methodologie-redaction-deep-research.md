# Méthodologie de rédaction "Deep Research" — Export Direct Info

_Distillée de tests manuels validés (juillet 2026) sur les sujets HACCP puis Karité._

---

## Le principe qui fait la différence de qualité

Un seul appel de recherche (une requête large, un seul prompt) produit systématiquement un article **superficiel** — fourchettes de coûts génériques, pas de noms d'organismes précis, pas de chiffres datés. C'est le défaut constaté sur les workflows n8n existants (`Redaction_EDI`, plan de recherche Sonar Pro seul).

**Ce qui marche** : une recherche dédiée par donnée précise attendue, pas une recherche large par grand thème. Concrètement, avant de rédiger, faire une recherche séparée pour chacun de ces axes (adapter selon le sujet) :
- Volumes / chiffres de marché par année
- Coût d'installation ou de mise en conformité (par pays/organisme si pertinent)
- Délais réels (avec source)
- Organismes / structures nommés (certificateurs, bailleurs, programmes)
- Emplois / impact social si pertinent
- Financements et incitations disponibles
- Logistique / accès marché
- Acheteurs / partenariats commerciaux connus

Pour les sources les plus riches, lire la page complète (pas seulement le résumé de recherche) avant de rédiger — ça évite de perdre les chiffres précis noyés dans un résumé.

**Vigilance obligatoire** : toujours vérifier le pays/l'entité exacte d'un exemple avant de le citer. Une confusion pays a été détectée et corrigée pendant les tests (une usine citée comme référence Burkina Faso était en réalité en Côte d'Ivoire) — sourcer systématiquement évite ce type d'erreur.

---

## Structure attendue (calibrée sur les articles déjà publiés)

- **Ancres internes** : chaque section H2 a un `id="sectionN"`, l'introduction annonce le plan sous forme de liens vers ces ancres.
- **Tableaux** : denses, avec des chiffres réels et nommés (pas de fourchettes vagues quand une donnée précise existe). Un tableau par section quand pertinent. Si une donnée est introuvable, écrire "Non communiqué précisément" plutôt que d'inventer.
- **Citations / sources** : lien direct sur le mot-clé ou le chiffre quand la source est fiable et l'URL fonctionnelle. Sinon, citation entre parenthèses en fin de phrase : `(Organisation, nom du document, année)`. Jamais de chiffre sans source.
- **Points clés à retenir** : encadré après les sections les plus denses en données, format `**Titre court** – description` en liste à puces (voir l'exemple réel : https://exportdirectinfo.com/financer-la-production-sans-credit-bancaire-classique/).
- **FAQ finale** : format `<details><summary>Question</summary><p>Réponse autonome</p></details>`. Aucun lien dans la FAQ.
- **Liens internes** : vers 2-3 articles déjà publiés sur exportdirectinfo.com, intégrés dans une phrase de contexte (pas une liste "à lire aussi" brute).
- **Ton et forme** : phrases courtes, paragraphes de 4-5 lignes, vocabulaire simple (compréhensible par un agriculteur), texte justifié sauf titres et en-têtes de tableau (alignés à gauche).
- **Longueur** : pas de plafond artificiel — prioriser la densité d'information même si ça dépasse 2000 mots. Les articles de référence font 3500-4500 mots.

---

## Articles déjà publiés utilisés comme référence de calibration

- https://exportdirectinfo.com/valorisation-noix-de-cajou-cote-divoire/
- https://exportdirectinfo.com/combien-coute-une-certification-agroalimentaire-et-comment-la-financer/
- https://exportdirectinfo.com/haccp-et-iso-22000-pourquoi-ces-certifications-ouvrent-les-portes-de-leurope/
- https://exportdirectinfo.com/financer-la-production-sans-credit-bancaire-classique/

---

## Écriture dans Notion — piège connu

L'ancien script `ops/n8n_create_redaction.py` tronquait l'article à 2000 caractères avant de l'écrire dans Notion (limite d'un bloc `rich_text`). **Un article complet doit être découpé en plusieurs blocs Notion** (un bloc `code`/`html` par tranche de ≤ 1900 caractères, dans l'ordre), jamais tronqué.

---

## Chaîne de statuts Notion (base "Article EDI")

```
Projet d'articles → Brief → Brief validé → [validation humaine manuelle] → Rédaction
   → [routine de rédaction] → Article validé → [validation humaine manuelle] → Publication → Archivé
```

La routine de rédaction se déclenche sur état = **"Rédaction"** et se termine en écrivant l'article + en passant l'état à **"Article validé"**. Elle ne touche pas aux images (déjà générées par `Brief_EDI`) ni au plan de recherche déjà présent dans la page.
