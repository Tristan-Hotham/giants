"""Step 1. Collect every giant name, giant monument and giant legend, and the monument pools used as controls.

Writes
  ../data/giant_places.csv   one row per distinct giant-named place (OS Open Names GB, Irish Sites and Monuments Record,
                             OpenStreetMap Ireland, barrows, megaliths and hillforts), with what the place actually is
  ../data/irish_tombs.csv    all megalithic tombs in the Irish Sites and Monuments Record, with the name the OS
                             six-inch maps give them, sorted into classes (terms.py)
  ../data/legends.csv        the named giants of legend and where they were placed (legends.py)
  ../data/hill_figures.csv   the giant hill figures in the Wikipedia "Hill figure" article, with their dates
  ../work/pools.pkl          the monument pools (Irish tombs, barrows, megaliths, hillforts, stone circles) with flags
  ../work/counts.json        counts used later
Shared inputs are read in place from the folder above this repository (set HIST to change it).
Run: python3 code/01_collect.py
"""
import gzip, json, os, re
import numpy as np, pandas as pd
from pyproj import Transformer
from scipy.spatial import cKDTree
from terms import is_giant, excluded, lang, noun, tomb_name, TOMB_LABEL
from legends import LEGENDS, SRC

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
HIST = os.environ.get("HIST", os.path.dirname(ROOT))
D10 = os.path.join(HIST, "_data10")
WORK = os.path.join(ROOT, "work"); os.makedirs(WORK, exist_ok=True)
DATA = os.path.join(ROOT, "data"); os.makedirs(DATA, exist_ok=True)
TE = Transformer.from_crs(4326, 3035, always_xy=True)   # ETRS89 LAEA Europe: one metric grid for Britain and Ireland
xy = lambda lon, lat: TE.transform(np.asarray(lon, float), np.asarray(lat, float))
C = {}

# ---------------- OS Open Names (Great Britain) ----------------
os_ = pd.read_csv(os.path.join(HIST, "osnames_gb.tsv"), sep="\t", dtype=str, keep_default_na=False)
for c in ("lat", "lon"):
    os_[c] = os_[c].astype(float)
os_["fid"] = np.arange(len(os_))
gm = np.array([is_giant(a) or is_giant(b) for a, b in zip(os_.name1, os_.name2)])
ex = np.array([excluded(a) or excluded(b) for a, b in zip(os_.name1, os_.name2)])
G = os_[gm].copy()
G["name"] = [a if is_giant(a) else b for a, b in zip(G.name1, G.name2)]
C["n_os_features"] = int(len(os_)); C["n_os_excluded"] = int(ex.sum())
OSTYPE = {"Hill Or Mountain": "Hill or mountain", "Hill Or Mountain Ranges": "Hill or mountain", "Other Coastal Landform": "Coastal rock or cliff",
          "Cliff Or Slope": "Coastal rock or cliff", "Valley": "Valley or hollow", "Cirque Or Hollow": "Valley or hollow", "Other Landform": "Valley or hollow",
          "Woodland Or Forest": "Wood", "Inland Water": "Water", "Waterfall": "Water", "Bay": "Water", "Suburban Area": "Settlement",
          "Other Landcover": "Other"}
rows = []
for r in G.itertuples():
    rows.append(dict(name=r.name, source="OS Open Names", src_id=f"os_row_{r.fid}", country=r.country, county=r.county or r.district,
                     lat=r.lat, lon=r.lon, lang=lang(r.name), noun=noun(r.name), os_local_type=r.local_type,
                     feature=OSTYPE.get(r.local_type, "Other"), monument_class="", os_fid=r.fid))
print("OS giant names", len(G), "excluded", int(ex.sum()))

# ---------------- Irish Sites and Monuments Record ----------------
smr = pd.DataFrame(json.load(gzip.open(os.path.join(D10, "ireland_smr_all.json.gz"))))
smr = smr.dropna(subset=["LATITUDE", "LONGITUDE"])
# some records carry a placeholder position far out in the Atlantic (46.49 N, 15.82 W); they have no usable location
badpos = ~(smr.LATITUDE.between(51.2, 55.6) & smr.LONGITUDE.between(-10.8, -5.8))
C["n_smr_no_position"] = int(badpos.sum()); C["n_smr_all"] = int(len(smr))
C["n_smr_giant_no_position"] = int((badpos & smr.FIRST_EDITION.fillna("").str.cat(smr.LATEST_EDITION.fillna("")).str.contains("giant", case=False)).sum())
C["n_tombs_no_position"] = int((badpos & smr.MONUMENT_CLASS.fillna("").str.startswith("Megalithic")).sum())
smr = smr[~badpos]
smr["nm_class"], smr["os_map_name"] = zip(*[tomb_name(a, b) for a, b in zip(smr.FIRST_EDITION, smr.LATEST_EDITION)])
smr["giant"] = [bool(re.search(r"giant", f"{a} {b}", re.I)) for a, b in zip(smr.FIRST_EDITION.fillna(""), smr.LATEST_EDITION.fillna(""))]
smr["giant_first"] = smr.FIRST_EDITION.fillna("").str.contains("giant", case=False)
C["n_smr"] = int(len(smr)); C["n_smr_giant"] = int(smr.giant.sum())


def smr_feature(c):
    c = c or ""
    if c.startswith("Megalithic"): return "Megalithic tomb"
    if re.match(r"Cairn|Barrow|Mound|Cist|Boulder-burial", c): return "Barrow, cairn or mound"
    if re.match(r"Standing stone|Stone circle|Anomalous stone|Inscribed stone|Cross-inscribed|Stone row|Stone pair", c): return "Standing stone or stone setting"
    if re.match(r"Enclosure|Ringfort|Fortification|Hillfort|Promontory", c): return "Fort or enclosure"
    return "Other monument"


for r in smr[smr.giant].itertuples():
    nm = re.sub(r"\s*\(.*?\)", "", (r.LATEST_EDITION if "iant" in str(r.LATEST_EDITION) else r.FIRST_EDITION) or "").strip().rstrip(".")
    rows.append(dict(name=nm, source="Irish SMR (OS map name)", src_id=r.ENTITY_ID, country="Ireland", county=str(r.COUNTY).title(),
                     lat=r.LATITUDE, lon=r.LONGITUDE, lang="English", noun=noun(nm), os_local_type="", feature=smr_feature(r.MONUMENT_CLASS),
                     monument_class=r.MONUMENT_CLASS, os_fid=-1))
tombs = smr[smr.MONUMENT_CLASS.fillna("").str.startswith("Megalithic")].copy()
tombs["tclass"] = tombs.MONUMENT_CLASS.str.replace(r"\s*\(present location\)", "", regex=True)
print("Irish tombs", len(tombs), tombs.nm_class.value_counts().to_dict())

# ---------------- other monument pools ----------------
B = pd.read_csv(os.path.join(HIST, "barrows-of-europe", "data", "barrows.csv"), usecols=["src", "id", "name", "lon", "lat", "country", "kind", "cls"])
B = B[B.country.isin(["United Kingdom", "Isle of Man", "Ireland"])].reset_index(drop=True)
M = pd.read_csv(os.path.join(HIST, "megalith-highway", "data", "megaliths.csv"), usecols=["osm", "lat", "lon", "name", "cls", "country"])
M = M[M.country.isin(["United Kingdom", "Isle of Man", "Ireland"])].reset_index(drop=True)
H = pd.read_csv(os.path.join(HIST, "within-sight", "data", "forts_visibility.csv"), usecols=["atlas_id", "name", "country", "county", "lat", "lon", "area_ha", "ramparts"])
S = pd.read_csv(os.path.join(HIST, "stone-circles", "data", "stone_circles.csv"), usecols=["id", "name", "country", "lat", "lon"])
S = S[S.country.isin(["United Kingdom", "Isle of Man", "Ireland"])].reset_index(drop=True)
for df in (B, M, S):
    df["name"] = df.name.fillna("")
    df["giant"] = [is_giant(n) for n in df.name]
H["giant"] = [is_giant(n) for n in H.name]
C["pools"] = {"barrows": int(len(B)), "megaliths": int(len(M)), "hillforts": int(len(H)), "stone_circles": int(len(S)), "irish_tombs": int(len(tombs))}
C["pool_giants"] = {"barrows": int(B.giant.sum()), "megaliths": int(M.giant.sum()), "hillforts": int(H.giant.sum()), "stone_circles": int(S.giant.sum())}
MEG_FEAT = {"chamber": "Megalithic tomb", "cpw": "Megalithic tomb", "dolmen": "Megalithic tomb", "passage": "Megalithic tomb", "longb": "Megalithic tomb",
            "gallery": "Megalithic tomb", "menhir": "Standing stone or stone setting", "circle": "Standing stone or stone setting", "rows": "Standing stone or stone setting"}
for r in B[B.giant].itertuples():
    rows.append(dict(name=r.name, source="Barrows (OSM, Wikidata)", src_id=str(r.id), country=r.country, county="", lat=r.lat, lon=r.lon, lang=lang(r.name),
                     noun=noun(r.name), os_local_type="", feature="Barrow, cairn or mound", monument_class=f"{r.kind} ({r.cls})", os_fid=-1))
for r in M[M.giant].itertuples():
    f = MEG_FEAT.get(r.cls) or ("Standing stone or stone setting" if re.search("Stone|Quoit", r.name) else "Megalithic tomb")
    rows.append(dict(name=r.name, source="Megaliths (OSM)", src_id=str(r.osm), country=r.country, county="", lat=r.lat, lon=r.lon, lang=lang(r.name),
                     noun=noun(r.name), os_local_type="", feature=f, monument_class=r.cls, os_fid=-1))
for r in H[H.giant].itertuples():
    nm = r.name
    rows.append(dict(name=nm, source="Atlas of Hillforts", src_id=f"atlas_{r.atlas_id}", country=r.country, county=r.county, lat=r.lat, lon=r.lon,
                     lang=lang(nm), noun=noun(re.sub(r",.*", "", nm)), os_local_type="", feature="Hillfort", monument_class="hillfort", os_fid=-1))

# ---------------- OpenStreetMap, Republic of Ireland ----------------
bund = json.load(gzip.open(os.path.join(D10, "wd_osm_bundle10.json.gz")))
lines = bund["osm_ie_folk_names"].splitlines()
ie_ex = 0
for l in lines[1:]:
    p = l.split("\t")
    nm = p[1].strip('"'); wkt = p[3]
    if not re.search(r"giant", nm, re.I): continue
    if not is_giant(nm): ie_ex += 1; continue
    nums = np.array(re.findall(r"(-?\d+\.\d+) (-?\d+\.\d+)", wkt), float)
    lon, lat = nums[:, 0].mean(), nums[:, 1].mean()
    nn = noun(nm)
    feat = {"Water": "Water", "Stone, rock or quoit": "Rock or boulder"}.get(nn, "Not recorded (OSM)")
    if nm == "Giantsgrave": feat = "Settlement"  # a townland boundary (OSM relation), Irish name An Chloch Fhada
    rows.append(dict(name=nm, source="OpenStreetMap Ireland", src_id=p[0].strip("<>"), country="Ireland", county="", lat=lat, lon=lon, lang="English",
                     noun=nn, os_local_type="", feature=feat, monument_class="", os_fid=-1))
C["n_osm_ie_excluded"] = ie_ex

# ---------------- de-duplicate across sources ----------------
# Two records are the same place when they are within 400 m and their names use the same noun (Grave with Grave),
# or within 150 m when a name has no English noun (Gaelic and Welsh names).
P = pd.DataFrame(rows)
P["noun"] = P.noun.fillna("")
PRI = {"Irish SMR (OS map name)": 0, "Atlas of Hillforts": 1, "Megaliths (OSM)": 2, "Barrows (OSM, Wikidata)": 3, "OS Open Names": 4, "OpenStreetMap Ireland": 5}
P["pri"] = P.source.map(PRI)
P = P.sort_values(["pri"]).reset_index(drop=True)
P["x"], P["y"] = xy(P.lon, P.lat)
keep = np.ones(len(P), bool); also = [""] * len(P)
T = cKDTree(np.c_[P.x, P.y])
for i, j in sorted(T.query_pairs(400.0)):
    a, b = (i, j) if P.pri[i] <= P.pri[j] else (j, i)
    na, nb = str(P.noun[a] or ""), str(P.noun[b] or "")
    same = (na == nb) if (na and nb) else (np.hypot(P.x[a] - P.x[b], P.y[a] - P.y[b]) < 150)
    if same and keep[a] and keep[b] and not (P.source[a] == P.source[b] == "Irish SMR (OS map name)"):
        keep[b] = False
        also[a] = (also[a] + "; " if also[a] else "") + f"{P.source[b]}: {P.name[b]}"
P["also_in"] = also
C["n_rows_before_dedupe"] = int(len(P)); C["n_duplicates_removed"] = int((~keep).sum())
P = P[keep].drop(columns=["pri"]).reset_index(drop=True)
P["region"] = np.where(P.country.isin(["Ireland", "Republic of Ireland"]), "Ireland", np.where(P.country.eq("Northern Ireland") | ((P.country == "United Kingdom") & (P.lon < -5.4) & (P.lat > 54) & (P.lat < 55.4)), "Northern Ireland", np.where(P.country.isin(["Isle of Man"]), "Isle of Man", "Great Britain")))
P.loc[P.region == "Ireland", "country"] = "Ireland"
P.insert(0, "gid", [f"g{i:03d}" for i in range(len(P))])
P.round(6).to_csv(os.path.join(DATA, "giant_places.csv"), index=False)
print("giant places", len(P), P.region.value_counts().to_dict())
print(P.groupby(["region", "feature"]).size())

# ---------------- legends ----------------
lg = []
for L in LEGENDS:
    o = {k: L[k] for k in ("id", "giant", "region", "thing", "explains", "src", "phrase")}
    o["source"], o["url"] = SRC[L["src"]]
    if "os" in L:
        nm, ct = L["os"][:2]
        m = os_[((os_.name1 == nm) | (os_.name2 == nm)) & ((os_.county == ct) | (os_.district == ct))]
        if len(L["os"]) > 2:
            la, lo = L["os"][2]; m = m.iloc[[int(np.argmin((m.lat - la) ** 2 + (m.lon - lo) ** 2))]]
        assert len(m) == 1, (L["id"], len(m))
        r = next(m.itertuples())
        o.update(lat=r.lat, lon=r.lon, os_name=r.name1, os_local_type=r.local_type, os_fid=r.fid, country=r.country,
                 placed=f"OS Open Names {r.local_type} '{r.name1}' ({ct}), the place named in the source")
    else:
        la, lo, how = L["at"]
        o.update(lat=la, lon=lo, os_name="", os_local_type="", os_fid=-1, country="Northern Ireland" if L["id"] == "causeway" else "",
                 placed=how + "; the place is not in OS Open Names")
    lg.append(o)
LG = pd.DataFrame(lg)
LG.to_csv(os.path.join(DATA, "legends.csv"), index=False)
print("legends", len(LG), LG.thing.value_counts().to_dict())

# ---------------- giant hill figures (Wikipedia, Hill figure) ----------------
HF = pd.DataFrame([
    dict(figure="Cerne Abbas Giant", county="Dorset", status="surviving", first="10th century (dated 2020)", known_from=950, lost_by=None,
         note="documented history cannot be traced back further than the late 17th century; dated in 2020 to the 10th century", lat=50.813676, lon=-2.4747),
    dict(figure="Long Man of Wilmington", county="East Sussex", status="surviving", first="16th or 17th century", known_from=1550, lost_by=None,
         note="University of Reading work suggests the figure dates from the 16th or 17th century", lat=50.81, lon=0.188),
    dict(figure="The Giant Ghyst, Clifton", county="Bristol", status="lost", first="before 1480", known_from=1480, lost_by=None, note="lost figures table", lat=51.457132, lon=-2.62664),
    dict(figure="Plymouth Hoe Gogmagog", county="Devon", status="lost", first="before 1486", known_from=1486, lost_by=1668, note="lost in the late 1660s", lat=50.37001, lon=-4.14207),
    dict(figure="Wandlebury Hill Gogmagog", county="Cambridgeshire", status="lost", first="before 1605", known_from=1605, lost_by=1730, note="lost around 1730", lat=52.15888, lon=0.18288),
    dict(figure="The Giant of Hindover Hill", county="East Sussex", status="lost", first="before 1850", known_from=1850, lost_by=1924, note="lost by 1924", lat=50.80338, lon=0.16399),
])
HF["source"] = "Wikipedia: Hill figure (wikitext of 27 Oct 2026), https://en.wikipedia.org/wiki/Hill_figure"
HF["coords_from"] = ["Wikipedia article coordinates", "Wikipedia article coordinates", "Atlas of Hillforts, Clifton Down Camp", "OS Open Names, Plymouth (city)",
                     "Atlas of Hillforts, Wandlebury Camp", "OS Open Names, Litlington (East Sussex)"]
HF.to_csv(os.path.join(DATA, "hill_figures.csv"), index=False)
C["white_horses_uk"] = 16  # "There are 16 known white horse hill figures in the UK, or 17 including the painted one at Cleadon Hills" (Hill figure article)
C["white_horses_uk_note"] = "Wikipedia, Hill figure: 16 known white horse hill figures in the UK, or 17 including the painted one at Cleadon Hills"

# ---------------- save pools ----------------
tombs["x"], tombs["y"] = xy(tombs.LONGITUDE, tombs.LATITUDE)
pd.to_pickle(dict(G=G, tombs=tombs, B=B, M=M, H=H, S=S), os.path.join(WORK, "pools.pkl"))
tombs[["ENTITY_ID", "COUNTY", "TOWNLAND", "tclass", "LATITUDE", "LONGITUDE", "FIRST_EDITION", "LATEST_EDITION", "nm_class", "os_map_name", "giant", "giant_first"]].rename(
    columns={"ENTITY_ID": "smr_id", "COUNTY": "county", "TOWNLAND": "townland", "tclass": "monument_class", "LATITUDE": "lat", "LONGITUDE": "lon",
             "FIRST_EDITION": "first_edition", "LATEST_EDITION": "latest_edition", "nm_class": "name_class"}).to_csv(os.path.join(WORK, "irish_tombs_raw.csv"), index=False)
json.dump(C, open(os.path.join(WORK, "counts.json"), "w"), indent=1)
print(json.dumps(C)[:600])
