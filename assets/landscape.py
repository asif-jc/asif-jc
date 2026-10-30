"""Generates the animated footer scene: hills, a lake and a lit cabin, night in dark mode, day in light.

Run `python3 assets/landscape.py` from the repo root after editing; it rewrites both SVGs.
Landscape layers use the contribution-grid greens, darkest-to-brightest from far to near,
so the scene reads as built from the same palette as the snake above it.
"""

import math
import random
from pathlib import Path

W, H = 850, 240
HORIZON = 168  # lake surface

THEMES = {
    "dark": {
        "layers": ["#01311f", "#034525", "#0f6d31"],
        "fern": "#00c647",
        "lake": "#0b1a14",
        "shimmer": "#3d6b55",
        "cabin": "#0a1f15",
        "window": "#f2b45a",
        "night": True,
    },
    "light": {
        "layers": ["#9be9a8", "#40c463", "#30a14e"],
        "fern": "#216e39",
        "lake": "#d6efe0",
        "shimmer": "#ffffff",
        "cabin": "#1f4d2e",
        "window": "#f2b45a",
        "night": False,
    },
}


def ridge(rng, base, amp, step, jagged):
    """Closed path for one hill layer; jagged=True gives alpine peaks, False gives rolling hills."""
    pts = [(x, base - rng.uniform(0.3, 1.0) * amp) for x in range(-20, W + 2 * step, step)]
    d = f"M{pts[0][0]},{H} L{pts[0][0]},{pts[0][1]:.1f}"
    if jagged:
        d += "".join(f" L{x},{y:.1f}" for x, y in pts[1:])
    else:
        # Quadratic segments through midpoints keep the curve smooth without a spline library.
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            d += f" Q{x0},{y0:.1f} {(x0 + x1) / 2:.1f},{(y0 + y1) / 2:.1f}"
    return d + f" L{pts[-1][0]},{H} Z"


def frond(x0, y0, length, lean, colour):
    """A fern frond ending in a koru: curvature grows toward the tip so it rolls into a spiral."""
    n = 60
    theta0 = math.radians(-90 + 12 * lean)
    pts, x, y = [], x0, y0
    for i in range(n):
        t = i / n
        theta = theta0 + lean * (math.radians(60) * t + math.radians(300) * t**6)
        ds = length / n * (1 - 0.75 * t)
        x += ds * math.cos(theta)
        y += ds * math.sin(theta)
        pts.append((x, y, theta))
    stem = "M" + " L".join(f"{px:.1f},{py:.1f}" for px, py, _ in [(x0, y0, 0)] + pts)
    leaves = []
    for i in range(3, int(n * 0.72), 3):
        px, py, th = pts[i]
        size = 16 * (1 - i / n) ** 0.8
        for side in (1, -1):
            a = th + side * math.radians(70) - lean * math.radians(15)
            leaves.append(f"M{px:.1f},{py:.1f} l{size * math.cos(a):.1f},{size * math.sin(a):.1f}")
    return (
        f'<path d="{stem}" stroke="{colour}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        f'<path d="{" ".join(leaves)}" stroke="{colour}" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
    )


def build(theme):
    t = THEMES[theme]
    rng = random.Random(7)  # fixed seed so both themes share the same geography
    far = ridge(rng, 120, 55, 34, jagged=True)
    mid = ridge(rng, 150, 30, 70, jagged=False)
    # One continuous foreground that dips into a valley; the lake is then laid into the dip.
    near = (f"M-10,{H} L-10,150 Q90,140 170,152 Q230,162 270,{HORIZON} L600,{HORIZON} "
            f"Q660,160 740,150 Q810,144 860,140 L860,{H} Z")
    lake = f"M250,{HORIZON} L620,{HORIZON} C600,200 520,222 435,222 C350,222 270,200 250,{HORIZON} Z"

    sky = []
    if t["night"]:
        for i in range(55):
            sx, sy = rng.uniform(0, W), rng.uniform(4, 100)
            sky.append(
                f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="{rng.uniform(0.5, 1.3):.1f}" fill="#e6edf3" '
                f'class="star" style="animation-delay:-{rng.uniform(0, 6):.1f}s;animation-duration:{rng.uniform(3, 7):.1f}s"/>'
            )
        sky.append(
            '<g transform="translate(640 42)"><circle r="26" fill="#e6edf3" opacity=".06"/>'
            '<circle r="13" fill="#e6edf3" opacity=".9" mask="url(#crescent)"/></g>'
            '<line x1="0" y1="0" x2="46" y2="14" stroke="url(#trail)" stroke-width="1.4" class="meteor"/>'
        )
    else:
        sky.append(
            '<g transform="translate(640 44)"><circle r="30" fill="#f2cc60" opacity=".15"/>'
            '<circle r="15" fill="#f2cc60" opacity=".85"/></g>'
        )
        for i, (by, dur, delay) in enumerate([(40, 48, 0), (52, 56, 18), (34, 64, 33)]):
            sky.append(
                f'<g class="bird" style="animation-duration:{dur}s;animation-delay:-{delay}s">'
                f'<path transform="translate(0 {by})" stroke="#57606a" stroke-width="1.3" fill="none">'
                f'<animate attributeName="d" dur="{0.9 + 0.2 * i:.1f}s" repeatCount="indefinite" '
                'values="M0,0 q4,-4 8,0 q4,-4 8,0;M0,0 q4,3 8,0 q4,3 8,0;M0,0 q4,-4 8,0 q4,-4 8,0"/></path></g>'
            )
    cloud_fill, cloud_op = ("#30363d", ".35") if t["night"] else ("#d0d7de", ".55")
    for cy, dur, delay, s in [(30, 140, 20, 1.0), (62, 180, 95, 0.7)]:
        sky.append(
            f'<g class="cloud" style="animation-duration:{dur}s;animation-delay:-{delay}s" fill="{cloud_fill}" opacity="{cloud_op}">'
            f'<g transform="translate(0 {cy}) scale({s})"><ellipse cx="0" cy="0" rx="34" ry="8"/>'
            '<ellipse cx="-12" cy="-6" rx="16" ry="8"/><ellipse cx="10" cy="-8" rx="18" ry="9"/></g></g>'
        )

    shimmer = "".join(
        f'<line x1="{x:.0f}" y1="{y:.0f}" x2="{x + rng.uniform(10, 26):.0f}" y2="{y:.0f}" stroke="{t["shimmer"]}" '
        f'stroke-width="1" class="ripple" style="animation-delay:-{rng.uniform(0, 5):.1f}s"/>'
        for x, y in ((rng.uniform(320, 540), rng.uniform(HORIZON + 5, 210)) for _ in range(16))
    )
    # The cabin sits on the left shore; its light spills onto the water as a warm streak.
    cabin = (
        f'<g transform="translate(206 140)" fill="{t["cabin"]}">'
        '<rect x="0" y="0" width="34" height="20"/><path d="M-4,1 L17,-15 L38,1 Z"/>'
        '<rect x="25" y="-14" width="5" height="9"/>'
        f'<rect x="9" y="6" width="7" height="7" fill="{t["window"]}" class="window"/></g>'
        f'<rect x="258" y="{HORIZON + 4}" width="26" height="1.5" fill="{t["window"]}" opacity=".45" class="window"/>'
    )
    if t["night"]:
        cabin += (
            '<g class="smoke" fill="#8b949e"><circle cx="233" cy="118" r="3"/>'
            '<circle cx="236" cy="110" r="4" style="animation-delay:-1.5s"/></g>'
        )
    flies = ""
    if t["night"]:
        flies = "".join(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="1.6" fill="#7ee787" filter="url(#glow)" class="fly" '
            f'style="animation-delay:-{rng.uniform(0, 8):.1f}s;animation-duration:{rng.uniform(6, 10):.1f}s"/>'
            for x, y in [(rng.choice([rng.uniform(20, 280), rng.uniform(580, 830)]), rng.uniform(140, 215)) for _ in range(12)]
        )

    ferns = []
    for x, length, lean, dur in [(34, 190, 1, 7), (66, 150, 1, 8.5), (14, 120, -1, 6.5),
                                 (816, 195, -1, 7.5), (786, 145, -1, 9), (838, 115, 1, 6)]:
        ferns.append(
            f'<g class="sway" style="transform-origin:{x}px {H}px;animation-duration:{dur}s">'
            + frond(x, H, length, lean, t["fern"]) + "</g>"
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<!-- Generated by assets/landscape.py; edit that, not this. -->
<defs>
  <mask id="crescent"><circle r="13" fill="#fff"/><circle cx="6" cy="-4" r="11" fill="#000"/></mask>
  <linearGradient id="trail"><stop offset="0" stop-color="#e6edf3" stop-opacity="0"/><stop offset="1" stop-color="#e6edf3"/></linearGradient>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<style>
  .star {{ animation: twinkle ease-in-out infinite alternate; }}
  @keyframes twinkle {{ from {{ opacity: .15 }} to {{ opacity: .9 }} }}
  .cloud, .bird {{ animation: drift linear infinite; }}
  @keyframes drift {{ from {{ transform: translateX(-80px) }} to {{ transform: translateX({W + 80}px) }} }}
  .meteor {{ opacity: 0; animation: meteor 11s ease-out infinite 3s; }}
  @keyframes meteor {{ 0%, 90% {{ opacity: 0; transform: translate(80px, 10px) }} 92% {{ opacity: 1 }} 100% {{ opacity: 0; transform: translate(260px, 64px) }} }}
  .ripple {{ animation: ripple 5s ease-in-out infinite; }}
  @keyframes ripple {{ 0%, 100% {{ opacity: 0; transform: translateX(0) }} 50% {{ opacity: .55; transform: translateX(6px) }} }}
  .window {{ animation: flicker 4s ease-in-out infinite; }}
  @keyframes flicker {{ 0%, 100% {{ opacity: 1 }} 45% {{ opacity: .8 }} 60% {{ opacity: .95 }} }}
  .smoke circle {{ animation: smoke 4s ease-out infinite; }}
  @keyframes smoke {{ from {{ opacity: .35; transform: translate(0, 0) }} to {{ opacity: 0; transform: translate(6px, -22px) }} }}
  .fly {{ animation: fly ease-in-out infinite alternate; }}
  @keyframes fly {{ 0% {{ opacity: .1; transform: translate(0, 0) }} 50% {{ opacity: 1 }} 100% {{ opacity: .2; transform: translate(8px, -10px) }} }}
  .sway {{ animation: sway ease-in-out infinite alternate; }}
  @keyframes sway {{ from {{ transform: rotate(-1.8deg) }} to {{ transform: rotate(1.8deg) }} }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; }} }}
</style>
{"".join(sky)}
<path d="{far}" fill="{t["layers"][0]}"/>
<path d="{mid}" fill="{t["layers"][1]}"/>
<path d="{near}" fill="{t["layers"][2]}"/>
<path d="{lake}" fill="{t["lake"]}"/>
{shimmer}
{cabin}
{flies}
{"".join(ferns)}
</svg>
"""


if __name__ == "__main__":
    here = Path(__file__).parent
    for theme in THEMES:
        (here / f"landscape-{theme}.svg").write_text(build(theme))
