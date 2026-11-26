#!/usr/bin/env python3
"""Gera e valida o kit de midia do RecompLauncher (arte original, procedural).

Generates and validates the RecompLauncher media kit (original, procedural art).

Slots e tamanhos / slots and sizes (RecompLauncher `ui/customize.js` + `docs/CATALOG-MEDIA.md`):
  icon 256x256 (PNG + ICO), cover 600x900, hero 1920x620, logo 1000x500 (PNG transparente),
  wallpaper 1920x1080, artwork 1024x1024, catalog-entry.json (media_design kind "ds").

A arte e desenhada do zero com Pillow (sem imagens de terceiros): castelo gotico, lua de sangue e
selo magico azul-gelo. Requer `pip install pillow` (so para gerar; os testes nao precisam).
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
except ImportError as exc:  # pragma: no cover - mensagem amigavel
    raise SystemExit("Pillow nao encontrado. Rode: python -m pip install pillow") from exc

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "recomplauncher"
SHOTS = ROOT / "assets" / "screenshots"
REPO = "Neguchads/cdos-nintendods-recomp"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/main/assets/recomplauncher"
MAX_BYTES = 1_800_000  # abaixo do limite de 2 MiB do guarda clean-room do CI

INK = (7, 4, 12)
ICE = (120, 200, 255)
BONE = (236, 230, 244)
CRIMSON_DARK = (46, 6, 20)

FONT_CANDIDATES = [
    r"C:\Windows\Fonts\georgiab.ttf",
    r"C:\Windows\Fonts\timesbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
]

# arquivo -> (largura, altura, modo esperado ou None)
EXPECTED = {
    "icon.png": (256, 256, "RGBA"),
    "cover.png": (600, 900, None),
    "cover.jpg": (600, 900, None),
    "hero.png": (1920, 620, None),
    "hero.jpg": (1920, 620, None),
    "logo.png": (1000, 500, "RGBA"),
    "wallpaper.png": (1920, 1080, None),
    "artwork.png": (1024, 1024, None),
}
EXPECTED_SHOTS = {
    "gameplay-dx12-pip.png": (1920, 1080),
    "imgui-menu-f1.png": (1920, 1080),
    "vulkan-spirv-ptbr.png": (1920, 1080),
}
ICO_SIZES = [(256, 256), (64, 64), (48, 48), (32, 32), (16, 16)]


# ----------------------------------------------------------------------------- utilidades
def lerp(a: tuple[int, ...], b: tuple[int, ...], t: float) -> tuple[int, ...]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size)


def glow(base: Image.Image, layer: Image.Image, radius: float, strength: float = 1.0) -> None:
    blurred = layer.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        r, g, b, a = blurred.split()
        a = a.point(lambda v: min(255, int(v * strength)))
        blurred = Image.merge("RGBA", (r, g, b, a))
    base.alpha_composite(blurred)


# ----------------------------------------------------------------------------- cena
def sky(w: int, h: int, horizon: float) -> Image.Image:
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    top, mid, low = (8, 5, 26), (30, 10, 44), (104, 20, 42)
    for y in range(h):
        t = min(y / (h * horizon), 1.0)
        c = lerp(top, mid, t * 2) if t < 0.5 else lerp(mid, low, (t - 0.5) * 2)
        d.line([(0, y), (w, y)], fill=c)
    return img.convert("RGBA")


def stars(img: Image.Image, rng: random.Random, count: int) -> None:
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(count):
        x, y = rng.randrange(w), rng.randrange(int(h * 0.6))
        b = rng.uniform(0.35, 0.95)
        s = rng.choice((1, 1, 1, 2))
        d.ellipse([x, y, x + s, y + s], fill=(int(220 * b), int(220 * b), int(255 * b), 255))


def magic_seal(img: Image.Image, cx: float, cy: float, r: float, alpha: int = 235, rot: float = 0.0) -> None:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = ICE + (alpha,)
    lw = max(2, int(r * 0.012))
    for rad, wid in ((1.0, lw * 2), (0.94, lw), (0.72, lw), (0.5, lw)):
        d.ellipse([cx - r * rad, cy - r * rad, cx + r * rad, cy + r * rad], outline=col, width=int(wid))
    for k in range(72):
        a = rot + k * math.tau / 72
        r0, r1 = (0.945, 0.995) if k % 6 == 0 else (0.96, 0.985)
        d.line([(cx + math.cos(a) * r * r0, cy + math.sin(a) * r * r0), (cx + math.cos(a) * r * r1, cy + math.sin(a) * r * r1)], fill=col, width=lw)
    pts = [(cx + math.cos(rot - math.pi / 2 + k * math.tau / 5) * r * 0.72, cy + math.sin(rot - math.pi / 2 + k * math.tau / 5) * r * 0.72) for k in range(5)]
    for k in range(5):
        d.line([pts[k], pts[(k + 2) % 5]], fill=col, width=lw)
    box = [cx - r * 0.61, cy - r * 0.61, cx + r * 0.61, cy + r * 0.61]
    for k in range(12):
        deg = math.degrees(rot) + k * 30
        d.arc(box, start=deg, end=deg + 16, fill=col, width=lw * 3)
    glow(img, layer, r * 0.025 + 2, 1.3)
    glow(img, layer, r * 0.08 + 4, 0.9)
    img.alpha_composite(layer)


def blood_moon(img: Image.Image, cx: float, cy: float, r: float, rng: random.Random) -> None:
    halo = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse([cx - r * 1.5, cy - r * 1.5, cx + r * 1.5, cy + r * 1.5], fill=(190, 28, 48, 150))
    glow(img, halo, r * 0.8)
    moon = Image.new("RGBA", img.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    steps = 24
    for i in range(steps):
        t = i / steps
        rr = r * (1 - t * 0.55)
        off = -r * 0.18 * t
        md.ellipse([cx + off - rr, cy + off - rr, cx + off + rr, cy + off + rr], fill=lerp((120, 12, 30), (226, 70, 60), t) + (255,))
    for _ in range(7):
        a, dist = rng.uniform(0, math.tau), rng.uniform(0.05, 0.55) * r
        x, y, cr = cx + math.cos(a) * dist, cy + math.sin(a) * dist, rng.uniform(0.05, 0.12) * r
        md.ellipse([x - cr, y - cr, x + cr, y + cr], fill=(104, 12, 28, 160))
    img.alpha_composite(moon)


def ridge(img: Image.Image, y: float, amp: float, color: tuple[int, int, int], rng: random.Random) -> None:
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    pts = [(0, h)]
    x = 0.0
    while x <= w + 40:
        pts.append((x, y - rng.uniform(0, amp)))
        x += w / 14
    pts.append((w, h))
    ImageDraw.Draw(layer).polygon(pts, fill=color + (255,))
    img.alpha_composite(layer)


def castle(img: Image.Image, cx: float, base_y: float, u: float) -> None:
    """Silhueta de castelo gotico; u e a unidade de escala (altura total ~24u)."""
    w, h = img.size
    sil = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sil)
    ink = INK + (255,)
    d.polygon(
        [(cx - 15 * u, h), (cx - 11 * u, base_y + 3 * u), (cx - 7 * u, base_y + u), (cx - 3 * u, base_y), (cx + 5 * u, base_y), (cx + 9 * u, base_y + 2 * u), (cx + 13 * u, base_y + 4 * u), (cx + 15 * u, h)],
        fill=ink,
    )
    d.rectangle([cx - 5 * u, base_y - 9 * u, cx + 5 * u, base_y + 0.5 * u], fill=ink)
    for k in range(8):
        bx = cx - 5 * u + k * (10 * u / 8)
        d.rectangle([bx, base_y - 10 * u, bx + 0.7 * u, base_y - 9 * u], fill=ink)
    towers = [(-6.5, 2.2, 14, 1), (6.5, 2.2, 12, 1), (-2.6, 2.0, 17, 1), (2.7, 2.4, 20, 1), (0, 3.0, 24, 1), (-9.2, 1.6, 8, 1), (9.2, 1.6, 9, 1)]
    windows: list[tuple[float, float, float]] = []
    for dx, tw, th, _ in towers:
        x = cx + dx * u
        top = base_y - th * u
        d.rectangle([x - tw * u / 2, top, x + tw * u / 2, base_y + 0.5 * u], fill=ink)
        d.polygon([(x - tw * u * 0.75, top), (x, top - tw * u * 2.1), (x + tw * u * 0.75, top)], fill=ink)
        d.line([(x, top - tw * u * 2.1), (x, top - tw * u * 2.8)], fill=ink, width=max(1, int(u * 0.25)))
        windows.append((x, top + th * u * 0.28, tw * u * 0.28))
    for gx in (-3.2, -1.1, 1.1, 3.2):
        windows.append((cx + gx * u, base_y - 5.5 * u, 0.5 * u))
    img.alpha_composite(sil)
    wl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    wd = ImageDraw.Draw(wl)
    for x, y, ww in windows:
        wd.rectangle([x - ww / 2, y, x + ww / 2, y + ww * 1.8], fill=(255, 176, 74, 255))
        wd.ellipse([x - ww / 2, y - ww / 2, x + ww / 2, y + ww / 2], fill=(255, 176, 74, 255))
    glow(img, wl, u * 0.6 + 1, 1.2)
    img.alpha_composite(wl)


def mist(img: Image.Image, rng: random.Random, y: float, count: int, alpha: int) -> None:
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        x = rng.uniform(-0.1, 1.1) * w
        ew, eh = rng.uniform(0.18, 0.4) * w, rng.uniform(0.02, 0.05) * h
        yy = y + rng.uniform(-0.04, 0.04) * h
        d.ellipse([x - ew, yy - eh, x + ew, yy + eh], fill=(214, 150, 184, alpha))
    glow(img, layer, h * 0.025 + 2)


def bats(img: Image.Image, rng: random.Random, count: int, area: tuple[float, float, float, float]) -> None:
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(count):
        x, y = rng.uniform(area[0], area[2]) * w, rng.uniform(area[1], area[3]) * h
        s = rng.uniform(0.008, 0.016) * min(w, h) * 2
        d.polygon([(x - s, y - s * 0.2), (x - s * 0.5, y - s * 0.55), (x, y), (x + s * 0.5, y - s * 0.55), (x + s, y - s * 0.2), (x + s * 0.4, y + s * 0.2), (x, y + s * 0.4), (x - s * 0.4, y + s * 0.2)], fill=INK + (255,))


def tombstones(img: Image.Image, rng: random.Random, count: int, y: float) -> None:
    w, h = img.size
    d = ImageDraw.Draw(img)
    for _ in range(count):
        x = rng.uniform(0.0, 0.5) * w
        tw, th = rng.uniform(0.012, 0.022) * w, rng.uniform(0.04, 0.09) * h
        top = y - th
        d.rectangle([x, top + tw / 2, x + tw, y + 0.1 * h], fill=INK + (255,))
        d.ellipse([x, top, x + tw, top + tw], fill=INK + (255,))


def vignette(img: Image.Image, strength: float = 0.7) -> None:
    mask = Image.radial_gradient("L").resize(img.size, Image.Resampling.BICUBIC)
    mask = mask.point(lambda v: int(v * strength))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.putalpha(mask)
    img.alpha_composite(layer)


def scene(
    w: int,
    h: int,
    seed: int,
    *,
    moon: tuple[float, float, float],
    seal: tuple[float, float, float],
    castle_at: tuple[float, float, float],
    horizon: float = 0.8,
    bat_count: int = 8,
    stars_scale: float = 1.0,
    graveyard: bool = False,
) -> Image.Image:
    rng = random.Random(seed)
    m = min(w, h)
    img = sky(w, h, horizon)
    stars(img, rng, int(w * h / 9000 * stars_scale))
    magic_seal(img, seal[0] * w, seal[1] * h, seal[2] * m, alpha=170, rot=0.2)
    blood_moon(img, moon[0] * w, moon[1] * h, moon[2] * m, rng)
    ridge(img, h * (horizon - 0.04), h * 0.08, (28, 11, 42), rng)
    ridge(img, h * (horizon + 0.01), h * 0.06, (17, 8, 30), rng)
    if bat_count:
        bats(img, rng, bat_count, (0.05, 0.08, 0.95, 0.5))
    mist(img, rng, h * (horizon + 0.02), 10, 26)
    castle(img, castle_at[0] * w, castle_at[1] * h, castle_at[2] * m)
    if graveyard:
        tombstones(img, rng, 14, h * 0.96)
    mist(img, rng, h * 0.97, 8, 30)
    vignette(img)
    return img


# ----------------------------------------------------------------------------- texto
def text_width(text: str, f: ImageFont.FreeTypeFont | ImageFont.ImageFont, track: float) -> float:
    return sum(f.getlength(ch) for ch in text) + track * (len(text) - 1)


def fit_font(text: str, width: float, track_frac: float = 0.12, max_size: int = 400):
    lo, hi = 8, max_size
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if text_width(text, font(mid), mid * track_frac) <= width:
            lo = mid
        else:
            hi = mid - 1
    return font(lo), lo * track_frac, lo


def draw_tracked(img: Image.Image, cx: float, cy: float, text: str, width: float, fill, stroke_fill, glow_color, track_frac: float = 0.12) -> int:
    f, track, size = fit_font(text, width, track_frac)
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x = cx - text_width(text, f, track) / 2
    asc, desc = f.getmetrics()
    y = cy - (asc + desc) / 2
    stroke = max(1, int(size * 0.045))
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        x += f.getlength(ch) + track
    halo = Image.new("RGBA", img.size, glow_color + (0,))
    halo.putalpha(layer.getchannel("A"))
    glow(img, halo, size * 0.12 + 2, 1.4)
    img.alpha_composite(layer)
    return size


def wordmark(img: Image.Image, cx: float, cy: float, width: float, tagline: bool = True) -> None:
    s1 = draw_tracked(img, cx, cy, "CASTLEVANIA", width, BONE + (255,), CRIMSON_DARK + (255,), (190, 28, 48))
    y2 = cy + s1 * 0.95
    s2 = draw_tracked(img, cx, y2, "DAWN OF SORROW", width * 0.62, (214, 226, 246, 255), CRIMSON_DARK + (255,), ICE, 0.16)
    if tagline:
        draw_tracked(img, cx, y2 + s2 * 1.25, "RECOMPILED", width * 0.3, ICE + (255,), INK + (255,), ICE, 0.3)


def bottom_shade(img: Image.Image, start: float, max_alpha: int) -> None:
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(h * start)
    for y in range(y0, h):
        d.line([(0, y), (w, y)], fill=(4, 2, 8, int(max_alpha * (y - y0) / max(1, h - y0))))
    img.alpha_composite(layer)


def left_shade(img: Image.Image, end: float, max_alpha: int) -> None:
    w, h = img.size
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x1 = int(w * end)
    for x in range(x1):
        d.line([(x, 0), (x, h)], fill=(4, 2, 8, int(max_alpha * (1 - x / x1))))
    img.alpha_composite(layer)


# ----------------------------------------------------------------------------- ativos
def make_cover() -> Image.Image:
    img = scene(600, 900, 11, moon=(0.68, 0.2, 0.16), seal=(0.68, 0.2, 0.42), castle_at=(0.5, 0.72, 0.036), horizon=0.74, bat_count=6)
    bottom_shade(img, 0.62, 215)
    wordmark(img, 300, 770, 500)
    return img


def make_hero() -> Image.Image:
    img = scene(1920, 620, 21, moon=(0.78, 0.3, 0.2), seal=(0.78, 0.3, 0.6), castle_at=(0.78, 0.8, 0.03), horizon=0.82, bat_count=8)
    left_shade(img, 0.62, 190)
    wordmark(img, 560, 270, 880)
    return img


def make_wallpaper() -> Image.Image:
    img = scene(1920, 1080, 31, moon=(0.7, 0.3, 0.12), seal=(0.7, 0.3, 0.44), castle_at=(0.72, 0.8, 0.024), horizon=0.8, bat_count=10, graveyard=True)
    left_shade(img, 0.6, 150)
    wordmark(img, 580, 470, 900)
    return img


def make_icon_base() -> Image.Image:
    img = scene(1024, 1024, 51, moon=(0.5, 0.42, 0.17), seal=(0.5, 0.42, 0.46), castle_at=(0.5, 0.92, 0.018), horizon=0.9, bat_count=0, stars_scale=0.5)
    return img


def make_icon() -> Image.Image:
    base = make_icon_base()
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, base.size[0] - 1, base.size[1] - 1], radius=int(base.size[0] * 0.18), fill=255)
    base.putalpha(mask)
    return base.resize((256, 256), Image.Resampling.LANCZOS)


def make_logo() -> Image.Image:
    img = Image.new("RGBA", (1000, 500), (0, 0, 0, 0))
    magic_seal(img, 500, 92, 62, alpha=240, rot=0.2)
    s1 = draw_tracked(img, 500, 262, "CASTLEVANIA", 900, BONE + (255,), CRIMSON_DARK + (255,), (190, 28, 48))
    s2 = draw_tracked(img, 500, 262 + s1 * 0.95, "DAWN OF SORROW", 560, (214, 226, 246, 255), CRIMSON_DARK + (255,), ICE, 0.16)
    draw_tracked(img, 500, 262 + s1 * 0.95 + s2 * 1.35, "RECOMPILED", 280, ICE + (255,), INK + (255,), ICE, 0.3)
    return img


def ds_cartridge(canvas: Image.Image, cx: int, cy: int, label_art: Image.Image) -> None:
    w, h = canvas.size
    cw, ch = 330, 360
    x0, y0, x1, y1 = cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rectangle([x0 + 10, y0 + 24, x1 + 10, y1 + 24], fill=(0, 0, 0, 200))
    glow(canvas, shadow, 22)
    body = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    chamfer = 46
    poly = [(x0 + 18, y0), (x1 - chamfer, y0), (x1, y0 + chamfer), (x1, y1 - 18), (x1 - 18, y1), (x0 + 18, y1), (x0, y1 - 18), (x0, y0 + 18)]
    d.polygon(poly, fill=(168, 170, 180, 255), outline=(236, 238, 244, 255))
    d.line([(x0 + 4, y0 + 22), (x0 + 4, y1 - 22)], fill=(214, 216, 224, 255), width=3)
    lx0, ly0, lx1, ly1 = x0 + 22, y0 + 26, x1 - 22, y0 + 232
    d.rectangle([lx0 - 3, ly0 - 3, lx1 + 3, ly1 + 3], fill=(40, 42, 52, 255))
    canvas.alpha_composite(body)
    crop = label_art.copy()
    cw_, ch_ = lx1 - lx0, ly1 - ly0
    scale = max(cw_ / crop.size[0], ch_ / crop.size[1])
    crop = crop.resize((int(crop.size[0] * scale), int(crop.size[1] * scale)), Image.Resampling.LANCZOS)
    ox, oy = (crop.size[0] - cw_) // 2, int((crop.size[1] - ch_) * 0.25)
    canvas.paste(crop.crop((ox, oy, ox + cw_, oy + ch_)).convert("RGBA"), (lx0, ly0))
    d2 = ImageDraw.Draw(canvas)
    for k in range(9):
        yy = ly1 + 22 + k * 7
        d2.line([(x0 + 40, yy), (x1 - 40, yy)], fill=(138, 140, 150, 255), width=2)
    d2.rectangle([x0 + 70, y1 - 30, x1 - 70, y1 - 8], fill=(30, 30, 38, 255))
    for k in range(16):
        px = x0 + 78 + k * ((cw - 156) / 16)
        d2.rectangle([px, y1 - 26, px + 5, y1 - 12], fill=(206, 170, 74, 255))
    f = font(15)
    d2.text((x0 + 26, ly1 + 6), "ACVE", font=f, fill=(40, 42, 52, 255))


def make_artwork(cover: Image.Image) -> Image.Image:
    img = scene(1024, 1024, 41, moon=(0.5, 0.22, 0.12), seal=(0.5, 0.26, 0.42), castle_at=(0.5, 0.56, 0.018), horizon=0.58, bat_count=7)
    bottom_shade(img, 0.5, 170)
    ds_cartridge(img, 512, 720, cover)
    draw_tracked(img, 512, 960, "NATIVE STATIC RECOMPILATION", 700, ICE + (255,), INK + (255,), ICE, 0.2)
    return img


# ----------------------------------------------------------------------------- saida
def save_png(img: Image.Image, path: Path) -> None:
    img.save(path, optimize=True)
    if path.stat().st_size > MAX_BYTES and img.mode == "RGB":
        img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(path, optimize=True)


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    cover = make_cover()
    hero = make_hero()
    wallpaper = make_wallpaper()
    icon = make_icon()
    logo = make_logo()
    artwork = make_artwork(cover)
    save_png(icon, OUT / "icon.png")
    icon.save(OUT / "icon.ico", format="ICO", sizes=ICO_SIZES)
    save_png(cover.convert("RGB"), OUT / "cover.png")
    cover.convert("RGB").save(OUT / "cover.jpg", quality=90, optimize=True)
    save_png(hero.convert("RGB"), OUT / "hero.png")
    hero.convert("RGB").save(OUT / "hero.jpg", quality=90, optimize=True)
    save_png(logo, OUT / "logo.png")
    save_png(wallpaper.convert("RGB"), OUT / "wallpaper.png")
    save_png(artwork.convert("RGB"), OUT / "artwork.png")
    write_catalog_entry()


def write_catalog_entry() -> None:
    entry = {
        "id": "cdos-nintendods-recomp",
        "name": "Castlevania: Dawn of Sorrow: Recompiled",
        "game": "Castlevania: Dawn of Sorrow",
        "origin": "ds",
        "repo": REPO,
        "blurb": "Play Castlevania: Dawn of Sorrow natively on PC with 60 FPS gameplay, HD-2D graphics, widescreen layouts, modular mods, custom music and modern controls. Your own original USA Nintendo DS ROM is required.",
        "author": REPO.split("/")[0],
        "icon": f"{RAW_BASE}/icon.png",
        "cover": f"{RAW_BASE}/cover.jpg",
        "hero": f"{RAW_BASE}/hero.jpg",
        "logo": f"{RAW_BASE}/logo.png",
        "systems": ["windows"],
        "tags": ["Widescreen", "60 FPS", "Mods", "HD-2D", "Custom Music", "Controller Support", "Save States", "Native PC"],
        "genre": "action",
        "media_design": {
            "kind": "ds",
            "art": "cover",
            "style": "image",
            "crop": {"x": 0.5, "y": 0.2, "z": 1, "w": 600, "h": 900},
            "logo": {"on": False},
        },
    }
    (OUT / "catalog-entry.json").write_text(json.dumps(entry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def validate() -> list[str]:
    errors: list[str] = []
    for name, (w, h, mode) in EXPECTED.items():
        path = OUT / name
        if not path.is_file():
            errors.append(f"ausente: {path}")
            continue
        if path.stat().st_size > MAX_BYTES:
            errors.append(f"{name}: {path.stat().st_size} B excede {MAX_BYTES} B")
        with Image.open(path) as im:
            if im.size != (w, h):
                errors.append(f"{name}: {im.size} != {(w, h)}")
            if mode and im.mode != mode:
                errors.append(f"{name}: modo {im.mode} != {mode}")
            if name == "logo.png":
                px = im.convert("RGBA")
                if any(px.getpixel(c)[3] != 0 for c in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))):
                    errors.append("logo.png: cantos nao sao transparentes")
    ico = OUT / "icon.ico"
    if not ico.is_file():
        errors.append(f"ausente: {ico}")
    else:
        with Image.open(ico) as im:
            got = set(im.info.get("sizes", set()))
        if not set(ICO_SIZES).issubset(got):
            errors.append(f"icon.ico: tamanhos {sorted(got)} nao cobrem {ICO_SIZES}")
    if not (OUT / "catalog-entry.json").is_file():
        errors.append("ausente: catalog-entry.json")
    for name, (w, h) in EXPECTED_SHOTS.items():
        path = SHOTS / name
        if not path.is_file():
            errors.append(f"ausente: {path}")
            continue
        if path.stat().st_size > MAX_BYTES:
            errors.append(f"{name}: {path.stat().st_size} B excede {MAX_BYTES} B")
        with Image.open(path) as im:
            if im.size != (w, h):
                errors.append(f"{name}: {im.size} != {(w, h)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check-only", action="store_true", help="Apenas valida os arquivos existentes")
    ap.add_argument(
        "--regenerate-procedural",
        action="store_true",
        help="Regera os placeholders procedurais sobrescrevendo as artes de assets/recomplauncher/",
    )
    args = ap.parse_args(argv)
    if args.regenerate_procedural or (not args.check_only and validate()):
        build()
    errors = validate()
    for e in errors:
        print(f"[erro] {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"[media] OK: {len(EXPECTED)} imagens + icon.ico + catalog-entry.json + {len(EXPECTED_SHOTS)} capturas validados")
    return 0


if __name__ == "__main__":
    sys.exit(main())
