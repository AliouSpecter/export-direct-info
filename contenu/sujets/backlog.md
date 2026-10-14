# Backlog de sujets — Export Direct Info

*Mis à jour : 2026-10-14*

> **Fonctionnement actuel** : la routine "EDI — Alimentation Backlog" ne tire plus ses sujets d'une liste pré-écrite. À chaque exécution, elle propose toujours 2 sujets :
> 1. Un sujet trouvé par recherche web sur l'actualité récente (2026) dans les domaines du site
> 2. Un sujet de renforcement, tiré du tableau ci-dessous
>
> Seule la section "Renforcement" est lue par la routine.

---

## Renforcement (positions à consolider)

> Alimenté manuellement par Claude à partir de Google Search Console (pas d'automatisation pour l'instant — mise à jour à la demande).
> Format : mot-clé cible, page existante à améliorer, position actuelle, impressions (90 jours).
>
> *(tableau vide — les 4 opportunités identifiées le 2026-10-09 ont toutes été traitées, voir historique ci-dessous. Nouvelle collecte GSC à faire à la demande.)*

| Mot-clé | Page existante | Position | Impressions |
|---|---|---|---|

---

## Traité (historique)

- **certification agroalimentaire** → https://exportdirectinfo.com/combien-coute-une-certification-agroalimentaire-et-comment-la-financer/ (2026-10-10) : diagnostic GSC montre l'opportunité déjà largement exploitée on-page (mot-clé présent 5 fois, H2 couvrant coût/financement). Vérifié que les pages sœurs du cluster publiées par le pipeline récent (3230 HACCP micro-entreprise, 3242 Certification Bio) lient déjà vers cette page : le maillage interne est déjà en place. Tentative d'ajouter un lien supplémentaire depuis une page plus ancienne (Elementor, post 106 HACCP/ISO 22000) abandonnée à cause d'une anomalie de rendu — cause racine identifiée depuis (voir entrée suivante), non re-testée sur cette page précise. Opportunité considérée couverte ; retirée du tableau actif.
- **financement pme afrique** → https://exportdirectinfo.com/financement-des-pme-ouest-africaines-en-2025-defis-et-solutions/ (2026-10-13) : le mot-clé exact n'apparaissait nulle part dans le contenu (seulement "PME ouest-africaines"/"PME africaines"). Actions : (1) title/meta RankMath reformulés pour inclure "Afrique" explicitement ; (2) ajout d'un paragraphe intégrant la phrase "financement des PME en Afrique" + lien interne vers la page sœur du cluster Financements (post 88, "PME agroalimentaire : 7 solutions pour financer vos projets en Afrique de l'Ouest"), absent dans les deux sens auparavant. Page découverte Elementor malgré l'absence de `_elementor_data` dans le `meta` REST (faux négatif) — édition initiale faite par erreur sur `post_content` (sans effet), repérée et corrigée en éditant `_elementor_data` directement avec purge de `_elementor_element_cache`/`_elementor_page_assets` en plus de `_elementor_css`. **Cette purge supplémentaire a résolu l'anomalie documentée le 2026-10-10** — cause racine désormais connue (voir CLAUDE.md, section Elementor). Vérifié en live après coup.
- **agroalimentaire certification pme afrique** → https://exportdirectinfo.com/certifications-et-financements-pour-pme-agroalimentaires-en-afrique-de-louest/ (2026-10-14) : diagnostic GSC détaillé par query+page a montré que le hub domine déjà très largement la variante à forte volumétrie (faute de frappe "certifcation", 204 impressions, position 2.2) mais n'apparaissait pas du tout sur la variante bien orthographiée "agroalimentaire certification pme afrique", où 3 pages (études de cas post 84, 7 solutions financement post 88, coût certification post 2596) se partageaient les positions 20-24 sans qu'aucune ne domine. Les 3 pages liaient déjà vers le hub (maillage déjà en place, rien à ajouter côté liens). Cause identifiée : le H1 du hub contient bien "...en Afrique de l'Ouest" mais le title SEO (`rank_math_title`) omettait complètement "Afrique" — désalignement H1/SEO-title. Correction : title RankMath mis à jour en "Certifications et financements pour PME agroalimentaires en Afrique". Page confirmée Elementor via SSH direct (pas via le `meta` REST, cf. piège documenté) ; édition limitée au title/meta (pas de risque de contenu). La page orpheline "elementor-2989" qui apparaissait aussi dans les résultats GSC est un résidu d'indexation déjà 301-redirigé vers labels-environnementaux-benefices-pme-agroalimentaires/ — aucune action requise, l'entrée disparaîtra de l'index au prochain crawl.
- **export produits alimentaires** → https://exportdirectinfo.com/opportunites-dexport-agroalimentaire-vers-leurope-et-lasie/ (2026-10-14) : la page (hub "Agroalimentaire Ouest-Africain 2025", déjà bien maillée vers les pages sœurs du cluster export) ne contenait jamais l'expression exacte "produits alimentaires" (uniquement "agroalimentaire"). Action strictement additive, sur demande explicite de ne rien casser ni écraser : insertion d'une seule nouvelle phrase ("l'export de produits alimentaires transformés ou bruts constitue un levier de croissance majeur...") entre deux paragraphes existants de l'introduction, sans toucher au reste du contenu ni aux liens. Vérifié par contrôle d'intégrité (nombre de liens `href=` inchangé, delta de longueur de texte brut = exactement la phrase ajoutée) puis par vérification live avec contrôle d'ordre par offset octet (texte avant/après intact, nouvelle phrase bien insérée au bon endroit). Title/meta non modifiés (position faible, pas de mismatch flagrant comme sur les cas précédents). **Tableau "Renforcement" actif désormais vide** — les 4 opportunités GSC du 2026-10-09 sont toutes traitées ; prochaine collecte à faire à la demande.
