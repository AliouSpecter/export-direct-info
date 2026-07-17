import os
import urllib.request, json
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

base = os.environ.get("N8N_BASE_URL", "https://n8n.automationact.com")
key = os.environ["N8N_API_KEY"]

req = urllib.request.Request(
    f"{base}/api/v1/workflows/o5tsXNCUXy65mmQb",
    headers={"X-N8N-API-KEY": key}
)
with urllib.request.urlopen(req, timeout=30) as r:
    wf = json.loads(r.read())

print("=== NODES ===")
for n in wf["nodes"]:
    print(f"  [{n.get('disabled',False)}] {n['name']}  |  {n['type']}")

print("\n=== CONNECTIONS ===")
for src, val in wf["connections"].items():
    for branch_idx, branch in enumerate(val.get("main", [])):
        for dest in branch:
            print(f"  {src} --[{branch_idx}]--> {dest['node']}")

# Chercher des noms de noeuds référencés dans connections mais absents des nodes
node_names = {n["name"] for n in wf["nodes"]}
print("\n=== REFERENCES MANQUANTES ===")
for src, val in wf["connections"].items():
    if src not in node_names:
        print(f"  SOURCE introuvable: '{src}'")
    for branch in val.get("main", []):
        for dest in branch:
            if dest["node"] not in node_names:
                print(f"  DEST introuvable: '{dest['node']}' (depuis '{src}')")
