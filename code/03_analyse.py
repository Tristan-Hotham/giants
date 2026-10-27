"""Step 3. Compare giant places with their controls and write every number used anywhere.

Each test compares an observed statistic (a median or a share) for the giant places with 2,000 replicate control
sets; each replicate takes one control at random for every giant place (see 02_measure.py for how controls are drawn).
Chance values are two-sided: twice the share of replicates on the far side of the observed value.
Writes ../data/results.json, ../data/test_results.csv, ../data/irish_tombs.csv, ../data/giant_names_gb.csv,
../data/legends_measured.csv, ../data/giant_monuments_measured.csv, ../data/controls.csv.gz and ../work/site.json.
Run: python3 code/03_analyse.py
"""
import json, os, warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)
import numpy as np, pandas as pd
from terms import TOMB_LABEL, TOMB_ORDER

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, "work"); DATA = os.path.join(ROOT, "data")
NREP = 2000; K = 50
rng = np.random.default_rng(1405)
D = pd.read_pickle(os.path.join(WORK, "measured.pkl"))
CNT = json.load(open(os.path.join(WORK, "counts.json")))
PTS, tombs, Bg, Mg, H, CT = D["PTS"], D["tombs"], D["B"], D["M"], D["H"], D["CT"]
GP = pd.read_csv(os.path.join(DATA, "giant_places.csv"), keep_default_na=False, na_values=[""])
LG = pd.read_csv(os.path.join(DATA, "legends.csv"), keep_default_na=False, na_values=[""])
R = {"n_rep": NREP, "k_controls": K, "counts": CNT}


def stat(v, kind, thr=None):
    ok = np.isfinite(v)
    if kind == "median": return np.nanmedian(v, -1)
    if kind == "mean": return np.nanmean(v, -1)
    if kind == "lt": return np.where(ok, v < thr, False).sum(-1) / np.maximum(ok.sum(-1), 1)
    if kind == "ge": return np.where(ok, v >= thr, False).sum(-1) / np.maximum(ok.sum(-1), 1)


def test(o, C, kind, thr=None):
    """o: observed values (n); C: control values (n, K)."""
    keep = np.isfinite(o)
    o, C = o[keep], C[keep]
    ov = float(stat(o[None], kind, thr)[0])
    pick = rng.integers(0, C.shape[1], size=(NREP, C.shape[0]))
    b = stat(np.take_along_axis(np.broadcast_to(C, (NREP,) + C.shape), pick[..., None], 2)[..., 0], kind, thr)
    allc = float(stat(C.ravel()[None], kind, thr)[0])
    p = min(1.0, 2 * min((b >= ov).mean(), (b <= ov).mean()))
    return dict(obs=ov, base=allc, base_lo=float(np.nanpercentile(b, 2.5)), base_hi=float(np.nanpercentile(b, 97.5)), p=float(p), n=int(keep.sum()),
                diff=ov - allc)


rows = []


def record(group, measure, label, control, r):
    rows.append(dict(group=group, measure=measure, label=label, control=control, **r))
    R.setdefault("tests", {}).setdefault(group, {}).setdefault(measure, {})[control] = r


TERR = {"tpi1k": ("tpi1k", "median", None, "Median height above the ground 1 km around (m)"),
        "tpi500": ("tpi500", "median", None, "Median height above the ground 500 m around (m)"),
        "pct1k": ("pct1k", "median", None, "Median share of ground within 1 km that lies lower"),
        "high": ("pct1k", "ge", 0.75, "Share on a local high point (higher than 75% of the ground within 1 km)"),
        "elev": ("elev", "median", None, "Median height above sea level (m)"),
        "relief1k": ("relief1k", "median", None, "Median relief within 1 km (m)")}

# ---------- monuments ----------
mon_sets = {"tomb_all": (tombs, "Irish giant tombs v. same class, all"), "tomb_named": (tombs, "Irish giant tombs v. same class, named otherwise"),
            "dermot_all": (tombs, "Dermot and Grania tombs v. same class"), "barrow": (Bg, "Giant barrows and cairns, Britain and Man"),
            "megalith": (Mg, "Giant megaliths, Britain and Man"), "hillfort": (H, "Giant hillforts")}
for g, (df, lab) in mon_sets.items():
    idx, strata = CT[g]
    gi = np.array(sorted(idx)); ci = np.stack([idx[i] for i in gi])
    R.setdefault("strata", {})[g] = pd.Series([strata[i] for i in gi]).value_counts().to_dict()
    for mk, (col, kind, thr, l) in TERR.items():
        record(g, mk, l, "match", test(df[col].values[gi], df[col].values[ci], kind, thr))
    if g == "hillfort":
        record(g, "area", "Median enclosed area (ha)", "match", test(df.area_ha.values[gi], df.area_ha.values[ci], "median"))
        record(g, "multi", "Share with two or more ramparts", "match", test((df.ramparts.values[gi] >= 2).astype(float), (df.ramparts.values[ci] >= 2).astype(float), "mean"))
    print(g, len(gi))

# ---------- names and legends (points) ----------
obs = PTS[PTS.set == "obs"].reset_index(drop=True)
DIST = {"any_1": ("any_km", "lt", 1.0, "Share within 1 km of a prehistoric monument"),
        "any_2": ("any_km", "lt", 2.0, "Share within 2 km of a prehistoric monument"),
        "any_med": ("any_km", "median", None, "Median distance to a prehistoric monument (km)"),
        "barrow_2": ("barrow_km", "lt", 2.0, "Share within 2 km of a barrow or cairn"),
        "megalith_2": ("megalith_km", "lt", 2.0, "Share within 2 km of a megalith"),
        "circle_2": ("circle_km", "lt", 2.0, "Share within 2 km of a stone circle"),
        "hillfort_2": ("hillfort_km", "lt", 2.0, "Share within 2 km of a hillfort")}
ALLM = {**TERR, **DIST}


def mats(kind, setname):
    q = PTS[(PTS.kind == kind) & (PTS.set == setname)]
    return q


for kind in ("name", "legend"):
    ob = obs[obs.kind == kind].reset_index(drop=True)
    for setname in ("match", "rand"):
        q = mats(kind, setname)
        if len(q) == 0: continue
        ctrl = {p: g for p, g in q.groupby("parent", sort=False)}
        have = ob.parent.isin(ctrl.keys()).values
        obk = ob[have].reset_index(drop=True)
        if kind == "name":
            sub = {"names": np.ones(len(obk), bool), "names_english": obk.name.str.contains("Giant").values,
                   "names_gaelic": obk.name.str.contains("amh?air", regex=True).values,
                   "names_hill": obk.local_type.str.startswith("Hill").values,
                   "names_coast": obk.local_type.isin(["Other Coastal Landform", "Cliff Or Slope"]).values}
        else:
            th = LG.set_index("id").thing.reindex(obk.parent).values
            sub = {"legends": np.ones(len(obk), bool), "legends_monument": np.isin(th, ["prehistoric"]),
                   "legends_natural": np.isin(th, ["natural"])}
        for mk, (col, kd, thr, l) in ALLM.items():
            C = np.stack([ctrl[p][col].values for p in obk.parent])
            for g, m in sub.items():
                if m.sum() < 3: continue
                record(g, mk, l, setname, test(obk[col].values[m], C[m], kd, thr))
        for g, m in sub.items(): R.setdefault("group_n", {})[g] = int(m.sum())

# ---------- Irish tombs: names by class and county ----------
tombs["name_label"] = tombs.nm_class.map(TOMB_LABEL)
ct = pd.crosstab(tombs.tclass, tombs.nm_class).reindex(columns=TOMB_ORDER, fill_value=0)
R["tomb_classes"] = {c.replace("Megalithic tomb - ", "").replace("Megalithic ", ""): {k: int(v) for k, v in r.items()} for c, r in ct.iterrows()}
R["tomb_name_counts"] = tombs.nm_class.value_counts().reindex(TOMB_ORDER).fillna(0).astype(int).to_dict()
R["n_tombs"] = int(len(tombs)); R["n_tombs_giant"] = int(tombs.giant.sum())
named = tombs.nm_class.isin(["giant", "dermot", "druid", "other_named", "descriptive"])
R["n_tombs_named"] = int(named.sum())
R["giant_share_named"] = float(tombs.giant.sum() / named.sum())
R["legend_share_named"] = float(tombs.nm_class.isin(["giant", "dermot", "druid"]).sum() / named.sum())
R["giant_share_all"] = float(tombs.giant.mean())
by = tombs.groupby("tclass").agg(n=("giant", "size"), giant=("giant", "sum"), dermot=("dermot", "sum"))
R["tomb_class_share"] = {c.replace("Megalithic tomb - ", "").replace("Megalithic ", ""): dict(n=int(r.n), giant=int(r.giant), dermot=int(r.dermot), giant_share=float(r.giant / r.n), dermot_share=float(r.dermot / r.n)) for c, r in by.iterrows()}
cty = tombs.groupby("COUNTY").agg(n=("giant", "size"), giant=("giant", "sum"), dermot=("dermot", "sum"), lat=("LATITUDE", "mean"), lon=("LONGITUDE", "mean"))
cty["giant_share"] = cty.giant / cty.n
R["tomb_counties"] = {c.title(): dict(n=int(r.n), giant=int(r.giant), dermot=int(r.dermot), giant_share=float(r.giant_share)) for c, r in cty.sort_values("giant", ascending=False).iterrows()}
R["top_giant_counties"] = [c.title() for c in cty.sort_values("giant", ascending=False).index[:6]]
N_HALF = 53.5
R["giant_north_share"] = float((tombs[tombs.giant].LATITUDE > N_HALF).mean())
R["dermot_north_share"] = float((tombs[tombs.dermot].LATITUDE > N_HALF).mean())
R["tombs_north_share"] = float((tombs.LATITUDE > N_HALF).mean())
R["north_cut"] = N_HALF
fe = tombs.FIRST_EDITION.fillna("").str.strip()
fe_rec = ~fe.isin(["", "NULL"])
g = tombs.giant
R["giant_first_recorded"] = int((g & fe_rec).sum())
R["giant_in_first"] = int((g & fe.str.contains("iant")).sum())
R["giant_later_only"] = int((g & fe_rec & ~fe.str.contains("iant")).sum())
R["giant_first_blank"] = int((g & ~fe_rec).sum())
R["giant_first_not_shown"] = int((g & fe.str.match(r"(?i)not ind")).sum())
R["giant_first_other_label"] = int((g & fe_rec & ~fe.str.contains("iant") & ~fe.str.match(r"(?i)not ind")).sum())
R["giant_first_other_labels"] = tombs[g & fe_rec & ~fe.str.contains("iant") & ~fe.str.match(r"(?i)not ind")].FIRST_EDITION.value_counts().to_dict()
ln = tombs.LATEST_EDITION.fillna("")
R["giant_site_of"] = int((g & ln.str.contains("Site of")).sum())
yrs = ln[g].str.extract(r"\((\d{4})")[0].dropna().astype(int)
R["giant_latest_dated"] = int(len(yrs)); R["giant_latest_1900"] = int((yrs >= 1900).sum()); R["giant_latest_min"] = int(yrs.min()); R["giant_latest_max"] = int(yrs.max())
pt = tombs[tombs.tclass.str.contains("passage")]
R["passage_named"] = int(pt.nm_class.isin(["giant", "dermot", "druid", "other_named", "descriptive"]).sum())
R["passage_carn"] = int(pt.os_map_name.fillna("").str.match(r"Carns?$").sum())
R["tomb_terrain_by_name"] = {k: {m: float(tombs.loc[tombs.nm_class == k, m].median()) for m in ("tpi1k", "pct1k", "elev", "relief1k")} | {"n": int((tombs.nm_class == k).sum())} for k in TOMB_ORDER}

# ---------- giant places: what giants are attached to ----------
R["n_places"] = int(len(GP))
R["places_by_region"] = GP.region.value_counts().to_dict()
R["places_by_source"] = GP.source.value_counts().to_dict()
R["feature_by_region"] = {r: g.feature.value_counts().to_dict() for r, g in GP.groupby("region")}
gb = GP[GP.region.isin(["Great Britain", "Isle of Man"])]
R["n_gb_places"] = int(len(gb))
R["gb_monument_share"] = float(gb.feature.isin(["Barrow, cairn or mound", "Hillfort", "Standing stone or stone setting", "Megalithic tomb"]).mean())
ie = GP[GP.region.isin(["Ireland", "Northern Ireland"])]
R["n_ie_places"] = int(len(ie))
R["ie_monument_share"] = float(ie.feature.isin(["Barrow, cairn or mound", "Fort or enclosure", "Standing stone or stone setting", "Megalithic tomb", "Other monument"]).mean())
R["ie_tomb_share"] = float((ie.feature == "Megalithic tomb").mean())
en = GP[GP.lang == "English"]
R["noun_counts"] = en.noun.replace("", "Other").value_counts().to_dict()
R["noun_grave_share"] = float((en.noun == "Grave or bed").mean())
R["noun_counts_gb"] = en[en.region != "Ireland"].noun.replace("", "Other").value_counts().to_dict()
R["lang_counts"] = GP.lang.value_counts().to_dict()
R["gb_names"] = {"n": int(len(D["PTS"][(D["PTS"].set == "obs") & (D["PTS"].kind == "name")])),
                 "by_type": PTS[(PTS.set == "obs") & (PTS.kind == "name")].local_type.value_counts().to_dict()}
from terms import lang as _lang
_ob = PTS[(PTS.set == "obs") & (PTS.kind == "name")]
R["os_lang_all"] = pd.Series([_lang(n) for n in _ob.name]).value_counts().to_dict()
R["os_country_all"] = pd.read_pickle(os.path.join(WORK, "pools.pkl"))["G"].country.value_counts().to_dict()
osg = GP[GP.source == "OS Open Names"]
R["os_names_by_lang"] = osg.lang.value_counts().to_dict()
R["os_names_by_country"] = osg.country.value_counts().to_dict()
R["os_names_feature"] = osg.feature.value_counts().to_dict()

# ---------- legends ----------
lo = obs[obs.kind == "legend"].set_index("parent")
LGm = LG.join(lo[["elev", "tpi1k", "pct1k", "relief1k", "barrow_km", "megalith_km", "circle_km", "hillfort_km", "any_km"]], on="id")
LGm.round(4).to_csv(os.path.join(DATA, "legends_measured.csv"), index=False)
R["n_legends"] = int(len(LG))
R["legends_by_thing"] = LG.thing.value_counts().to_dict()
R["legends_by_country"] = LGm.assign(c=LGm.country.replace("", np.nan).fillna("England")).c.value_counts().to_dict()
R["legends_placed_os"] = int((LG.os_fid >= 0).sum())
R["legend_rows"] = [{k: (None if pd.isna(v) else (round(v, 3) if isinstance(v, float) else v)) for k, v in r.items()}
                    for r in LGm[["id", "giant", "region", "thing", "explains", "any_km", "tpi1k", "elev"]].to_dict(orient="records")]
R["legends_any_1"] = int((LGm.any_km < 1).sum())
R["legends_natural_or_monument"] = int(LG.thing.isin(["natural", "prehistoric", "figure"]).sum())

# ---------- hill figures ----------
HF = pd.read_csv(os.path.join(DATA, "hill_figures.csv"))
R["hill_figures"] = HF[["figure", "county", "status", "first", "known_from", "lost_by"]].to_dict(orient="records")
R["n_giant_figures"] = int(len(HF)); R["n_giant_figures_surviving"] = int((HF.status == "surviving").sum())

# ---------- named examples ----------
hg = H[H.giant].copy()
R["giant_hillforts"] = [dict(name=r.name, country=r.country, area_ha=(None if pd.isna(r.area_ha) else float(r.area_ha)), ramparts=(None if pd.isna(r.ramparts) else int(r.ramparts)),
                             tpi1k=float(r.tpi1k), elev=float(r.elev)) for r in hg.sort_values("area_ha", ascending=False).itertuples()]
R["hillfort_area_all_median"] = float(H.area_ha.median())
R["n_hillforts_area"] = int(H.area_ha.notna().sum())
R["n_hillforts_gb"] = int(H.country.isin(["England", "Scotland", "Wales"]).sum())
R["layers"] = D["LAY"]

# ---------- curves for charts ----------
def hist(vals, ctrl, edges):
    clip = lambda v: np.clip(v[np.isfinite(v)], edges[0], edges[-1] - 1e-9)
    a, c = clip(vals), clip(ctrl)
    return dict(edges=list(map(float, edges)), obs=(np.histogram(a, edges)[0] / len(a)).round(4).tolist(), ctrl=(np.histogram(c, edges)[0] / len(c)).round(4).tolist(), n_obs=int(len(a)))


idx, _ = CT["tomb_all"]; gi = np.array(sorted(idx)); ci = np.stack([idx[i] for i in gi])
R["curves"] = {"tomb_tpi": hist(tombs.tpi1k.values[gi], tombs.tpi1k.values[ci].ravel(), np.arange(-40, 45, 5)),
               "tomb_pct": hist(tombs.pct1k.values[gi], tombs.pct1k.values[ci].ravel(), np.arange(0, 1.01, 0.1))}
nob = obs[obs.kind == "name"]; nm = PTS[(PTS.kind == "name") & (PTS.set == "match")]; nr = PTS[(PTS.kind == "name") & (PTS.set == "rand")]
R["curves"]["names_any"] = hist(nob.any_km.values, nm.any_km.values, np.arange(0, 8.5, 0.5))
R["curves"]["names_any"]["rand"] = hist(nob.any_km.values, nr.any_km.values, np.arange(0, 8.5, 0.5))["ctrl"]
json.dump(R, open(os.path.join(DATA, "results.json"), "w"), indent=1, default=lambda v: None if v != v else (int(v) if isinstance(v, (np.integer,)) else float(v)))
pd.DataFrame(rows).to_csv(os.path.join(DATA, "test_results.csv"), index=False, float_format="%.4f")

# ---------- data files ----------
T = tombs[["ENTITY_ID", "COUNTY", "TOWNLAND", "tclass", "LATITUDE", "LONGITUDE", "FIRST_EDITION", "LATEST_EDITION", "nm_class", "name_label", "os_map_name", "giant",
           "elev", "tpi500", "tpi1k", "pct1k", "relief1k"]].rename(columns={"ENTITY_ID": "smr_id", "COUNTY": "county", "TOWNLAND": "townland", "tclass": "monument_class",
           "LATITUDE": "lat", "LONGITUDE": "lon", "FIRST_EDITION": "first_edition", "LATEST_EDITION": "latest_edition", "nm_class": "name_class"})
for c in ("first_edition", "latest_edition", "os_map_name", "townland"):  # source labels use en dashes in year ranges
    T[c] = T[c].astype("string").str.replace(chr(0x2013), "-").str.replace(chr(0x2014), "-")
T.round(5).to_csv(os.path.join(DATA, "irish_tombs.csv"), index=False)
n = obs[obs.kind == "name"].drop(columns=["set", "kind"]).rename(columns={"parent": "os_ref"})
n.round(4).to_csv(os.path.join(DATA, "giant_names_gb.csv"), index=False)
mm = []
for g, df, lab in (("barrow", Bg, "barrow"), ("megalith", Mg, "megalith"), ("hillfort", H, "hillfort")):
    q = df[df.giant].copy(); q["pool"] = lab
    mm.append(q[["pool", "name", "country", "lat", "lon", "elev", "tpi500", "tpi1k", "pct1k", "relief1k"] + (["area_ha", "ramparts"] if lab == "hillfort" else [])])
pd.concat(mm).round(4).to_csv(os.path.join(DATA, "giant_monuments_measured.csv"), index=False)
cc = PTS[PTS.set.isin(["match", "rand"])][["set", "kind", "parent", "name", "local_type", "lat", "lon", "elev", "tpi1k", "pct1k", "barrow_km", "megalith_km", "circle_km", "hillfort_km", "any_km"]]
cc.round(4).to_csv(os.path.join(DATA, "controls.csv.gz"), index=False, compression="gzip")

# ---------- compact data for the page ----------
GPm = GP.copy()
r5 = lambda v: None if pd.isna(v) else round(float(v), 5)
site = dict(
    places=[[r5(r.lat), r5(r.lon), r.name, r.feature, r.source, r.region, r.lang, r.monument_class if isinstance(r.monument_class, str) else "", r.county if isinstance(r.county, str) else ""]
            for r in GPm.itertuples()],
    leg=[[r5(r.lat), r5(r.lon), r.giant, r.thing, r.explains, r.region, r.phrase, r.source, r.url, r.placed, None if pd.isna(r.any_km) else round(r.any_km, 2)] for r in LGm.itertuples()],
    tombs=[[round(r.LATITUDE, 4), round(r.LONGITUDE, 4), TOMB_ORDER.index(r.nm_class), r.tclass.replace("Megalithic tomb - ", "").replace("Megalithic ", ""), str(r.TOWNLAND).title(),
            str(r.COUNTY).title(), r.os_map_name, None if pd.isna(r.tpi1k) else round(r.tpi1k, 1)] for r in tombs.itertuples()],
    hf=HF[["figure", "status", "first", "lat", "lon"]].values.tolist(),
)
json.dump(site, open(os.path.join(WORK, "site.json"), "w"), separators=(",", ":"))
print("results written", len(rows), "tests")
