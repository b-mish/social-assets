# -*- coding: utf-8 -*-
import json
from datetime import datetime, timezone

import publish

NOW = datetime(2026, 7, 12, 16, 0, tzinfo=timezone.utc)  # 19:00 Israel


def make_post(**over):
    p = {"id": "2026-07-12-georgia-x", "site": "georgia", "post_type": "attraction-of-week",
         "publish_at": "2026-07-12T18:00:00+03:00", "status": "pending", "attempts": 0,
         "facebook": {"page_id": "947115751809312", "image_url": "https://x/1.jpg",
                      "message": "m", "link_comment": "c"},
         "instagram": None}
    p.update(over)
    return p


def write_post(qdir, post):
    f = qdir / f"{post['id']}.json"
    f.write_text(json.dumps(post), encoding="utf-8")
    return f


def test_is_due_pending_past():
    assert publish.is_due(make_post(), NOW) is True


def test_is_due_future():
    assert publish.is_due(make_post(publish_at="2026-07-12T23:30:00+03:00"), NOW) is False


def test_is_due_not_pending():
    assert publish.is_due(make_post(status="published"), NOW) is False


def test_scrub_removes_tokens():
    s = '{"access_token": "EAAG123abc", "id": "1_2"}'
    out = publish.scrub(s)
    assert "EAAG123abc" not in out and "1_2" in out


def test_process_success_moves_to_published(tmp_path):
    q, pub = tmp_path / "q", tmp_path / "p"
    q.mkdir(); pub.mkdir()
    write_post(q, make_post())
    res = publish.process_queue(q, pub, NOW, publish_fn=lambda p: {"fb_post_id": "1_2"}, dry_run=False)
    assert res["published"] == ["2026-07-12-georgia-x"]
    assert not list(q.glob("*.json"))
    archived = json.loads((pub / "2026-07-12-georgia-x.json").read_text(encoding="utf-8"))
    assert archived["status"] == "published" and archived["result"]["fb_post_id"] == "1_2"


def test_process_failure_increments_attempts(tmp_path):
    q, pub = tmp_path / "q", tmp_path / "p"
    q.mkdir(); pub.mkdir()
    f = write_post(q, make_post())
    def boom(p): raise RuntimeError("api down")
    res = publish.process_queue(q, pub, NOW, publish_fn=boom, dry_run=False)
    assert res["failed"] == ["2026-07-12-georgia-x"]
    updated = json.loads(f.read_text(encoding="utf-8"))
    assert updated["attempts"] == 1 and updated["status"] == "pending"


def test_process_failure_third_attempt_marks_failed(tmp_path):
    q, pub = tmp_path / "q", tmp_path / "p"
    q.mkdir(); pub.mkdir()
    f = write_post(q, make_post(attempts=2))
    def boom(p): raise RuntimeError("api down")
    publish.process_queue(q, pub, NOW, publish_fn=boom, dry_run=False)
    assert json.loads(f.read_text(encoding="utf-8"))["status"] == "failed"


def test_dry_run_touches_nothing(tmp_path):
    q, pub = tmp_path / "q", tmp_path / "p"
    q.mkdir(); pub.mkdir()
    f = write_post(q, make_post())
    called = []
    res = publish.process_queue(q, pub, NOW, publish_fn=lambda p: called.append(p), dry_run=True)
    assert res["published"] == ["2026-07-12-georgia-x"] and not called
    assert json.loads(f.read_text(encoding="utf-8"))["status"] == "pending"
