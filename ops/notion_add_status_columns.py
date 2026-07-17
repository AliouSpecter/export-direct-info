"""
Ajoute les colonnes "Brief OK" et "Redaction OK" à la propriété État
de la base Notion Article EDI.
"""
import urllib.request, urllib.error, json, os
from pathlib import Path

def load_dotenv(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
token = os.environ["NOTION_API_KEY"]
raw   = "3548e6c9f9d480d8918add48a51f9198"
db_id = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
hdrs  = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28",
         "Content-Type": "application/json"}

# 1. Récupérer le schéma actuel
req = urllib.request.Request(f"https://api.notion.com/v1/databases/{db_id}", headers=hdrs)
with urllib.request.urlopen(req, timeout=20) as r:
    db = json.loads(r.read())

etat = db["properties"]["État"]["status"]
existing_names = {o["name"] for o in etat["options"]}
print("Options actuelles :", [o["name"] for o in etat["options"]])
print("Groupes actuels   :", [{g["name"]: g["option_ids"]} for g in etat["groups"]])

# 2. Ajouter les nouvelles options si elles n'existent pas déjà
NEW_OPTIONS = [
    {"name": "Brief OK",     "color": "green"},
    {"name": "Redaction OK", "color": "green"},
]
added = []
for opt in NEW_OPTIONS:
    if opt["name"] not in existing_names:
        etat["options"].append(opt)
        added.append(opt["name"])
        print(f"+ Ajout option : {opt['name']}")
    else:
        print(f"  Déjà présent : {opt['name']}")

if not added:
    print("Rien à faire.")
else:
    # 3. PATCH la base avec les nouvelles options
    body = json.dumps({"properties": {"État": {"status": etat}}}).encode()
    req2 = urllib.request.Request(
        f"https://api.notion.com/v1/databases/{db_id}",
        data=body, method="PATCH", headers=hdrs
    )
    try:
        with urllib.request.urlopen(req2, timeout=20) as r:
            result = json.loads(r.read())
            new_names = [o["name"] for o in result["properties"]["État"]["status"]["options"]]
            print("Options apres PATCH :", new_names)
            print("OK - colonnes ajoutees dans Notion.")
    except urllib.error.HTTPError as e:
        print(f"Erreur {e.code}: {e.read().decode()[:500]}")
