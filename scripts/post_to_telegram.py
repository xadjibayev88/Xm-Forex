#!/usr/bin/env python3
"""Kunlik postni Telegram kanalga yuboradi (content/posts.json dan navbat bilan)."""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RISK_FOOTER = (
    "\n\n⚠️ Forex va CFD savdosi yuqori xavf bilan bog'liq, "
    "mijozlarning katta qismi pul yo'qotadi. Bu moliyaviy maslahat emas."
)


def load_config() -> dict:
    path = Path("config.json")
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    cfg = load_config()
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = (os.environ.get("TELEGRAM_CHAT_ID", "").strip()
               or str(cfg.get("telegram_chat_id", "")).strip())
    link = (os.environ.get("AFFILIATE_LINK", "").strip()
            or str(cfg.get("affiliate_link", "")).strip())
    dry_run = os.environ.get("DRY_RUN", "").strip().lower() == "true"

    posts = json.loads(Path("content/posts.json").read_text(encoding="utf-8"))
    if not posts:
        print("XATO: content/posts.json bo'sh.")
        return 1

    manual = os.environ.get("POST_INDEX", "").strip()
    if manual:
        idx = int(manual) % len(posts)
    else:
        start = datetime.strptime(
            os.environ.get("START_DATE", "").strip()
            or str(cfg.get("start_date", "")).strip()
            or "2026-11-05",
            "%Y-%m-%d",
        ).date()
        today = datetime.now(timezone(timedelta(hours=5))).date()  # Toshkent vaqti
        days = (today - start).days
        if days < 0:
            print(f"Hali boshlanmagan: START_DATE = {start}")
            return 0
        idx = days % len(posts)

    text = posts[idx]["text"]
    if "{LINK}" in text:
        if not link.startswith("https://"):
            print("XATO: AFFILIATE_LINK repo variable belgilanmagan (https:// bilan boshlanishi kerak).")
            return 1
        text = text.replace("{LINK}", link)
    text += RISK_FOOTER

    if len(text) > 4096:
        print("XATO: post 4096 belgidan uzun.")
        return 1

    print(f"Post #{idx} ({len(text)} belgi)")
    if dry_run:
        print("--- DRY RUN: yuborilmadi ---")
        print(text)
        return 0

    if not token or not chat_id:
        print("XATO: TELEGRAM_BOT_TOKEN va TELEGRAM_CHAT_ID secrets belgilanmagan.")
        return 1

    data = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            desc = json.loads(e.read().decode()).get("description", "")
        except Exception:
            desc = ""
        print(f"XATO: Telegram {e.code}: {desc}")
        return 1
    except Exception as e:  # tarmoq xatosi
        print(f"XATO: {type(e).__name__}")
        return 1

    if not body.get("ok"):
        print(f"XATO: {body.get('description', 'noma`lum')}")
        return 1
    print("Yuborildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
