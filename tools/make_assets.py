#!/usr/bin/env python3
"""
Generates the SVG plates used by the profile README.

The blade sections on the cover and the detail sheet are drawn with the same
formulae as engine/airfoil.py in f110-turbofan: NACA 4-digit half-thickness
(with the -0.1036 closing coefficient) over a parabolic mid-chord camber line,
plus the leading-edge radius boost applied above 10% thickness. Names and
parameters come from the BladeRow entries in engine/spec.py, so nothing here is
decoration -- if a number changes there, change it here too.

    python3 tools/make_assets.py
"""

import math
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG = "#0B1412"
GRID = "#12201C"
GRIDF = "#0F1A17"
INK = "#E9F2EE"
MUTED = "#7E918B"
FAINT = "#54665F"
ACCENT = "#4FA98A"
PULSE = "#8FE3BE"
LINE = "#1C2E29"

# Straight out of engine/spec.py. Rows that omit thickness/camber take the
# BladeRow defaults: thickness 0.08, camber 0.06.
ROWS = [
    ("IGV", "inlet guide vane", 0.05, 0.03),
    ("HPC R1", "compressor rotor", 0.08, 0.06),
    ("HPT NGV", "turbine nozzle guide vane", 0.16, 0.14),
]


def naca_thickness(xc, tc):
    if xc < 0.0:
        xc = 0.0
    return 5.0 * tc * (0.2969 * math.sqrt(xc) - 0.1260 * xc - 0.3516 * xc ** 2
                       + 0.2843 * xc ** 3 - 0.1036 * xc ** 4)


def camber_line(xc, mc):
    return 4.0 * mc * xc * (1.0 - xc), 4.0 * mc * (1.0 - 2.0 * xc)


def le_boost_for(tc):
    return 1.8 if tc > 0.10 else 1.0


def section_points(n_pts, tc, mc, boost=1.0):
    n_half = n_pts // 2 + 1
    xs = [0.5 * (1.0 - math.cos(math.pi * i / (n_half - 1))) for i in range(n_half)]
    upper, lower = [], []
    for xc in xs:
        yt = naca_thickness(xc, tc)
        if xc < 0.05 and boost != 1.0:
            yt *= 1.0 + (boost - 1.0) * (1.0 - xc / 0.05)
        yc, dyc = camber_line(xc, mc)
        th = math.atan(dyc)
        st, ct = math.sin(th), math.cos(th)
        upper.append((xc - yt * st, yc + yt * ct))
        lower.append((xc + yt * st, yc - yt * ct))
    return list(reversed(upper)) + lower[1:-1]


def path_d(pts):
    return "M" + "L".join(f"{x:.2f},{y:.2f}" for x, y in pts)


def ref_points(tc, mc, n=400):
    """Upper and lower surface plus the max-thickness station, at unit chord."""
    up, lo = [], []
    for i in range(n + 1):
        xc = i / n
        yt = naca_thickness(xc, tc)
        if xc < 0.05:
            yt *= 1.0 + (le_boost_for(tc) - 1.0) * (1.0 - xc / 0.05)
        yc, dyc = camber_line(xc, mc)
        th = math.atan(dyc)
        st, ct = math.sin(th), math.cos(th)
        up.append((xc - yt * st, yc + yt * ct))
        lo.append((xc + yt * st, yc - yt * ct))
    xc_t = max((i / n for i in range(n + 1)), key=lambda v: naca_thickness(v, tc))
    return up, lo, xc_t


# --------------------------------------------------------------------- cover

def cover():
    W, H = 1200, 320
    datum, scale = 1130, 2.30
    sw = 1.25 / scale
    bands = [(96, 0.52), (160, 0.74), (224, 0.95)]

    solid, pulses, labels = [], [], []
    for (name, _, tc, mc), (yt_center, opacity) in zip(ROWS, bands):
        pts = section_points(72, tc, mc, le_boost_for(tc))
        vs = [v for _, v in pts]
        tx = datum - 100 * scale
        ty = yt_center - scale * (min(vs) + max(vs)) / 2
        d = path_d([(u * 100, v * 100) for u, v in pts])
        xf = f"translate({tx:.2f},{ty:.2f}) scale({scale})"
        solid.append(f'    <g transform="{xf}">\n      <path d="{d}" opacity="{opacity}"/>\n    </g>')
        pulses.append(
            f'    <g transform="{xf}">\n'
            f'      <path d="{d}" pathLength="100" stroke-dasharray="7 93" stroke-dashoffset="100"'
            f' opacity="{min(1.0, opacity + 0.25):.2f}" stroke-width="{sw * 1.6:.3f}">\n'
            f'        <animate attributeName="stroke-dashoffset" from="100" to="0" dur="6s"'
            f' begin="{len(pulses) * 1.1}s" repeatCount="indefinite"/>\n'
            f'      </path>\n    </g>')
        labels.append(f'    <text x="{datum + 12}" y="{yt_center + 3:.0f}" fill="#4A5D56"'
                      f' font-size="9.5" letter-spacing="1.4">{name}</text>')

    m, L = 10, 14
    marks = ""
    for x, y, dx, dy in [(0, 0, 1, 1), (W, 0, -1, 1), (0, H, 1, -1), (W, H, -1, -1)]:
        marks += (f'  <path d="M{x + dx * m} {y} H{x + dx * (m + L)}'
                  f' M{x} {y + dy * m} V{y + dy * (m + L)}" stroke="{LINE}" stroke-width="1" fill="none"/>\n')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Keenan Casalegno. Parametric CAD, market microstructure, systems. Three blade sections from the F110 turbofan, drawn to their real thickness and camber.">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BG}"/><stop offset="1" stop-color="#070C0B"/></linearGradient>
    <pattern id="g1" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="{GRID}" stroke-width="1"/></pattern>
    <pattern id="g2" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern>
    <linearGradient id="glow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#1E5C49" stop-opacity="0.5"/><stop offset="1" stop-color="#1E5C49" stop-opacity="0"/></linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{ACCENT}"/><stop offset="0.7" stop-color="{ACCENT}" stop-opacity="0.15"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></linearGradient>
    <filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="26"/></filter>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#g2)"/>
  <rect width="{W}" height="{H}" fill="url(#g1)"/>
  <ellipse cx="200" cy="160" rx="300" ry="130" fill="url(#glow)" filter="url(#soft)"><animate attributeName="opacity" values="0.75;1;0.75" dur="12s" repeatCount="indefinite"/></ellipse>
{marks}  <line x1="{datum}" y1="52" x2="{datum}" y2="264" stroke="{LINE}" stroke-width="1" stroke-dasharray="2 5"/>
  <g fill="none" stroke="{ACCENT}" stroke-width="{sw:.3f}" stroke-linejoin="round" stroke-linecap="round">
{chr(10).join(solid)}
  </g>
  <g fill="none" stroke="{PULSE}" stroke-linejoin="round" stroke-linecap="round">
{chr(10).join(pulses)}
  </g>
{chr(10).join(labels)}
  <rect x="0" y="0" width="1.5" height="{H}" fill="{ACCENT}" opacity="0.2"><animate attributeName="x" values="-10;1210" dur="12s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;0.24;0.24;0" keyTimes="0;0.1;0.8;1" dur="12s" repeatCount="indefinite"/></rect>
  <g font-family="{MONO}">
    <text x="72" y="140" fill="{INK}" font-size="54" letter-spacing="7" font-weight="600">KEENAN</text>
    <text x="72" y="202" fill="{INK}" font-size="54" letter-spacing="7" font-weight="600" opacity="0.38">CASALEGNO</text>
    <line x1="74" y1="232" x2="580" y2="232" stroke="url(#rule)" stroke-width="2" pathLength="100" stroke-dasharray="100"><animate attributeName="stroke-dashoffset" from="100" to="0" dur="1.8s" begin="0.3s" fill="freeze"/></line>
    <text x="74" y="264" fill="{MUTED}" font-size="14" letter-spacing="2.5">PARAMETRIC CAD · MARKET MICROSTRUCTURE · SYSTEMS</text>
    <text x="74" y="46" fill="#3A4A44" font-size="10" letter-spacing="3">KRABDUKE</text>
    <text x="{W - 72}" y="46" fill="#3A4A44" font-size="10" letter-spacing="3" text-anchor="end">SHEET 00 · 2026</text>
  </g>
</svg>
'''


# ------------------------------------------------------------- title blocks

def title_block(sheet, name, figures):
    w, h = 1200, 78
    x0, cw = 596, 194
    cells = ""
    for i, (label, value) in enumerate(figures):
        x = x0 + i * cw
        if i:
            cells += f'  <line x1="{x}" y1="14" x2="{x}" y2="{h - 14}" stroke="{LINE}" stroke-width="1"/>\n'
        cells += (f'  <text x="{x + 16}" y="33" fill="{FAINT}" font-size="8.5" letter-spacing="1.7">{label}</text>\n'
                  f'  <text x="{x + 16}" y="58" fill="{INK}" font-size="16" letter-spacing="0.5">{value}</text>\n')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Sheet {sheet}, {name}">
  <defs><pattern id="g" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern></defs>
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <rect width="{w}" height="{h}" fill="url(#g)"/>
  <line x1="0" y1="0.5" x2="{w}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
  <line x1="0" y1="{h - 0.5}" x2="{w}" y2="{h - 0.5}" stroke="{LINE}" stroke-width="1"/>
  <rect x="24" y="18" width="4" height="42" fill="{ACCENT}"/>
  <text x="44" y="33" fill="{FAINT}" font-size="8.5" letter-spacing="1.7">SHEET {sheet}</text>
  <text x="44" y="58" fill="{INK}" font-size="19" letter-spacing="3" font-family="{MONO}">{name}</text>
  <line x1="580" y1="14" x2="580" y2="{h - 14}" stroke="{LINE}" stroke-width="1"/>
{cells}</svg>
'''


# ------------------------------------------------------------- detail sheet

def arrow_h(x, y, direction, size=5.0):
    return f'<path d="M{x} {y} l{direction * size} -{size * 0.5} l0 {size} z" fill="{ACCENT}"/>'


def arrow_v(x, y, direction, size=5.0):
    return f'<path d="M{x} {y} l-{size * 0.5} {direction * size} l{size} 0 z" fill="{ACCENT}"/>'


def detail():
    W = 1200
    panels_x = [26, 424, 822]
    panel_w = 352
    chord_px = 296
    chord_y = 268

    geom = []
    for (name, subtitle, tc, mc), x0 in zip(ROWS, panels_x):
        pts = section_points(200, tc, mc, le_boost_for(tc))
        up, lo, xc_t = ref_points(tc, mc)
        geom.append({
            "name": name, "subtitle": subtitle, "tc": tc, "mc": mc, "x0": x0,
            "poly": [(x0 + u * chord_px, chord_y - v * chord_px) for u, v in pts],
            "camber": "".join(f"{x0 + i / 40 * chord_px:.1f},"
                              f"{chord_y - camber_line(i / 40, mc)[0] * chord_px:.1f} " for i in range(41)),
            "x_t": x0 + xc_t * chord_px,
            "y_top": chord_y - max(v for _, v in up) * chord_px,
            "y_bot": chord_y - min(v for _, v in lo) * chord_px,
        })

    # One dimension line for all three, set below the deepest section, so the
    # chord stays directly comparable across the row.
    dim_y = max(g["y_bot"] for g in geom) + 32

    body = []
    for g in geom:
        x0, chord = g["x0"], chord_px
        body.append(f'''  <g>
    <text x="{x0}" y="138" fill="{INK}" font-size="21" letter-spacing="2.6" font-family="{MONO}">{g["name"]}</text>
    <text x="{x0}" y="161" fill="{FAINT}" font-size="14" letter-spacing="1.2">{g["subtitle"]}</text>
    <text x="{x0 + panel_w}" y="138" fill="{ACCENT}" font-size="14" letter-spacing="1.2" text-anchor="end" font-family="{MONO}">t {g["tc"] * 100:.0f}% · m {g["mc"] * 100:.0f}%</text>
    <line x1="{x0}" y1="{chord_y}" x2="{x0 + chord}" y2="{chord_y}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>
    <polygon points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in g["poly"])}" fill="{ACCENT}" fill-opacity="0.10" stroke="{ACCENT}" stroke-width="1.4" stroke-linejoin="round"/>
    <polyline points="{g["camber"]}" fill="none" stroke="{PULSE}" stroke-width="1" stroke-dasharray="3 3" opacity="0.7"/>
    <line x1="{g["x_t"]}" y1="{g["y_top"]}" x2="{g["x_t"]}" y2="{g["y_bot"]}" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="2 3"/>
    {arrow_v(g["x_t"], g["y_top"], -1)}{arrow_v(g["x_t"], g["y_bot"], 1)}
    <line x1="{x0}" y1="{dim_y}" x2="{x0 + chord}" y2="{dim_y}" stroke="{ACCENT}" stroke-width="1"/>
    {arrow_h(x0, dim_y, 1)}{arrow_h(x0 + chord, dim_y, -1)}
    <line x1="{x0}" y1="{dim_y - 8}" x2="{x0}" y2="{chord_y + 6}" stroke="{LINE}" stroke-width="1"/>
    <line x1="{x0 + chord}" y1="{dim_y - 8}" x2="{x0 + chord}" y2="{chord_y + 6}" stroke="{LINE}" stroke-width="1"/>
    <text x="{x0 + chord / 2}" y="{dim_y - 10}" fill="{MUTED}" font-size="14" text-anchor="middle" font-family="{MONO}">chord = 1.000</text>
  </g>''')

    legend_y = dim_y + 46
    legend = f'''  <g font-family="{MONO}" font-size="12" letter-spacing="1.1">
    <line x1="26" y1="{legend_y}" x2="70" y2="{legend_y}" stroke="{LINE}" stroke-width="1" stroke-dasharray="4 4"/>
    <text x="82" y="{legend_y + 4}" fill="{FAINT}">CHORD LINE</text>
    <line x1="240" y1="{legend_y}" x2="284" y2="{legend_y}" stroke="{PULSE}" stroke-width="1" stroke-dasharray="3 3" opacity="0.7"/>
    <text x="296" y="{legend_y + 4}" fill="{FAINT}">MEAN CAMBER LINE</text>
    <line x1="500" y1="{legend_y}" x2="544" y2="{legend_y}" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="2 3"/>
    {arrow_v(500, legend_y, -1, 4.5)}{arrow_v(544, legend_y, -1, 4.5)}
    <text x="556" y="{legend_y + 4}" fill="{FAINT}">MAX THICKNESS STATION</text>
  </g>
  <text x="26" y="{legend_y + 30}" fill="{FAINT}" font-size="12" letter-spacing="1.1" font-family="{MONO}">TRAILING EDGE CLOSED AT −0.1036 · LEADING-EDGE RADIUS ×1.8 ABOVE t 10% · 2,044 AIRFOILS ACROSS 99 PARTS</text>'''

    H = legend_y + 48
    ticks = "".join(f'<line x1="{x}" y1="{H - 12}" x2="{x}" y2="{H - 6}" stroke="{LINE}" stroke-width="1"/>'
                    for x in range(26, W - 24, 24))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Detail sheet: three blade sections from the F110 turbofan drawn to their real thickness and camber.">
  <defs><pattern id="g" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M10 0H0V10" fill="none" stroke="{GRIDF}" stroke-width="0.6"/></pattern></defs>
  <rect width="{W}" height="{H}" fill="{BG}"/>
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <line x1="0" y1="0.5" x2="{W}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
  <rect x="26" y="36" width="4" height="38" fill="{ACCENT}"/>
  <text x="46" y="53" fill="{FAINT}" font-size="10" letter-spacing="1.7">DETAIL · SHEET 03</text>
  <text x="46" y="78" fill="{INK}" font-size="18" letter-spacing="2.4" font-family="{MONO}">BLADE SECTIONS, DRAWN TO SCALE</text>
  <text x="{W - 26}" y="53" fill="{FAINT}" font-size="11" letter-spacing="1.4" text-anchor="end" font-family="{MONO}">engine/spec.py → engine/airfoil.py</text>
  <text x="{W - 26}" y="78" fill="{FAINT}" font-size="11" letter-spacing="1.4" text-anchor="end" font-family="{MONO}">NACA THICKNESS · MID-CHORD PARABOLIC CAMBER</text>
  <line x1="26" y1="100" x2="{W - 26}" y2="100" stroke="{LINE}" stroke-width="1"/>
{chr(10).join(body)}
{legend}
{ticks}
</svg>
'''


# ------------------------------------------------------------------- footer

def footer():
    w, h = 1200, 46
    ticks = "".join(f'<line x1="{x}" y1="{h - 14}" x2="{x}" y2="{h - 6}" stroke="{LINE}" stroke-width="1"/>'
                    for x in range(24, w - 24, 24))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Standard library only. Tested. Documented.">
  <rect width="{w}" height="{h}" fill="{BG}"/>
  <line x1="0" y1="0.5" x2="{w}" y2="0.5" stroke="{LINE}" stroke-width="1"/>
{ticks}
  <text x="{w / 2}" y="24" fill="{FAINT}" font-size="10" letter-spacing="3.4" text-anchor="middle" font-family="{MONO}">STANDARD LIBRARY ONLY · TESTED · DOCUMENTED</text>
</svg>
'''


def main():
    files = {
        "hero.svg": cover(),
        "strip-01.svg": title_block("01", "MODEL-GALLERY",
                                    [("MACHINES", "4"), ("AIRFOILS", "2,044"), ("SOURCE", "1 spec file")]),
        "strip-02.svg": title_block("02", "POLYMARKET-BTC-SCALPER",
                                    [("TRADES", "1,062"), ("WIN RATE", "87.75%"), ("NET P&amp;L", "+$373.76")]),
        "sheet-03.svg": detail(),
        "footer.svg": footer(),
    }
    for name, svg in files.items():
        with open(os.path.join(HERE, name), "w") as fh:
            fh.write(svg)
        print(f"  {name:16} {len(svg):>7} bytes")


if __name__ == "__main__":
    main()