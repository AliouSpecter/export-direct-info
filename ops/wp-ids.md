# IDs WordPress — exportdirectinfo.com

_Mis à jour : 2026-07-21_

> Catégories réelles du site (récupérées via `GET /wp-json/wp/v2/categories?per_page=100`).
> Les catégories initialement prévues (Export & Commerce international, Filières & Marchés, Compétitivité & Outils) n'ont pas été créées telles quelles — le site utilise une taxonomie plus simple, alignée sur Polylang FR/EN.

---

## Catégories FR

| Nom | ID WordPress | Domaine `contenu/strategie.md` correspondant |
|-----|-------------|-----|
| Agroalimentaire | 4 | Filières & Marchés, Compétitivité & Outils (fourre-tout par défaut) |
| Certifications | 6 | Certifications & Normes |
| Financements | 19 | Financement |
| Logistique & Douanes | 2 | Logistique |
| Opportunités d'export | 5 | Export & Commerce international |
| Uncategorized | 1 | (ne jamais utiliser — catégorie par défaut WP, toujours choisir une vraie catégorie) |

## Catégories EN (miroir Polylang)

| Nom | ID WordPress |
|-----|-------------|
| Agri-food | 45 |
| Certifications | 48 |
| Financing | 51 |
| Logistics & Customs | 54 |
| Export Opportunities | 57 |
| Uncategorized (EN) | 25 |

---

## Règle de choix pour la routine de rédaction

À partir du sujet de l'article, choisir la catégorie FR la plus proche :
- Certifications, normes, réglementation, HACCP, ISO, labels → **Certifications (6)**
- Financement, crédit, subventions, aides → **Financements (19)**
- Transport, douanes, incoterms, chaîne du froid → **Logistique & Douanes (2)**
- Trouver des acheteurs, accès marché, contrats export, salons → **Opportunités d'export (5)**
- Filières (cajou, karité, café...), compétitivité, outils de gestion, tout ce qui ne rentre pas ailleurs → **Agroalimentaire (4)**

Ne jamais laisser un article en "Uncategorized" (1).

---

## Tags

Seulement 3 tags existent actuellement sur le site, dont un manifestement mal saisi (une phrase entière au lieu d'un mot-clé). Pas de liste de tags fiable à réutiliser pour l'instant — la routine peut laisser les tags vides plutôt que d'en créer au hasard. À revoir plus tard si une vraie stratégie de tags est définie.

---

## Langue (si plugin bilingue)

| Langue | Code |
|--------|------|
| Français | `fr` |
| Anglais | `en` |

Plugin utilisé : Polylang.
