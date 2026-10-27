"""Step 5. Render ../header.png (1200x630 social card) with Playwright Chromium.

Land outline: Natural Earth 1:10m land (public domain), clipped to Britain and Ireland.
Fonts: set FONT_DIR to a folder holding FrauncesVar.ttf, SourceSerif4-Regular.ttf and IBMPlexMono-Regular.ttf
(from github.com/google/fonts); otherwise system serif fonts are used.
Usage: FONT_DIR=/path/to/fonts python3 code/05_header.py
"""
import json, math, os
import numpy as np, shapely
from shapely.geometry import shape, box
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HIST = os.environ.get("HIST", os.path.dirname(ROOT))
S = json.load(open(os.path.join(ROOT, "work", "site.json")))
R = json.load(open(os.path.join(ROOT, "data", "results.json")))
FD = os.environ.get("FONT_DIR", "")
proj = lambda lat, lon: (lon * math.cos(math.radians(54.5)), -lat)
ne = json.load(open(os.path.join(HIST, "_data3", "ne", "geojson", "ne_10m_land.geojson")))
clip = box(-10.8, 49.8, 2.0, 59.0)
land = shapely.union_all([shape(f["geometry"]).intersection(clip) for f in ne["features"] if shape(f["geometry"]).intersects(clip)]).simplify(0.01)
x0, y0 = proj(59.0, -10.8); x1, y1 = proj(49.8, 2.0)
H, PAD = 600, 14
sc = (H - 2 * PAD) / (y1 - y0)
P = lambda p: ((p[0] - x0) * sc + PAD, (p[1] - y0) * sc + PAD)
W = (x1 - x0) * sc + 2 * PAD
path = ""
for pg_ in shapely.get_parts(land):
    if pg_.geom_type != "Polygon" or pg_.area < 0.003: continue
    pts = [P(proj(la, lo)) for lo, la in np.array(pg_.exterior.coords)]
    path += "M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z"
tomb = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8"/>' for x, y in (P(proj(r[0], r[1])) for r in S["tombs"] if r[2] == 0))
oth = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3"/>' for x, y in (P(proj(r[0], r[1])) for r in S["places"] if r[4] != "Irish SMR (OS map name)"))
legs = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#17231B"/><circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="#17231B" stroke-width="1.3"/>' for x, y in (P(proj(r[0], r[1])) for r in S["leg"]))
ff = ""
if FD:
    ff = "".join(f"@font-face{{font-family:'{n}';src:url('file://{FD}/{f}');font-weight:{w};}}" for n, f, w in [
        ("Fraunces", "FrauncesVar.ttf", "100 900"), ("Source Serif 4", "SourceSerif4-Regular.ttf", "400"), ("IBM Plex Mono", "IBMPlexMono-Regular.ttf", "400")])
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>{ff}
body{{margin:0;width:1200px;height:630px;background:#F4F6EE;color:#17231B;overflow:hidden;position:relative;font-family:'Source Serif 4',Georgia,serif}}
.k{{position:absolute;left:70px;top:62px;font:400 15px/1 'IBM Plex Mono',monospace;letter-spacing:.14em;text-transform:uppercase;color:#4F6352;display:flex;gap:12px;align-items:center}}
.k b{{background:#B03F27;color:#fff;padding:7px 9px;font-weight:400}}
h1{{position:absolute;left:64px;top:104px;margin:0;font:900 112px/.88 Fraunces,Georgia,serif;letter-spacing:-.02em}}
h1 em{{font-style:normal;color:#B03F27;display:block}}
p{{position:absolute;left:70px;top:380px;width:600px;margin:0;font-size:26px;line-height:1.36}}
.f{{position:absolute;left:70px;bottom:40px;font:400 14px/1 'IBM Plex Mono',monospace;letter-spacing:.12em;text-transform:uppercase;color:#4F6352}}
.rule{{position:absolute;left:70px;right:560px;top:358px;border-top:3px double #3D7438}}
svg{{position:absolute;right:40px;top:15px}}
</style></head><body>
<div class="k"><b>Data study</b><span>Folklore × landscape</span></div>
<h1>Giants in the<em>landscape</em></h1>
<div class="rule"></div>
<p>{R['n_tombs_giant']} Irish Giant's Graves, {R['gb_names']['n']} British giant names and {R['n_legends']} legends. Giants own graves, not mountains, and the giant's tomb is not the big one.</p>
<div class="f">Dr Tristan Hotham · Independent researcher</div>
<svg width="{W:.0f}" height="{H}" viewBox="0 0 {W:.0f} {H}"><path d="{path}" fill="#DCE7D2" stroke="#A9BDA0" stroke-width="1"/><g fill="#B03F27" fill-opacity=".85">{tomb}</g><g fill="#3D7438" stroke="#F4F6EE" stroke-width=".8">{oth}</g>{legs}</svg>
</body></html>"""
tmp = os.path.join(ROOT, "work", "header.html")
open(tmp, "w").write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1200, "height": 630})
    pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(ROOT, "header.png")); b.close()
os.remove(tmp)
print("header.png written")
