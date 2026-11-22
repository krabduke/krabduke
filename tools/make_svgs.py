"""Generate interests.svg (ASCII icon tiles) and terminal.svg (typed-out readout).

    python tools/make_svgs.py
"""
import os
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INK, LINE, GOLD, BONE, DIM, FAINT = "#08080C", "#2A251C", "#C9A56B", "#F1E7D2", "#8A8070", "#5A5448"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# (label, description for the terminal, icon)
INTERESTS = [
    ("robotics", "things that move", r"""
          (_)==[>
          //
         //
   _____//___
  |   (o)    |
  |__________|
 ==============
"""),
    ("ai", "things that think", r"""
  o         o
  |\       /|
  o-o-----o-o
  |/ \   / \|
  o   o-o   o
  |\ /   \ /|
  o-o-----o-o
"""),
    ("markets", "order books, microstructure", r"""
              |
         |   [#]
    |   [#]   |
   [ ]   |   [ ]   |
   [ ]       |    [#]
    |              |
 ___________________
"""),
    ("games", "co-op, strange, in the browser", r"""
   _____________
  /   _      o  \
 |  _| |_  o   o |
 | |_   _|   o   |
 |   |_|  _____  |
  \______/     \_/
"""),
    ("physics", "how any of it works", r"""
       .---.
    .-'  |  '-.
   /  .--+--.  \
  |  (  (@)  )  |
   \  '--+--'  /
    '-.  |  .-'
       '---'
"""),
]


def nb(t):
    # non-breaking spaces: renderers collapse normal spaces in SVG text
    return escape(t).replace(' ', '&#160;')


def icon_lines(icon):
    lines = icon.strip("\n").split("\n")
    return lines


def interests_svg():
    W, gap, H = 1200, 12, 215
    n = len(INTERESTS)
    tw = (W - gap * (n - 1)) / n
    fs, lh, cwf = 15, 17.5, 0.602  # monospace advance ~0.6em
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Interests: {", ".join(i[0] for i in INTERESTS)}">',
           f'<rect width="{W}" height="{H}" fill="{INK}"/>']
    for k, (label, _, icon) in enumerate(INTERESTS):
        x0 = k * (tw + gap)
        out.append(f'<rect x="{x0 + .5:.1f}" y=".5" width="{tw - 1:.1f}" height="{H - 1}" fill="{INK}" stroke="{LINE}"/>')
        lines = icon_lines(icon)
        wmax = max(len(l) for l in lines) * fs * cwf
        ix = x0 + (tw - wmax) / 2
        iy = 22 + (7 - len(lines)) * lh / 2
        out.append(f'<g font-family="{MONO}" font-size="{fs}" fill="{GOLD}" xml:space="preserve" style="white-space:pre">')
        for j, l in enumerate(lines):
            out.append(f'<text x="{ix:.1f}" y="{iy + j * lh + fs:.1f}">{nb(l)}</text>')
        out.append('</g>')
        out.append(f'<text x="{x0 + tw / 2:.1f}" y="{H - 26}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="17" fill="{BONE}">{escape(label)}</text>')
    out.append('</svg>')
    return "\n".join(out)


def terminal_svg():
    W, fs, lh, pad = 1200, 17, 28, 30
    prompt = [(GOLD, "krabduke"), (FAINT, "@"), (GOLD, "earth"), (FAINT, " ~ $ "), (BONE, "cat interests")]
    rows = [prompt]
    for label, desc, _ in INTERESTS:
        rows.append([(DIM, f"{label} ".ljust(18, ".") + " "), (BONE, desc)])
    rows.append([(FAINT, "~ $ ")])
    H = pad * 2 + lh * len(rows) - (lh - fs)
    cw = fs * 0.602
    step, typing = 0.42, 0.38
    css = f"""
.c{{animation:type {typing}s steps(28,end) both}}
.cur{{opacity:0;animation:blink 1.06s steps(1,end) infinite}}
@keyframes type{{from{{transform:translateX(0)}}to{{transform:translateX({W}px)}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion: reduce){{.c{{display:none}}.cur{{animation:none;opacity:1}}}}
"""
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
           f'aria-label="Interests: ' + "; ".join(f"{l}, {d}" for l, d, _ in INTERESTS) + '">',
           f'<style>{css}</style>',
           f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" fill="{INK}" stroke="{LINE}"/>',
           f'<g font-family="{MONO}" font-size="{fs}" xml:space="preserve" style="white-space:pre">']
    for i, parts in enumerate(rows):
        y = pad + i * lh + fs
        out.append(f'<text x="{pad}" y="{y}">' + "".join(
            f'<tspan fill="{c}">{nb(t)}</tspan>' for c, t in parts) + '</text>')
    out.append('</g>')
    # cover rects slide away left-to-right, one row after another: the typing reveal
    for i in range(len(rows)):
        y = pad + i * lh - 6
        out.append(f'<rect class="c" style="animation-delay:{0.3 + i * step:.2f}s" x="{pad - 2}" y="{y}" '
                   f'width="{W - pad}" height="{lh}" fill="{INK}"/>')
    last = len(rows) - 1
    cx = pad + len("~ $ ") * cw
    cy = pad + last * lh + 2
    out.append(f'<rect class="cur" style="animation-delay:{0.3 + last * step + typing:.2f}s" x="{cx:.1f}" '
               f'y="{cy}" width="{cw:.1f}" height="{fs + 3}" fill="{GOLD}"/>')
    out.append('</svg>')
    return "\n".join(out)


if __name__ == "__main__":
    for name, svg in (("interests.svg", interests_svg()), ("terminal.svg", terminal_svg())):
        with open(os.path.join(ROOT, name), "w") as f:
            f.write(svg + "\n")
        print("wrote", name)
