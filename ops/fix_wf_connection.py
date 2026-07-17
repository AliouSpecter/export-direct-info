"""Retire la connexion orpheline vers 'Reporter Sujet et plan de recherche'."""
import json, urllib.request, urllib.error, time
from pathlib import Path

def load_dotenv(path):
    if not path.exists(): return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        import os; os.environ.setdefault(k.strip(), v.strip())

import os
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
base = os.environ["N8N_BASE_URL"].rstrip("/")
key  = os.environ["N8N_API_KEY"]
wf_id = "o5tsXNCUXy65mmQb"

req = urllib.request.Request(f"{base}/api/v1/workflows/{wf_id}", headers={"X-N8N-API-KEY": key})
with urllib.request.urlopen(req, timeout=30) as r:
    wf = json.loads(r.read())

allowed = ("name", "nodes", "connections", "settings")
slim = {k: wf[k] for k in allowed if k in wf}
st = wf.get("settings") or {}
slim["settings"] = {k: st[k] for k in ("executionOrder","callerPolicy","errorWorkflow") if k in st}

node_names = {n["name"] for n in slim["nodes"]}

# Supprimer les connexions dont la SOURCE n'existe plus
for src in list(slim["connections"]):
    if src not in node_names:
        del slim["connections"][src]
        print(f"Source orpheline supprimee: '{src}'")

# Supprimer les destinations qui n'existent plus
for src in list(slim["connections"]):
    branches = slim["connections"][src].get("main", [])
    new_branches = []
    for branch in branches:
        new_branch = [d for d in branch if d["node"] in node_names]
        new_branches.append(new_branch)
    slim["connections"][src]["main"] = new_branches

print("Noeuds presents:", [n["name"] for n in slim["nodes"]])

time.sleep(1)
body = json.dumps(slim).encode("utf-8")
req2 = urllib.request.Request(
    f"{base}/api/v1/workflows/{wf_id}",
    data=body, method="PUT",
    headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(req2, timeout=60) as r:
        print(f"PUT {r.status} - OK")
except urllib.error.HTTPError as e:
    print(f"PUT {e.code}: {e.read().decode()[:500]}")
