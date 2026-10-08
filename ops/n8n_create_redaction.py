"""
DEPRECIE (2026-10-08) : ce script est conserve pour memoire uniquement, ne pas executer.

Recreait le workflow n8n Redaction_EDI dans un etat buge et obsolete :
poll 3 min (pas 15), aucun verrou anti-collision, troncature HTML a 2000
caracteres, max_tokens 8000, pas de bloc JSON metadata. Le reexecuter
ecraserait la configuration actuelle de production et romprait la publication
WordPress. Redaction_EDI est de toute facon desactive depuis le 2026-10-08
(voir plus bas) : la redaction est faite par la routine Claude, pas par n8n.

Voir automatisations/methodologie-redaction-deep-research.md pour l'architecture
actuelle du pipeline, et automatisations/workflows/*.export.json pour l'etat
reel des workflows n8n.
"""
raise SystemExit("Script deprecie : voir le commentaire en tete de fichier, ne pas executer.")
