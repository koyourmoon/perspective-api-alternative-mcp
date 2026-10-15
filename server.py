"""Stdio MCP server for Perspective API Alternative (toxicity detection).

This is a thin client. It lists the analyze_toxicity tool locally and sends
tool calls to the hosted server on Apify. Set APIFY_TOKEN to call the tool.
No third-party packages are necessary (Python 3.9+).
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

REMOTE_URL = os.environ.get(
    "PERSPECTIVE_ALT_URL",
    "https://koyourmoon--perspective-api-alternative.apify.actor/mcp",
)
SERVER_INFO = {"name": "perspective-api-alternative", "version": "1.0.9"}
PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]
ATTRIBUTES = ["TOXICITY", "SEVERE_TOXICITY", "INSULT", "PROFANITY", "THREAT", "IDENTITY_ATTACK"]
TIMEOUT_SECONDS = 120

TOOLS = [
    {
        "name": "analyze_toxicity",
        "title": "Analyze toxicity",
        "description": (
            "Score English text for toxicity, severe toxicity, insults, profanity, threats and identity "
            "attacks (0-1 probabilities, same attributes as Google Perspective API). Use it to moderate "
            "user-generated content, filter LLM output, or triage comments before an agent posts them. "
            "Pass up to 100 texts at once. Read-only: it does not store or publish text. Each call is "
            "billed to your Apify account ($0.50 for 1,000 text units). The first call after an idle "
            "period can take 10 to 30 seconds. Non-English text returns an error."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "texts": {
                    "type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 100,
                    "description": "Texts to score (English). One item per comment or message.",
                },
                "attributes": {
                    "type": "array", "items": {"type": "string", "enum": ATTRIBUTES},
                    "description": "Attributes to return. Defaults to all six.",
                },
                "threshold": {
                    "type": "number", "minimum": 0, "maximum": 1, "default": 0.5,
                    "description": "TOXICITY score at or above which a text is marked flagged.",
                },
            },
            "required": ["texts"],
        },
        "annotations": {"readOnlyHint": True, "openWorldHint": False},
    }
]


def result(msg_id, payload):
    return {"jsonrpc": "2.0", "id": msg_id, "result": payload}


def error(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def tool_error(msg_id, message):
    return result(msg_id, {"content": [{"type": "text", "text": message}], "isError": True})


def call_remote(msg_id, params):
    token = os.environ.get("APIFY_TOKEN", "").strip()
    if not token:
        return tool_error(msg_id, "APIFY_TOKEN is not set. Get a token in Apify Console > Settings > API & Integrations.")
    body = json.dumps({"jsonrpc": "2.0", "id": msg_id, "method": "tools/call", "params": params}).encode()
    req = urllib.request.Request(
        REMOTE_URL,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            text = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return tool_error(msg_id, f"Remote server returned HTTP {e.code}.")
    except (urllib.error.URLError, TimeoutError) as e:
        return tool_error(msg_id, f"Cannot reach the remote server: {e}")
    if text.lstrip().startswith("event:") or text.lstrip().startswith("data:"):
        text = "".join(line[5:] for line in text.splitlines() if line.startswith("data:"))
    try:
        reply = json.loads(text)
    except json.JSONDecodeError:
        return tool_error(msg_id, "The remote server returned an incorrect response.")
    reply["id"] = msg_id
    return reply


def handle(msg):
    if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
        return error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
    if "id" not in msg:
        return None
    method, msg_id, params = msg["method"], msg["id"], msg.get("params") or {}
    if method == "initialize":
        requested = params.get("protocolVersion")
        return result(msg_id, {
            "protocolVersion": requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": SERVER_INFO,
            "instructions": "Use analyze_toxicity to score English text for toxicity before publishing or replying.",
        })
    if method == "ping":
        return result(msg_id, {})
    if method == "tools/list":
        return result(msg_id, {"tools": TOOLS})
    if method == "tools/call":
        if params.get("name") != "analyze_toxicity":
            return error(msg_id, -32602, f"Unknown tool: {params.get('name')}")
        return call_remote(msg_id, params)
    return error(msg_id, -32601, f"Method not found: {method}")


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            reply = error(None, -32700, "Parse error")
        else:
            reply = handle(msg)
        if reply is not None:
            sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
