"""Inspecte la nouvelle base Notion articles pour lister les propriétés."""
import urllib.request, json
from pathlib import Path
import os

def load_dotenv(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
token = os.environ["NOTION_API_KEY"]

raw = "3548e6c9f9d480d8918add48a51f9198"
db_id = f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"

# --- Schéma de la base ---
req = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{db_id}",
    headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
)
with urllib.request.urlopen(req, timeout=20) as r:
    db = json.loads(r.read())

print("=== BASE:", db.get("title", [{}])[0].get("plain_text", "?"))
print("\n=== PROPRIETES ===")
for name, prop in db["properties"].items():
    t = prop["type"]
    extra = ""
    if t == "status":
        opts = [o["name"] for o in prop["status"].get("options", [])]
        extra = f"  options={opts}"
    elif t == "select":
        opts = [o["name"] for o in prop["select"].get("options", [])]
        extra = f"  options={opts}"
    print(f"  {name!r:30s} type={t}{extra}")

# --- Quelques pages pour voir les valeurs réelles ---
body = json.dumps({"page_size": 3}).encode()
req2 = urllib.request.Request(
    f"https://api.notion.com/v1/databases/{db_id}/query",
    data=body, method="POST",
    headers={"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28",
             "Content-Type": "application/json"}
)
with urllib.request.urlopen(req2, timeout=20) as r:
    pages = json.loads(r.read())

print("\n=== EXEMPLES DE PAGES ===")
for p in pages["results"]:
    title = ""
    etat = ""
    for name, val in p["properties"].items():
        if val["type"] == "title":
            texts = val["title"]
            title = texts[0]["plain_text"] if texts else "(vide)"
        if val["type"] == "status":
            etat = val["status"]["name"] if val["status"] else "?"
        if val["type"] == "select":
            etat = val["select"]["name"] if val["select"] else "?"
    print(f"  Titre={title!r}  Etat={etat!r}")
