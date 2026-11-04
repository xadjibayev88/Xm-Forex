#!/usr/bin/env python3
"""Tayyor Reels videosini Telegram kanalga va (sozlangan bo'lsa) Instagram'ga joylaydi.

Ishlatish: post_reel.py <video_url> <caption.txt>
video_url ommaviy (https) bo'lishi kerak: Telegram va Instagram videoni shu manzildan oladi.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GRAPH = "https://graph.facebook.com/v21.0"


def http(url, data=None, method=None, timeout=60):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode() if data else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def wait_for_url(url, tries=40):
    for _ in range(tries):
        try:
            status, _ = http(url, method="HEAD", timeout=20)
            if status == 200:
                return True
        except Exception:
            pass
        time.sleep(10)
    return False


def post_telegram(video_url, caption, link, token, chat_id, button):
    markup = json.dumps({"inline_keyboard": [[{"text": button, "url": link}]]})
    status, body = http(f"https://api.telegram.org/bot{token}/sendVideo", {
        "chat_id": chat_id, "video": video_url, "caption": caption[:1024],
        "reply_markup": markup, "supports_streaming": "true"})
    ok = status == 200 and json.loads(body).get("ok")
    print("Telegram:", "yuborildi" if ok else f"XATO {status}: {json.loads(body).get('description', '') if body else ''}")
    return bool(ok)


def post_instagram(video_url, caption, user_id, token):
    status, body = http(f"{GRAPH}/{user_id}/media", {
        "media_type": "REELS", "video_url": video_url, "caption": caption[:2200],
        "share_to_feed": "true", "access_token": token})
    data = json.loads(body or b"{}")
    if status != 200 or "id" not in data:
        print("Instagram: konteyner yaratilmadi:", data.get("error", {}).get("message", status))
        return False
    cid = data["id"]
    for _ in range(40):
        time.sleep(10)
        status, body = http(f"{GRAPH}/{cid}?fields=status_code&access_token={urllib.parse.quote(token)}")
        code = json.loads(body or b"{}").get("status_code")
        if code == "FINISHED":
            break
        if code in ("ERROR", "EXPIRED"):
            print("Instagram: video qayta ishlanmadi:", code)
            return False
    else:
        print("Instagram: kutish vaqti tugadi")
        return False
    status, body = http(f"{GRAPH}/{user_id}/media_publish", {"creation_id": cid, "access_token": token})
    data = json.loads(body or b"{}")
    ok = status == 200 and "id" in data
    print("Instagram:", "joylandi" if ok else data.get("error", {}).get("message", status))
    return ok


def main():
    if len(sys.argv) != 3:
        sys.exit("Ishlatish: post_reel.py <video_url> <caption.txt>")
    video_url = sys.argv[1]
    caption = Path(sys.argv[2]).read_text(encoding="utf-8")
    cfg = json.loads(Path("config.json").read_text(encoding="utf-8")) if Path("config.json").exists() else {}
    link = os.environ.get("AFFILIATE_LINK", "").strip() or str(cfg.get("affiliate_link", ""))
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip() or str(cfg.get("telegram_chat_id", ""))
    button = str(cfg.get("button_text", "")).strip() or "Hisob ochish"
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    ig_user = os.environ.get("IG_USER_ID", "").strip()
    ig_token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    dry = os.environ.get("DRY_RUN", "").strip().lower() == "true"

    print("Video:", video_url)
    print("--- caption ---\n" + caption + "\n---")
    if dry:
        print("DRY RUN: hech narsa yuborilmadi.")
        return 0
    if not wait_for_url(video_url):
        print("XATO: video manzili ochilmadi:", video_url)
        return 1

    results = []
    if token and chat_id and link.startswith("https://"):
        results.append(post_telegram(video_url, caption, link, token, chat_id, button))
    else:
        print("Telegram: o'tkazib yuborildi (TELEGRAM_BOT_TOKEN yoki sozlamalar yo'q)")
    if ig_user and ig_token:
        results.append(post_instagram(video_url, caption, ig_user, ig_token))
    else:
        print("Instagram: o'tkazib yuborildi (IG_USER_ID va IG_ACCESS_TOKEN secrets sozlanmagan)")
    return 0 if all(results) and results else (1 if results else 0)


if __name__ == "__main__":
    sys.exit(main())
