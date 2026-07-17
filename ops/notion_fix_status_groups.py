"""
Assigne Brief OK et Redaction OK au groupe "En cours" dans la propriété État.
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

# Récupérer le schéma actuel
req = urllib.request.Request(f"https://api.notion.com/v1/databases/{db_id}", headers=hdrs)
with urllib.request.urlopen(req, timeout=20) as r:
    db = json.loads(r.read())

etat = db["properties"]["État"]["status"]

# Afficher l'état actuel pour diagnostic
print("Options avec IDs :")
for o in etat["options"]:
    print(f"  id={o.get('id','?'):40s}  name={o['name']}")

print("\nGroupes :")
for g in etat["groups"]:
    print(f"  {g['name']}: {g['option_ids']}")

# Trouver les IDs des nouvelles options
targets = {"Brief OK", "Redaction OK"}
new_ids = {o["name"]: o["id"] for o in etat["options"] if o["name"] in targets}
print(f"\nIDs a assigner : {new_ids}")

# Trouver le groupe "En cours" et y ajouter les nouvelles options
for g in etat["groups"]:
    if "cours" in g["name"].lower() or g["name"] in ("En cours", "In progress"):
        for name, oid in new_ids.items():
            if oid not in g["option_ids"]:
                g["option_ids"].append(oid)
                print(f"  Ajoute {name} ({oid}) dans groupe '{g['name']}'")

# PATCH
body = json.dumps({"properties": {"État": {"status": etat}}}).encode()
req2 = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{db_id}",
    data=body, method="PATCH", headers=hdrs
)
try:
    with urllib.request.urlopen(req2, timeout=20) as r:
        result = json.loads(r.read())
        print("\nGroupes apres PATCH :")
        for g in result["properties"]["État"]["status"]["groups"]:
            print(f"  {g['name']}: {g['option_ids']}")
        print("OK.")
except urllib.error.HTTPError as e:
    print(f"Erreur {e.code}: {e.read().decode()[:800]}")
