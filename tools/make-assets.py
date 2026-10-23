#!/usr/bin/env python3
"""Render the PNG assets for the Cyborg 15 Plymouth theme.

Everything is drawn at 4x and downsampled for clean anti-aliasing. Sizes are
designed for a 1080p screen; cyborg.script scales them to the real resolution.
Usage: make-assets.py OUTPUT_DIR
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else "cyborg")
SS = 4  # supersampling factor

CYAN = (0, 229, 255)
MAGENTA = (255, 43, 214)
FONT = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
FONT_MED = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def finish(img, w, h, name):
    img.resize((w, h), Image.LANCZOS).save(OUT / name)


def glow(layer, radius, strength=1.0):
    """Return layer composited over a blurred copy of itself."""
    blur = layer.filter(ImageFilter.GaussianBlur(radius * SS))
    if strength != 1.0:
        a = blur.getchannel("A").point(lambda v: min(255, int(v * strength)))
        blur.putalpha(a)
    return Image.alpha_composite(blur, layer)


def lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def ring(size=240):
    """Rotating outer ring: two neon arcs fading cyan -> magenta, plus tick marks."""
    img = canvas(size, size)
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    r = size * SS * 0.40
    width = int(5 * SS)
    for start, span in ((0, 200), (220, 110)):
        steps = span * 2
        for i in range(steps):
            t = i / steps
            a0 = start + span * t
            col = lerp(CYAN, MAGENTA, t) + (int(70 + 185 * t),)
            d.arc([c - r, c - r, c + r, c + r], a0, a0 + span / steps + 0.6, fill=col, width=width)
    # tick marks on a slightly larger radius
    for k in range(24):
        ang = math.radians(k * 15)
        r1, r2 = r + 12 * SS, r + (20 if k % 6 == 0 else 15) * SS
        d.line([c + r1 * math.cos(ang), c + r1 * math.sin(ang), c + r2 * math.cos(ang), c + r2 * math.sin(ang)],
               fill=CYAN + (150 if k % 6 == 0 else 60,), width=int(2 * SS))
    finish(glow(img, 6, 1.4), size, size, "ring.png")


def inner_ring(size=240):
    """Static thin inner circle with a counter-rotating dashed track."""
    img = canvas(size, size)
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    r = size * SS * 0.30
    for k in range(36):
        a0 = k * 10
        d.arc([c - r, c - r, c + r, c + r], a0, a0 + 5, fill=CYAN + (140,), width=int(2 * SS))
    finish(glow(img, 3), size, size, "inner.png")


def core(size=240):
    """Glowing hexagonal core that pulses in the middle."""
    img = canvas(size, size)
    d = ImageDraw.Draw(img)
    c = size * SS / 2
    r = size * SS * 0.13
    pts = [(c + r * math.cos(math.radians(60 * k + 30)), c + r * math.sin(math.radians(60 * k + 30))) for k in range(6)]
    d.polygon(pts, outline=CYAN + (255,), width=int(3 * SS))
    r2 = r * 0.45
    d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=(200, 250, 255, 255))
    finish(glow(img, 10, 2.0), size, size, "core.png")


def logo(w=640, h=110):
    """'CYBORG 15' wordmark with glow and a split cyan/magenta underline."""
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 54 * SS)
    text = "CYBORG"
    spacing = 14 * SS
    # measure with letter spacing
    widths = [d.textlength(ch, font=font) for ch in text]
    num_font = ImageFont.truetype(FONT, 54 * SS)
    num = "15"
    num_w = d.textlength(num, font=num_font)
    gap = 30 * SS
    total = sum(widths) + spacing * (len(text) - 1) + gap + num_w
    x = (w * SS - total) / 2
    y = 8 * SS
    for ch, cw in zip(text, widths):
        d.text((x, y), ch, font=font, fill=(235, 252, 255, 255))
        x += cw + spacing
    x += gap - spacing
    d.text((x, y), num, font=num_font, fill=CYAN + (255,))
    # underline: cyan left part, magenta right accent
    uy = 88 * SS
    left = (w * SS - total) / 2
    right = left + total
    split = left + (right - left) * 0.72
    d.rectangle([left, uy, split - 6 * SS, uy + 3 * SS], fill=CYAN + (230,))
    d.rectangle([split + 6 * SS, uy, right, uy + 3 * SS], fill=MAGENTA + (230,))
    finish(glow(img, 5, 1.2), w, h, "logo.png")


def bar(w=440, h=14):
    """Progress bar track and fill (fill is a cyan -> magenta gradient)."""
    track = canvas(w, h)
    d = ImageDraw.Draw(track)
    m = 4 * SS
    d.rounded_rectangle([0 + m, m, w * SS - m, h * SS - m], radius=3 * SS, outline=CYAN + (70,), width=SS,
                        fill=(10, 30, 40, 180))
    finish(track, w, h, "bar-track.png")

    fill = canvas(w, h)
    d = ImageDraw.Draw(fill)
    for x in range(m, w * SS - m):
        t = (x - m) / (w * SS - 2 * m)
        d.line([x, m + SS, x, h * SS - m - SS], fill=lerp(CYAN, MAGENTA, t) + (255,))
    finish(glow(fill, 3, 1.3), w, h, "bar-fill.png")


def entry(w=460, h=56):
    """Password box with a lock glyph on the left."""
    img = canvas(w, h)
    d = ImageDraw.Draw(img)
    m = 6 * SS
    d.rounded_rectangle([m, m, w * SS - m, h * SS - m], radius=10 * SS, outline=CYAN + (220,), width=2 * SS,
                        fill=(4, 16, 24, 230))
    # lock: shackle + body
    lx, cy = 22 * SS + m, h * SS / 2
    d.arc([lx, cy - 14 * SS, lx + 16 * SS, cy + 2 * SS], 180, 360, fill=CYAN + (255,), width=int(2.5 * SS))
    d.rounded_rectangle([lx - 3 * SS, cy - 5 * SS, lx + 19 * SS, cy + 11 * SS], radius=3 * SS, fill=CYAN + (255,))
    d.ellipse([lx + 6 * SS, cy + 0 * SS, lx + 10 * SS, cy + 4 * SS], fill=(4, 16, 24, 255))
    finish(glow(img, 4, 0.9), w, h, "entry.png")


def bullet(size=18):
    img = canvas(size, size)
    d = ImageDraw.Draw(img)
    c, r = size * SS / 2, size * SS * 0.24
    d.ellipse([c - r, c - r, c + r, c + r], fill=(220, 252, 255, 255))
    finish(glow(img, 2, 1.5), size, size, "bullet.png")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ring()
    inner_ring()
    core()
    logo()
    bar()
    entry()
    bullet()
    print("assets written to", OUT)


if __name__ == "__main__":
    main()
