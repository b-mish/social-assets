# -*- coding: utf-8 -*-
"""Publish due social posts from queue/ via Composio (MCP-over-HTTP).

Queue JSON schema (one file per post):
{
  "id": str, "site": str, "post_type": str,
  "publish_at": ISO-8601 with offset ("2026-07-12T18:00:00+03:00"),
  "status": "pending" | "published" | "failed", "attempts": int,
  "facebook": {"page_id", "image_url", "message", "link_comment"} | null,
  "instagram": {"ig_user_id", "connected_account_id", "format": "carousel"|"single",
                "image_urls": [str], "caption"} | null
}
SECURITY: Composio responses contain page access tokens. Never log raw responses.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_ATTEMPTS = 3
ROOT = Path(__file__).resolve().parent.parent


def is_due(post, now):
    return post["status"] == "pending" and datetime.fromisoformat(post["publish_at"]) <= now


def scrub(text):
    text = re.sub(r'("?access_token"?\s*[:=]\s*"?)[A-Za-z0-9._-]+', r"\1***", str(text))
    return re.sub(r"[A-Za-z0-9._-]{35,}", "***", text)


def process_queue(queue_dir, published_dir, now, publish_fn, dry_run):
    result = {"published": [], "failed": [], "skipped": 0}
    for f in sorted(queue_dir.glob("*.json")):
        post = json.loads(f.read_text(encoding="utf-8"))
        if not is_due(post, now):
            result["skipped"] += 1
            continue
        if dry_run:
            print(f"[dry-run] would publish {post['id']} (due {post['publish_at']})")
            result["published"].append(post["id"])
            continue
        try:
            ids = publish_fn(post)
        except Exception as e:
            post["attempts"] += 1
            if post["attempts"] >= MAX_ATTEMPTS:
                post["status"] = "failed"
            post["last_error"] = scrub(e)
            f.write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"FAILED {post['id']} (attempt {post['attempts']}): {scrub(e)}")
            result["failed"].append(post["id"])
            continue
        post["status"] = "published"
        post["published_at_actual"] = now.isoformat()
        post["result"] = ids
        (published_dir / f.name).write_text(
            json.dumps(post, ensure_ascii=False, indent=2), encoding="utf-8")
        f.unlink()
        print(f"published {post['id']}: {ids}")
        result["published"].append(post["id"])
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    from composio_client import publish_post
    res = process_queue(ROOT / "queue", ROOT / "published",
                        datetime.now(timezone.utc), publish_post, args.dry_run)
    print(f"summary: {res}")
    if res["failed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
