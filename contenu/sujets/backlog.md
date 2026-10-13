# Backlog de sujets — Export Direct Info

*Mis à jour : 2026-10-13*

> **Fonctionnement actuel** : la routine "EDI — Alimentation Backlog" ne tire plus ses sujets d'une liste pré-écrite. À chaque exécution, elle propose toujours 2 sujets :
> 1. Un sujet trouvé par recherche web sur l'actualité récente (2026) dans les domaines du site
> 2. Un sujet de renforcement, tiré du tableau ci-dessous
>
> Seule la section "Renforcement" est lue par la routine.

---

## Renforcement (positions à consolider)

> Alimenté manuellement par Claude à partir de Google Search Console (pas d'automatisation pour l'instant — mise à jour à la demande).
> Format : mot-clé cible, page existante à améliorer, position actuelle, impressions (90 jours).

| Mot-clé | Page existante | Position | Impressions |
|---|---|---|---|
| agroalimentaire certification pme afrique | https://exportdirectinfo.com/certifications-et-financements-pour-pme-agroalimentaires-en-afrique-de-louest/ | ~20-24 (cannibalisée sur 4 pages, hub visé) | ~60 cumulées |
| export produits alimentaires | https://exportdirectinfo.com/opportunites-dexport-agroalimentaire-vers-leurope-et-lasie/ | 25.9 | 49 |

---

## Traité (historique)

- **certification agroalimentaire** → https://exportdirectinfo.com/combien-coute-une-certification-agroalimentaire-et-comment-la-financer/ (2026-10-10) : diagnostic GSC montre l'opportunité déjà largement exploitée on-page (mot-clé présent 5 fois, H2 couvrant coût/financement). Vérifié que les pages sœurs du cluster publiées par le pipeline récent (3230 HACCP micro-entreprise, 3242 Certification Bio) lient déjà vers cette page : le maillage interne est déjà en place. Tentative d'ajouter un lien supplémentaire depuis une page plus ancienne (Elementor, post 106 HACCP/ISO 22000) abandonnée à cause d'une anomalie de rendu — cause racine identifiée depuis (voir entrée suivante), non re-testée sur cette page précise. Opportunité considérée couverte ; retirée du tableau actif.
- **financement pme afrique** → https://exportdirectinfo.com/financement-des-pme-ouest-africaines-en-2025-defis-et-solutions/ (2026-10-13) : le mot-clé exact n'apparaissait nulle part dans le contenu (seulement "PME ouest-africaines"/"PME africaines"). Actions : (1) title/meta RankMath reformulés pour inclure "Afrique" explicitement ; (2) ajout d'un paragraphe intégrant la phrase "financement des PME en Afrique" + lien interne vers la page sœur du cluster Financements (post 88, "PME agroalimentaire : 7 solutions pour financer vos projets en Afrique de l'Ouest"), absent dans les deux sens auparavant. Page découverte Elementor malgré l'absence de `_elementor_data` dans le `meta` REST (faux négatif) — édition initiale faite par erreur sur `post_content` (sans effet), repérée et corrigée en éditant `_elementor_data` directement avec purge de `_elementor_element_cache`/`_elementor_page_assets` en plus de `_elementor_css`. **Cette purge supplémentaire a résolu l'anomalie documentée le 2026-10-10** — cause racine désormais connue (voir CLAUDE.md, section Elementor). Vérifié en live après coup.
