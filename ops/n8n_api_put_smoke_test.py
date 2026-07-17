"""Smoke test de l'API n8n : GET workflow, PUT renommage temporaire, PUT restauration.

Prérequis : `.env` à la racine du projet avec N8N_BASE_URL et N8N_API_KEY.
Voir `automatisations/n8n-api.md` pour les bonnes pratiques (couches PUT, rate limit, etc.).

Usage (depuis la racine « Export Direct Info ») :
    python ops/n8n_api_put_smoke_test.py
"""
import json
import os
import time
import urllib.error
import urllib.request

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


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    base = os.environ.get("N8N_BASE_URL", "").rstrip("/")
    key = os.environ.get("N8N_API_KEY", "")
    if not base or not key:
        raise SystemExit("N8N_BASE_URL ou N8N_API_KEY manquant (.env)")

    wf_id = "o5tsXNCUXy65mmQb"
    url = f"{base}/api/v1/workflows/{wf_id}"

    def http(method: str, body: bytes | None = None) -> tuple[int, str]:
        req = urllib.request.Request(
            url,
            data=body,
            headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.status, r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            return e.code, err_body

    status, raw = http("GET")
    if status != 200:
        raise SystemExit(f"GET failed {status}: {raw[:500]}")

    wf = json.loads(raw)
    orig = wf.get("name", "")
    print(f"GET: OK | name={orig!r}")

    allowed = ("name", "nodes", "connections", "settings")
    slim = {k: wf[k] for k in allowed if k in wf}
    st_obj = wf.get("settings") or {}
    slim["settings"] = {
        k: st_obj[k]
        for k in ("executionOrder", "callerPolicy", "errorWorkflow")
        if k in st_obj
    }
    slim["name"] = orig + " [API-test]"
    st, out = http("PUT", json.dumps(slim).encode("utf-8"))
    if st not in (200, 201):
        raise SystemExit(f"PUT rename failed {st}: {out[:800]}")
    print(f"PUT rename: OK (HTTP {st})")
    time.sleep(2)

    slim["name"] = orig
    st2, out2 = http("PUT", json.dumps(slim).encode("utf-8"))
    if st2 not in (200, 201):
        raise SystemExit(f"PUT revert failed {st2}: {out2[:800]}")
    print(f"PUT revert: OK (HTTP {st2})")


if __name__ == "__main__":
    main()
