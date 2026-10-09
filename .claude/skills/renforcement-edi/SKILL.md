---
name: renforcement-edi
description: Traite une tâche de renforcement SEO sur une page existante d'exportdirectinfo.com (carte Notion préfixée "[RENFORCEMENT]"). Édite la page en place (title/meta, contenu, maillage) au lieu de créer un nouvel article. À utiliser quand l'utilisateur demande de traiter un renforcement, une carte [RENFORCEMENT], ou de consolider une position GSC existante.
---

# Renforcement SEO — Export Direct Info

Traite une page **existante** pour améliorer son classement, sans jamais créer de nouvel article ni de nouvelle URL. Le pipeline automatisé (Brief_EDI → routine Rédaction → Publier_EDI) ne sait PAS faire ça — il crée toujours un post neuf. Cette tâche se fait uniquement ici, en session Claude Code, avec accès direct SSH/WordPress.

## 0. Retrouver la tâche

Si l'utilisateur ne donne pas directement l'URL cible :
- Cherche dans Notion (base "Article EDI", UUID `3548e6c9-f9d4-80d8-918a-dd48a51f9198`) une carte dont le titre commence par `[RENFORCEMENT]`.
- Le champ "Résumé" de la carte contient l'URL de la page existante à améliorer.
- Sinon, consulte `contenu/sujets/backlog.md` section "## Renforcement (positions à consolider)" pour la ligne correspondante (mot-clé, page, position, impressions).

## 1. Comprendre l'opportunité (avant de toucher à quoi que ce soit)

- Interroge le MCP `gscServer` (`get_advanced_search_analytics`, dimensions `query,page`) filtré sur l'URL cible pour voir : position actuelle, impressions, CTR, et **quelles requêtes précises** amènent du trafic vers cette page.
- Vérifie s'il y a cannibalisation (plusieurs pages du site qui rankent sur le même mot-clé) — si oui, lis la règle éditoriale dans `CLAUDE.md` (section Éditorial) avant d'agir : consolider vers un hub plutôt que dupliquer.
- Regarde le title/meta actuels (champs `rank_math_title` / `rank_math_description` exposés via l'API REST WordPress, cf. mu-plugin `edi-rankmath-rest-meta.php` déjà déployé).

## 2. Décider l'action

Selon ce que montrent les données, une ou plusieurs de ces actions (pas besoin de toutes les faire) :
- **Title/meta** : reformuler pour mieux coller à la requête réelle qui génère des impressions (priorité n°1 si CTR faible malgré bonne position).
- **Maillage interne** : ajouter un lien contextuel vers/depuis le hub du cluster concerné (voir carte des clusters si elle existe, sinon regarder `contenu/strategie.md` et les pages déjà publiées sur un sujet proche).
- **Contenu** : enrichir une section trop légère, ajouter des données/chiffres manquants, corriger un point faible identifié dans les requêtes GSC.
- **Ne jamais** changer l'URL/slug sans mettre en place une redirection 301 (voir mu-plugin `edi-slug-redirects.php` existant comme modèle).

## 3. Vérifier AVANT d'éditer le contenu : Elementor ou post_content ?

**Piège connu, documenté dans `CLAUDE.md`.** Certaines pages utilisent Elementor (`_elementor_data` en postmeta), d'autres l'éditeur standard (`post_content`). Éditer le mauvais champ est silencieusement sans effet.

```bash
# Depuis ce terminal (pas besoin d'aller sur le serveur pour ce check) :
curl -s "https://exportdirectinfo.com/wp-json/wp/v2/posts/<ID>?context=edit&_fields=content" \
  -H "Authorization: $(grep '^WP_ADMIN_BASIC_AUTH=' .env | cut -d= -f2-)"
# Compare ensuite avec le HTML rendu en live (curl simple sur l'URL publique).
# Si le texte de post_content n'apparaît pas dans le rendu public → c'est Elementor.
```

## 4. Éditer en sécurité

**Si post_content (éditeur standard)** : édition directe via l'API REST (`POST /wp-json/wp/v2/posts/<ID>`), pas de piège particulier au-delà de la vérification d'intégrité (voir ci-dessous).

**Si Elementor** : **jamais d'endpoint REST générique exposé publiquement** (risque de sécurité — classificateur de sécurité le bloquera, et c'est justifié). Toujours un script PHP à usage unique, exécuté directement dans le conteneur :

```bash
ssh -i ~/.ssh/id_ed25519 -o BatchMode=yes root@91.98.130.53 \
  "docker cp /tmp/script.php wordpress:/tmp/script.php && docker exec wordpress php /tmp/script.php && docker exec wordpress rm /tmp/script.php && rm /tmp/script.php"
```

Le script doit TOUJOURS :
1. Sauvegarder l'original dans une meta de backup (`_elementor_data_backup_<date>`) avant modification.
2. Faire la modification sur une copie en mémoire, jamais en place directe.
3. **Vérifier l'intégrité du texte visible** avant d'enregistrer : extraire le texte brut (balises retirées) avant/après, comparer, et **abandonner sans sauvegarder** si le texte diffère au-delà de l'insertion prévue.
4. Comparer aussi le nombre de liens (`href=`) avant/après si la modification ne doit pas en retirer.
5. Faire un `delete_post_meta($id, '_elementor_css')` après modification pour forcer la régénération du CSS.
6. Si erreur "Permission denied" sur l'écriture du CSS : `docker exec wordpress chown -R www-data:www-data /var/www/html/wp-content/`.

## 5. Vérifier en live

Toujours confirmer le changement sur la page publique après coup (curl avec cache-busting `?v=$(date +%s)`), pas seulement en base. Pour les pages Elementor volumineuses (>100 Ko), vérifier aussi que le rendu via `\Elementor\Plugin::$instance->documents->get($id)->get_content(true)` correspond à la donnée brute — un widget trop chargé en balises peut faire perdre du contenu silencieusement au rendu (bug déjà rencontré).

## 6. Après l'édition

- Si le changement est significatif (nouveau title/meta), pas besoin de resoumettre le sitemap individuellement — le sitemap RankMath se met à jour automatiquement et Google recrawle naturellement (délai : 1-3 semaines pour voir l'effet sur les positions).
- Retire ou marque la ligne traitée dans `contenu/sujets/backlog.md` (section Renforcement) — **et pousse sur GitHub** (`AliouSpecter/export-direct-info`, pas seulement en local, car c'est le repo que lit la routine).
- Archive la carte Notion correspondante (État = "Archivé", jamais de suppression définitive — la déduplication de la routine "EDI — Alimentation Backlog" dépend de voir tous les titres, y compris archivés).

## Rappels transverses

- Avant toute modification de contenu, vérifier la règle anti-cannibalisation de `CLAUDE.md` : est-ce que ce renforcement risque de créer un conflit avec une autre page du même cluster ?
- Jamais de `.env` affiché/imprimé en clair dans une commande — toujours extraire via `grep ... | cut -d= -f2-` dans la même commande.
- Confirmer avec l'utilisateur avant toute action destructive ou tout déploiement touchant un autre service que WordPress (ex: modifier une règle Traefik affecte aussi `export-direct-solutions`).
