# -*- coding: utf-8 -*-
import composio_client as cc


def test_publish_facebook_posts_then_comments(monkeypatch):
    calls = []
    def fake(slug, arguments, connected_account_id=None):
        calls.append((slug, arguments))
        return {"post_id": "947_111"} if slug == "FACEBOOK_CREATE_PHOTO_POST" else {"id": "c1"}
    monkeypatch.setattr(cc, "execute_tool", fake)
    post = {"facebook": {"page_id": "947", "image_url": "https://x/1.jpg",
                         "message": "m", "link_comment": "לינק 👉 https://georgia-travel.co.il"},
            "instagram": None}
    ids = cc.publish_post(post)
    assert ids["fb_post_id"] == "947_111"
    assert calls[0][0] == "FACEBOOK_CREATE_PHOTO_POST"
    assert calls[1] == ("FACEBOOK_CREATE_COMMENT",
                        {"object_id": "947_111", "message": "לינק 👉 https://georgia-travel.co.il"})


def test_publish_instagram_carousel(monkeypatch):
    calls = []
    def fake(slug, arguments, connected_account_id=None):
        calls.append((slug, arguments, connected_account_id))
        if slug == "INSTAGRAM_CREATE_CAROUSEL_CONTAINER":
            return {"id": "cont9"}
        return {"id": "media7"}
    monkeypatch.setattr(cc, "execute_tool", fake)
    post = {"facebook": None,
            "instagram": {"ig_user_id": "269", "connected_account_id": "ca_1",
                          "format": "carousel", "image_urls": ["u1", "u2"], "caption": "לינק בביו"}}
    ids = cc.publish_post(post)
    assert ids["ig_media_id"] == "media7"
    assert calls[0][0] == "INSTAGRAM_CREATE_CAROUSEL_CONTAINER" and calls[0][2] == "ca_1"
    assert calls[1][1]["creation_id"] == "cont9"


def test_publish_instagram_single(monkeypatch):
    calls = []
    def fake(slug, arguments, connected_account_id=None):
        calls.append(slug)
        return {"id": "z"}
    monkeypatch.setattr(cc, "execute_tool", fake)
    post = {"facebook": None,
            "instagram": {"ig_user_id": "269", "connected_account_id": "ca_1",
                          "format": "single", "image_urls": ["u1"], "caption": "c"}}
    cc.publish_post(post)
    assert calls[0] == "INSTAGRAM_CREATE_MEDIA_CONTAINER"
