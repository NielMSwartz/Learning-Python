"""Generate the PWA icons with Pillow (no external assets required).

Run: python scripts/generate_icons.py
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "app" / "static" / "icons"
OUT.mkdir(parents=True, exist_ok=True)


def font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()  # type: ignore[return-value]


def make(size: int, maskable: bool = False) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Full-bleed gradient background (also safe for maskable icons).
    top = (55, 118, 171)
    bottom = (24, 47, 70)
    for y in range(size):
        ratio = y / max(1, size - 1)
        color = tuple(round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, size, y), fill=(*color, 255))

    # Subtle grid evokes an editor.
    grid = max(18, size // 10)
    for position in range(grid, size, grid):
        draw.line((position, 0, position, size), fill=(255, 255, 255, 14), width=max(1, size // 256))
        draw.line((0, position, size, position), fill=(255, 255, 255, 14), width=max(1, size // 256))

    # Rounded card for "any" icons; maskable icons keep the full background.
    if not maskable:
        inset = int(size * 0.06)
        draw.rounded_rectangle(
            (inset, inset, size - inset, size - inset),
            radius=int(size * 0.2),
            fill=(21, 33, 48, 255),
            outline=(255, 212, 59, 210),
            width=max(2, size // 96),
        )

    # Two Python-inspired interlocking tiles.
    tile = int(size * (0.34 if maskable else 0.38))
    x0 = (size - tile * 2 + int(size * 0.03)) // 2
    y0 = (size - tile) // 2
    radius = int(size * 0.07)
    draw.rounded_rectangle((x0, y0, x0 + tile, y0 + tile), radius=radius, fill=(55, 118, 171, 255))
    draw.rounded_rectangle(
        (x0 + tile - int(size * 0.03), y0, x0 + tile * 2 - int(size * 0.03), y0 + tile),
        radius=radius,
        fill=(255, 212, 59, 255),
    )
    dot = max(3, size // 48)
    for cx in (x0 + int(tile * 0.28), x0 + tile + int(tile * 0.28) - int(size * 0.03)):
        draw.ellipse((cx - dot, y0 + int(tile * 0.28) - dot, cx + dot, y0 + int(tile * 0.28) + dot), fill=(21, 33, 48, 255))

    # Label.
    label = "Py"
    fnt = font(int(size * (0.22 if maskable else 0.24)))
    bbox = draw.textbbox((0, 0), label, font=fnt)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(
        ((size - tw) / 2 - bbox[0], (size - th) / 2 - bbox[1] + size * 0.01),
        label,
        font=fnt,
        fill=(255, 255, 255, 255),
        stroke_width=max(1, size // 192),
        stroke_fill=(21, 33, 48, 255),
    )
    return image.convert("RGB")


for name, size, maskable in [
    ("icon-192.png", 192, False),
    ("icon-512.png", 512, False),
    ("maskable-512.png", 512, True),
]:
    make(size, maskable).save(OUT / name, "PNG", optimize=True)
    print("wrote", OUT / name)
