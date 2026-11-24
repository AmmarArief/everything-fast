"""Renders the everything-fast logo, wordmark and social card (Pillow, 4x supersampled).
The mark is a lightning bolt: the hot path, cut out of everything else. Its gradient runs
from cool blue (the original code) to forge orange (the part moved to Rust), with speed
lines falling away behind it.
    python scripts/logo.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets"
SS = 4  # supersampling

# Bolt on the 1024 grid, clockwise from the top tip.
BOLT = [(596, 72), (300, 568), (486, 568), (414, 952), (736, 452), (534, 452)]
# Speed lines: (x, y, width, alpha) behind the bolt.
LINES = [(96, 392, 152, 190), (120, 486, 104, 150), (150, 566, 64, 110)]


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(len(a)))


def vertical_gradient(size, stops):
    w, h = size
    img = Image.new("RGBA", size)
    px = img.load()
    for y in range(h):
        t = y / max(1, h - 1)
        for i in range(len(stops) - 1):
            (t0, c0), (t1, c1) = stops[i], stops[i + 1]
            if t0 <= t <= t1:
                c = lerp(c0, c1, (t - t0) / max(1e-9, t1 - t0))
                break
        for x in range(w):
            px[x, y] = c
    return img


def rounded_mask(size, radius):
    m = Image.new("L", (size, size), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    return m


def mark(size=1024, background=True):
    S = size * SS
    k = S / 1024
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    if background:
        bg = vertical_gradient((S, S), [(0, (26, 32, 44, 255)), (1, (9, 11, 16, 255))])
        glow = Image.new("L", (S, S), 0)
        ImageDraw.Draw(glow).ellipse([S * 0.16, S * 0.44, S * 0.84, S * 1.04], fill=140)
        glow = glow.filter(ImageFilter.GaussianBlur(S * 0.10))
        warm = Image.new("RGBA", (S, S), (249, 115, 22, 255))
        bg = Image.composite(Image.blend(bg, warm, 0.20), bg, glow)
        canvas.paste(bg, (0, 0), rounded_mask(S, int(S * 0.22)))
        rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(rim).rounded_rectangle(
            [2 * k, 2 * k, S - 2 * k, S - 2 * k], radius=int(S * 0.22), outline=(255, 255, 255, 26), width=int(3 * k)
        )
        canvas = Image.alpha_composite(canvas, rim)

    bolt_mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(bolt_mask).polygon([(x * k, y * k) for x, y in BOLT], fill=255)
    lines_mask = Image.new("L", (S, S), 0)
    dl = ImageDraw.Draw(lines_mask)
    for (x, y, w, a) in LINES:
        dl.rounded_rectangle([x * k, y * k, (x + w) * k, (y + 26) * k], radius=int(13 * k), fill=a)

    if background:
        halo = bolt_mask.filter(ImageFilter.GaussianBlur(34 * k))
        halo_rgba = Image.new("RGBA", (S, S), (249, 115, 22, 0))
        halo_rgba.putalpha(halo.point(lambda v: int(v * 0.85)))
        canvas = Image.alpha_composite(canvas, halo_rgba)

    bolt_fill = vertical_gradient(
        (S, S),
        [
            (0.00, (191, 219, 254, 255)),
            (0.22, (96, 165, 250, 255)),
            (0.46, (37, 99, 235, 255)),
            (0.68, (249, 115, 22, 255)),
            (0.86, (234, 88, 12, 255)),
            (1.00, (154, 52, 18, 255)),
        ],
    )
    bolt = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bolt.paste(bolt_fill, (0, 0), bolt_mask)
    # thin inner highlight along the left edge of the bolt
    edge = bolt_mask.filter(ImageFilter.GaussianBlur(2 * k))
    shine = Image.new("RGBA", (S, S), (255, 255, 255, 0))
    shine.putalpha(edge.point(lambda v: int(v * 0.10)))
    bolt = Image.alpha_composite(bolt, shine)
    canvas = Image.alpha_composite(canvas, bolt)

    line_fill = vertical_gradient((S, S), [(0.0, (96, 165, 250, 255)), (1.0, (59, 130, 246, 255))])
    lines = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    lines.paste(line_fill, (0, 0), lines_mask)
    canvas = Image.alpha_composite(canvas, lines)
    return canvas.resize((size, size), Image.LANCZOS)


def font(names, size):
    dirs = [
        Path("C:/Windows/Fonts"),
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/Library/Fonts"),
        Path("/usr/share/fonts/truetype/dejavu"),
        Path("/usr/share/fonts/truetype/liberation"),
    ]
    for n in names:
        for d in dirs:
            p = d / n
            if p.exists():
                return ImageFont.truetype(str(p), size)
    return ImageFont.load_default(size)


BOLD = ["segoeuib.ttf", "seguisb.ttf", "Arial Bold.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
REG = ["segoeui.ttf", "Arial.ttf", "arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]


def wordmark(width, height, logo_size, title_size, tagline=None, bg=True):
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    if bg:
        img = vertical_gradient((width, height), [(0, (17, 21, 28, 255)), (1, (8, 10, 14, 255))])
    logo = mark(logo_size) if bg else mark(logo_size, background=False)
    title = font(BOLD, title_size)
    small = font(REG, int(title_size * 0.34))
    d = ImageDraw.Draw(img)
    part = [("everything", (240, 246, 252)), ("-fast", (255, 122, 26))]
    text_w = sum(d.textlength(t, font=title) for t, _ in part)
    total = logo_size + title_size * 0.45 + text_w
    x = (width - total) / 2
    y = (height - logo_size) / 2 - (title_size * 0.30 if tagline else 0)
    img.alpha_composite(logo, (int(x), int(y)))
    tx = x + logo_size + title_size * 0.45
    ty = y + logo_size / 2
    for t, c in part:
        d.text((tx, ty), t, font=title, fill=c, anchor="lm")
        tx += d.textlength(t, font=title)
    if tagline:
        d.text((width / 2, y + logo_size + title_size * 0.62), tagline, font=small, fill=(139, 148, 158), anchor="mm")
    return img


def post_card(width=1200, height=720):
    img = Image.new("RGBA", (width, height), (13, 17, 23, 255))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([24, 24, width - 24, height - 24], radius=28, fill=(22, 27, 34), outline=(48, 54, 61), width=2)
    logo = mark(150)
    img.alpha_composite(logo, ((width - 150) // 2, 60))
    title = font(BOLD, 78)
    italic = font(REG, 30)
    body = font(REG, 22)
    x = width / 2
    part = [("everything", (240, 246, 252)), ("-fast", (255, 122, 26))]
    tx = (width - sum(d.textlength(t, font=title) for t, _ in part)) / 2
    for t, c in part:
        d.text((tx, 272), t, font=title, fill=c, anchor="lm")
        tx += d.textlength(t, font=title)
    d.line([(150, 336), (width - 150, 336)], fill=(48, 54, 61), width=2)
    d.text((x, 384), "Don't rewrite it all. Rewrite the 5% that's slow.", font=italic, fill=(230, 237, 243), anchor="mm")
    d.text((x, 426), "Python, Node, TypeScript, Ruby, Java, Go, PHP, C, C++, C#, R · checked against real calls", font=body, fill=(139, 148, 158), anchor="mm")
    stats = "up to 116× faster · every recorded call replayed · one command"
    d.text((x, 520), stats, font=font(BOLD, 24), fill=(240, 246, 252), anchor="mm")
    link = "github.com/AmmarArief/everything-fast"
    d.text((x - 120, 600), link, font=font(REG, 20), fill=(88, 166, 255), anchor="rm")
    d.text((x - 100, 600), "·  MIT", font=font(REG, 20), fill=(139, 148, 158), anchor="lm")
    return img.convert("RGB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    mark(1024).save(OUT / "logo.png")
    mark(256).save(OUT / "logo-256.png")
    mark(1024, background=False).resize((512, 512), Image.LANCZOS).save(OUT / "mark.png")
    wordmark(1600, 400, 260, 150, bg=False).save(OUT / "wordmark.png")
    wordmark(1280, 640, 250, 128, tagline="Don't rewrite it all. Rewrite the 5% that's slow.").convert("RGB").save(
        OUT / "social.png"
    )
    post_card().save(OUT / "post-card.png")
    print("ok")
