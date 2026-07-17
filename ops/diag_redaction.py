import urllib.request, json, os
from pathlib import Path

def load_dotenv(p):
    for l in p.read_text(encoding="utf-8").splitlines():
        l = l.strip()
        if not l or l.startswith("#") or "=" not in l: continue
        k, _, v = l.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
base = os.environ["N8N_BASE_URL"].rstrip("/")
key  = os.environ["N8N_API_KEY"]

req = urllib.request.Request(
    f"{base}/api/v1/workflows/X7qmiUHCQk8DvsXx",
    headers={"X-N8N-API-KEY": key}
)
with urllib.request.urlopen(req, timeout=20) as r:
    wf = json.loads(r.read())

print(f"Nom: {wf['name']} | Actif: {wf.get('active')}")
print("NOEUDS:")
for n in wf["nodes"]:
    print(f"  {n['name']} | type={n['type'].split('.')[-1]}")
print("CONNEXIONS:")
for src, val in wf["connections"].items():
    for branch in val.get("main", []):
        for d in branch:
            print(f"  {src} --> {d['node']}")
