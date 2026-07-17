# Export Direct Info — Tableau de bord projet

_Mis à jour : 2026-05-01_

> Plateforme de contenu pour les dirigeants et managers de TPE/micro-entreprises agroalimentaires africaines.
> Site : [exportdirectinfo.com](https://exportdirectinfo.com)

---

## Structure du dossier

```
Export Direct Info/
├── README.md                              ← Vous êtes ici
│
├── projet/
│   └── vision.md                          ← Mission, cible, proposition de valeur
│
├── business-plan/
│   └── modeles.md                         ← Modèles de revenus, hypothèses
│
├── infrastructure/
│   └── infrastructure.md                  ← DNS, stack, VPS, n8n, pipeline
│
├── contenu/
│   ├── strategie.md                       ← Domaines, SEO+GEO, pipeline éditorial
│   ├── sujets/
│   │   └── backlog.md                     ← Sujets à produire
│   └── templates/
│       └── brief-article.md               ← Template à remplir avant chaque article
│
├── automatisations/
│   ├── README.md                          ← Pipeline (workflows n8n)
│   └── workflows/                         ← JSONs n8n exportés
│
└── ops/
    ├── creds-template.md                  ← Clés API à configurer (jamais de valeurs réelles ici)
    └── checklist-lancement.md             ← Checklist en 5 phases
```

---

## Statut du projet

| Bloc | Statut |
|------|--------|
| DNS → Cloudflare | ✅ Fait |
| Infrastructure Hetzner + n8n opérationnelle | ✅ Fait |
| Vision & Business plan | ✅ Documenté |
| Stratégie éditoriale | ✅ Documenté |
| Pipeline rédaction Deep Research (test manuel) | ✅ Validé |
| Pipeline automatisé bout-en-bout (routine) | ⏳ En construction |

---

## Liens utiles

- WordPress Admin : `https://exportdirectinfo.com/wp-admin`
- n8n : `https://n8n.automationact.com`
- Cloudflare Dashboard : `https://dash.cloudflare.com`
- Anthropic Console : `https://console.anthropic.com`
