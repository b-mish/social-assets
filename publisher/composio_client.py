# -*- coding: utf-8 -*-
"""Composio calls via MCP JSON-RPC over HTTPS (connect.composio.dev/mcp).

Transport proven in the 2026-07-07 spike: the ck_ key only authenticates the MCP
endpoint, not backend REST. Flow per session: initialize -> notifications/initialized
-> tools/call COMPOSIO_MULTI_EXECUTE_TOOL. Responses are SSE-framed.

SECURITY: responses contain FB page access tokens. NEVER print raw responses.
"""
import json
import os
import urllib.request

from publish import scrub

MCP_URL = "https://connect.composio.dev/mcp"
_session = {"id": None}


def _post(payload, session_id=None):
    headers = {
        "Authorization": f"Bearer {os.environ['COMPOSIO_API_KEY']}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(MCP_URL, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=180) as r:
        sid = r.headers.get("mcp-session-id", session_id)
        body = r.read().decode("utf-8", errors="replace")
    result = None
    for line in body.splitlines():
        if line.startswith("data: "):
            result = json.loads(line[6:])
    return sid, result


def _ensure_session():
    if _session["id"]:
        return _session["id"]
    sid, init = _post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                       "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                                  "clientInfo": {"name": "social-publisher", "version": "1.0"}}})
    if not (init and "result" in init):
        raise RuntimeError(f"MCP initialize failed: {scrub(init)}")
    _post({"jsonrpc": "2.0", "method": "notifications/initialized"}, session_id=sid)
    _session["id"] = sid
    return sid


def execute_tool(slug, arguments, connected_account_id=None):
    sid = _ensure_session()
    entry = {"tool_slug": slug, "arguments": arguments}
    if connected_account_id:
        entry["account"] = connected_account_id
    _, resp = _post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                     "params": {"name": "COMPOSIO_MULTI_EXECUTE_TOOL",
                                "arguments": {"tools": [entry],
                                              "sync_response_to_workbench": False,
                                              "thought": f"scheduled publish: {slug}"}}},
                    session_id=sid)
    if resp is None or "error" in resp:
        raise RuntimeError(f"{slug}: MCP error {scrub((resp or {}).get('error'))}")
    outer = json.loads(resp["result"]["content"][0]["text"])
    results = (outer.get("data") or {}).get("results") or []
    inner = (results[0].get("response") or {}) if results else {}
    if not inner.get("successful", False):
        detail = (inner.get("error") or (results[0].get("error") if results else None)
                  or outer.get("error") or "empty results")
        raise RuntimeError(f"{slug}: {scrub(detail)}")
    return inner.get("data") or {}


def publish_post(post):
    ids = {"fb_post_id": None, "ig_media_id": None}
    fb = post.get("facebook")
    if fb:
        data = execute_tool("FACEBOOK_CREATE_PHOTO_POST",
                            {"page_id": fb["page_id"], "url": fb["image_url"],
                             "message": fb["message"]})
        ids["fb_post_id"] = data.get("post_id") or data.get("id")
        if fb.get("link_comment"):
            execute_tool("FACEBOOK_CREATE_COMMENT",
                         {"object_id": ids["fb_post_id"], "message": fb["link_comment"]})
    ig = post.get("instagram")
    if ig:
        acct = ig.get("connected_account_id")
        if ig["format"] == "carousel":
            cont = execute_tool("INSTAGRAM_CREATE_CAROUSEL_CONTAINER",
                                {"ig_user_id": ig["ig_user_id"],
                                 "child_image_urls": ig["image_urls"],
                                 "caption": ig["caption"]}, acct)
        else:
            cont = execute_tool("INSTAGRAM_CREATE_MEDIA_CONTAINER",
                                {"ig_user_id": ig["ig_user_id"],
                                 "image_url": ig["image_urls"][0],
                                 "caption": ig["caption"]}, acct)
        pub = execute_tool("INSTAGRAM_POST_IG_USER_MEDIA_PUBLISH",
                           {"ig_user_id": ig["ig_user_id"],
                            "creation_id": cont.get("id") or cont.get("creation_id"),
                            "max_wait_seconds": 90}, acct)
        ids["ig_media_id"] = pub.get("id")
    return ids
