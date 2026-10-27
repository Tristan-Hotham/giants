"""Named giants of legend and the places their stories sit.

Each legend is tied to a place by a written source that I read on 27 October 2026. "phrase" is a short quotation
or close paraphrase of the sentence in that source that names the place. "explains" is what the story accounts for,
in my own words, and "thing" sorts that into:
  natural      a natural landform (gorge, island, hill, mountain, coastal rock, bay)
  prehistoric  a prehistoric monument (hillfort, stone circle, cairn)
  later        a Roman or medieval structure (road, castle, church grave or cross)
  figure       a hill figure of a giant
  dwelling     the story says only that the giant lived or sat there
Placement ("os"): (name, county) of the OS Open Names feature, with an optional (lat, lon) to choose between features of
the same name in one county. Where OS Open Names has no such feature, "at" gives coordinates from a named dataset on disk.
Sources:
  WHF  Wikipedia, Hill figure (wikitext of 27 Oct 2026)          WCG  Wikipedia, Cerne Abbas Giant
  WLM  Wikipedia, Long Man of Wilmington                           WGV  Wikipedia, Goram and Vincent (read 27 Oct 2026)
  WWA  Wikipedia, Wade (folklore)                                  WCO  Wikipedia, Cormoran
  WJK  Wikipedia, Jack the Giant Killer                            WBR  Wikipedia, Brân the Blessed
  WWG  Wikipedia, Giants (Welsh folklore) (read 27 Oct 2026)       WGC  Wikipedia, Giant's Causeway
  WPH  Wikipedia, Penhill Giant (read 27 Oct 2026)                 WJL  Wikipedia, Jack o' Legs (read 27 Oct 2026)
  WTH  Wikipedia, Tom Hickathrift (read 27 Oct 2026)               WBD  Wikipedia, Bolster Day (read 27 Oct 2026)
  EH   English Heritage, "A short history of giants and where to find them" (blog, read 27 Oct 2026)
"""

SRC = {
    "WHF": ("Wikipedia: Hill figure", "https://en.wikipedia.org/wiki/Hill_figure"),
    "WCG": ("Wikipedia: Cerne Abbas Giant", "https://en.wikipedia.org/wiki/Cerne_Abbas_Giant"),
    "WLM": ("Wikipedia: Long Man of Wilmington", "https://en.wikipedia.org/wiki/Long_Man_of_Wilmington"),
    "WGV": ("Wikipedia: Goram and Vincent", "https://en.wikipedia.org/wiki/Goram_and_Vincent"),
    "WWA": ("Wikipedia: Wade (folklore)", "https://en.wikipedia.org/wiki/Wade_(folklore)"),
    "WCO": ("Wikipedia: Cormoran", "https://en.wikipedia.org/wiki/Cormoran"),
    "WJK": ("Wikipedia: Jack the Giant Killer", "https://en.wikipedia.org/wiki/Jack_the_Giant_Killer"),
    "WBR": ("Wikipedia: Brân the Blessed", "https://en.wikipedia.org/wiki/Br%C3%A2n_the_Blessed"),
    "WWG": ("Wikipedia: Giants (Welsh folklore)", "https://en.wikipedia.org/wiki/Giants_(Welsh_folklore)"),
    "WGC": ("Wikipedia: Giant's Causeway", "https://en.wikipedia.org/wiki/Giant%27s_Causeway"),
    "WPH": ("Wikipedia: Penhill Giant", "https://en.wikipedia.org/wiki/Penhill_Giant"),
    "WJL": ("Wikipedia: Jack o' Legs", "https://en.wikipedia.org/wiki/Jack_o%27_Legs"),
    "WTH": ("Wikipedia: Tom Hickathrift", "https://en.wikipedia.org/wiki/Tom_Hickathrift"),
    "WBD": ("Wikipedia: Bolster Day", "https://en.wikipedia.org/wiki/Bolster_Day"),
    "EH": ("English Heritage: A short history of giants and where to find them",
           "https://www.english-heritage.org.uk/visit/inspire-me/blog/articles/a-short-history-of-giants-and-where-to-find-them/"),
}

# at: (lat, lon, "where the coordinates come from")
ATLAS = "Atlas of Hillforts of Britain and Ireland (as used in Within Sight), site "
WD = "Wikidata item coordinates (UK structures bundle), "
LEGENDS = [
    dict(id="cerne", giant="The Cerne Abbas Giant", region="Dorset", thing="figure", explains="a chalk figure of a giant with a club, cut on the hill",
         src="WHF", phrase="a hill figure of a giant naked man", os=("Giant Hill", "Dorset")),
    dict(id="longman", giant="The Long Man of Wilmington", region="East Sussex", thing="figure", explains="a chalk outline of a giant holding two staves",
         src="WLM", phrase="located on one of the steep slopes of Windover Hill", os=("Windover Hill", "East Sussex")),
    dict(id="firle", giant="The giant of Firle Beacon", region="East Sussex", thing="figure", explains="the Long Man marks where a giant fell, killed by a hammer thrown from Firle Beacon",
         src="WHF", phrase="the giant on Firle Beacon threw his hammer at the Wilmington giant and killed him", os=("Firle Beacon", "East Sussex")),
    dict(id="hoe", giant="Gogmagog (and Corineus), Plymouth Hoe", region="Devon", thing="figure", explains="lost turf-cut figures of two giants, before 1486 to the late 1660s",
         src="WHF", phrase="large outline images of the two giants ... had for a long time been cut into the turf of Plymouth Hoe", os=("Plymouth", "City of Plymouth")),
    dict(id="wandlebury", giant="Gogmagog, Wandlebury Hill", region="Cambridgeshire", thing="figure", explains="a lost giant figure at Wandlebury, before 1605 to around 1730",
         src="WHF", phrase="Wandlebury Hill Gogmagog (lost figures table)", at=(52.15888, 0.18288, ATLAS + "3025 Wandlebury Camp")),
    dict(id="hindover", giant="The Giant of Hindover Hill", region="East Sussex", thing="figure", explains="a lost chalk giant beside the old Litlington White Horse",
         src="WHF", phrase="a lost chalk hill figure ... on Hindover Hill in Litlington", os=("Litlington", "East Sussex")),
    dict(id="ghyst", giant="Ghyst", region="Bristol", thing="prehistoric", explains="the hillfort on Clifton Down, above St Vincent's Rocks",
         src="WGV", phrase="a hillfort above it \"founded by a certain giant called Ghyst\" (William Worcester, 1480)", at=(51.457132, -2.62664, ATLAS + "4035 Clifton Down Camp")),
    dict(id="avon", giant="Vincent and Goram", region="Bristol", thing="natural", explains="the Avon Gorge, dug by two giant brothers competing for the giantess Avona",
         src="WGV", phrase="the Avon Gorge through which the Avon now flows", os=("Avon Gorge", "North Somerset")),
    dict(id="henbury", giant="Goram", region="Bristol", thing="natural", explains="the Hazel Brook gorge at Henbury, Goram's Chair and the Giant's Footprint",
         src="WGV", phrase="The Giant's Footprint in the woods above Henbury gorge", os=("Henbury", "City of Bristol")),
    dict(id="holms", giant="Goram", region="Bristol Channel", thing="natural", explains="Steep Holm and Flat Holm, the drowned giant's head and shoulder",
         src="WGV", phrase="Steep Holm and Flat Holm, are his head and shoulder", os=("Steep Holm", "North Somerset")),
    dict(id="maes", giant="Goram or Vincent", region="Somerset", thing="prehistoric", explains="Maes Knoll hillfort and the Wansdyke, dug by accident",
         src="WGV", phrase="One or the other giant is said to have created Maes Knoll hillfort", at=(51.392023, -2.57559, ATLAS + "3970 Maes Knoll Camp")),
    dict(id="stantondrew", giant="Vincent", region="Somerset", thing="prehistoric", explains="the Stanton Drew stone circles",
         src="WGV", phrase="did some other major construction work like the Stanton Drew stone circles", at=(51.367082, -2.576885, "stone circles of Britain and Ireland (Stone Circles project), Stanton Drew Great Circle")),
    dict(id="stonehenge", giant="The giants of Geoffrey of Monmouth", region="Wiltshire", thing="prehistoric", explains="Stonehenge, whose stones giants first brought from Africa to Ireland",
         src="EH", phrase="the stones \"was originally brought from Africa to Mount Killaurus in Ireland by giants\"", at=(51.17883, -1.82707, "stone circles of Britain and Ireland (Stone Circles project), Stonehenge")),
    dict(id="wade", giant="Wade and his wife Bell", region="North Yorkshire", thing="later", explains="the road called Wade's Causeway, and a hammer thrown over the moors",
         src="WWA", phrase="A tale was told of Sleights Moor in Eskdale ... Wade's Causeway ... also said to have been built in this manner", os=("Sleights Moor", "North Yorkshire")),
    dict(id="mulgrave", giant="Wade", region="North Yorkshire", thing="later", explains="Mulgrave Castle, and stones called Wade's grave",
         src="WWA", phrase="Stones at Mulgrave near Whitby were said to be the grave of the dead sea-giant", at=(54.4935, -0.705598, WD + "Q6933971 Mulgrave Castle")),
    dict(id="pickering", giant="Bell, Wade's wife", region="North Yorkshire", thing="later", explains="Pickering Castle",
         src="EH", phrase="is said to have erected Pickering Castle nearby", at=(54.2502, -0.775923, WD + "Q7190805 Pickering Castle")),
    dict(id="mount", giant="Cormoran", region="Cornwall", thing="natural", explains="St Michael's Mount, built of granite carried from the moors",
         src="WCO", phrase="attributed with constructing St. Michael's Mount, a tidal island", os=("St Michael's Mount", "Cornwall")),
    dict(id="chapelrock", giant="Cormelian, Cormoran's wife", region="Cornwall", thing="natural", explains="Chapel Rock, stones that fell from her apron",
         src="WCO", phrase="The stones fell from her apron and formed Chapel Rock", os=("Chapel Rock", "Cornwall", (50.122, -5.476))),
    dict(id="trencrom", giant="Trecobben", region="Cornwall", thing="prehistoric", explains="the giant of Trencrom Hill, whose hillfort crowns the top",
         src="WJK", phrase="Trecobben, the giant of Trencrom Hill (near St Ives)", at=(50.173744, -5.477641, ATLAS + "637 Trencrom Castle")),
    dict(id="blunderbore", giant="Blunderbore", region="Cornwall", thing="dwelling", explains="a giant who lived at Ludgvan Lese and preyed on travellers",
         src="WJK", phrase="living in Ludgvan Lese (a manor in Ludgvan)", os=("Ludgvan", "Cornwall")),
    dict(id="bolster", giant="Bolster", region="Cornwall", thing="dwelling", explains="a giant of the St Agnes cliffs, who fought his challengers at Chapel Porth",
         src="WBD", phrase="Legend says that the fights took place at Chapel Porth", os=("Chapel Porth", "Cornwall")),
    dict(id="penhill", giant="The Penhill Giant", region="North Yorkshire", thing="dwelling", explains="a giant who lived in a fortress on Penhill",
         src="WPH", phrase="said to have lived in a fortress on Penhill in Wensleydale", os=("Penhill", "North Yorkshire")),
    dict(id="jackolegs", giant="Jack o' Legs", region="Hertfordshire", thing="later", explains="a giant's grave in Weston churchyard, two stones far apart",
         src="WJL", phrase="His supposed grave is in the churchyard of Holy Trinity Church, Weston", os=("Weston", "Hertfordshire")),
    dict(id="hickathrift", giant="Tom Hickathrift", region="Norfolk", thing="later", explains="the stone cross called Hickathrift's Candlesticks, Tilney All Saints",
         src="WTH", phrase="A large stone cross remains in Tilney All Saints churchyard", os=("Tilney All Saints", "Norfolk")),
    dict(id="stokesay", giant="Two giant brothers", region="Shropshire", thing="later", explains="treasure under Stokesay Castle, guarded by a raven",
         src="EH", phrase="Stokesay Castle ... Two giant brothers shared a treasure chest", at=(52.4303, -2.8313, WD + "Q7618555 Stokesay Castle")),
    dict(id="bran", giant="Brân the Blessed", region="Gwynedd", thing="dwelling", explains="the giant king sitting on the rocks at Harlech",
         src="WBR", phrase="King Bran was sitting on the rocky shore at Harlech", os=("Harlech", "Gwynedd - Gwynedd")),
    dict(id="branhead", giant="Brân the Blessed", region="London", thing="later", explains="Brân's head, buried on the White Hill where the White Tower stands",
         src="WBR", phrase="Brân's head was buried in London where the White Tower now stands", at=(51.5081, -0.075977, WD + "Q1528473 White Tower")),
    dict(id="idris", giant="Idris Gawr", region="Gwynedd", thing="dwelling", explains="Idris Gawr, the giant of Cadair Idris",
         src="WWG", phrase="Idris Gawr of Cader Idris", os=("Cadair Idris", "Gwynedd - Gwynedd")),
    dict(id="rhitta", giant="Rhitta Gawr", region="Gwynedd", thing="natural", explains="Yr Wyddfa (Snowdon), the mountain named for the giant buried under a cairn",
         src="WWG", phrase="Arthur commands that a cairn be built over his body ... Gwyddfa Rhudda became known as Yr Wyddfa", os=("Yr Wyddfa", "Gwynedd - Gwynedd")),
    dict(id="maelor", giant="Maelor Gawr", region="Ceredigion", thing="dwelling", explains="the giant of Castell Maelor, now Penparcau",
         src="WWG", phrase="the giant of Castell Maelor (now the village of Penparcau)", os=("Penparcau", "Sir Ceredigion - Ceredigion")),
    dict(id="cribwr", giant="Cribwr", region="Bridgend", thing="dwelling", explains="a giant who lived at Castell Cefn Cribwr",
         src="WWG", phrase="lived in Castell Cefn Cribwr in Morgannwg", os=("Cefn Cribwr", "Pen-y-bont ar Ogwr - Bridgend")),
    dict(id="canthrig", giant="Canthrig Bwt", region="Gwynedd", thing="dwelling", explains="a giantess who lived under a great stone in Nant Peris",
         src="WWG", phrase="lived under a great stone in Nant Peris", os=("Nant Peris", "Gwynedd - Gwynedd", (53.10547, -4.07983))),
    dict(id="causeway", giant="Fionn mac Cumhaill and Benandonner", region="County Antrim", thing="natural", explains="the Giant's Causeway, built across the North Channel",
         src="WGC", phrase="the columns are the remains of a causeway built by a giant", at=(55.24083333, -6.51166667, "English Wikipedia article coordinates, Giant's Causeway")),
]
