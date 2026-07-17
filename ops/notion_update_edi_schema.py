"""
Met à jour le schéma de la base Notion « Export Direct Info » :
- Statut « État » : ajoute Brouillon (1er) et Validé (entre En cours et Terminé)
- Propriétés checkbox : Brief généré, Article rédigé

Usage : depuis la racine du projet
    python ops/notion_update_edi_schema.py

Charge NOTION_API_KEY et NOTION_DATABASE_ID depuis .env
"""
from __future__ import annotations

import json
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

NOTION_VERSION = "2022-06-28"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def to_uuid_hyphenated(raw: str) -> str:
    h = raw.replace("-", "").strip()
    if len(h) != 32:
        raise ValueError(f"NOTION_DATABASE_ID invalide (attendu 32 hex): {raw!r}")
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def notion_request(
    method: str,
    url: str,
    token: str,
    body: dict | None = None,
) -> tuple[int, dict | str]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        try:
            return e.code, json.loads(err)
        except json.JSONDecodeError:
            return e.code, err


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    token = os.environ.get("NOTION_API_KEY", "").strip()
    db_raw = os.environ.get("NOTION_DATABASE_ID", "").strip()
    if not token or not db_raw:
        print("NOTION_API_KEY ou NOTION_DATABASE_ID manquant dans .env", file=sys.stderr)
        sys.exit(1)

    db_id = to_uuid_hyphenated(db_raw)
    base_url = f"https://api.notion.com/v1/databases/{db_id}"

    code, db = notion_request("GET", base_url, token)
    if code != 200:
        print(f"GET database échoué ({code}): {db}", file=sys.stderr)
        sys.exit(1)

    props = db.get("properties", {})
    status_key: str | None = None
    for name, meta in props.items():
        if meta.get("type") == "status" and name.strip() == "État":
            status_key = name
            break
    if not status_key:
        print("Propriété de type « status » nommée « État » introuvable.", file=sys.stderr)
        sys.exit(1)

    st = props[status_key].get("status") or {}
    existing_opts = {o["id"]: o for o in st.get("options", [])}
    required = ["not-started", "in-progress", "done", "archived"]
    for rid in required:
        if rid not in existing_opts:
            print(f"Option statut attendue {rid!r} absente — arrêt.", file=sys.stderr)
            sys.exit(1)

    brouillon_id = str(uuid.uuid4())
    valide_id = str(uuid.uuid4())
    validation_group_id = str(uuid.uuid4())

    new_options = [
        {"id": brouillon_id, "name": "Brouillon", "color": "purple"},
        {"id": "not-started", "name": "Pas commencé", "color": "default"},
        {"id": "in-progress", "name": "En cours", "color": "blue"},
        {"id": valide_id, "name": "Validé", "color": "yellow"},
        {"id": "done", "name": "Terminé", "color": "green"},
        {"id": "archived", "name": "Archivé", "color": "gray"},
    ]

    new_groups = [
        {
            "id": "todo-status-group",
            "name": "À faire",
            "color": "gray",
            "option_ids": [brouillon_id, "not-started"],
        },
        {
            "id": "in-progress-status-group",
            "name": "En cours",
            "color": "blue",
            "option_ids": ["in-progress"],
        },
        {
            "id": validation_group_id,
            "name": "À valider",
            "color": "orange",
            "option_ids": [valide_id],
        },
        {
            "id": "complete-status-group",
            "name": "Terminé",
            "color": "green",
            "option_ids": ["done", "archived"],
        },
    ]

    patch_body: dict = {
        "properties": {
            "Brief généré": {"checkbox": {}},
            "Article rédigé": {"checkbox": {}},
            status_key: {
                "status": {
                    "options": new_options,
                    "groups": new_groups,
                },
            },
        },
    }

    code2, res = notion_request("PATCH", base_url, token, patch_body)
    if code2 != 200:
        print(f"PATCH database échoué ({code2}): {json.dumps(res, ensure_ascii=False) if isinstance(res, dict) else res}", file=sys.stderr)
        sys.exit(1)

    print("OK — schéma Notion mis à jour :")
    print("  - Statut : Brouillon, Pas commencé, En cours, Validé, Terminé, Archivé")
    print("  - Propriétés : Brief généré, Article rédigé (checkbox)")


if __name__ == "__main__":
    main()
