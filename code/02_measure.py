"""Step 2. Measure how "big" each place is, and how close it is to prehistoric monuments, and draw the controls.

"Big" here means prominent in the terrain, since none of the monument sources records a size (the Atlas of Hillforts
does record enclosed area, which is also used). From the elevation model (AWS Terrain Tiles, zoom 10, about 95 m
cells at these latitudes; reader in dem.py, from Within Sight):
  elev      ground height (m)
  tpi500    height above the mean of 16 points on a 500 m ring (m): positive = the place stands above its surroundings
  tpi1k     the same on a 1 km ring (m)
  pct1k     share of 64 points within 1 km (rings at 250, 500, 750 and 1,000 m) that lie lower than the place
  relief1k  highest minus lowest of those points and the place (m)
Points over the sea (height 0 in the model) are left out of the rings, so coastal places are compared with land only.

Distances (km, straight line on ETRS89 LAEA) from the GB names, their controls and the legends to the nearest
barrow or cairn, megalith (tombs, standing stones, circles and rows in OpenStreetMap), stone circle, hillfort, and the
nearest of any of these ("prehistoric monument").

Controls
  OS names: K ordinary OS Open Names features of the same local type from the same 50 km square (100 km, then the
            country, when fewer than 20), and K random points of land in the same square.
  Monuments: for each giant-named monument, K monuments of the same pool and type (Irish tombs by class; barrows by kind;
            megaliths by class; hillforts) from the same 50 km square, without a giant name. When fewer than 20 are
            available: the same type within 100 km, then any type of the pool within 50 km, then within 100 km, then the
            same type anywhere in the country.
            For Irish tombs a second set is drawn only from tombs that carry another name on the OS maps.
Writes ../work/measured.pkl.
Run: python3 code/02_measure.py
"""
import json, os, time
import numpy as np, pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
import shapely
from shapely.geometry import shape
from dem import DEM

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HIST = os.environ.get("HIST", os.path.dirname(ROOT))
WORK = os.path.join(ROOT, "work"); DATA = os.path.join(ROOT, "data")
K = 50
rng = np.random.default_rng(20261027)
TE = Transformer.from_crs(4326, 3035, always_xy=True); TI = Transformer.from_crs(3035, 4326, always_xy=True)
xy = lambda lon, lat: TE.transform(np.asarray(lon, float), np.asarray(lat, float))
t0 = time.time()
PO = pd.read_pickle(os.path.join(WORK, "pools.pkl"))
dem = DEM()

# ---------- terrain measures ----------
ANG = np.linspace(0, 2 * np.pi, 16, endpoint=False)


def ring(lat, lon, r):
    lat = np.asarray(lat, float)[:, None]; lon = np.asarray(lon, float)[:, None]
    dla = r * np.cos(ANG)[None] / 111320.0
    dlo = r * np.sin(ANG)[None] / (111320.0 * np.cos(np.radians(lat)))
    return dem.elev(lat + dla, lon + dlo)


def terrain(lat, lon):
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    out = {k: np.full(len(lat), np.nan) for k in ("elev", "tpi500", "tpi1k", "pct1k", "relief1k")}
    for i0 in range(0, len(lat), 20000):
        la, lo = lat[i0:i0 + 20000], lon[i0:i0 + 20000]
        z = dem.elev(la, lo)
        R = {r: ring(la, lo, r) for r in (250, 500, 750, 1000)}
        def m(a):
            a = np.where(a > 0, a, np.nan); ok = np.isfinite(a).sum(1) >= 4
            return np.where(ok, np.nanmean(a, 1), np.nan)
        allr = np.concatenate([R[r] for r in (250, 500, 750, 1000)], 1)
        land = allr > 0
        sl = slice(i0, i0 + len(la))
        out["elev"][sl] = z
        out["tpi500"][sl] = z - m(R[500])
        out["tpi1k"][sl] = z - m(R[1000])
        n = land.sum(1)
        out["pct1k"][sl] = np.where(n >= 8, ((allr < z[:, None]) & land).sum(1) / np.maximum(n, 1), np.nan)
        hi = np.nanmax(np.where(land, allr, np.nan), 1); lo_ = np.nanmin(np.where(land, allr, np.nan), 1)
        out["relief1k"][sl] = np.where(n >= 8, np.maximum(hi, z) - np.minimum(lo_, z), np.nan)
    for k in out:
        out[k][np.asarray(dem.elev(lat, lon)) <= 0] = np.nan if k != "elev" else 0
    return out


def add_terrain(df, lat="lat", lon="lon"):
    t = terrain(df[lat].values, df[lon].values)
    for k, v in t.items(): df[k] = v
    return df


tombs = add_terrain(PO["tombs"].reset_index(drop=True), "LATITUDE", "LONGITUDE")
B = add_terrain(PO["B"]); M = add_terrain(PO["M"]); H = add_terrain(PO["H"])
print("pools measured", round(time.time() - t0))

# ---------- GB prehistoric monument layers (for distances) ----------
gbB = B[B.country.eq("United Kingdom")]
gbM = M[M.country.eq("United Kingdom")]
S = PO["S"]; gbS = S[S.country.eq("United Kingdom")]
gbH = H[H.country.isin(["England", "Scotland", "Wales"])]
LAY = {k: np.c_[xy(d.lon.values, d.lat.values)] for k, d in (("barrow", gbB), ("megalith", gbM), ("circle", gbS), ("hillfort", gbH))}
LAY["any"] = np.concatenate(list(LAY.values()))
TREES = {k: cKDTree(v) for k, v in LAY.items()}


def dists(df):
    X = np.c_[df.x.values, df.y.values]
    for k, T in TREES.items():
        df[f"{k}_km"] = T.query(X)[0] / 1000
    return df


# ---------- OS names: points and controls ----------
os_ = pd.read_csv(os.path.join(HIST, "osnames_gb.tsv"), sep="\t", dtype=str, keep_default_na=False)
for c in ("lat", "lon"): os_[c] = os_[c].astype(float)
os_["fid"] = np.arange(len(os_))
os_["x"], os_["y"] = xy(os_.lon, os_.lat)
for s in (50000, 100000):
    os_[f"c{s//1000}"] = (os_.x // s).astype(int).astype(str) + "_" + (os_.y // s).astype(int).astype(str)
G = PO["G"]
pool = os_[~os_.fid.isin(G.fid)]
groups = {s: pool.groupby([f"c{s}", "local_type"]).indices for s in (50, 100)}
gc = pool.groupby(["country", "local_type"]).indices
cty = json.load(open(os.path.join(HIST, "how-roman-is-your-road", "data", "counties.geojson")))
land = shapely.union_all([shape(f["geometry"]) for f in cty["features"]]); shapely.prepare(land)
rows = []


def draw_os(r, kind, key):
    idx = None
    for s in (50, 100):
        ii = groups[s].get((r[f"c{s}"], r["local_type"]))
        if ii is not None and len(ii) >= 20:
            idx, st = ii, f"{s} km"; break
    if idx is None:
        idx, st = gc[(r["country"], r["local_type"])], "country"
    for j in rng.choice(idx, K, replace=len(idx) < K):
        q = pool.iloc[j]
        rows.append(dict(set="match", kind=kind, parent=key, name=q.name1, local_type=q.local_type, lat=q.lat, lon=q.lon, x=q.x, y=q.y, stratum=st))
    cx, cy = (r["x"] // 50000) * 50000, (r["y"] // 50000) * 50000
    got = []
    while len(got) < K:
        xs = cx + rng.random(400) * 50000; ys = cy + rng.random(400) * 50000
        lo, la = TI.transform(xs, ys)
        ok = shapely.contains_xy(land, lo, la)
        got += [(a, b, c, d) for a, b, c, d, o in zip(xs, ys, la, lo, ok) if o]
    for a, b, c, d in got[:K]:
        rows.append(dict(set="rand", kind=kind, parent=key, name="", local_type="", lat=c, lon=d, x=a, y=b, stratum="50 km"))
    return st


for r in G.itertuples():
    rr = os_.iloc[r.fid]
    st = draw_os(rr, "name", f"os_{r.fid}")
    rows.append(dict(set="obs", kind="name", parent=f"os_{r.fid}", name=r.name, local_type=r.local_type, lat=r.lat, lon=r.lon, x=rr.x, y=rr.y, stratum=st))
# legends in Great Britain: random land only (they are placed at many kinds of feature)
LG = pd.read_csv(os.path.join(DATA, "legends.csv"))
LG["x"], LG["y"] = xy(LG.lon, LG.lat)
for r in LG.itertuples():
    rows.append(dict(set="obs", kind="legend", parent=r.id, name=r.giant, local_type=r.os_local_type, lat=r.lat, lon=r.lon, x=r.x, y=r.y, stratum=""))
    if r.id == "causeway": continue
    cx, cy = (r.x // 50000) * 50000, (r.y // 50000) * 50000
    got = []
    while len(got) < K:
        xs = cx + rng.random(400) * 50000; ys = cy + rng.random(400) * 50000
        lo, la = TI.transform(xs, ys); ok = shapely.contains_xy(land, lo, la)
        got += [(a, b, c, d) for a, b, c, d, o in zip(xs, ys, la, lo, ok) if o]
    for a, b, c, d in got[:K]:
        rows.append(dict(set="rand", kind="legend", parent=r.id, name="", local_type="", lat=c, lon=d, x=a, y=b, stratum="50 km"))
PTS = pd.DataFrame(rows)
PTS = add_terrain(PTS)
PTS = dists(PTS)
print("os points", len(PTS), round(time.time() - t0))


# ---------- monument controls ----------
def draw_mon(df, typecol, giantcol="giant", cgroup=None, mask_ctrl=None):
    """Return {giant row index: array of K control row indices} for every giant row of df."""
    df = df.reset_index(drop=True)
    X, Y = xy(df.lon if "lon" in df else df.LONGITUDE, df.lat if "lat" in df else df.LATITUDE)
    c50 = (X // 50000).astype(int).astype(str) + "_" + (Y // 50000).astype(int).astype(str)
    c100 = (X // 100000).astype(int).astype(str) + "_" + (Y // 100000).astype(int).astype(str)
    ok = ~df[giantcol].values & np.isfinite(df.tpi1k.values)
    if mask_ctrl is not None: ok &= mask_ctrl
    out, strata = {}, {}
    for i in np.where(df[giantcol].values)[0]:
        t = df[typecol].values[i]
        idx = None
        T = df[typecol].values == t
        for nm, cell, same in (("50 km", c50, True), ("100 km", c100, True), ("50 km, any type", c50, False), ("100 km, any type", c100, False)):
            ii = np.where(ok & (cell == cell[i]) & (T if same else True))[0]
            if len(ii) >= 20: idx, st = ii, nm; break
        if idx is None:
            cg = (df[cgroup].values == df[cgroup].values[i]) if cgroup else True
            ii = np.where(ok & T & cg)[0]
            if len(ii) < 20: ii = np.where(ok & cg)[0]
            idx, st = ii, "country"
        out[i] = rng.choice(idx, K, replace=len(idx) < K); strata[i] = st
    return out, strata


tombs["cgroup"] = "IE"
named_other = tombs.nm_class.isin(["dermot", "druid", "other_named", "descriptive"]).values
CT = {}
CT["tomb_all"] = draw_mon(tombs, "tclass", cgroup="cgroup")
CT["tomb_named"] = draw_mon(tombs, "tclass", cgroup="cgroup", mask_ctrl=named_other)
tombs["dermot"] = tombs.nm_class.eq("dermot")
CT["dermot_all"] = draw_mon(tombs, "tclass", giantcol="dermot", cgroup="cgroup", mask_ctrl=~tombs.giant.values)
Bg = B[B.country.isin(["United Kingdom", "Isle of Man"])].reset_index(drop=True)
CT["barrow"] = draw_mon(Bg, "kind", cgroup="country")
Mg = M[M.country.isin(["United Kingdom", "Isle of Man"])].reset_index(drop=True)
Mg["mtype"] = np.where(Mg.cls.isin(["menhir", "circle", "rows"]) | Mg.name.str.contains("Stone|Quoit"), "stone", "tomb")
CT["megalith"] = draw_mon(Mg, "mtype", cgroup="country")
H = H.reset_index(drop=True); H["all"] = "hillfort"
CT["hillfort"] = draw_mon(H, "all", cgroup="country")
print({k: len(v[0]) for k, v in CT.items()}, round(time.time() - t0))
pd.to_pickle(dict(PTS=PTS, tombs=tombs, B=Bg, M=Mg, H=H, CT=CT, LAY={k: len(v) for k, v in LAY.items()}), os.path.join(WORK, "measured.pkl"))
print("done", round(time.time() - t0))
