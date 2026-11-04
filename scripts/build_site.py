#!/usr/bin/env python3
"""site/ papkasini dist/ ga nusxalaydi va havolalarni joyiga qo'yadi."""
import html
import json
import os
import shutil
import sys
from pathlib import Path

cfg_path = Path("config.json")
cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
link = os.environ.get("AFFILIATE_LINK", "").strip() or str(cfg.get("affiliate_link", "")).strip()
tg = os.environ.get("TELEGRAM_URL", "").strip() or str(cfg.get("telegram_url", "")).strip()

if not link.startswith("https://"):
    sys.exit("XATO: affiliate_link (config.json) yoki AFFILIATE_LINK variable belgilanmagan (https:// bilan boshlanishi kerak).")
if tg and not tg.startswith("https://"):
    sys.exit("XATO: TELEGRAM_URL https:// bilan boshlanishi kerak (masalan, https://t.me/kanal_nomi).")
tg = tg or "#"

src, dst = Path("site"), Path("dist")
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

for page in dst.rglob("*.html"):
    t = page.read_text(encoding="utf-8")
    t = t.replace("{{AFFILIATE_LINK}}", html.escape(link, quote=True))
    t = t.replace("{{TELEGRAM_URL}}", html.escape(tg, quote=True))
    page.write_text(t, encoding="utf-8")

print("Sayt tayyor: dist/")
