"""Liste les credentials et les workflows n8n pour récupérer les IDs utiles."""
import urllib.request, json, os
from pathlib import Path

def load_dotenv(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
base = os.environ["N8N_BASE_URL"].rstrip("/")
key  = os.environ["N8N_API_KEY"]

def get(path):
    req = urllib.request.Request(f"{base}{path}", headers={"X-N8N-API-KEY": key})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

# Extraire credentials depuis le workflow Brief_EDI existant
wf = get("/api/v1/workflows/o5tsXNCUXy65mmQb")
print("=== CREDENTIALS dans Brief_EDI ===")
for n in wf["nodes"]:
    creds = n.get("credentials", {})
    for ctype, cval in creds.items():
        print(f"  node={n['name'][:40]:40s}  type={ctype:25s}  id={cval.get('id','?')}  name={cval.get('name','?')}")

# Lister tous les workflows pour trouver si Redaction existe déjà
wfs = get("/api/v1/workflows?limit=50")
print("\n=== WORKFLOWS N8N ===")
for w in wfs.get("data", []):
    name = w['name'].encode('ascii', errors='replace').decode()
    print(f"  id={w['id']:20s}  actif={w['active']}  name={name}")
