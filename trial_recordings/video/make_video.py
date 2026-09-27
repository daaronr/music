"""Build a YouTube video for one trial tune, framed as a game: which AI tune wins?

The recording starts at 0:00 under a title card ("Who wins the AI jazz game?").
Then the score follows the music, zoomed onto the system being played (plus the
next one), with a thin top bar (round, form, vote badge) and a coloured caption
band describing each 8-bar stretch. Ends on a "your move: vote" card.
Also writes a YouTube description with chapters and the prompt.

usage: python3 make_video.py halation|parallax|glass_meridian
(miniforge python: Pillow + numpy; uses ffmpeg and pdftoppm)
"""
from __future__ import annotations

import subprocess
import sys
import textwrap
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from captions import TUNES
from systems import systems as find_systems

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "output"
W, H = 1920, 1080
FFMPEG = "/usr/local/bin/ffmpeg"
PAGE_URL = "ai-jazz-tune-trial.netlify.app"
PLAYLIST = "bit.ly/jazztuba"
PROMPT_DIR = (HERE.parents[1] / "ai_jazz_trial").as_posix()

# Blue Note-ish palette
NAVY, COBALT, ORANGE, MUSTARD = (14, 24, 43), (31, 78, 163), (232, 116, 42), (227, 178, 60)
RED, TEAL, CREAM, INK = (200, 65, 45), (38, 140, 130), (243, 234, 216), (24, 24, 28)
PAPER = (250, 247, 240)
TUNE_COLOR = {"halation": COBALT, "parallax": MUSTARD, "glass_meridian": ORANGE}
BAND_CYCLE = [COBALT, ORANGE, TEAL, RED, MUSTARD, NAVY]
ROUNDS = [(0, 4, "Warm-up", "The band counts it in"), (4, 36, "Round 1", "The head"),
          (36, 68, "Round 2", "Duo chorus 1"), (68, 100, "Round 3", "Duo chorus 2"),
          (100, 999, "Final round", "Head out")]
SERIF_B = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_I = "/System/Library/Fonts/Supplemental/Georgia Bold Italic.ttf"
SANS = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap_draw(d, xy, text, fnt, fill, width_px, line_gap=1.3):
    x, y = xy
    avg = fnt.getlength("abcdefghijklmnopqrstuvwxyz") / 26
    for line in textwrap.wrap(text, max(10, int(width_px / avg))) or [""]:
        d.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * line_gap)
    return y


def pill(d, x, y, text, fnt, bg, fg, pad=(22, 10)):
    w = fnt.getlength(text)
    d.rounded_rectangle([x, y, x + w + 2 * pad[0], y + fnt.size + 2 * pad[1] + 4], radius=(fnt.size + 2 * pad[1]) // 2,
                        fill=bg)
    d.text((x + pad[0], y + pad[1]), text, font=fnt, fill=fg)
    return x + w + 2 * pad[0]


def pdf_pages(pdf, stem, height):
    ASSETS.mkdir(parents=True, exist_ok=True)
    existing = sorted(ASSETS.glob(f"{stem}-*.png"))
    if not existing:
        subprocess.run(["pdftoppm", "-png", "-scale-to-y", str(height), "-scale-to-x", "-1", pdf,
                        str(ASSETS / stem)], check=True)
    return [Image.open(p).convert("RGB") for p in sorted(ASSETS.glob(f"{stem}-*.png"))]


def round_for(b):
    return next(r for r in ROUNDS if r[0] <= b < r[1])


# ------------------------------------------------------------------ frames

def page_backdrop():
    shot = Image.open(ASSETS / "page_full.png").convert("RGB")
    crop = shot.crop((0, 0, shot.width, int(shot.width * 9 / 16))).resize((W, H))
    img = crop.filter(ImageFilter.GaussianBlur(10)).convert("RGBA")
    return Image.alpha_composite(img, Image.new("RGBA", img.size, NAVY + (222,))).convert("RGB")


def frame_opening(t, key):
    img = page_backdrop()
    d = ImageDraw.Draw(img)
    d.text((120, 95), "WHO WINS THE AI JAZZ GAME?", font=font(SERIF_B, 92), fill=MUSTARD)
    d.text((124, 215), "Three AI agents. One prompt. Three tunes. You're the judge.", font=font(SANS, 40),
           fill=CREAM)
    x = 124
    for k, name in [("halation", "Halation"), ("parallax", "Parallax"), ("glass_meridian", "Glass Meridian")]:
        now = k == key
        x = pill(d, x, 305, name, font(SERIF_B, 46 if now else 38), TUNE_COLOR[k] if now else (60, 66, 80),
                 NAVY if (now and k != "halation") else CREAM) + 22
    d.text((124, 420), "NOW PLAYING", font=font(SANS, 30), fill=TUNE_COLOR[key])
    d.text((120, 455), t["name"], font=font(SERIF_B, 150), fill=CREAM)
    wrap_draw(d, (124, 640), f"by {t['agent_short']}  ·  {t['facts']}", font(SANS, 34), (200, 196, 186), W - 260)
    d.text((124, 760), "…or do we all lose?", font=font(SERIF_I, 58), fill=ORANGE)
    x = pill(d, 124, 880, "LISTEN, THEN VOTE", font(SANS, 38), ORANGE, NAVY)
    d.text((x + 30, 892), PAGE_URL, font=font(SANS, 44), fill=CREAM)
    return img


def frame_end(key):
    img = page_backdrop()
    d = ImageDraw.Draw(img)
    d.text((120, 110), "YOUR MOVE.", font=font(SERIF_B, 130), fill=MUSTARD)
    d.text((124, 280), "Which AI tune wins? Or do we all lose?", font=font(SERIF_I, 56), fill=CREAM)
    x = 124
    for k, name in [("halation", "Halation"), ("parallax", "Parallax"), ("glass_meridian", "Glass Meridian")]:
        x = pill(d, x, 395, name, font(SERIF_B, 44), TUNE_COLOR[k], NAVY if k != "halation" else CREAM) + 24
    x = pill(d, 124, 520, "VOTE", font(SANS, 46), ORANGE, NAVY)
    d.text((x + 30, 530), PAGE_URL, font=font(SANS, 54), fill=CREAM)
    d.text((124, 690), "Play one of these live? Send me a link: daaronr@gmail.com", font=font(SANS, 40), fill=CREAM)
    d.text((124, 760), f"My own attempts: {PLAYLIST}", font=font(SANS, 40), fill=(200, 196, 186))
    d.text((124, 940), "An informal trial by David Reinstein", font=font(SANS, 32), fill=(170, 166, 158))
    return img


def zoom_view(page, systems, current, window, accent):
    """Crop the page to the current system and the next (window) systems."""
    chosen = systems[current:current + window]
    top = max(0, int(chosen[0][0] - 0.9 * (chosen[0][1] - chosen[0][0]) - 60))
    bot = min(page.height, int(chosen[-1][1] + 0.35 * (chosen[-1][1] - chosen[-1][0]) + 40))
    crop = page.crop((0, top, page.width, bot)).convert("RGBA")
    # fade systems after the current one
    s0 = systems[current]
    cur_bot = int(s0[1] + 0.35 * (s0[1] - s0[0]) + 25) - top
    over = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    od.rectangle([0, cur_bot, crop.width, crop.height], fill=PAPER + (150,))
    od.rectangle([0, 0, 14, cur_bot], fill=accent + (255,))
    return Image.alpha_composite(crop, over).convert("RGB")


def frame_music(t, key, zoom, b, seg_label, caption, band_color):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # top bar
    d.rectangle([0, 0, W, 96], fill=NAVY)
    rnd = round_for(b)
    x = pill(d, 28, 20, f"{rnd[2].upper()}", font(SANS, 30), TUNE_COLOR[key], NAVY if key != "halation" else CREAM)
    d.text((x + 22, 18), t["name"], font=font(SERIF_B, 48), fill=CREAM)
    d.text((x + 34 + font(SERIF_B, 48).getlength(t["name"]), 34), f"· {rnd[3]}", font=font(SANS, 30),
           fill=(190, 186, 176))
    vx = W - 28 - font(SANS, 28).getlength("VOTE  " + PAGE_URL) - 44
    pill(d, vx, 22, "VOTE  " + PAGE_URL, font(SANS, 28), ORANGE, NAVY)
    # form strip
    parts = [(0, 4), (4, 36), (36, 68), (68, 100), (100, t["end_bar"] + 1)]
    total = t["end_bar"] + 1
    for i, (a, e) in enumerate(parts):
        x0, x1 = a / total * W, e / total * W - 2
        active = a <= b < e
        d.rectangle([x0, 96, x1, 112], fill=band_color if active else (215, 208, 194))
    d.rectangle([b / total * W - 3, 92, b / total * W + 3, 116], fill=INK)
    # score, zoomed
    box_w, box_h = W - 80, 1080 - 112 - 380 - 24
    s = min(box_w / zoom.width, box_h / zoom.height)
    z = zoom.resize((int(zoom.width * s), int(zoom.height * s)), Image.LANCZOS)
    img.paste(z, ((W - z.width) // 2, 112 + 15 + (box_h - z.height) // 2))
    # caption band
    d.rectangle([0, H - 380, W, H], fill=band_color)
    fg = NAVY if band_color in (MUSTARD, ORANGE) else CREAM
    d.text((70, H - 360), seg_label.upper(), font=font(SANS, 36), fill=fg)
    wrap_draw(d, (70, H - 300), caption, font(SERIF_B, 56), fg, W - 140, 1.28)
    d.text((W - 330, H - 36), "sax plays the guitar part", font=font(SANS, 22), fill=fg)
    return img


# ------------------------------------------------------------------ audio / assembly

def to_wav(src, dst):
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", str(src), "-ar", "44100", "-ac", "2",
                    "-sample_fmt", "s16", str(dst)], check=True)


def wav_seconds(p):
    with wave.open(str(p)) as w:
        return w.getnframes() / w.getframerate()


def mmss(s):
    return f"{int(s // 60)}:{int(s % 60):02d}"


def main(key):
    t = TUNES[key]
    work = HERE / "work" / key
    work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("frame_*.png"):
        old.unlink()
    OUT.mkdir(exist_ok=True)
    bar = 4 * 60 / t["tempo"]

    lead = pdf_pages(t["lead"], f"{key}_lead_hi", 3240)[0]
    duo = pdf_pages(t["duo"], f"{key}_duo_hi", 3240)
    lead_sys = find_systems(lead, 1)
    lead_first = {"halation": 0, "parallax": 1, "glass_meridian": 0}[key]   # system holding head bar 1
    duo_layout = []
    for pi, starts in enumerate(t["systems"]):
        found = find_systems(duo[pi], 2)
        assert len(found) == len(starts), (key, pi, len(found), starts)
        duo_layout.append((starts, found))

    to_wav(t["audio"], work / "music.wav")
    music_len = wav_seconds(work / "music.wav")

    # views: one per system played, in recording bars
    views = []                                          # (start_bar, page, systems, index, window)
    for rep_start in (4, 100):                          # head in, head out on the lead sheet
        n_sys = 8 if rep_start == 4 else len(lead_sys) - lead_first
        for k in range(n_sys):
            views.append((rep_start + 4 * k, lead, lead_sys, lead_first + k, 2))
    for (starts, found), page in zip(duo_layout, duo):
        for i, sb in enumerate(starts):
            views.append((35 + sb, page, found, i, 1))
    views.sort(key=lambda v: v[0])

    TITLE_SECS = 7.0
    end_card = t["end_bar"] * bar
    segs = sorted(t["segments"], key=lambda s: s[0])
    clips = [(frame_opening(t, key), TITLE_SECS)]
    cuts = sorted({v[0] for v in views} | {s[0] for s in segs if s[0] >= 4})
    for i, b in enumerate(cuts):
        start_s = max(b * bar, TITLE_SECS)
        end_s = min(cuts[i + 1] * bar if i + 1 < len(cuts) else end_card, end_card)
        if end_s <= start_s:
            continue
        view = max((v for v in views if v[0] <= b), key=lambda v: v[0])
        seg_i = max(i2 for i2, s in enumerate(segs) if s[0] <= b)
        seg = segs[seg_i]
        band = BAND_CYCLE[seg_i % len(BAND_CYCLE)]
        accent = BAND_CYCLE[(seg_i + 1) % len(BAND_CYCLE)]
        zoom = zoom_view(view[1], view[2], view[3], view[4], accent)
        clips.append((frame_music(t, key, zoom, b, seg[1], seg[2], band), end_s - start_s))
    clips.append((frame_end(key), music_len - end_card))

    lines = []
    for n, (img, dur) in enumerate(clips):
        p = work / f"frame_{n:03d}.png"
        img.save(p)
        lines += [f"file '{p}'", f"duration {dur:.3f}"]
    lines.append(f"file '{work / f'frame_{len(clips) - 1:03d}.png'}'")
    (work / "frames.txt").write_text("\n".join(lines) + "\n")
    mp4 = OUT / f"{t['name'].replace(' ', '_')}_AI_jazz_trial.mp4"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i",
                    str(work / "frames.txt"), "-i", str(work / "music.wav"),
                    "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-tune", "stillimage",
                    "-crf", "18", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    str(mp4)], check=True)

    sys.path.insert(0, PROMPT_DIR)
    from trial_data import PROMPT_CLAUDE  # noqa: E402
    chapters = [("0:00", "Warm-up: band intro"), (mmss(4 * bar), "Round 1: the head"),
                (mmss(36 * bar), "Round 2: duo chorus 1 (trumpet and sax)"),
                (mmss(68 * bar), "Round 3: duo chorus 2"), (mmss(100 * bar), "Final round: head out"),
                (mmss(end_card), "Your move: vote")]
    desc = f"""Who wins the AI jazz game? Three AI agents got the same prompt and wrote three tunes: Halation, Parallax and Glass Meridian. This is {t['name']}, by {t['agent_short']}. Listen to all three, then vote: https://{PAGE_URL}
(Or do we all lose?)

The prompt asked for an original straight-ahead post-bop tune with some bright, lydian sounds, plus two written choruses of a trumpet and guitar duo solo with counterpoint and theme development, delivered as sheet music, MuseScore files and an iReal Pro chart. The score follows along in the video, with notes on what's happening.

The recording is programmed, not played: sampled trumpet (University of Iowa samples) and alto sax, piano, bass and drums (Apple GarageBand instruments), with the rhythm section generated from the tune's chord chart. The sax plays the score's guitar line. All three tunes were recorded with the same recipe.

I'd love to hear these played live. Record one and send me a link (daaronr@gmail.com). My own attempts go on this playlist: https://www.youtube.com/playlist?list=PLwCHmz77VrK1TvvBeyKYlk52rQ6PeHJzk

An informal trial by David Reinstein. A personal project, not connected to The Unjournal.

""" + "\n".join(f"{a} {b}" for a, b in chapters) + """

The prompt (the same for all three agents):
""" + PROMPT_CLAUDE.split("\n", 1)[1].strip() + "\n"
    (OUT / f"{t['name'].replace(' ', '_')}_youtube_description.txt").write_text(desc)
    print(mp4, f"{music_len:.1f}s, {len(clips)} frames")


if __name__ == "__main__":
    main(sys.argv[1])
