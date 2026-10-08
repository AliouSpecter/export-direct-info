# Méthodologie de rédaction "Deep Research" — Export Direct Info

_Distillée de tests manuels validés (juillet 2026) sur les sujets HACCP puis Karité, affinée après plusieurs passages réels de la routine._

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
- Citations à sourcer : rechercher spécifiquement des déclarations ou témoignages exploitables (dirigeant, expert, responsable d'organisme, producteur) — souvent trouvables dans la presse locale en ligne et sur les réseaux sociaux, pas seulement dans les rapports institutionnels

Pour les sources les plus riches, lire la page complète (pas seulement le résumé de recherche) avant de rédiger — ça évite de perdre les chiffres précis noyés dans un résumé.

**Vigilance obligatoire** : toujours vérifier le pays/l'entité exacte d'un exemple avant de le citer. Une confusion pays a été détectée et corrigée pendant les tests (une usine citée comme référence Burkina Faso était en réalité en Côte d'Ivoire) — sourcer systématiquement évite ce type d'erreur.

**Citations et témoignages** : si la recherche fait remonter une citation ou un témoignage pertinent (dirigeant, expert, responsable d'organisme), l'intégrer dans l'article — ça renforce la crédibilité et l'ancrage terrain. Attribuer normalement (nom, fonction, source) sans mise en avant particulière du type de source.

---

## Structure attendue (calibrée sur les articles déjà publiés)

- **Ancres internes — format obligatoire** : chaque section H2 a un `id="sectionN"`. L'introduction annonce le plan sous forme d'une **liste à puces `<ul><li>`**, une puce par section, chaque puce étant un lien `<a href="#sectionN">` (lien de saut dans la même page — PAS de `target="_blank"` sur celui-ci, voir règle des liens sortants ci-dessous). PAS de liens en prose inline dans un paragraphe (ex: "on verra X, Y et Z") — toujours une vraie liste HTML, comme dans https://exportdirectinfo.com/financer-la-production-sans-credit-bancaire-classique/.
- **Tableaux** : denses, avec des chiffres réels et nommés (pas de fourchettes vagues quand une donnée précise existe). Un tableau par section quand pertinent. Si une donnée est introuvable, écrire "Non communiqué précisément" plutôt que d'inventer.
- **Citations / sources — priorité de lien** : quand une affirmation est sourcée, lier en priorité (1) la page/l'article/le rapport précis qui contient l'information ; si introuvable, (2) la sous-page ou catégorie du site source la plus proche du sujet ; si introuvable, (3) la page d'accueil du site source. Ne faire ce lien que si le site source a une autorité de domaine probable (institution officielle, média spécialisé reconnu, organisme international, grande entreprise établie) — l'objectif est de renforcer le SEO/GEO de l'article, pas de lier vers n'importe quel site trouvé en recherche. Si aucune source fiable n'a de lien exploitable, citation entre parenthèses en fin de phrase : `(Organisation, nom du document, année)`. Jamais de chiffre sans source.
- **Points clés à retenir** : encadré après les sections les plus denses en données, format `**Titre court** – description` en liste à puces (voir l'exemple réel : https://exportdirectinfo.com/financer-la-production-sans-credit-bancaire-classique/).
- **FAQ finale** : format `<details><summary>Question</summary><p>Réponse autonome</p></details>`. Aucun lien dans la FAQ.
- **Liens internes** : vers 2-3 articles déjà publiés sur exportdirectinfo.com, intégrés dans une phrase de contexte (pas une liste "à lire aussi" brute).
- **Liens sortants — règle obligatoire** : TOUT lien `<a href="...">` qui fait quitter la page courante (sources externes, liens vers d'autres articles du site) doit avoir `target="_blank" rel="noopener"` pour s'ouvrir dans un nouvel onglet et ne jamais écraser la page en cours. Seuls les liens d'ancre internes (`href="#sectionN"`, saut dans la même page) restent sans `target`.
- **Ponctuation — pas de tiret cadratin** : ne jamais utiliser le caractère `—` (tiret cadratin / em dash) dans le texte de l'article, ni dans les titres. Reformuler avec une virgule, un point, ou deux phrases séparées à la place. Un article publié en contenait, ils ont été retirés a posteriori (août 2026) — ne pas reproduire.
- **Ton et forme** : phrases courtes, paragraphes **de 5 lignes maximum** avec des retours à la ligne fréquents (mieux vaut trop découper que pas assez), vocabulaire simple (compréhensible par un agriculteur), texte justifié sauf titres et en-têtes de tableau (alignés à gauche).
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

## Architecture : rédaction (routine) et publication WordPress (n8n) sont séparées

**Découverte (août 2026)** : l'environnement cloud où tourne la routine de rédaction bloque les connexions réseau sortantes vers des domaines externes (dont `exportdirectinfo.com`) — seul le connecteur Notion (infra Anthropic) passe. La routine ne peut donc pas créer le brouillon WordPress elle-même.

**Découpage des responsabilités :**
- **Routine "EDI — Rédaction Deep Research"** : recherche + rédaction, puis écrit dans le corps de la page Notion, dans cet ordre :
  1. Un bloc `code` (langage `json`) : `{"titre_wp": "...", "categorie_wp": <id>, "image_couverture_id": <id ou null>}`
  2. Le HTML complet de l'article, découpé en blocs `code` (langage `html`, ≤1900 caractères chacun)
  3. Passe l'État à `Article validé`
  
  Elle ne touche jamais à la propriété `Résumé` et n'appelle jamais l'API WordPress.

- **Workflow n8n `Publier_EDI`** (actif, poll toutes les 3h) : cherche les pages `Article validé` dont `Résumé` est encore vide, lit les blocs Notion, reconstruit le JSON + le HTML, crée le brouillon WordPress (catégorie + image à la une), puis écrit le lien du brouillon dans `Résumé` — c'est ce remplissage qui marque la page comme traitée (empêche un retraitement).

## Chaîne de statuts Notion (base "Article EDI")

```
Projet d'articles → Brief → Brief validé → [validation humaine manuelle] → Rédaction
   → [routine de rédaction] → Article validé → [Publier_EDI, automatique] → [validation humaine manuelle] → Publication → Archivé
```

`Brief_EDI` (n8n) ne touche pas non plus à Notion pour les images : depuis août 2026, il les upload directement dans la médiathèque WordPress et n'écrit que les ID/liens en texte dans la page (voir `Brief_EDI` dans n8n).

---

## Compte auteur WordPress

Les articles créés par le pipeline sont publiés sous le compte `bot-redaction` (nom d'affichage : **Aliou BA**, changé en août 2026 pour ne pas afficher un nom de bot sur le site). Ne pas confondre avec le compte administrateur principal (`Aliou90b@`), qui a créé quelques articles antérieurs à l'existence de `bot-redaction` — ces articles-là nécessitent les identifiants admin pour être modifiés (édition impossible avec `bot-redaction`, qui n'a pas les droits sur les contenus d'un autre auteur).
