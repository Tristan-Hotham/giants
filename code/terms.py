"""Matching rules for giant names, and the classes used to sort them.

A match means only that a word for giant is in the name. It says nothing about when or why the
name was given. I make no etymological claims: the Gaelic word famhair and the Welsh word cawr
both mean "giant" in the dictionary sense, and that is all that is assumed.

GIANT names (any source)
  English   the word Giant, Giants, Giant's or Giants' (word boundary at the start), and the run-together
            townland form Giantsgrave
  Gaelic    Famhair, Fhamhair, Fhamair, Famhairean (Scottish Gaelic famhair, "giant")
  Welsh     Cawr or Gawr as a word of its own (Welsh cawr, "giant", with its soft mutation)
  Named     Gog Magog, Magog (only the Cambridgeshire Gog Magog names; "Gog" alone is not used)
Excluded, and counted: commercial and modern names that use the English word as an adjective or brand
  (EuroGiant shops, Giant Auto Parts, Tile Giant, Giant Tap, giant trees, sculpture trail figures,
  "Giant's Leap Trail" paths, which repeat the Giant's Leap feature, and The Giant's Garden, a modern
  park in Dublin named after a story by Oscar Wilde). Wade's and Bran names are not used, because
  Wade is a common surname (General Wade's Military Road) and Bran a common word.
Run the tests: python3 code/terms.py
"""
import re

GIANT = re.compile(r"\bGiant|Giantsgrave|\bF(?:h)?amh?air|\bCawr\b|\bGawr\b|\bMagog\b", re.I)
EXCLUDE = re.compile(r"EuroGiant|Eurogiant|Auto Parts|Tile Giant|Giant Tap|Giant Redwood|Giant pine|Introduced Giant|"
                     r"Giants of the Forest|giant hare|Little Green Giants|Land of the Giants|Leap Trail|Giant's Garden|"
                     r"^Giant$|Roddy-Den-Drum Giant|Banba Giant|Big Ross Giant|Spike Giant|Red Wolf Giant|Druid Giant|"
                     r"Thoth Giant|Ailinn Giant|Muireann Giant|Red Squirrel Giant|Connemara Giant", re.I)


def lang(name):
    if re.search(r"F(?:h)?amh?air", name, re.I): return "Gaelic"
    if re.search(r"\bCawr\b|\bGawr\b", name): return "Welsh"
    if re.search(r"Magog", name): return "Named giant"
    return "English"


def is_giant(name):
    return bool(name) and bool(GIANT.search(name)) and not EXCLUDE.search(name)


def excluded(name):
    return bool(name) and bool(GIANT.search(name)) and bool(EXCLUDE.search(name))


# What the English name says the thing is (the noun after Giant's). Gaelic and Welsh names are not translated
# here; for them the OS feature type is used instead.
NOUN = [("Grave or bed", r"Grave|Graves|\bBeds?\b|\bDen\b|Basin"),
        ("Chair or seat", r"Chair|Seat"),
        ("Stone, rock or quoit", r"Stone|Rock|Quoit|Boulder|Griddle|Wedge"),
        ("Hill", r"\bHills?\b|Hill\)|\bHill$"),
        ("Causeway, dyke, bank or cut", r"Causeway|Dike|Dyke|Bank|\bCut\b|Leap"),
        ("Castle, fort or hall", r"Castle|Round|Hall|Fort|Cottage|Oven"),
        ("Body part", r"\bLeg\b|Thumb|\bRib\b|Footprint"),
        ("Wood", r"Wood|Plantation"),
        ("Water", r"Lake|Loch|Well")]


def noun(name):
    if lang(name) != "English": return ""
    for lab, pat in NOUN:
        if re.search(pat, name, re.I): return lab
    return "Other"


# Names given to Irish megalithic tombs on the Ordnance Survey six-inch maps (SMR FIRST_EDITION / LATEST_EDITION).
# Checked in this order; the first that matches wins. Anything else that is a name is "other_named".
TOMB_RULES = [("giant", r"giant"),
              ("dermot", r"dermot|grania|grainne"),
              ("druid", r"druid"),
              ("other_named", r"\bbed\b|labba|leaba|mans grave|mccool|nialls|bredanes|bridgets|patrick|altoir|ho$"),
              ("descriptive", r"cromle|\bcarns?\b|cairn|dolmen|megal|stone|grave|monument|altar|cave|moat|fort|burial|"
                              r"piles|ancient|standing|gallaun|circle|dwelling")]
TOMB_LABEL = {"giant": "Giant's Grave or Bed", "dermot": "Dermot and Grania's Bed", "druid": "Druid's Altar",
              "other_named": "Other personal or local name", "descriptive": "Descriptive (Cromlech, Dolmen, Carn...)",
              "indicated": "Shown, no name", "none": "Not shown or not recorded"}
TOMB_ORDER = ["giant", "dermot", "druid", "other_named", "descriptive", "indicated", "none"]


def tomb_name(first, latest):
    vals = []
    for v in (first, latest):
        v = re.sub(r"\s*\(.*?\)", "", (v or "")).strip().rstrip(".")
        if not v or v.upper() == "NULL" or re.match(r"not ind", v, re.I):
            continue
        vals.append(v)
    if not vals:
        return "none", ""
    s = " | ".join(dict.fromkeys(vals))
    for k, pat in TOMB_RULES:
        if re.search(pat, s, re.I): return k, s
    if all(re.match(r"(indicated|hachured)", v, re.I) for v in vals): return "indicated", s
    return "other_named", s


if __name__ == "__main__":
    T = {"Giant's Grave": True, "Giants Grave": True, "Giant Hill": True, "Little Giant Wood": True, "Giantsgrave": True,
         "Cnoc an Fhamhair": True, "Coire an Fhamair": True, "Na Famhairean": True, "Llyn Cawr": True, "Castell Cawr": True,
         "Gog Magog Hills": True, "Magog Down": True, "Allt Gog": False, "EuroGiant": False, "Giant Auto Parts": False,
         "Giant's Leap Trail": False, "Giant's Leap": True, "Wade's Hill": False, "Cormorant Creek": False, "The Giant's Garden": False}
    for k, v in T.items():
        assert is_giant(k) == v, (k, is_giant(k), v)
    assert noun("Giant's Grave Bottom") == "Grave or bed" and noun("Giants Chair") == "Chair or seat" and noun("Giant Hill") == "Hill"
    assert noun("Giant's Quoiting Stone") == "Stone, rock or quoit" and noun("The Giants Thumb") == "Body part"
    TT = {("", "Giants Grave (1902)"): "giant", ("Not indicated", "Dermot & Granias Bed"): "dermot", ("NULL", "Druids Altar"): "druid",
          ("", "Cromlech"): "descriptive", ("Hachured", "Indicated"): "indicated", ("", ""): "none", ("NULL", "Not indicated"): "none",
          ("", "Labbacallee"): "other_named", ("", "The Big Mans Grave"): "other_named", ("", "Carn"): "descriptive",
          ("Giants Grave(1834)", "Not indicated"): "giant", ("", "Fin McCools Ho"): "other_named", ("", "Stone Circle"): "descriptive"}
    for (a, b), v in TT.items():
        assert tomb_name(a, b)[0] == v, (a, b, tomb_name(a, b), v)
    print("terms ok")
