# Giants in the Landscape

Did people explain big things with big people? Giant's Grave, Giant's Chair, Giant's Causeway, Giant Hill, the Cerne Abbas Giant and the Long Man, Gog and Magog, Wade, Cormoran, Bran. This study gathers {{n_places|int}} giant-named places in Britain and Ireland (OS Open Names, the Irish Sites and Monuments Record, OpenStreetMap, and open barrow, megalith and hillfort datasets), all {{n_tombs|int}} Irish megalithic tombs with the names the Ordnance Survey maps gave them, and {{n_legends|int}} giant legends tied to places by written sources. It asks what giants are attached to, whether giant monuments are bigger or more prominent than ordinary monuments of the same kind nearby, and whether giant names sit closer to prehistoric monuments than matched ordinary names.

**Interactive version:** https://tristan-hotham.github.io/giants/

**Paper:** https://doi.org/10.5281/zenodo.23691920

**Blog post:** https://blog.tristanhotham.com/2026/10/27/giants/

By Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349). Companion studies: [Here Be Dragons](https://tristan-hotham.github.io/here-be-dragons/) (the same matched-control design), [Is the Barrow a European Thing?](https://tristan-hotham.github.io/barrows-of-europe/), [The Megalith Highway](https://tristan-hotham.github.io/megalith-highway/), [Within Sight](https://tristan-hotham.github.io/within-sight/).

## Headline results

- Giants own graves: {{noun_grave_share|pct0}} of the {{lang_counts.English|int}} English giant names call the place a grave or a bed. In Ireland {{ie_tomb_share|pct0}} of the {{n_ie_places|int}} giant places are megalithic tombs; in Great Britain and Man {{gb_monument_share|pct0}} of {{n_gb_places|int}} are monuments and the rest hills, coastal rocks, woods and water.
- {{n_tombs_giant|int}} of {{n_tombs|int}} Irish megalithic tombs ({{giant_share_named|pct0}} of the {{n_tombs_named|int}} that carry a name on the OS maps) are called Giant's Grave or Bed; {{tomb_name_counts.dermot|int}} are Dermot and Grania's Bed and {{tomb_name_counts.druid|int}} Druid's Altar.
- The giant prefers some tombs: {{tomb_class_share.court tomb.giant_share|pct0}} of court tombs and {{tomb_class_share.wedge tomb.giant_share|pct0}} of wedge tombs, but only {{tomb_class_share.passage tomb.giant_share|pct0}} of passage tombs, the class that includes Newgrange, Knowth, Carrowkeel and Loughcrew.
- The giant is northern: {{giant_north_share|pct0}} of Giant's Graves lie north of {{north_cut|f1}} degrees, against {{tombs_north_share|pct0}} of all tombs (Sligo {{tomb_counties.Sligo.giant|int}}, Donegal {{tomb_counties.Donegal.giant|int}}, Cavan {{tomb_counties.Cavan.giant|int}}).
- The giant's tomb is not the big one: {{tests.tomb_named.high.match.obs|pct0}} of Giant's Graves sit on a local high point, against {{tests.tomb_named.high.match.base|pct0}} of other named tombs of the same kind nearby (chance {{tests.tomb_named.high.match.p|p}}) and {{tests.tomb_all.high.match.base|pct0}} of all tombs (chance {{tests.tomb_all.high.match.p|p}}). Giant hillforts enclose a median {{tests.hillfort.area.match.obs|f2}} ha against {{tests.hillfort.area.match.base|f2}} ha for matched hillforts (chance {{tests.hillfort.area.match.p|p}}, n = {{tests.hillfort.area.match.n|int}}).
- Giant names stick to the ancient: {{tests.names.any_1.match.obs|pct0}} of the {{gb_names.n|int}} British giant names lie within 1 km of a recorded prehistoric monument, against {{tests.names.any_1.match.base|pct0}} of matched names and {{tests.names.any_1.rand.base|pct0}} of random land (chance {{tests.names.any_1.match.p|p}}). Giant hills are not taller: {{tests.names_hill.tpi1k.match.obs|f1}} m above the ground 1 km around against {{tests.names_hill.tpi1k.match.base|f1}} m for matched hills (chance {{tests.names_hill.tpi1k.match.p|p}}).
- Legends: of {{n_legends|int}} placed stories, {{legends_by_thing.natural|int}} explain a natural landform, {{legends_by_thing.prehistoric|int}} a prehistoric monument, {{legends_by_thing.later|int}} a Roman or medieval work and {{legends_by_thing.figure|int}} are giant hill figures; {{legends_by_thing.dwelling|int}} say only where the giant lived.

## Files

- `index.html`: the interactive page (Leaflet map, charts). Data are embedded. `header.png`: social card.
- `data/giant_places.csv`: one row per distinct giant-named place: name, source, source id, country, county, coordinates, language of the giant word, the noun the name uses, OS local type, what the feature is, monument class, records merged into it.
- `data/irish_tombs.csv`: every megalithic tomb in the Irish Sites and Monuments Record with a usable position: SMR id, county, townland, class, coordinates, first and latest edition map labels, the name class (`code/terms.py`) and terrain measures.
- `data/giant_names_gb.csv`, `data/giant_monuments_measured.csv`, `data/legends.csv`, `data/legends_measured.csv`, `data/hill_figures.csv`: the giant names, giant monuments, legends (with source, phrase and how each was placed) and giant hill figures, with their measures.
- `data/controls.csv.gz`: the matched names and random points for every British giant name and legend, with measures.
- `data/test_results.csv`: every test. `data/results.json`: every number used on the page, in the paper, the blog post and the collage.
- `code/terms.py` (matching rules, with tests), `code/legends.py` (the legends and sources), `code/dem.py` (terrain reader, from Within Sight), then `01_collect.py`, `02_measure.py`, `03_analyse.py`, `04_build_site.py`, `05_header.py`, run in that order. `release/` holds the paper and blog figure scripts and `reddit/` the collage.

## Method in brief

Matching rule: the English word Giant (Giant, Giants, Giant's, Giants', and the townland form Giantsgrave), the Scottish Gaelic famhair (Famhair, Fhamhair, Fhamair, Famhairean), the Welsh cawr or gawr as words of their own, and Gog Magog. Excluded: Wade and Bran names (surname and common word), and {{counts.n_osm_ie_excluded|int}} OpenStreetMap names in Ireland that use Giant as a brand or adjective. Irish tomb names come from the SMR first-edition and latest-edition map fields; {{counts.n_smr_no_position|int}} SMR records with a placeholder position were dropped. Records within 400 m whose names use the same noun are merged. "Big" is measured from AWS Terrain Tiles (zoom 10): height, height above the mean of rings at 500 m and 1 km, and the share of ground within 1 km lying lower; the Atlas of Hillforts also gives enclosed area. Controls: for each giant tomb or monument, {{k_controls|int}} monuments of the same type from the same 50 km square without a giant name (falling back to 100 km, then any type of the pool within 50 or 100 km); for each British name, {{k_controls|int}} OS names of the same local type from the same 50 km square and {{k_controls|int}} random land points. 2,000 replicate control sets, two-sided chance values.

Caveats: the names say nothing about when or why a place was named; the Irish names are the surveyors' record; the British open gazetteer keeps few antiquity names, so only {{gb_names.n|int}} British names; terrain at about 95 m cells measures prominence, not monument size; the legends come from a few written sources; many tests were run.

## Rerun

Needs Python 3 with pandas, numpy, scipy, shapely 2 and pyproj (and playwright for the header). Shared inputs are read from one folder above this repository (or set `HIST`): `osnames_gb.tsv`, `_data10/ireland_smr_all.json.gz`, `_data10/wd_osm_bundle10.json.gz`, `barrows-of-europe/data/barrows.csv`, `megalith-highway/data/megaliths.csv`, `within-sight/data/forts_visibility.csv`, `stone-circles/data/stone_circles.csv`, `how-roman-is-your-road/data/counties.geojson`, `_data3/ne/geojson/ne_10m_land.geojson`, and the terrain tiles (`DEM_BIN`, `DEM_IDX`, see `code/dem.py`).

## Sources and licence

- Irish monuments: National Monuments Service, Department of Housing, Local Government and Heritage, Sites and Monuments Record (Archaeological Survey of Ireland), CC BY 4.0.
- Place names: OS Open Names. Contains OS data © Crown copyright and database right 2026. Open Government Licence v3.0. Land outline: Office for National Statistics, OGL v3.0.
- OpenStreetMap names and monuments: © OpenStreetMap contributors, ODbL 1.0; Wikidata, CC0 (via https://github.com/Tristan-Hotham/barrows-of-europe and https://github.com/Tristan-Hotham/megalith-highway).
- Hillforts: Lock, G. and Ralston, I. (2017) Atlas of Hillforts of Britain and Ireland, https://hillforts.arch.ox.ac.uk, CC BY-SA 4.0. Stone circles via https://github.com/Tristan-Hotham/stone-circles.
- Legends and hill figures: English Wikipedia, CC BY-SA 4.0 (articles listed in `data/legends.csv`), and English Heritage, "A short history of giants and where to find them" (short quoted phrases).
- Terrain: AWS Terrain Tiles (Mapzen/Tilezen). Natural Earth land (public domain) for the header map. Base map tiles on the page: Esri. Map library: Leaflet.

Derived data (`data/`) and text are released under CC BY-SA 4.0; parts derive from OpenStreetMap under the ODbL. Code (`code/`) is MIT (see `LICENSE`).

## Citation

Hotham, T. (2026) *Giants in the Landscape: did people explain big things with big people?* Data study and paper. Zenodo. https://doi.org/10.5281/zenodo.23691920

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
