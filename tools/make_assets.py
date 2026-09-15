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

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(HERE, "assets")

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG = "#0B1412"
GRID = "#12201C"
GRIDF = "#0F1A17"
INK = "#E9F2EE"
MUTED = "#7E918B"
FAINT = "#54665F"
ACCENT = "#4FA98A"
LINE = "#1C2E29"

CARDS = [
    {
        "sheet": "01",
        "name": "MODEL-GALLERY",
        "hook": "Four machines, each generated in Blender from one specification file.",
        "figures": [("MACHINES", "4"), ("AIRFOILS", "2,044"), ("SOURCE", "1 spec file")],
        "asset": "assets/render.jpg",
        "fit": "slice",
        "region_bg": "#010102",
    },
    {
        "sheet": "02",
        "name": "POLYMARKET-BTC-SCALPER",
        "hook": "1,062 trades, 87.75% won — and a stop that filled at 67¢ instead of 80¢.",
        "figures": [("TRADES", "1,062"), ("WIN RATE", "87.75%"), ("NET P&L", "+$373.76")],
        "asset": "assets/curve.png",
        "fit": "slice",
        "region_bg": "#1F1F1F",
    },
]


def data_uri(rel_path, mime):
    with open(os.path.join(HERE, rel_path), "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode("ascii")


def esc(text):
    """Card copy is hand-written, so a bare & in a label would break the XML."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# --------------------------------------------------------------------- cover

def cover():
    W, H = 1200, 160
    m, L = 9, 12
    marks = ""
    for x, y, dx, dy in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        marks += (f'  <path d="M{x + dx * m} {y} H{x + dx * (m + L)}'
                  f' M{x} {y + dy * m} V{y + dy * (m + L)}" stroke="{LINE}" stroke-width="1" fill="none"/>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Keenan Casalegno — robotics, AI, market microstructure">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#070C0B"/></linearGradient>
    <pattern id="g1" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
    <pattern id="g2" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1E5C49" stop-opacity="0.5"/><stop offset="1" stop-color="#1E5C49" stop-opacity="0"/></linearGradient>
    <linearGradient id="rule" gradientUnits="userSpaceOnUse" x1="74" y1="0" x2="620" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="0.7" stop-color="{ACCENT}" stop-opacity="0.15"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#g2)"/>
  <rect width="{W}" height="{H}" fill="url(#g1)"/>
  <ellipse cx="210" cy="80" rx="300" ry="95" fill="url(#glow)" filter="url(#soft)"><animate attributeName="opacity" values="0.75;1;0.75" dur="12s" repeatCount="indefinite"/></ellipse>
{marks}  <rect x="0" y="0" width="1.5" height="{H}" fill="{ACCENT}" opacity="0.2"><animate attributeName="x" values="-10;1210" dur="12s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.24;0.24;0" keyTimes="0;0.1;0.8;1" dur="12s" repeatCount="indefinite"/></rect>
  <g font-family="{MONO}">
    <text x="72" y="72" fill="{INK}" font-size="42" letter-spacing="6" font-weight="600">KEENAN</text>
    <text x="72" y="114" fill="{INK}" font-size="42" letter-spacing="6" font-weight="600" opacity="0.38">CASALEGNO</text>
    <line x1="74" y1="130" x2="620" y2="130" stroke="url(#rule)" stroke-width="2" pathLength="100" stroke-dasharray="100" stroke-dashoffset="0"><animate attributeName="stroke-dashoffset" from="100" to="0" dur="1.8s" begin="0.3s" fill="freeze"/></line>
    <text x="74" y="148" fill="{MUTED}" font-size="13.5" letter-spacing="2.4">ROBOTICS · AI · MARKET MICROSTRUCTURE</text>
    <text x="74" y="26" fill="#3A4A44" font-size="9.5" letter-spacing="2.8">KRABDUKE</text>
  </g>
</svg>
'''


# ---------------------------------------------------------------- project card

def card(spec):
    W, H, IMG_W = 1200, 230, 560
    uri = data_uri(spec["asset"], "image/jpeg" if spec["asset"].endswith(".jpg") else "image/png")
    x_text = 600
    figures = spec["figures"]
    cw = (1176 - x_text) / len(figures)

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
  <line x1="{IMG_W}" y1="0" x2="{IMG_W}" y2="{H}" stroke="{LINE}" stroke-width="1"/>
  <line x1="0" y1="0.5" x2="{W}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
  <line x1="0" y1="{H - 0.5}" x2="{W}" y2="{H - 0.5}" stroke="{LINE}" stroke-width="1"/>
  <rect x="{x_text - 12}" y="46" width="3" height="44" fill="{ACCENT}"/>
  <g font-family="{MONO}">
    <text x="{x_text}" y="56" fill="{FAINT}" font-size="9" letter-spacing="1.8">SHEET {spec["sheet"]}</text>
    <text x="{x_text}" y="90" fill="{INK}" font-size="25" letter-spacing="2.4">{esc(spec["name"])}</text>
    <text x="{x_text}" y="122" fill="{MUTED}" font-size="13.5">{esc(spec["hook"])}</text>
    <line x1="{x_text}" y1="156" x2="1176" y2="156" stroke="{LINE}" stroke-width="1"/>
{cells}  </g>
</svg>
'''


# ------------------------------------------------------------------- footer

def footer():
    w, h = 1200, 40
    ticks = "".join(f'<line x1="{x}" y1="{h - 10}" x2="{x}" y2="{h - 4}" stroke="{LINE}" stroke-width="1"/>'
                    for x in range(24, w - 24, 24))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Standard library only. Tested. Documented.">
  <rect width="{w}" height="{h}" fill="{BG}"/>
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