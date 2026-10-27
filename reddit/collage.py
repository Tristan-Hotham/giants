"""r/dataisbeautiful collage for Giants in the Landscape. Run from this folder: python3 collage.py
Every number comes from ../data/results.json and the CSV files in ../data/.
Fonts: FONT_DIR with FrauncesVar.ttf, IBMPlexMono-Regular.ttf, IBMPlexMono-Medium.ttf, SourceSerif4-Regular.ttf.
"""
import json, os
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly, Ellipse
from pyproj import Transformer
import shapely
from shapely.geometry import shape, box

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HIST = os.environ.get("HIST", os.path.dirname(ROOT))
F = os.environ.get("FONT_DIR", "/tmp/claude-0/-home-claude/c232619d-81e0-53f3-9de6-41e973630753/scratchpad/fonts/")
for f in ["FrauncesVar.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf", "SourceSerif4-Regular.ttf", "SourceSerif4-Semibold.ttf", "SourceSerif4-It.ttf"]:
    fm.fontManager.addfont(os.path.join(F, f))
DISP = fm.FontProperties(fname=os.path.join(F, "FrauncesVar.ttf"), weight=900)
SER, MONO = "Source Serif 4", "IBM Plex Mono"
BG, FG, MUT, LAND, EDGE = "#F4F6EE", "#17231B", "#55685A", "#DCE7D2", "#B9CBB0"
HOT, GOLD, VIO, TURF, BAND, BLUE, TEAL = "#B03F27", "#A0720E", "#5B4A8C", "#3D7438", "#A3B39C", "#2E5F86", "#1F6E62"
R = json.load(open(os.path.join(ROOT, "data", "results.json"))); T = R["tests"]
TB = pd.read_csv(os.path.join(ROOT, "data", "irish_tombs.csv"))
GP = pd.read_csv(os.path.join(ROOT, "data", "giant_places.csv"), keep_default_na=False)
LG = pd.read_csv(os.path.join(ROOT, "data", "legends.csv"))
TR = Transformer.from_crs(4326, 3035, always_xy=True)
ne = json.load(open(os.path.join(HIST, "_data3", "ne", "geojson", "ne_10m_land.geojson")))
clip = box(-11, 49.8, 2.0, 61.0)
land = shapely.union_all([shape(f["geometry"]).intersection(clip) for f in ne["features"] if shape(f["geometry"]).intersects(clip)]).simplify(0.004)
polys = []
for p in shapely.get_parts(land):
    if p.geom_type != "Polygon" or p.area < 0.0004: continue
    if p.centroid.x > -2.0 and p.centroid.y < 51.0: continue
    c = np.array(p.exterior.coords); x, y = TR.transform(c[:, 0], c[:, 1]); polys.append(np.c_[x, y])
pct = lambda v: f"{v*100:.0f}%"

fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BG)

# ---- chalk giant on a turf hill (top right) ----
gx = fig.add_axes([0.80, 0.86, 0.17, 0.115]); gx.set_xlim(0, 100); gx.set_ylim(0, 60); gx.axis("off")
t = np.linspace(0, 100, 200); gx.fill_between(t, 0, 16 + 22 * np.sin(np.pi * t / 100) ** 1.5, color=TURF, lw=0)
W = dict(color="white", lw=4.2, solid_capstyle="round", solid_joinstyle="round")
gx.add_patch(Ellipse((50, 33.5), 6.5, 6.5, fill=False, ec="white", lw=4.2))
gx.plot([50, 50], [30, 18], **W); gx.plot([50, 41, 40], [27, 21, 15], **W); gx.plot([50, 59, 61, 61], [27, 28, 34, 40], **W)
gx.plot([50, 45], [18, 7], **W); gx.plot([50, 55], [18, 7], **W); gx.plot([59.5, 62.5], [42, 40], **W)

# ---- title ----
fig.text(0.04, 0.972, "Giants in the landscape", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(0.04, 0.917, "Did people explain big things with big people?", family=SER, fontsize=21, color=HOT, va="top", style="italic")
fig.text(0.04, 0.884, f"Giant's Grave, Giant's Chair, Giant's Causeway, Giant Hill: {R['n_places']:,} giant-named places in Britain\n"
         f"and Ireland, all {R['n_tombs']:,} Irish megalithic tombs with their old Ordnance Survey map names and\n"
         f"{R['n_legends']} giant legends, each measured against ordinary places and monuments of the same kind nearby.", family=SER, fontsize=13.2, color=FG, va="top", linespacing=1.38)

# ---- hero map ----
ax = fig.add_axes([0.0, 0.295, 0.58, 0.52]); ax.set_facecolor(BG)
for P in polys: ax.add_patch(MPoly(P, closed=True, fc=LAND, ec=EDGE, lw=0.6))
rest = TB[~TB.name_class.isin(["giant", "dermot", "druid"])]
x, y = TR.transform(rest.lon.values, rest.lat.values); ax.scatter(x, y, s=3.2, c="#B3C1AC", lw=0, rasterized=True)
for k, c, s_ in (("druid", VIO, 9), ("dermot", GOLD, 11), ("giant", HOT, 17)):
    q = TB[TB.name_class == k]; x, y = TR.transform(q.lon.values, q.lat.values)
    ax.scatter(x, y, s=s_, c=c, lw=0.35, ec="white", zorder=4, rasterized=True)
o = GP[GP.source != "Irish SMR (OS map name)"]; x, y = TR.transform(o.lon.values, o.lat.values)
ax.scatter(x, y, s=22, c=TURF, lw=0.6, ec="white", zorder=5)
x, y = TR.transform(LG.lon.values, LG.lat.values); ax.scatter(x, y, s=95, facecolors="none", edgecolors=FG, lw=1.3, zorder=6)
allp = np.concatenate(polys); ax.set_xlim(allp[:, 0].min() - 15000, allp[:, 0].max() + 15000); ax.set_ylim(allp[:, 1].min() - 10000, allp[:, 1].max() + 10000)
ax.set_aspect("equal"); ax.axis("off")
def ann(lon, lat, tx, ty, s, ha="left"):
    X, Y = TR.transform(lon, lat); ax.annotate(s, xy=(X, Y), xytext=(tx, ty), textcoords="axes fraction", family=MONO, fontsize=10, color=FG, ha=ha,
                                               arrowprops=dict(arrowstyle="-", color=FG, lw=0.8))
ann(-8.45, 54.25, 0.02, 0.70, f"Sligo: {R['tomb_counties']['Sligo']['giant']} Giant's Graves")
ann(-9.0, 52.9, 0.0, 0.10, f"Clare: {R['tomb_counties']['Clare']['dermot']} Dermot and\nGrania beds, {R['tomb_counties']['Clare']['giant']} giants")
ann(-6.5117, 55.2408, 0.30, 0.60, "Giant's Causeway")
# legend
lx = fig.add_axes([0.035, 0.705, 0.28, 0.085]); lx.axis("off"); lx.set_xlim(0, 1); lx.set_ylim(0, 1)
items = [(HOT, f"Giant's Grave or Bed  {R['n_tombs_giant']}", 70), (GOLD, f"Dermot and Grania's Bed  {R['tomb_name_counts']['dermot']}", 55),
         (VIO, f"Druid's Altar  {R['tomb_name_counts']['druid']}", 45), ("#B3C1AC", "other Irish tombs", 30), (TURF, "other giant places", 60), (None, f"giant legends  {R['n_legends']}", 95)]
for i, (c, l, s_) in enumerate(items):
    yy = 1 - i * 0.2
    if c: lx.scatter([0.03], [yy], s=s_, c=c, ec="white", lw=0.4, clip_on=False)
    else: lx.scatter([0.03], [yy], s=s_, facecolors="none", edgecolors=FG, lw=1.3, clip_on=False)
    lx.text(0.09, yy, l, family=MONO, fontsize=10, va="center", color=FG)

# ---- big numbers ----
tx = fig.add_axes([0.60, 0.31, 0.38, 0.49]); tx.axis("off"); tx.set_xlim(0, 1); tx.set_ylim(0, 1)
cs = R["tomb_class_share"]
notes = [(f"{R['n_tombs_giant']}", HOT, f"Irish tombs are called Giant's Grave or Bed\non the Ordnance Survey maps: {pct(R['giant_share_named'])} of\nall named tombs, and mostly in the north."),
         (f"{pct(cs['court tomb']['giant_share'])} v. {pct(cs['passage tomb']['giant_share'])}", HOT, "of court tombs v. passage tombs are giants'.\nNewgrange, Knowth and Carrowkeel, the most\nfamous, are a Tumulus, a Moat and Carn."),
         (f"{pct(T['tomb_named']['high']['match']['obs'])} v. {pct(T['tomb_named']['high']['match']['base'])}", HOT, "of Giant's Graves v. other named tombs\nnearby sit on a local high point. The giant's\ntomb is not the big one."),
         (f"{pct(T['names']['any_1']['match']['obs'])} v. {pct(T['names']['any_1']['match']['base'])}", TURF, "of British giant names v. matched ordinary\nnames lie within 1 km of a prehistoric\nmonument. Giants stick to the ancient.")]
for (big, c, small), y in zip(notes, [0.99, 0.73, 0.47, 0.21]):
    tx.text(0, y, big, fontproperties=DISP, fontsize=34, color=c, va="top")
    tx.text(0, y - 0.085, small, family=SER, fontsize=12.2, color=FG, va="top", linespacing=1.3)

# ---- small multiples ----
fig.text(0.04, 0.272, "Who gets the tomb?", fontproperties=DISP, fontsize=17, color=FG)
fig.text(0.37, 0.272, "Is the giant's tomb higher?", fontproperties=DISP, fontsize=17, color=FG)
fig.text(0.70, 0.272, "Near old monuments?", fontproperties=DISP, fontsize=17, color=FG)
a1 = fig.add_axes([0.11, 0.128, 0.22, 0.13], facecolor=BG)
order = ["passage tomb", "portal tomb", "structure", "wedge tomb", "unclassified", "court tomb"]
vals = [cs[k]["giant_share"] for k in order]
a1.barh(range(6), vals, color=HOT, height=0.68)
for i, v in enumerate(vals): a1.text(v + 0.006, i, pct(v), va="center", family=MONO, fontsize=10, color=FG)
a1.set_yticks(range(6)); a1.set_yticklabels([k.replace(" tomb", "") for k in order], family=MONO, fontsize=10.5)
a1.set_xlim(0, 0.25); a1.set_xticks([])
a1.set_xlabel("share of each kind of tomb\ncalled a Giant's Grave", family=MONO, fontsize=9.5, color=MUT)
a2 = fig.add_axes([0.47, 0.128, 0.19, 0.13], facecolor=BG)
h = T["tomb_named"]["high"]["match"]; ha_ = T["tomb_all"]["high"]["match"]
lab = ["Giant's\nGraves", "other\nnamed", "all\nother"]; v = [h["obs"], h["base"], ha_["base"]]
a2.barh([2, 1, 0], v, color=[HOT, BAND, BAND], height=0.66)
for yv, (lo, hi) in ((1, (h["base_lo"], h["base_hi"])), (0, (ha_["base_lo"], ha_["base_hi"]))): a2.plot([lo, hi], [yv, yv], color=FG, lw=1.2)
for i, val in zip([2, 1, 0], v): a2.text(max(val, 0.02) + 0.012 + (0.05 if i < 2 else 0), i, pct(val), va="center", family=MONO, fontsize=10, color=FG)
a2.set_yticks([2, 1, 0]); a2.set_yticklabels(lab, family=MONO, fontsize=10); a2.set_xlim(0, 0.42); a2.set_xticks([])
a2.set_xlabel("share on a local high point\n(above 75% of ground within 1 km)", family=MONO, fontsize=9.5, color=MUT)
a3 = fig.add_axes([0.80, 0.128, 0.17, 0.13], facecolor=BG)
n1 = T["names"]["any_1"]
v = [n1["match"]["obs"], n1["match"]["base"], n1["rand"]["base"]]
a3.barh([2, 1, 0], v, color=[TURF, BAND, "#C9D3C3"], height=0.66)
for yv, (lo, hi) in ((1, (n1["match"]["base_lo"], n1["match"]["base_hi"])), (0, (n1["rand"]["base_lo"], n1["rand"]["base_hi"]))): a3.plot([lo, hi], [yv, yv], color=FG, lw=1.2)
for i, val in zip([2, 1, 0], v): a3.text(val + 0.012 + (0.11 if i < 2 and i != 2 else 0), i, pct(val), va="center", family=MONO, fontsize=10, color=FG)
a3.set_yticks([2, 1, 0]); a3.set_yticklabels(["giant\nnames", "matched\nnames", "random\nland"], family=MONO, fontsize=10); a3.set_xlim(0, 0.5); a3.set_xticks([])
a3.set_xlabel("within 1 km, Great Britain", family=MONO, fontsize=9.5, color=MUT)
for a in (a1, a2, a3):
    for k in ("top", "right", "left"): a.spines[k].set_visible(False)
    a.spines["bottom"].set_color(MUT); a.tick_params(length=0, colors=FG)
fig.text(0.04, 0.08, "Grey bars: matched controls of the same kind from the same 50 km square; lines: 95% range of 2,000 random draws. Terrain shows prominence,\n"
         "not monument size, which no open record gives. Names are matched by word only and say nothing about when or why a place was named.", family=MONO, fontsize=9, color=MUT, va="top", linespacing=1.4)

# ---- footer ----
fig.add_artist(plt.Line2D([0.04, 0.96], [0.051, 0.051], color=FG, lw=1.2))
fig.text(0.04, 0.045, "Sources: National Monuments Service, Sites and Monuments Record (CC BY 4.0); OS Open Names, contains OS data © Crown copyright 2026 (OGL v3);\n"
         "OpenStreetMap (ODbL); Wikidata (CC0); Atlas of Hillforts of Britain and Ireland (CC BY-SA 4.0); Wikipedia (CC BY-SA 4.0); AWS Terrain Tiles; Natural Earth.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib.  Interactive: tristan-hotham.github.io/giants", family=MONO, fontsize=8.6, color=FG, va="top", linespacing=1.4)
out = os.path.join(HERE, "giants_in_the_landscape.png")
fig.savefig(out, dpi=200, facecolor=BG)
print("written", out)
