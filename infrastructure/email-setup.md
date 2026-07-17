# Configuration Email Pro — À faire

_Créé : 2026-05-04_

---

## Objectif

Créer des adresses email professionnelles pour les deux sites, redirigées vers un nouveau Gmail dédié, avec possibilité d'envoyer depuis les adresses pro.

## Adresses cibles

- `contact@exportdirectinfo.com`
- `contact@automationact.com`

---

## Étapes

### Étape 1 — Créer un nouveau compte Gmail dédié
- Choisir une adresse neutre, dédiée aux deux sites (pas le Gmail personnel)

### Étape 2 — Configurer Cloudflare Email Routing
- `contact@exportdirectinfo.com` → nouveau Gmail
- `contact@automationact.com` → nouveau Gmail

### Étape 3 — Configurer "Envoyer en tant que" dans Gmail
Utiliser **Brevo SMTP** (compte déjà existant) :
- Serveur : `smtp-relay.brevo.com`
- Port : `587`
- Login : email du compte Brevo
- Mot de passe : clé API SMTP Brevo

---

## Statut

- [ ] Nouveau compte Gmail créé
- [ ] Cloudflare Email Routing configuré (exportdirectinfo.com)
- [ ] Cloudflare Email Routing configuré (automationact.com)
- [ ] Gmail configuré pour envoyer depuis contact@exportdirectinfo.com
- [ ] Gmail configuré pour envoyer depuis contact@automationact.com
