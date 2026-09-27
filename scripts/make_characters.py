"""Ports Mamu and Mia (companion/Reigns/Pet/PetView.swift) to static SVGs for the site.

Writes public/<name>.svg (Calm portrait) and public/stages/<name>-<stage>.svg (each heat stage as the
app shows it: peeking up from the floor, with accessories and a sample heat badge).
Coordinates follow the Swift 64x84 horse frame: centre (32, 42), ZStack children centred then offset.

Run: python3 scripts/make_characters.py
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public"
MANE = "#381F14"  # HorsePalette.mane (0.22, 0.13, 0.08)
STAGES = ["calm", "curious", "concerned", "alarmed", "meltdown", "recovered"]
VISIBLE = {"calm": 44, "curious": 54, "concerned": 64, "alarmed": 80, "meltdown": 84, "recovered": 84}
SAMPLE_HEAT = {"calm": 5, "curious": 22, "concerned": 44, "alarmed": 70, "meltdown": 97, "recovered": 0}
SAMPLE_UNVERIFIED = {"curious": 2, "concerned": 3}


def rgb(r, g, b):
    return "#%02X%02X%02X" % (round(r * 255), round(g * 255), round(b * 255))


PALETTES = {  # (coat, muzzle, inner ear)
    "brown": (rgb(0.55, 0.34, 0.20), rgb(0.80, 0.64, 0.50), rgb(0.85, 0.62, 0.55)),
    "pearl": (rgb(0.99, 0.97, 0.98), rgb(1.00, 0.87, 0.91), rgb(1.00, 0.72, 0.84)),
    "curious": (rgb(0.74, 0.54, 0.37), rgb(0.91, 0.80, 0.68), rgb(0.93, 0.72, 0.66)),
    "concerned": (rgb(0.30, 0.50, 0.82), rgb(0.70, 0.82, 0.96), rgb(0.62, 0.74, 0.95)),
    "alarmed": (rgb(0.96, 0.78, 0.20), rgb(1.00, 0.93, 0.66), rgb(1.00, 0.86, 0.55)),
    "meltdown": (rgb(0.86, 0.22, 0.20), rgb(0.98, 0.68, 0.62), rgb(0.98, 0.60, 0.56)),
}


def palette(stage, mia):
    if stage in ("calm", "recovered"):
        return PALETTES["pearl" if mia else "brown"]
    return PALETTES[stage]


def triangle(x, y, w, h):
    return f"M{x + w / 2:.2f} {y:.2f} L{x + w:.2f} {y + h:.2f} L{x:.2f} {y + h:.2f} Z"


def ears(coat, inner, outline, outline_opacity):
    out = []
    for cx, deg in ((17.5, -12), (46.5, 12)):
        out.append(
            f'<g transform="rotate({deg} {cx} 21.5)">'
            f'<path d="{triangle(cx - 7.5, 2.5, 15, 19)}" fill="{coat}" stroke="{outline}" '
            f'stroke-opacity="{outline_opacity}" stroke-width="1" stroke-linejoin="round"/>'
            f'<path d="{triangle(cx - 3.5, 10, 7, 10)}" fill="{inner}"/></g>'
        )
    return "".join(out)


def head(coat, outline, outline_opacity):
    return (f'<rect x="9.5" y="13.5" width="45" height="69" rx="21.5" fill="{coat}" '
            f'stroke="{outline}" stroke-opacity="{outline_opacity}" stroke-width="1"/>')


def jitter(i, salt):
    x = math.sin(i * 12_989 + salt * 78_233) * 43_758.5453
    return x - math.floor(x)


def mamu_mane():
    base = rgb(0.24, 0.12, 0.05)
    shades = [rgb(0.36, 0.19, 0.08), rgb(0.50, 0.27, 0.11), rgb(0.30, 0.15, 0.06), rgb(0.58, 0.33, 0.14)]
    golden = rgb(0.93, 0.70, 0.36)
    out = [f'<ellipse cx="32" cy="13" rx="7" ry="5" fill="{base}"/>']
    for i in range(70):
        r1, r2, r3 = jitter(i, 1), jitter(i, 2), jitter(i, 3)
        across = r1 * 2 - 1
        rx, ry = 32 + across * 7, 16 + across * across * 2.5
        length = (7.5 + r2 * 7.5) * (1 - 0.35 * across * across)
        angle = across * 0.55 + (r3 - 0.5) * 0.5
        wiggle = math.sin(i) * 0.35
        tx, ty = rx + math.sin(angle) * length + wiggle, ry - math.cos(angle) * length
        cx, cy = (rx + tx) / 2 + (r3 - 0.5) * 2.5, (ry + ty) / 2
        color, op = (golden, 0.9) if i % 8 == 5 else (shades[i % 4], 1)
        out.append(f'<path d="M{rx:.2f} {ry:.2f} Q{cx:.2f} {cy:.2f} {tx:.2f} {ty:.2f}" stroke="{color}" '
                   f'stroke-opacity="{op}" stroke-width="{1 + r1 * 0.8:.2f}" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def hair_lock(x, y, w, h, mirror):
    pts = [
        ("M", [(0.1 * w, 0)]),
        ("Q", [(0.45 * w, -0.03 * h), (0.75 * w, 0.05 * h)]),
        ("C", [(0.95 * w, 0.4 * h), (0.6 * w, 0.8 * h), (w, h)]),
        ("C", [(0.3 * w, 0.75 * h), (0, 0.35 * h), (0.1 * w, 0)]),
    ]
    d = ""
    for cmd, ps in pts:
        coords = " ".join(f"{x + ((w - px) if mirror else px):.2f} {y + py:.2f}" for px, py in ps)
        d += f"{cmd}{coords} "
    return d + "Z"


def horn():
    x, y, w, h = 28, -6.5, 8, 19
    shape = (f"M{x + w / 2} {y} Q{x + w * 0.8} {y + h / 2} {x + w} {y + h} L{x} {y + h} "
             f"Q{x + w * 0.2} {y + h / 2} {x + w / 2} {y} Z")
    grooves = "".join(f"M{x} {y + h * i / 5 + 2:.2f} L{x + w} {y + h * i / 5 - 2:.2f} " for i in range(1, 5))
    edge = rgb(0.85, 0.62, 0.20)
    return (f'<defs><linearGradient id="horn" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{rgb(1.0, 0.95, 0.70)}"/><stop offset="1" stop-color="{rgb(0.98, 0.78, 0.30)}"/>'
            f'</linearGradient><clipPath id="hornClip"><path d="{shape}"/></clipPath></defs>'
            f'<path d="{shape}" fill="url(#horn)"/>'
            f'<path d="{grooves}" stroke="{edge}" stroke-width="0.8" stroke-linecap="round" clip-path="url(#hornClip)"/>'
            f'<path d="{shape}" fill="none" stroke="{edge}" stroke-opacity="0.6" stroke-width="0.5"/>')


def mia_mane():
    stops = [rgb(1.00, 0.62, 0.80), rgb(0.76, 0.62, 1.00), rgb(0.55, 0.80, 1.00)]
    grad = lambda gid, x2, y2: (f'<linearGradient id="{gid}" x1="0" y1="0" x2="{x2}" y2="{y2}">' +
                                "".join(f'<stop offset="{i / 2}" stop-color="{c}"/>' for i, c in enumerate(stops)) +
                                "</linearGradient>")
    return (f"<defs>{grad('rainbowH', 1, 0)}{grad('rainbowV', 0, 1)}</defs>"
            f'<ellipse cx="30" cy="17" rx="13" ry="8" transform="rotate(-12 30 17)" fill="url(#rainbowH)"/>'
            f'<path d="{hair_lock(4.5, 18, 9, 34, True)}" fill="url(#rainbowV)"/>'
            f'<path d="{hair_lock(50.5, 18, 9, 34, False)}" fill="url(#rainbowV)"/>')


def star(cx, cy, size):
    r, inner = size / 2, size / 2 * 0.28
    pts = []
    for k in range(8):
        a = k * math.pi / 4 - math.pi / 2
        rad = r if k % 2 == 0 else inner
        pts.append(f"{cx + rad * math.cos(a):.2f} {cy + rad * math.sin(a):.2f}")
    return f'<path d="M{" L".join(pts)} Z" fill="{rgb(1.0, 0.85, 0.40)}"/>'


def eye(x, stage, right, coat):
    y = 36
    if stage == "recovered":  # happy closed "∩"
        return (f'<path d="M{x - 6} 39 Q{x} 29.4 {x + 6} 39" stroke="{MANE}" stroke-width="2.2" '
                f'stroke-linecap="round" fill="none"/>')
    if stage == "meltdown":  # spinning spiral
        pts = []
        for i in range(91):
            th = i / 90 * 3 * 2 * math.pi * (1 if right else -1)
            r = 6 * i / 90
            pts.append(f"{x + r * math.cos(th):.2f} {y + r * math.sin(th):.2f}")
        return (f'<circle cx="{x}" cy="{y}" r="7.5" fill="#fff"/>'
                f'<path d="M{" L".join(pts)}" stroke="#000" stroke-width="1.3" stroke-linecap="round" fill="none"/>')
    size = {"alarmed": 16, "curious": 15.5 if right else 13}.get(stage, 13)
    pupil = 4.5 if stage == "alarmed" else 7
    lx, ly = {"curious": (1, -1.5), "concerned": (3, 1)}.get(stage, (0, 0))
    r = size / 2
    out = (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff"/>'
           f'<circle cx="{x + lx}" cy="{y + ly}" r="{pupil / 2}" fill="#000"/>'
           f'<circle cx="{x + lx + 1.5}" cy="{y + ly - 1.5}" r="1.25" fill="#fff"/>')
    if stage == "concerned":  # heavy upper lid, clipped to the eye
        cid = f"lid{'R' if right else 'L'}"
        out += (f'<clipPath id="{cid}"><circle cx="{x}" cy="{y}" r="{r}"/></clipPath>'
                f'<rect x="{x - r}" y="{y - r}" width="{size}" height="{size * 0.42:.2f}" fill="{coat}" '
                f'clip-path="url(#{cid})"/>')
    return out


def lashes(x, right):
    roots = [(0.55, 0.95), (0.72, 1.0), (0.88, 1.15)]
    tips = [(0.62, 0.15), (0.86, 0.2), (1.08, 0.45)]
    left, top = x - 6.5, 26
    fx = (lambda u: left + 13 * u) if right else (lambda u: left + 13 * (1 - u))
    d = " ".join(f"M{fx(r[0]):.2f} {top + 5 * r[1]:.2f} L{fx(t[0]):.2f} {top + 5 * t[1]:.2f}"
                 for r, t in zip(roots, tips))
    return f'<path d="{d}" stroke="#000" stroke-width="1.1" stroke-linecap="round"/>'


BROWS = {  # stage: (angle, lift) per eyebrow, from Eyebrow.angle / Eyebrow.lift
    "calm": lambda right: (0, 0),
    "curious": lambda right: (8, -5) if right else (0, 0),
    "concerned": lambda right: (18, 1),
    "alarmed": lambda right: (-10, -5),
    "meltdown": lambda right: (-28, -6),
    "recovered": lambda right: (-6, -4),
}


def eyebrow(x, stage, right):
    angle, lift = BROWS[stage](right)
    deg = -angle if right else angle
    h = 3.2 if stage == "meltdown" else 2.5
    cy = 26 + lift
    return (f'<rect x="{x - 5}" y="{cy - h / 2}" width="10" height="{h}" rx="{h / 2}" fill="{MANE}" '
            f'transform="rotate({deg} {x} {cy})"/>')


def mouth(stage):
    s = f'stroke="{MANE}" stroke-width="1.8" stroke-linecap="round" fill="none"'
    if stage == "calm":
        return f'<path d="M25 73.5 Q32 78.5 39 73.5" {s}/>'
    if stage == "curious":
        return f'<rect x="27" y="75.1" width="10" height="1.8" rx="0.9" fill="{MANE}"/>'
    if stage == "concerned":
        return f'<rect x="24" y="75.1" width="16" height="1.8" rx="0.9" fill="{MANE}"/>'
    if stage == "alarmed":
        return f'<ellipse cx="32" cy="76" rx="4" ry="5" fill="{MANE}"/>'
    if stage == "meltdown":
        pts = " L".join(f"{23 + 18 * i / 24:.2f} {76 + 2 * math.sin(i / 24 * 6 * math.pi):.2f}" for i in range(25))
        return f'<path d="M{pts}" {s}/>'
    return f'<path d="M22 71.5 L42 71.5 Q32 87.7 22 71.5 Z" fill="{MANE}"/>'  # recovered grin


def teardrop(x, y, w, h):
    r = w / 2
    cy = y + h - r
    return (f"M{x + r} {y} Q{x + w} {y + r} {x + w} {cy} A{r} {r} 0 0 1 {x} {cy} "
            f"Q{x} {y + r} {x + r} {y} Z")


def red_flag():
    pole = f'<rect x="0.2" y="5" width="1.8" height="54" rx="0.9" fill="#595959"/>'
    steps, x0, w, y0, y1 = 16, -13.5, 14, 6, 16
    def y(i, edge):
        from_pole = (steps - i) / steps
        return edge + math.sin(from_pole * 2 * math.pi) * 1.4 * from_pole
    top = [f"{x0 + w * i / steps:.2f} {y(i, y0):.2f}" for i in range(steps + 1)]
    bottom = [f"{x0 + w * i / steps:.2f} {y(i, y1):.2f}" for i in range(steps, -1, -1)]
    return pole + f'<path d="M{" L".join(top + bottom)} Z" fill="#FF3B30"/>'


def accessories(stage):
    out = ""
    if stage in ("curious", "concerned"):
        label = f"? {SAMPLE_UNVERIFIED[stage]}"
        out += (f'<rect x="-2" y="5" width="24" height="14" rx="7" fill="#FF9500" stroke="#fff" '
                f'stroke-opacity="0.8" stroke-width="0.8"/>'
                f'<text x="10" y="15.4" text-anchor="middle" font-family="ui-rounded, -apple-system, Helvetica, sans-serif" '
                f'font-size="10" font-weight="900" fill="#fff">{label}</text>')
    if stage in ("alarmed", "meltdown"):
        out += red_flag()
        out += f'<path d="{teardrop(54, 22.5, 6, 9)}" fill="#8CCCFF" stroke="#fff" stroke-opacity="0.9" stroke-width="0.6"/>'
    if stage == "meltdown":
        for cx, side in ((25, -1), (39, 1)):
            for p in (0, 1 / 3, 2 / 3):
                out += (f'<circle cx="{cx + side * p * 28:.2f}" cy="{60 + p * 5:.2f}" r="{(3 + p * 7) / 2:.2f}" '
                        f'fill="#DBDBDB" stroke="#808080" stroke-width="0.6" opacity="{(1 - p) * 0.9:.2f}"/>')
        out += ('<g transform="rotate(-3 27 -9)"><rect x="-3" y="-15.5" width="60" height="13" rx="2.5" fill="#8C1414" '
                'stroke="#fff" stroke-width="0.7"/><text x="27" y="-6.4" text-anchor="middle" '
                'font-family="ui-rounded, -apple-system, Helvetica, sans-serif" font-size="7.5" font-weight="900" '
                'fill="#fff" letter-spacing="0.3">START FRESH?</text></g>')
    return out


def heat_badge(heat):
    w = 16 if heat < 10 else 22
    return (f'<rect x="{78 - w}" y="-2" width="{w}" height="15" rx="7.5" fill="#000" fill-opacity="0.7"/>'
            f'<text x="{78 - w / 2}" y="9.2" text-anchor="middle" font-family="ui-rounded, -apple-system, Helvetica, sans-serif" '
            f'font-size="11" font-weight="800" fill="#fff">{heat}</text>')


def horse(character, stage):
    mia = character == "mia"
    coat, muzzle, inner = palette(stage, mia)
    outline, op = (rgb(0.93, 0.70, 0.84), 1) if mia else ("#000", 0.22)
    body = ears(coat, inner, outline, op) + head(coat, outline, op)
    body += (horn() + mia_mane()) if mia else mamu_mane()
    body += f'<ellipse cx="32" cy="68" rx="21" ry="14" fill="{muzzle}"/>'
    body += "".join(f'<ellipse cx="{x}" cy="66" rx="2.5" ry="3.5" fill="{MANE}" fill-opacity="0.8"/>' for x in (22.5, 41.5))
    body += mouth(stage)
    if mia:
        body += "".join(f'<ellipse cx="{x}" cy="48" rx="4" ry="2.5" fill="#FF738C" fill-opacity="0.45"/>' for x in (16, 48))
    for x, right in ((16.5, False), (47.5, True)):
        body += eye(x, stage, right, coat)
        if mia:
            body += lashes(x, right)
    body += "".join(eyebrow(x, stage, right) for x, right in ((18, False), (46, True)))
    if mia:
        body += star(17, 2, 5) + star(47, -4, 6) + star(52, 9, 4)
    return body


def svg(body, title, view_box="0 -10 64 96"):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" role="img">'
            f"<title>{title}</title>{body}</svg>\n")


def stage_svg(character, stage):
    body = horse(character, stage) + accessories(stage) + heat_badge(SAMPLE_HEAT[stage])
    if stage == "curious":  # head tilt away from the heat badge
        body = f'<g transform="rotate(-7 32 84)">{body}</g>'
    # Peek up from the floor (y = 84) by the stage's visible height; the viewBox clips the rest.
    body = f'<g transform="translate(0 {84 - VISIBLE[stage]})">{body}</g>'
    return svg(body, f"{character.title()}, {stage}", view_box="-18 -22 100 106")


for name in ("mamu", "mia"):
    (OUT / f"{name}.svg").write_text(svg(horse(name, "calm"), name.title()))
    (OUT / "stages").mkdir(exist_ok=True)
    for stage in STAGES:
        (OUT / "stages" / f"{name}-{stage}.svg").write_text(stage_svg(name, stage))
print("wrote portraits and", len(STAGES) * 2, "stage SVGs to", OUT)
