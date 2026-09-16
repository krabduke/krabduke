#!/usr/bin/env python3
"""
Generates the SVG plates used by the profile README.

Each project card embeds its image as a data URI rather than linking it. An SVG
loaded through <img> cannot fetch external files, and embedding is what lets a
card carry its own title block at a fixed height instead of two stacked
full-width images.

    python3 tools/make_assets.py
"""

import base64
import os
import random

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG = "#070C1E"
GRID = "#101A3A"
GRIDF = "#0C142C"
INK = "#E9EFFC"
MUTED = "#8698C4"
FAINT = "#6B7EAD"
ACCENT = "#4D8DF6"
LINE = "#1B2A52"

CARDS = [
    {
        "sheet": "01",
        "name": "MODEL-GALLERY",
        "hook": "Spools wind up, then the afterburner lights.",
        "figures": [("MACHINES", "4"), ("AIRFOILS", "2,044"), ("SOURCE", "1 spec file")],
        "asset": "assets/f110.gif",
        "img_w": 560,
        "h": 230,
        "fit": "slice",
        "region_bg": "#070C1E",
    },
    {
        "sheet": "02",
        "name": "POLYMARKET-BTC-SCALPER",
        "hook": "A stop that filled at 67¢ instead of 80¢.",
        "figures": [("TRADES", "1,062"), ("WIN RATE", "87.75%"), ("NET P&L", "+$373.76")],
        "asset": "assets/curve.png",
        "img_w": 780,
        "h": 232,
        "fit": "meet",
        "region_bg": "#1F1F1F",
    },
]


MIME = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".gif": "image/gif"}


def data_uri(rel_path):
    ext = os.path.splitext(rel_path)[1].lower()
    with open(os.path.join(HERE, rel_path), "rb") as fh:
        return f"data:{MIME[ext]};base64," + base64.b64encode(fh.read()).decode("ascii")


def esc(text):
    """Card copy is hand-written, so a bare & in a label would break the XML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


STAR = "#C9DBFF"


def starfield(rng, count, x0, x1, y0, y1, max_op=0.6, twinkle=0, spikes=0):
    """Deterministic star field.

    Every star carries a base opacity attribute, so the field still renders if
    the animation never runs -- the hero rule was invisible for three commits
    because its only visible state came from an animation.
    """
    out = []
    for i in range(count):
        cx, cy = rng.uniform(x0, x1), rng.uniform(y0, y1)
        r = rng.uniform(0.5, 1.5)
        op = rng.uniform(0.10, max_op)
        anim = ""
        if i < twinkle:
            anim = (f'<animate attributeName="opacity" '
                    f'values="{op:.2f};{op * 0.3:.2f};{op:.2f}" '
                    f'dur="{rng.uniform(3.5, 9.0):.1f}s" '
                    f'begin="{rng.uniform(0, 4.5):.1f}s" repeatCount="indefinite"/>')
        star = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{STAR}" opacity="{op:.2f}">{anim}</circle>'
        if i < spikes:
            arm = r * 5.5
            star = (f'<g opacity="{min(op * 2.1, 0.85):.2f}">'
                    f'<line x1="{cx - arm:.1f}" y1="{cy:.1f}" x2="{cx + arm:.1f}" y2="{cy:.1f}" stroke="{STAR}" stroke-width="0.35"/>'
                    f'<line x1="{cx:.1f}" y1="{cy - arm:.1f}" x2="{cx:.1f}" y2="{cy + arm:.1f}" stroke="{STAR}" stroke-width="0.35"/>'
                    f'</g>{star}')
        out.append("  " + star)
    return "\n".join(out)


# --------------------------------------------------------------------- cover

def cover():
    W, H = 1200, 160
    stars = starfield(random.Random(11), 150, 40, W - 30, 8, H - 8,
                      max_op=0.62, twinkle=20, spikes=4)
    m, L = 9, 12
    marks = ""
    for x, y, dx, dy in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        marks += (f'  <path d="M{x + dx * m} {y} H{x + dx * (m + L)}'
                  f' M{x} {y + dy * m} V{y + dy * (m + L)}" stroke="{LINE}" stroke-width="1" fill="none"/>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="krabduke — robotics, AI, market microstructure">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#04070F"/></linearGradient>
    <pattern id="g1" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
    <pattern id="g2" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1E3A78" stop-opacity="0.5"/><stop offset="1" stop-color="#1E3A78" stop-opacity="0"/></linearGradient>
    <linearGradient id="rule" gradientUnits="userSpaceOnUse" x1="74" y1="0" x2="620" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="0.7" stop-color="{ACCENT}" stop-opacity="0.15"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#g2)"/>
  <rect width="{W}" height="{H}" fill="url(#g1)"/>
  <ellipse cx="210" cy="80" rx="300" ry="95" fill="url(#glow)" filter="url(#soft)"><animate attributeName="opacity" values="0.75;1;0.75" dur="12s" repeatCount="indefinite"/></ellipse>
  <g>
{stars}
  </g>
{marks}  <rect x="0" y="0" width="1.5" height="{H}" fill="{ACCENT}" opacity="0.2"><animate attributeName="x" values="-10;1210" dur="12s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.24;0.24;0" keyTimes="0;0.1;0.8;1" dur="12s" repeatCount="indefinite"/></rect>
  <g font-family="{MONO}">
    <text x="72" y="80" fill="{INK}" font-size="58" letter-spacing="7" font-weight="600">KRABDUKE</text>
    <line x1="74" y1="102" x2="620" y2="102" stroke="url(#rule)" stroke-width="2" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" from="100" to="0" dur="1.8s" begin="0.3s" fill="freeze"/></line>
    <text x="74" y="124" fill="{MUTED}" font-size="13.5" letter-spacing="2.4">ROBOTICS · AI · MARKET MICROSTRUCTURE</text>
  </g>
</svg>
'''


# ---------------------------------------------------------------- project card

def card(spec):
    W = 1200
    IMG_W, H = spec["img_w"], spec["h"]
    uri = data_uri(spec["asset"])
    stars = starfield(random.Random(20 + int(spec["sheet"])), 26,
                      IMG_W + 12, W - 12, 8, H - 8, max_op=0.26)
    x_text = IMG_W + 40
    available = 1176 - x_text
    # The two cards carry different image widths, so the copy has to fit
    # whatever column is left rather than assume a fixed one.
    name_font = min(25, (available * 0.96) / (len(spec["name"]) * 0.70))
    hook_font = min(13.5, (available * 0.96) / (len(spec["hook"]) * 0.52))
    figures = spec["figures"]
    cw = available / len(figures)

    cells = ""
    for i, (label, value) in enumerate(figures):
        x = x_text + i * cw
        if i:
            cells += f'    <line x1="{x - 16:.0f}" y1="176" x2="{x - 16:.0f}" y2="216" stroke="{LINE}" stroke-width="1"/>\n'
        cells += (f'    <text x="{x:.0f}" y="184" fill="{FAINT}" font-size="8.5" letter-spacing="1.6">{esc(label)}</text>\n'
                  f'    <text x="{x:.0f}" y="210" fill="{INK}" font-size="17" letter-spacing="0.4">{esc(value)}</text>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Sheet {spec["sheet"]}, {esc(spec["name"])}: {esc(spec["hook"])}">
  <defs>
    <pattern id="g" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern>
    <clipPath id="clip"><rect x="0" y="0" width="{IMG_W}" height="{H}"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <rect x="0" y="0" width="{IMG_W}" height="{H}" fill="{spec["region_bg"]}"/>
  <g clip-path="url(#clip)">
    <image x="0" y="0" width="{IMG_W}" height="{H}" preserveAspectRatio="xMidYMid {spec["fit"]}" xlink:href="{uri}"/>
  </g>
  <g>
{stars}
  </g>
  <line x1="{IMG_W}" y1="0" x2="{IMG_W}" y2="{H}" stroke="{LINE}" stroke-width="1"/>
  <line x1="0" y1="0.5" x2="{W}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
  <line x1="0" y1="{H - 0.5}" x2="{W}" y2="{H - 0.5}" stroke="{LINE}" stroke-width="1"/>
  <rect x="{x_text - 12}" y="46" width="3" height="44" fill="{ACCENT}"/>
  <g font-family="{MONO}">
    <text x="{x_text}" y="56" fill="{FAINT}" font-size="9" letter-spacing="1.8">SHEET {spec["sheet"]}</text>
    <text x="{x_text}" y="90" fill="{INK}" font-size="{name_font:.1f}" letter-spacing="2.4">{esc(spec["name"])}</text>
    <text x="{x_text}" y="122" fill="{MUTED}" font-size="{hook_font:.1f}">{esc(spec["hook"])}</text>
    <line x1="{x_text}" y1="156" x2="1176" y2="156" stroke="{LINE}" stroke-width="1"/>
{cells}  </g>
</svg>
'''


# ------------------------------------------------------------------- footer

def footer():
    w, h = 1200, 40
    stars = starfield(random.Random(31), 22, 24, w - 24, 4, h - 4, max_op=0.30)
    ticks = "".join(f'<line x1="{x}" y1="{h - 10}" x2="{x}" y2="{h - 4}" stroke="{LINE}" stroke-width="1"/>'
                    for x in range(24, w - 24, 24))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Standard library only. Tested. Documented.">
  <rect width="{w}" height="{h}" fill="{BG}"/>
{stars}
  <line x1="0" y1="0.5" x2="{w}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
{ticks}
  <text x="{w / 2}" y="20" fill="{FAINT}" font-size="10" letter-spacing="3.4" text-anchor="middle" font-family="{MONO}">STANDARD LIBRARY ONLY · TESTED · DOCUMENTED</text>
</svg>
'''


def main():
    files = {"hero.svg": cover(), "footer.svg": footer()}
    for i, spec in enumerate(CARDS, start=1):
        files[f"card-{i:02d}.svg"] = card(spec)
    for name, svg in files.items():
        with open(os.path.join(HERE, name), "w") as fh:
            fh.write(svg)
        print(f"  {name:16} {len(svg) / 1024:7.1f} KB")


if __name__ == "__main__":
    main()