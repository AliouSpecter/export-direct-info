"""
Crée le workflow n8n « Redaction_EDI » :

Déclencheur : cron 3 min → pages Notion dont État = "Rédaction"
1. Lire le brief depuis le corps de la page Notion
2. Sonar Deep Research → recherche approfondie + sources
3. Claude → rédaction HTML avec le prompt EDI
4. Écrire l'article dans la page Notion (sous le brief)
5. Passer la carte en "Article validé"

Usage :
  python ops/n8n_create_redaction.py
"""
from __future__ import annotations
import json, os, time, uuid, urllib.request, urllib.error
from pathlib import Path

SKILL_PATH = Path(r"C:\Users\mamad\.agents\skills\edi-redacteur\SKILL.md")

def load_dotenv(path: Path) -> None:
    if not path.exists(): return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())

def n8n_post(base, key, path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{base}{path}", data=data, method="POST",
        headers={"X-N8N-API-KEY": key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")

def load_skill_prompt():
    """Charge le prompt rédacteur depuis le skill EDI."""
    if SKILL_PATH.exists():
        txt = SKILL_PATH.read_text(encoding="utf-8")
        if txt.startswith("---"):
            parts = txt.split("---", 2)
            return parts[2].strip() if len(parts) >= 3 else txt
    return "Tu es un redacteur expert en agroalimentaire africain. Redige un article HTML complet, optimise SEO, en francais."

def main():
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
    base = os.environ.get("N8N_BASE_URL", "").rstrip("/")
    key  = os.environ.get("N8N_API_KEY", "").strip()
    if not base or not key:
        raise SystemExit("N8N_BASE_URL ou N8N_API_KEY manquant")

    raw_db = "3548e6c9f9d480d8918add48a51f9198"
    db_uuid = f"{raw_db[:8]}-{raw_db[8:12]}-{raw_db[12:16]}-{raw_db[16:20]}-{raw_db[20:]}"

    # Credentials récupérés du workflow Brief_EDI (références d'ID n8n, pas des secrets)
    CRED_PERPLEXITY = {"id": "8y4LAqyV0ca2D8ie", "name": "Perplexity API"}
    CRED_CLAUDE     = {"id": "5JxCEGCMxT6Tcj9a", "name": "Claude Account"}
    CRED_NOTION     = {"id": "tKxKVhbNPuEi00Ii", "name": "Notion API"}

    REDACTEUR_PROMPT = load_skill_prompt()

    def nid(): return str(uuid.uuid4())

    id_poll    = nid()
    id_list    = nid()
    id_ctx     = nid()
    id_getblk  = nid()
    id_extract = nid()
    id_deep    = nid()
    id_build   = nid()
    id_write   = nid()
    id_fin     = nid()

    SCHEDULE = {
        "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 3}]}},
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [-600, 0],
        "id": id_poll,
        "name": "Poll Notion — redaction",
    }

    NOTION_LIST = {
        "parameters": {
            "resource": "databasePage",
            "operation": "getAll",
            "databaseId": {"__rl": True, "value": db_uuid, "mode": "id",
                           "cachedResultName": "Article EDI"},
            "returnAll": False,
            "limit": 3,
            "simple": False,
            "filterType": "manual",
            "matchType": "and",
            "filters": {
                "conditions": [
                    {"key": "État|status", "condition": "equals",
                     "statusValue": "Rédaction"}
                ]
            },
        },
        "type": "n8n-nodes-base.notion",
        "typeVersion": 2.2,
        "position": [-380, 0],
        "id": id_list,
        "name": "Notion — liste Redaction",
        "credentials": {"notionApi": CRED_NOTION},
    }

    CTX_CODE = {
        "parameters": {
            "jsCode": (
                "const p = $json.properties || {};\n"
                "const titleProp = p['Nom de la tâche'] || {};\n"
                "const title = (titleProp.title && titleProp.title[0] "
                    "&& titleProp.title[0].plain_text) || '';\n"
                "return [{ json: { sujet: title.trim(), notion_page_id: $json.id } }];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [-160, 0],
        "id": id_ctx,
        "name": "Contexte Notion (sujet)",
    }

    GET_BLOCKS = {
        "parameters": {
            "method": "GET",
            "url": "={{ 'https://api.notion.com/v1/blocks/' + $json.notion_page_id + '/children?page_size=100' }}",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "notionApi",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "Notion-Version", "value": "2022-06-28"},
            ]},
            "options": {},
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [60, 0],
        "id": id_getblk,
        "name": "Lire brief (blocks Notion)",
        "credentials": {"notionApi": CRED_NOTION},
    }

    EXTRACT_BRIEF = {
        "parameters": {
            "jsCode": (
                "// Reconstitue le texte du brief depuis les blocs Notion\n"
                "const results = $json.results || [];\n"
                "const sujet = $('Contexte Notion (sujet)').first().json.sujet;\n"
                "const pageId = $('Contexte Notion (sujet)').first().json.notion_page_id;\n"
                "const lines = [];\n"
                "for (const block of results) {\n"
                "  const type = block.type;\n"
                "  const richText = block[type] && block[type].rich_text;\n"
                "  if (!richText) continue;\n"
                "  const text = richText.map(t => t.plain_text || '').join('');\n"
                "  if (text.trim()) lines.push(text.trim());\n"
                "}\n"
                "return [{ json: { sujet, notion_page_id: pageId, brief: lines.join('\\n\\n') } }];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [280, 0],
        "id": id_extract,
        "name": "Extraire brief",
    }

    DEEP_RESEARCH = {
        "parameters": {
            "method": "POST",
            "url": "https://api.perplexity.ai/chat/completions",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "perplexityApi",
            "sendBody": True,
            "contentType": "json",
            "specifyBody": "json",
            "jsonBody": (
                "={\n"
                '  "model": "sonar-deep-research",\n'
                '  "messages": [\n'
                '    { "role": "system", "content": "Tu es un chercheur expert en agroalimentaire africain. Effectue une recherche approfondie sur le sujet donne. Fournis des faits precis, des statistiques datees (2022-2025), des sources credibles (Banque mondiale, FAO, BAD, BCEAO). Reponds en francais. Structure ta reponse avec des sections claires." },\n'
                '    { "role": "user", "content": "Sujet : " + $json.sujet + "\\n\\nPlan de recherche :\\n" + $json.brief }\n'
                '  ],\n'
                '  "max_tokens": 4000\n'
                "}"
            ),
            "options": {"timeout": 360000},
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [500, 0],
        "id": id_deep,
        "name": "Sonar Deep Research",
        "credentials": {"perplexityApi": CRED_PERPLEXITY},
    }

    BUILD_CLAUDE_INPUT = {
        "parameters": {
            "jsCode": (
                "const research = $json.choices && $json.choices[0]\n"
                "  ? $json.choices[0].message.content : '';\n"
                "const citations = ($json.citations || []).map((c, i) => `[${i+1}] ${c}`).join('\\n');\n"
                "const sujet = $('Extraire brief').first().json.sujet;\n"
                "const brief = $('Extraire brief').first().json.brief;\n"
                "const pageId = $('Extraire brief').first().json.notion_page_id;\n"
                "const userPrompt = [\n"
                "  'Sujet : ' + sujet,\n"
                "  '',\n"
                "  'Plan de recherche :',\n"
                "  brief,\n"
                "  '',\n"
                "  'Recherche approfondie et sources :',\n"
                "  research,\n"
                "  '',\n"
                "  'Sources :',\n"
                "  citations\n"
                "].join('\\n');\n"
                "return [{ json: { notion_page_id: pageId, sujet, user_prompt: userPrompt } }];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [720, 0],
        "id": id_build,
        "name": "Preparer input Claude",
    }

    CLAUDE_REDACTEUR = {
        "parameters": {
            "method": "POST",
            "url": "https://api.anthropic.com/v1/messages",
            "sendHeaders": True,
            "headerParameters": {"parameters": [
                {"name": "x-api-key",         "value": "={{ $credentials.anthropicApi.apiKey }}"},
                {"name": "anthropic-version",  "value": "2023-06-01"},
                {"name": "Content-Type",       "value": "application/json"},
            ]},
            "sendBody": True,
            "contentType": "json",
            "specifyBody": "json",
            "jsonBody": (
                "={\n"
                '  "model": "claude-opus-4-5",\n'
                '  "max_tokens": 8000,\n'
                '  "system": ' + json.dumps(REDACTEUR_PROMPT) + ',\n'
                '  "messages": [\n'
                '    { "role": "user", "content": {{ JSON.stringify($json.user_prompt) }} }\n'
                '  ]\n'
                "}"
            ),
            "options": {"timeout": 120000},
        },
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.3,
        "position": [940, 0],
        "id": nid(),
        "name": "Claude Redacteur",
    }

    id_claude_out = nid()
    BUILD_ARTICLE_BODY = {
        "parameters": {
            "jsCode": (
                "const content = $json.content && $json.content[0]\n"
                "  ? $json.content[0].text : '';\n"
                "const pageId = $('Preparer input Claude').first().json.notion_page_id;\n"
                "const notion_blocks = {\n"
                "  children: [\n"
                "    { type: 'heading_2', heading_2: { rich_text: [{ type: 'text', text: { content: 'Article' } }] } },\n"
                "    { type: 'code', code: {\n"
                "        language: 'html',\n"
                "        rich_text: [{ type: 'text', text: { content: content.substring(0, 2000) } }]\n"
                "    }},\n"
                "  ]\n"
                "};\n"
                "return [{ json: { notion_page_id: pageId, notion_blocks } }];"
            )
        },
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1160, 0],
        "id": id_claude_out,
        "name": "Build article body",
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
        "position": [1380, 0],
        "id": id_write,
        "name": "Notion — Ecrire article",
        "credentials": {"notionApi": CRED_NOTION},
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
                    {"key": "État|status", "statusValue": "Article validé"},
                ]
            },
            "options": {},
        },
        "type": "n8n-nodes-base.notion",
        "typeVersion": 2.2,
        "position": [1600, 0],
        "id": id_fin,
        "name": "Notion — fin redaction (etat)",
        "credentials": {"notionApi": CRED_NOTION},
    }

    nodes = [
        SCHEDULE, NOTION_LIST, CTX_CODE, GET_BLOCKS, EXTRACT_BRIEF,
        DEEP_RESEARCH, BUILD_CLAUDE_INPUT, CLAUDE_REDACTEUR,
        BUILD_ARTICLE_BODY, NOTION_WRITE, NOTION_FIN,
    ]

    connections = {
        "Poll Notion — redaction":     {"main": [[{"node": "Notion — liste Redaction",    "type": "main", "index": 0}]]},
        "Notion — liste Redaction":    {"main": [[{"node": "Contexte Notion (sujet)",      "type": "main", "index": 0}]]},
        "Contexte Notion (sujet)":     {"main": [[{"node": "Lire brief (blocks Notion)",   "type": "main", "index": 0}]]},
        "Lire brief (blocks Notion)":  {"main": [[{"node": "Extraire brief",               "type": "main", "index": 0}]]},
        "Extraire brief":              {"main": [[{"node": "Sonar Deep Research",           "type": "main", "index": 0}]]},
        "Sonar Deep Research":         {"main": [[{"node": "Preparer input Claude",         "type": "main", "index": 0}]]},
        "Preparer input Claude":       {"main": [[{"node": "Claude Redacteur",              "type": "main", "index": 0}]]},
        "Claude Redacteur":            {"main": [[{"node": "Build article body",            "type": "main", "index": 0}]]},
        "Build article body":          {"main": [[{"node": "Notion — Ecrire article",       "type": "main", "index": 0}]]},
        "Notion — Ecrire article":     {"main": [[{"node": "Notion — fin redaction (etat)", "type": "main", "index": 0}]]},
    }

    wf_body = {
        "name": "Redaction_EDI",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"},
    }

    status, resp = n8n_post(base, key, "/api/v1/workflows", wf_body)
    if status not in (200, 201):
        raise SystemExit(f"POST {status}: {str(resp)[:2000]}")

    wf_id = resp.get("id", "?")
    print(f"OK - Workflow Redaction_EDI cree. id={wf_id}")
    print("> Activer le workflow dans n8n (toggle Active).")
    print("> Verifier le noeud Claude Redacteur : l'API key Anthropic est injectee via credentials.")
    print(f"> Pour tester : une carte en colonne 'Redaction' dans Notion.")


if __name__ == "__main__":
    main()
