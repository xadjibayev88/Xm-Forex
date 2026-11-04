#!/usr/bin/env python3
"""content/reels.json dan navbatdagi Reels videosini yaratadi (9:16, 1080x1920).

Ishlatish: make_reel.py <video.mp4> <caption.txt>
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
PALETTES = [
    ("#0f2a24", "#1d6b4f"),
    ("#14213d", "#274c8f"),
    ("#2b1d3a", "#6a3d9a"),
    ("#3a1f14", "#b5532a"),
    ("#102a3a", "#1f7a8c"),
    ("#1f2a14", "#5a8a2a"),
]
RISK = "Forex/CFD savdosi yuqori xavfli, mijozlarning ko'pchiligi pul yo'qotadi. Foyda kafolatlanmaydi. Moliyaviy maslahat emas."
DISCLOSURE = "Men XM hamkorman: havolalarimda komissiya olishim mumkin."
HASHTAGS = "#forex #forexuz #trading #treyding #toshkent #uzbekistan #moliya"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    lines = []
    for para in text.split("\n"):
        cur = ""
        for word in para.split():
            test = (cur + " " + word).strip()
            if draw.textlength(test, font=fnt) <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def background(pal):
    mask = Image.linear_gradient("L").resize((W, H))
    top = Image.new("RGB", (W, H), pal[0])
    bottom = Image.new("RGB", (W, H), pal[1])
    return Image.composite(bottom, top, mask).convert("RGBA")


def draw_slide(path, pal, big, small=None, num=None, footer=None, brand="Apex Trader UZ", big_size=96):
    img = background(pal)
    if num is not None:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((80, 150), str(num), font=font(FONT_B, 340), fill=(255, 255, 255, 56))
        img = Image.alpha_composite(img, layer)
    d = ImageDraw.Draw(img)
    fb, fs = font(FONT_B, big_size), font(FONT_R, 52)
    max_w = W - 180
    big_lines = wrap(d, big, fb, max_w)
    small_lines = wrap(d, small, fs, max_w) if small else []
    big_lh, small_lh = int(big_size * 1.2), 74
    total = len(big_lines) * big_lh + (60 + len(small_lines) * small_lh if small_lines else 0)
    y = (H - total) // 2 + (100 if num is not None else 0)
    for line in big_lines:
        d.text((90, y), line, font=fb, fill="white")
        y += big_lh
    y += 60
    for line in small_lines:
        d.text((90, y), line, font=fs, fill=(255, 255, 255, 235))
        y += small_lh
    if footer:
        ff = font(FONT_R, 34)
        fl = wrap(d, footer, ff, max_w)
        fy = H - 360 - len(fl) * 50
        for line in fl:
            d.text((90, fy), line, font=ff, fill=(255, 255, 255, 205))
            fy += 50
    d.text((90, 130), brand, font=font(FONT_R, 38), fill=(255, 255, 255, 180))
    img.convert("RGB").save(path)


def encode_still(png, out, dur):
    tmp = out + ".part.mp4"
    fade_out = max(dur - 0.3, 0)
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", "30", "-i", png,
         "-vf", f"format=yuv420p,loop=-1:1,trim=duration={dur},fade=t=in:st=0:d=0.3,fade=t=out:st={fade_out}:d=0.3",
         "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", tmp],
        check=True)
    os.replace(tmp, out)


def pick_reel(reels):
    manual = os.environ.get("REEL_INDEX", "").strip()
    if manual:
        return int(manual) % len(reels)
    cfg = json.loads(Path("config.json").read_text(encoding="utf-8")) if Path("config.json").exists() else {}
    start = datetime.strptime(str(cfg.get("start_date", "2026-11-04")), "%Y-%m-%d").date()
    today = datetime.now(timezone(timedelta(hours=5))).date()
    return max((today - start).days, 0) % len(reels)


def main():
    if len(sys.argv) != 3:
        sys.exit("Ishlatish: make_reel.py <video.mp4> <caption.txt>")
    out_video, out_caption = Path(sys.argv[1]), Path(sys.argv[2])
    reels = json.loads(Path("content/reels.json").read_text(encoding="utf-8"))
    idx = pick_reel(reels)
    reel = reels[idx]
    pal = PALETTES[idx % len(PALETTES)]
    work = out_video.parent / f"_work_{reel['id']}"
    work.mkdir(parents=True, exist_ok=True)
    out_video.parent.mkdir(parents=True, exist_ok=True)

    scenes = []  # (png, duration)
    p = work / "hook.png"
    draw_slide(str(p), pal, reel["hook"], "Oxirigacha ko'ring", big_size=92)
    scenes.append((str(p), 3.5))
    for i, (title, detail) in enumerate(reel["points"], 1):
        p = work / f"p{i}.png"
        draw_slide(str(p), pal, title, detail, num=i)
        scenes.append((str(p), 4.0))
    p = work / "cta.png"
    draw_slide(str(p), PALETTES[0], "Har kuni bitta foydali dars",
               "Telegram: @Apex_Trader_Uz\nHavola bio'da",
               footer=f"{RISK} {DISCLOSURE}")
    scenes.append((str(p), 5.5))

    parts = []
    for n, (png, dur) in enumerate(scenes):
        part = str(work / f"s{n}.mp4")
        encode_still(png, part, dur)
        parts.append(part)
    lst = work / "list.txt"
    lst.write_text("".join(f"file '{Path(x).resolve()}'\n" for x in parts), encoding="utf-8")
    joined = str(work / "joined.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", joined], check=True)
    tmp = str(out_video) + ".part.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined, "-f", "lavfi",
                    "-i", "anullsrc=r=44100:cl=stereo", "-shortest", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "96k", tmp], check=True)
    os.replace(tmp, out_video)

    points = "\n".join(f"{i}. {t}" for i, (t, _) in enumerate(reel["points"], 1))
    caption = (f"{reel['hook']}\n\n{points}\n\n"
               f"Har kuni bitta dars: Telegram @Apex_Trader_Uz (havola bio'da).\n\n"
               f"{RISK} {DISCLOSURE}\n\n{HASHTAGS}")
    out_caption.write_text(caption, encoding="utf-8")
    print(f"Reel #{idx} ({reel['id']}): {out_video} ({out_video.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
