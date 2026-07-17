"""
Workflow Brief_EDI — version propre
====================================
Déclencheur : cron 3 min → pages Notion dont État = "Brief"
Traitement   : Sonar génère le plan → écrit dans la page Notion
Fin          : passe la carte en État = "Brief"

Base Notion : Article EDI  (3548e6c9f9d480d8918add48a51f9198)
Workflow n8n : o5tsXNCUXy65mmQb

Pas de checkboxes — la colonne Kanban EST le statut.

Usage :
  python ops/n8n_patch_brief_edi_notion.py
"""
from __future__ import annotations
import json, os, time, uuid, urllib.request, urllib.error
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


def n8n_get(base: str, key: str, wf_id: str) -> dict:
    req = urllib.request.Request(
        f"{base}/api/v1/workflows/{wf_id}",
        headers={"X-N8N-API-KEY": key},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def n8n_put(base: str, key: str, wf_id: str, slim: dict) -> tuple[int, str]:
    body = json.dumps(slim).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/v1/workflows/{wf_id}",
        data=body, method="PUT",
        headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")


def slim_wf(wf: dict) -> dict:
    """Réduit le workflow aux champs acceptés par PUT."""
    allowed = ("name", "nodes", "connections", "settings")
    s = {k: wf[k] for k in allowed if k in wf}
    st = wf.get("settings") or {}
    s["settings"] = {k: st[k] for k in ("executionOrder", "callerPolicy", "errorWorkflow") if k in st}
    return s


def clean_orphans(slim: dict) -> None:
    """Retire les connexions dont la source ou la destination n'existe plus."""
    names = {n["name"] for n in slim["nodes"]}
    for src in list(slim["connections"]):
        if src not in names:
            del slim["connections"][src]
            continue
        branches = slim["connections"][src].get("main", [])
        slim["connections"][src]["main"] = [
            [d for d in branch if d["node"] in names]
            for branch in branches
        ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    base = os.environ.get("N8N_BASE_URL", "").rstrip("/")
    key  = os.environ.get("N8N_API_KEY", "").strip()
    if not base or not key:
        raise SystemExit("N8N_BASE_URL ou N8N_API_KEY manquant dans .env")

    WF_ID = "o5tsXNCUXy65mmQb"

    raw_db = "3548e6c9f9d480d8918add48a51f9198"
    db_uuid = f"{raw_db[:8]}-{raw_db[8:12]}-{raw_db[12:16]}-{raw_db[16:20]}-{raw_db[20:]}"

    wf   = n8n_get(base, key, WF_ID)
    slim = slim_wf(wf)
    nodes = slim["nodes"]
    conns = slim["connections"]

    id_poll       = str(uuid.uuid4())
    id_list       = str(uuid.uuid4())
    id_ctx        = str(uuid.uuid4())
    id_build      = str(uuid.uuid4())
    id_write      = str(uuid.uuid4())
    id_fin        = str(uuid.uuid4())

    SCHEDULE = {
        "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 3}]}},
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [-500, 0],
        "id": id_poll,
        "name": "Poll Notion — articles",
    }

    NOTION_LIST = {
        "parameters": {
            "resource": "databasePage",
            "operation": "getAll",
            "databaseId": {"__rl": True, "value": db_uuid, "mode": "id",
                           "cachedResultName": "Article EDI"},
            "returnAll": False,
            "limit": 5,
            "simple": False,
            "filterType": "manual",
            "matchType": "and",
            "filters": {
                "conditions": [
                    {
                        "key": "État|status",
                        "condition": "equals",
                        "statusValue": "Brief",
                    }
                ]
            },
        },
        "type": "n8n-nodes-base.notion",
        "typeVersion": 2.2,
        "position": [-280, 0],
        "id": id_list,
        "name": "Notion — liste Projet articles",
        "credentials": {
            "notionApi": {"id": "REMPLACER_CREDENTIAL_NOTION_N8N",
                          "name": "Notion API"}
        },
    }

    CTX_CODE = {
        "parameters": {
            "jsCode": (
                "const p = $json.properties || {};\n"
                "const titleProp = p['Nom de la tâche'] || {};\n"
                "const title = (titleProp.title && titleProp.title[0] "
                    "&& titleProp.title[0].plain_text) || '';\n"
                "return [{\n"
                "  json: {\n"
                "    message: { text: title.trim() },\n"
                "    notion_page_id: $json.id,\n"
                "  },\n"
                "}];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-60, 0],
        "id": id_ctx,
        "name": "Contexte Notion (sujet)",
    }

    CODE_BUILD = {
        "parameters": {
            "jsCode": (
                "const raw = ($json.choices && $json.choices[0] && $json.choices[0].message)\n"
                "  ? $json.choices[0].message.content\n"
                "  : ($json.content || '');\n"
                "const plan = String(raw || '').substring(0, 1990);\n"
                "const pageId = $('Contexte Notion (sujet)').first().json.notion_page_id;\n"
                "const notion_blocks = {\n"
                "  children: [\n"
                "    { type: 'heading_2', heading_2: { rich_text: [{ type: 'text', "
                "text: { content: 'Brief genere' } }] } },\n"
                "    { type: 'paragraph', paragraph: { rich_text: [{ type: 'text', "
                "text: { content: plan } }] } }\n"
                "  ]\n"
                "};\n"
                "return [{ json: { notion_page_id: pageId, notion_blocks } }];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1200, 0],
        "id": id_build,
        "name": "Build brief body",
    }

    NOTION_WRITE = {
        "parameters": {
            "method": "PATCH",
            "url": "={{ 'https://api.notion.com/v1/blocks/' + $json.notion_page_id + '/children' }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "notionApi",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "Notion-Version", "value": "2022-06-28"},
            ]},
            "sendBody": True,
            "contentType": "json",
            "specifyBody": "json",
            "jsonBody": "={{ $json.notion_blocks }}",
            "options": {},
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [1440, 0],
        "id": id_write,
        "name": "Notion — Ecrire brief",
        "credentials": {
            "notionApi": {"id": "REMPLACER_CREDENTIAL_NOTION_N8N",
                          "name": "Notion API"}
        },
    }

    NOTION_FIN = {
        "parameters": {
            "resource": "databasePage",
            "operation": "update",
            "pageId": {
                "__rl": True,
                "value": "={{ $('Contexte Notion (sujet)').first().json.notion_page_id }}",
                "mode": "id",
            },
            "propertiesUi": {
                "propertyValues": [
                    {"key": "État|status", "statusValue": "Brief validé"},
                ]
            },
            "options": {},
        },
        "type": "n8n-nodes-base.notion",
        "typeVersion": 2.2,
        "position": [1680, 0],
        "id": id_fin,
        "name": "Notion — fin brief (etat)",
        "credentials": {
            "notionApi": {"id": "REMPLACER_CREDENTIAL_NOTION_N8N",
                          "name": "Notion API"}
        },
    }

    PATCHED = {
        "Poll Notion — Lancer brief",
        "Poll Notion — articles",
        "Notion — Lancer brief (liste)",
        "Notion — liste Projet articles",
        "Filtre Lancer brief",
        "Contexte Notion (sujet)",
        "Build brief body",
        "Notion — Ecrire brief",
        "Notion — fin brief (cases)",
        "Notion — fin brief (etat)",
    }
    nodes[:] = [n for n in nodes if n.get("name") not in PATCHED]
    nodes.extend([SCHEDULE, NOTION_LIST, CTX_CODE, CODE_BUILD, NOTION_WRITE, NOTION_FIN])

    conns["Poll Notion — articles"]          = {"main": [[{"node": "Notion — liste Projet articles", "type": "main", "index": 0}]]}
    conns["Notion — liste Projet articles"]  = {"main": [[{"node": "Contexte Notion (sujet)",        "type": "main", "index": 0}]]}
    conns["Contexte Notion (sujet)"]         = {"main": [[{"node": "Sonar Pro - Construire plan de recherche", "type": "main", "index": 0}]]}

    for dead in ("Telegram Trigger", "Valider le plan de recherche",
                 "Text Classifier", "Claude Opus 4 - Correcteur du plan de recherche"):
        conns.pop(dead, None)

    conns["Sonar Pro - Construire plan de recherche"] = {"main": [[{"node": "Build brief body", "type": "main", "index": 0}]]}
    conns["Build brief body"]       = {"main": [[{"node": "Notion — Ecrire brief",    "type": "main", "index": 0}]]}
    conns["Notion — Ecrire brief"]  = {"main": [[{"node": "Notion — fin brief (etat)","type": "main", "index": 0}]]}
    for dead in ("Extraire le plan de recherche", "Fixer les variables", "Nettoyer le texte"):
        conns.pop(dead, None)

    for node in nodes:
        name = node.get("name")
        if name == "set_build_prompts_request":
            assigns = node.get("parameters", {}).get("assignments", {}).get("assignments", [])
            for a in assigns:
                if isinstance(a.get("value"), str):
                    a["value"] = (a["value"]
                        .replace("$node[\"Telegram Trigger\"]", "$node[\"Contexte Notion (sujet)\"]")
                        .replace("$('Telegram Trigger')", "$('Contexte Notion (sujet)')"))

    clean_orphans(slim)

    time.sleep(1)
    status, body_resp = n8n_put(base, key, WF_ID, slim)
    if status not in (200, 201):
        raise SystemExit(f"PUT {status}: {body_resp[:2000]}")

    print("OK - workflow Brief_EDI mis a jour.")
    print("> Ouvrir n8n et lier le credential Notion API sur les 3 noeuds marques.")
    print("> Plus besoin des checkboxes Lancer brief / Brief genere dans Notion.")


if __name__ == "__main__":
    main()
