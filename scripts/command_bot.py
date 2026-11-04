#!/usr/bin/env python3
"""Telegram bot buyruqlari: GitHub Actions har soatda yangi xabarlarni o'qib, javob beradi.

Faqat config.json dagi admin_ids (yoki ADMIN_IDS) ro'yxatidagi foydalanuvchilar buyruq bera oladi.
Buyruqlar: /id, /help, /status, /stats, /post [n], /reel [n]
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def api(method, token=None, **params):
    token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    data = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/{method}", data=data)
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode())
        except Exception:
            return {"ok": False, "error_code": e.code, "description": "HTTP xato"}


def load_cfg():
    p = Path("config.json")
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def admin_ids(cfg):
    ids = set()
    for x in list(cfg.get("admin_ids", [])) + os.environ.get("ADMIN_IDS", "").replace(" ", "").split(","):
        if str(x).strip().lstrip("-").isdigit():
            ids.add(int(x))
    return ids


def reply(chat_id, text):
    api("sendMessage", chat_id=chat_id, text=text[:4000])


def run_script(script, **env):
    full = {**os.environ, **{k: str(v) for k, v in env.items()}}
    r = subprocess.run([sys.executable, script], env=full, capture_output=True, text=True, timeout=120)
    last = (r.stdout.strip().splitlines() or [""])[-1]
    return r.returncode == 0, last


def dispatch_reel(index):
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    gh_token = os.environ.get("GITHUB_TOKEN", "")
    if not repo or not gh_token:
        return False, "GITHUB_TOKEN yo'q"
    body = {"ref": "main", "inputs": {"reel_index": index, "dry_run": "false"}}
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/workflows/daily-reel.yml/dispatches",
        data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 204, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}"


def handle(msg, cfg, admins):
    chat = msg.get("chat", {})
    user = msg.get("from", {})
    text = (msg.get("text") or "").strip()
    if chat.get("type") != "private" or not text.startswith("/"):
        return
    parts = text.split()
    cmd = parts[0].split("@")[0].lower()
    arg = parts[1] if len(parts) > 1 else ""
    uid, cid = user.get("id"), chat["id"]

    if cmd == "/id":
        reply(cid, f"Sizning Telegram ID: {uid}")
        return
    if not admins:
        reply(cid, f"Bot hali sozlanmagan. Sizning ID: {uid}. Uni repo'dagi config.json ning admin_ids ro'yxatiga qo'shing.")
        return
    if uid not in admins:
        reply(cid, "Ruxsat yo'q.")
        return

    if cmd in ("/start", "/help"):
        reply(cid, "Buyruqlar:\n/status - bot holati\n/stats - kanal a'zolari soni\n"
                   "/post [n] - kanalga post yuborish (n bo'sh bo'lsa, bugungi)\n"
                   "/reel [n] - video yaratib joylash\n/id - sizning ID\n\n"
                   "Eslatma: bot buyruqlarni soatiga bir marta o'qiydi, javob kechikishi mumkin.")
    elif cmd == "/status":
        reply(cid, "Bot ishlayapti (GitHub Actions, har soatda tekshiradi).")
    elif cmd == "/stats":
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip() or str(cfg.get("telegram_chat_id", ""))
        r = api("getChatMemberCount", chat_id=chat_id)
        reply(cid, f"Kanal a'zolari: {r['result']}" if r.get("ok") else f"Xato: {r.get('description')}")
    elif cmd == "/post":
        if arg and not arg.isdigit():
            reply(cid, "Ishlatish: /post yoki /post 3")
            return
        ok, last = run_script("scripts/post_to_telegram.py", POST_INDEX=arg, DRY_RUN="")
        reply(cid, "Post yuborildi." if ok else f"Xato: {last}")
    elif cmd == "/reel":
        if arg and not arg.isdigit():
            reply(cid, "Ishlatish: /reel yoki /reel 3")
            return
        ok, info = dispatch_reel(arg)
        reply(cid, "Video yaratish boshlandi, bir necha daqiqada kanalga tushadi." if ok else f"Xato: {info}")
    else:
        reply(cid, "Noma'lum buyruq. /help")


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print("TELEGRAM_BOT_TOKEN yo'q, to'xtadi.")
        return 0
    cfg = load_cfg()
    admins = admin_ids(cfg)
    res = api("getUpdates", timeout=0, limit=100, allowed_updates=json.dumps(["message"]))
    if not res.get("ok"):
        code = res.get("error_code")
        hint = " (boshqa joyda, masalan Termux'da, bot buyruq tinglayapti)" if code == 409 else ""
        print(f"getUpdates xatosi {code}: {res.get('description')}{hint}")
        return 0
    updates = res["result"]
    print(f"Yangi xabarlar: {len(updates)}")
    if not updates:
        return 0
    # Avval tasdiqlaymiz: xato bo'lsa ham buyruq ikki marta bajarilmaydi.
    api("getUpdates", offset=max(u["update_id"] for u in updates) + 1, limit=1, timeout=0)
    for u in updates:
        try:
            if "message" in u:
                handle(u["message"], cfg, admins)
        except Exception as e:  # bitta xato boshqalarni to'xtatmasin
            print("Xato:", type(e).__name__)
    return 0


if __name__ == "__main__":
    sys.exit(main())
