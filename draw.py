#!/usr/bin/env python3
"""THE DAILY ATLAS - News Image 20261121, round-5 page for @rojanon11.

A fresh renderer for the round-5 rebuild. The page copies the STRUCTURE
of the edition's number one (measured pixel by pixel in the fleet's
dissection): the date alone as masthead on cream paper, three equal lead
columns, ten uniform mini cards, a small dot-matrix map in the
bottom-left, 27 hard one-line briefs, a DATE CHECK box with dated
discards plus an Unverified clause, and no numbers strip and no tally
bar anywhere. The paper's own name survives only in the claims bar.

Every story, number and date comes from the verified POOL21 pool for
Saturday 21 November 2026: 13 pictured cards + 27 briefs = 40 stories.
Original flat drawings throughout; stdlib + Pillow only; deterministic.
"""

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from mapdata import CONTINENTS

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
SERIF_BLACK = str(FONTS / "DejaVuSerif-Bold.ttf")
SERIF_BOLD = str(FONTS / "LiberationSerif-Bold.ttf")
SANS_BOLD = str(FONTS / "LiberationSans-Bold.ttf")
SANS = str(FONTS / "LiberationSans-Regular.ttf")

W = H = 1024
MX = 14
RIGHT = 1010
CW = RIGHT - MX  # 996 content width

PAPER = (245, 241, 224)
BLACK = (18, 18, 18)
RED = (192, 40, 25)
GREY = (110, 104, 92)
HAIR = (206, 198, 172)

_font_cache = {}


def F(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def tw(draw, text, font):
    return draw.textlength(text, font=font)


def fit_size(draw, text, path, maxw, start, minimum=7):
    size = start
    while size > minimum and tw(draw, text, F(path, size)) > maxw:
        size -= 1
    return size


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if tw(draw, trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, path, start, maxw, max_lines, minimum=8):
    """Shrink until the wrapped text fits max_lines; hard-cut as last resort."""
    size = start
    while size > minimum:
        lines = wrap(draw, text, F(path, size), maxw)
        if len(lines) <= max_lines:
            return F(path, size), lines
        size -= 1
    lines = wrap(draw, text, F(path, minimum), maxw)[:max_lines]
    if lines:
        last = lines[-1]
        while last and tw(draw, last + "..", F(path, minimum)) > maxw:
            last = last[:-1]
        lines[-1] = last + ".."
    return F(path, minimum), lines


# ---------------------------------------------------------------- stories
# slug, chip, location, region-line, headline, deck, lon, lat, scene key
CARDS = [
    ("3 WEAPONS CROSS", "CONFIRMED - AP", "WARSAW, POLAND",
     "EUROPE - CONFLICT",
     "Rutte flies to Warsaw after missiles land",
     "Two missiles and a suspected jet drone came down in the south-east, "
     "a Kh-101 near Nowy Lipowiec. Rutte calls it a \"grave violation\".",
     21.0, 52.2, "jet"),
    ("NO DEAL YET", "REPORTED - AP", "ANTALYA",
     "GLOBAL - CLIMATE TALKS",
     "COP31 runs into overtime, no deal yet",
     "Talks ran past Friday's close into Saturday. The draft drops every "
     "fossil-fuel reference and the $120bn target; a third draft is due.",
     30.7, 36.9, "dome"),
    ("NASDAQ -5.28%", "CONFIRMED - SIMPLELIFE", "NEW YORK",
     "AMERICAS - MARKETS",
     "Wall Street enters correction as AI rout deepens",
     "The S&P 500 fell about 3.7% on Friday, pushing it into correction. "
     "The Nasdaq dropped 5.28% as chip and AI shares plunged.",
     -74.0, 40.7, "chart"),
    ("2 DEAD - 42 HURT", "REPORTED - APPISTOS", "KRYVYI RIH, UKRAINE",
     "EUROPE - WAR",
     "Russian strike kills two, injures 42",
     "Strike kills two and injures 42, four of them children, the city chief says.",
     33.4, 47.9, "blast"),
    ("ATTACHE EXPELLED", "REPORTED - BBC", "COPENHAGEN, DENMARK",
     "EUROPE - SECURITY",
     "Denmark exposes 'assassination plot'",
     "Denmark says Russia planned a bid to kill a rapper; the attache is expelled.",
     12.6, 55.7, "shield"),
    ("400 DRONES - 110 MISSILES", "REPORTED - BBC", "KYIV, UKRAINE",
     "EUROPE - WAR",
     "Russia's barrage: 400 drones, 110 missiles",
     "Eight dead across Ukraine; the Austrian embassy is hit in Kyiv, France protests.",
     30.5, 50.4, "drones"),
    ("372,000 MOVED", "REPORTED - RIDHU TIMES", "ODISHA, INDIA",
     "ASIA - WEATHER",
     "After Akvan: 372,000 moved, no deaths",
     "A day after landfall no deaths are reported; relief under way, schools shut.",
     84.9, 19.3, "storm"),
    ("\u20ac1BN ADOPTED", "CONFIRMED - REUTERS", "BRUSSELS, BELGIUM",
     "EUROPE - AID",
     "EU adopts \u20ac1bn military aid for Ukraine",
     "Via the Peace Facility; Britain pledges 1,000+ drones in a \u00a3260m package.",
     4.3, 50.8, "stars"),
    ("3 NETWORKS HIT", "REPORTED - REUTERS", "NEW YORK",
     "AMERICAS - CYBER",
     "JPMorgan, Visa, Mastercard hit by cyberattack",
     "Incidents at third-party vendors; core payment networks unaffected, banks say.",
     -73.9, 40.8, "bank"),
    ("SNAP ELECTION NEXT", "CONFIRMED - REUTERS", "ULAANBAATAR, MONGOLIA",
     "ASIA - POLITICS",
     "Mongolia's president resigns",
     "The resignation sets up a snap election after a week of turmoil in the capital.",
     106.9, 47.9, "ger"),
    ("GENOCIDE VERDICT", "REPORTED - BBC", "THE HAGUE, NETHERLANDS",
     "GLOBAL - COURTS",
     "Myanmar ruling rattles Israel's Gaza defence",
     "The genocide verdict on Myanmar raises questions over Israel's own case, experts say.",
     4.3, 52.1, "court"),
    ("ANC 31%", "CONFIRMED - BBC", "JOHANNESBURG, SOUTH AFRICA",
     "AFRICA - POLITICS",
     "ANC scrambles after worst result since 1994",
     "The ANC wins 31% of the vote, its worst since 1994; coalition talks now race.",
     28.0, -26.2, "ballot"),
    ("159/1 - DAY TWO", "CONFIRMED - ICC", "WELLINGTON, NEW ZEALAND",
     "OCEANIA - CRICKET",
     "India fight back: 159/1 at stumps, day two",
     "India trail by 209 after the hosts made 368; Nicholls made 175 not out.",
     174.8, -41.3, "cricket"),
]

DAYPARTS = [
    ("OVERNIGHT", "Kryvyi Rih strike: two killed, 42 injured"),
    ("MORNING", "Rutte flies to Warsaw over the missiles"),
    ("MIDDAY", "Antalya: third COP31 draft due after talks"),
    ("AFTERNOON", "Denmark expels the Russian attache"),
    ("EVENING", "Stumps in Wellington: India 159/1"),
]

# number, bold lead-in, tail - all pool briefs 14..40, cut to one line
BRIEFS = [
    (14, "Kathmandu:", "Nepal's leader Balendra Shah faces an India test"),
    (15, "Washington:", "US releases still more UFO footage"),
    (16, "Los Angeles:", "Hyundai unveils the 2027 Elantra at the show"),
    (17, "Cardiff:", "Lauren Price beats Kotaskova, undisputed champion"),
    (18, "Paris:", "three police sentenced over the Zecler beating"),
    (19, "Oxford:", "life, 22 years minimum, for the Thames murder"),
    (20, "New York:", "Nikhil Gupta gets 19+ years in the Sikh plot case"),
    (21, "Cincinnati:", "Fiona the hippo dies after eating a hat"),
    (22, "Washington:", "US sanctions four Iranians over oil revenues"),
    (23, "Hormuz:", "a tanker is struck and on fire in the strait"),
    (24, "Los Angeles:", "jury convicts the man who started Palisades Fire"),
    (25, "Frankfurt:", "ECB names Boone and Brunnermeier for its board"),
    (26, "Buenos Aires:", "Senate backs a disability framework, 71-0"),
    (27, "Riyadh:", "coalition intercepts Houthi missiles overhead"),
    (28, "Barcelona:", "pill hailed as pancreatic breakthrough"),
    (29, "Gaza:", "children appeal for help on World Children's Day"),
    (30, "Madrid:", "Amnesty says police used excess force in the strike"),
    (31, "Rome:", "workers and students march against Meloni's rule"),
    (32, "Jeddah:", "Saudi Arabia warns of thunderstorms to Tuesday"),
    (33, "Kuala Lumpur:", "10,000 Rohingya to go to Turkey for training"),
    (34, "Kharkiv:", "Ukraine says its 'Bear Trap' there is finished"),
    (35, "Islamabad:", "minerals worth $8-10 trillion, minister says"),
    (36, "Singapore:", "US presses it and Malaysia on Iran sanctions"),
    (37, "Paris:", "France seeks a UN council meeting on Kyiv strikes"),
    (38, "Kyiv:", "war tally: 771 Ukrainians killed, 2,300+ missing"),
    (39, "Ankara:", "Turkey welcomes the World Court's Myanmar ruling"),
    (40, "Turin:", "ATP semis set: Alcaraz-Shelton, Zverev-Medvedev"),
]

DATECHECK_LINES = [
    "Left out on purpose - not Saturday's news: Kyiv's three bridges hit (Friday 20 Nov) - Cyclone Akvan's "
    "landfall at Gopalpur (20 Nov) - Asia's AI sell-off, Taipei -6.2% (20 Nov) - the UK-EU reset deal (20 Nov) - "
    "Phillips's 118 in the first innings (20 Nov).",
    "Not yet happened, so not shown: any final COP31 text, the ATP semi-final results, and BepiColombo's "
    "entry into orbit around Mercury (all due today).",
    "Unverified: the suspected jet drone over Poland - named by officials, not independently confirmed, "
    "so it is shown as suspected, never as fact.",
]

FOOTER = ("Every story happened, or was first reported, on Saturday 21 November 2026 \u00b7 "
          "AP \u00b7 BBC \u00b7 Reuters \u00b7 AFP \u00b7 ICC \u00b7 UKMTO \u00b7 OFAC \u00b7 SPA \u00b7 Anadolu \u00b7 "
          "Ukrinform \u00b7 ATP \u00b7 UN \u00b7 Original drawings")


# ---------------------------------------------------------------- scenes
# Each painter fills a (w x 65) tile. Max 3 large elements; the subject is
# at least half the scene height. Bright flat fills keep the page airy.

def _tile(w, colour):
    img = Image.new("RGB", (w, 65), colour)
    return img, ImageDraw.Draw(img)


def sc_jet(w):
    img, d = _tile(w, (243, 208, 148))
    cx, cy = w // 2, 34
    d.polygon([(cx - 78, cy + 6), (cx + 30, cy - 16), (cx + 84, cy - 2),
               (cx + 30, cy + 8), (cx - 40, cy + 14)], fill=(38, 44, 58))
    d.polygon([(cx - 20, cy + 4), (cx - 52, cy + 26), (cx - 30, cy + 26),
               (cx + 6, cy + 10)], fill=(28, 33, 46))
    d.polygon([(cx - 62, cy - 2), (cx - 92, cy - 18), (cx - 84, cy + 2),
               (cx - 66, cy + 8)], fill=(28, 33, 46))
    for i in range(5):
        d.ellipse([cx - 52 + i * 17, cy - 8, cx - 45 + i * 17, cy - 1],
                  fill=(170, 205, 230))
    d.polygon([(w - 58, 8), (w - 20, 22), (w - 52, 26)], fill=RED)
    return img


def sc_dome(w):
    img, d = _tile(w, (168, 216, 200))
    d.ellipse([w - 62, 6, w - 14, 54], fill=(246, 196, 70))
    d.pieslice([18, 14, 150, 96], 180, 360, fill=(240, 244, 238))
    d.rectangle([18, 54, 150, 63], fill=(52, 92, 80))
    d.rectangle([78, 22, 90, 54], fill=(52, 92, 80))
    return img


def sc_chart(w):
    img, d = _tile(w, (196, 222, 244))
    base = 58
    heights = [26, 34, 30, 42, 50]
    for i, hgt in enumerate(heights):
        x = 16 + i * 30
        d.rectangle([x, base - hgt, x + 20, base],
                    fill=(90, 160, 90) if i < 2 else RED)
    pts = [(26, 58 - 30), (56, 58 - 38), (86, 58 - 34), (116, 58 - 46),
           (150, 58 - 54)]
    d.line(pts, fill=BLACK, width=4)
    d.polygon([(150, 4), (168, 16), (146, 18)], fill=RED)
    return img


def sc_blast(w):
    img, d = _tile(w, (244, 178, 120))
    d.rectangle([0, 44, w, 65], fill=(70, 58, 66))
    d.rectangle([10, 20, 52, 65], fill=(52, 44, 56))
    d.rectangle([w - 56, 26, w - 12, 65], fill=(52, 44, 56))
    cx, cy = w // 2, 30
    for ang in range(0, 360, 45):
        import math
        x2 = cx + int(30 * math.cos(math.radians(ang)))
        y2 = cy + int(24 * math.sin(math.radians(ang)))
        d.line([cx, cy, x2, y2], fill=RED, width=4)
    d.ellipse([cx - 12, cy - 10, cx + 12, cy + 10], fill=(250, 220, 90))
    return img


def sc_shield(w):
    img, d = _tile(w, (186, 220, 240))
    cx = w // 2
    d.polygon([(cx - 24, 8), (cx + 24, 8), (cx + 24, 30), (cx, 58),
               (cx - 24, 30)], fill=(206, 48, 40))
    d.polygon([(cx - 17, 14), (cx + 17, 14), (cx + 17, 29), (cx, 49),
               (cx - 17, 29)], fill=(246, 240, 224))
    d.polygon([(cx, 20), (cx + 4, 30), (cx + 14, 30), (cx + 6, 36),
               (cx + 9, 46), (cx, 40), (cx - 9, 46), (cx - 6, 36),
               (cx - 14, 30), (cx - 4, 30)], fill=(240, 190, 50))
    return img


def sc_drones(w):
    img, d = _tile(w, (32, 48, 84))
    d.ellipse([w - 52, 6, w - 20, 38], fill=(238, 232, 200))
    for (cx, cy, s) in [(52, 28, 36), (120, 42, 28), (88, 14, 22)]:
        d.rectangle([cx - s, cy - 3, cx + s, cy + 3], fill=(200, 208, 220))
        d.rectangle([cx - 3, cy - s // 2, cx + 3, cy + s // 2],
                    fill=(200, 208, 220))
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    return img


def sc_storm(w):
    img, d = _tile(w, (172, 198, 216))
    cx, cy = 52, 32
    for r in (26, 19, 12):
        d.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(52, 84, 120),
              width=5)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=RED)
    for x in range(120, w - 12, 22):
        d.line([x, 10, x - 7, 30], fill=(52, 84, 120), width=3)
        d.line([x, 36, x - 7, 56], fill=(52, 84, 120), width=3)
    return img


def sc_stars(w):
    img, d = _tile(w, (64, 102, 178))
    import math
    cx, cy = 52, 32
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x, y = cx + int(21 * math.cos(ang)), cy + int(21 * math.sin(ang))
        d.polygon([(x, y - 6), (x + 2, y - 1), (x + 6, y - 1), (x + 3, y + 3),
                   (x + 4, y + 7), (x, y + 4), (x - 4, y + 7), (x - 3, y + 3),
                   (x - 6, y - 1), (x - 2, y - 1)], fill=(246, 200, 60))
    f = F(SANS_BOLD, 24)
    d.text((110, 20), "\u20ac1BN", font=f, fill=(255, 255, 255))
    return img


def sc_bank(w):
    img, d = _tile(w, (206, 216, 226))
    d.polygon([(26, 6), (w // 2, 22), (w - 26, 6)], fill=(90, 100, 116))
    d.rectangle([26, 22, w - 26, 27], fill=(90, 100, 116))
    for i in range(4):
        x = 40 + i * ((w - 80) // 3)
        d.rectangle([x, 27, x + 10, 56], fill=(240, 242, 244))
    d.rectangle([22, 56, w - 22, 62], fill=(90, 100, 116))
    d.ellipse([w // 2 - 10, 30, w // 2 + 10, 50], outline=RED, width=4)
    return img


def sc_ger(w):
    img, d = _tile(w, (170, 214, 168))
    d.rectangle([0, 48, w, 65], fill=(110, 168, 96))
    cx = w // 2
    d.pieslice([cx - 52, 8, cx + 52, 66], 180, 360, fill=(246, 244, 238))
    d.rectangle([cx - 52, 36, cx + 52, 52], fill=(240, 238, 230))
    d.rectangle([cx - 9, 34, cx + 9, 52], fill=(150, 84, 52))
    d.polygon([(cx + 66, 10), (cx + 96, 16), (cx + 66, 22)], fill=RED)
    d.line([cx + 66, 10, cx + 66, 52], fill=BLACK, width=3)
    return img


def sc_court(w):
    img, d = _tile(w, (216, 208, 188))
    d.polygon([(20, 4), (w - 20, 4), (w - 34, 16), (34, 16)],
              fill=(120, 96, 70))
    for i in range(5):
        x = 34 + i * ((w - 78) // 4)
        d.rectangle([x, 18, x + 9, 52], fill=(246, 242, 232))
    d.rectangle([24, 52, w - 24, 60], fill=(120, 96, 70))
    d.line([w // 2 - 16, 24, w // 2 + 16, 24], fill=BLACK, width=3)
    d.polygon([(w // 2 - 16, 24), (w // 2 - 22, 34), (w // 2 - 10, 34)],
              fill=BLACK)
    d.polygon([(w // 2 + 16, 24), (w // 2 + 10, 34), (w // 2 + 22, 34)],
              fill=BLACK)
    return img


def sc_ballot(w):
    img, d = _tile(w, (244, 206, 140))
    d.rectangle([30, 26, 130, 60], fill=(70, 70, 78))
    d.rectangle([24, 20, 136, 28], fill=(40, 40, 46))
    d.polygon([(58, 20), (76, 2), (96, 20)], fill=(246, 244, 238))
    d.line([66, 12, 72, 18], fill=(30, 150, 70), width=3)
    d.line([72, 18, 88, 6], fill=(30, 150, 70), width=3)
    f = F(SANS_BOLD, 25)
    d.text((142, 18), "31%", font=f, fill=RED)
    return img


def sc_cricket(w):
    img, d = _tile(w, (140, 196, 120))
    d.rectangle([0, 46, w, 65], fill=(104, 168, 88))
    for i, x in enumerate((44, 54, 64)):
        d.rectangle([x, 14, x + 5, 50], fill=(238, 226, 180))
    d.rectangle([40, 12, 70, 16], fill=(238, 226, 180))
    d.polygon([(120, 8), (132, 10), (112, 52), (102, 50)], fill=(196, 150, 84))
    d.ellipse([150, 26, 172, 48], fill=RED)
    return img


SCENES = {"jet": sc_jet, "dome": sc_dome, "chart": sc_chart,
          "blast": sc_blast, "shield": sc_shield, "drones": sc_drones,
          "storm": sc_storm, "stars": sc_stars, "bank": sc_bank,
          "ger": sc_ger, "court": sc_court, "ballot": sc_ballot,
          "cricket": sc_cricket}


# ---------------------------------------------------------------- cards

def draw_card(page, x, y, w, h, idx, lead):
    d = ImageDraw.Draw(page)
    slug, chip, loc, region, head, deck, _lon, _lat, scene = CARDS[idx]
    # scene tile
    tile = SCENES[scene](w)
    page.paste(tile, (x, y))
    td = ImageDraw.Draw(page)
    # slug: black box, top-left inside scene
    s_size = fit_size(td, slug, SANS_BOLD, int(w * 0.52), 11 if lead else 10)
    sf = F(SANS_BOLD, s_size)
    sw = tw(td, slug, sf)
    td.rectangle([x + 4, y + 4, x + 10 + sw, y + 8 + s_size + 5], fill=BLACK)
    td.text((x + 7, y + 6), slug, font=sf, fill=(255, 255, 255))
    # chip: white box, black border, top-right inside scene
    chip = chip.replace(" - ", " \u2013 ")
    c_size = fit_size(td, chip, SANS_BOLD, int(w * 0.46), 9 if lead else 8)
    cf = F(SANS_BOLD, c_size)
    cw_ = tw(td, chip, cf)
    td.rectangle([x + w - 8 - cw_, y + 4, x + w - 4, y + 8 + c_size + 4],
                 fill=(255, 255, 255), outline=BLACK, width=1)
    td.text((x + w - 6 - cw_, y + 6), chip, font=cf, fill=BLACK)
    # location bar: black, full card width
    ly = y + 65
    td.rectangle([x, ly, x + w, ly + 20], fill=BLACK)
    lf = F(SANS_BOLD, fit_size(td, loc, SANS_BOLD, w - 12, 12))
    td.text((x + 6, ly + 4), loc, font=lf, fill=(255, 255, 255))
    # badge row: red filled circle with white number + region in red caps
    by = ly + 23
    r = 10
    td.ellipse([x + 1, by, x + 1 + 2 * r, by + 2 * r], fill=RED)
    nf = F(SANS_BOLD, 12)
    num = str(idx + 1)
    nw = tw(td, num, nf)
    td.text((x + 1 + r - nw / 2, by + 3), num, font=nf, fill=(255, 255, 255))
    region = region.replace(" - ", " \u00b7 ")
    rf = F(SANS_BOLD, fit_size(td, region, SANS_BOLD, w - 30, 12 if lead else 11))
    td.text((x + 27, by + 4), region, font=rf, fill=RED)
    # headline: serif bold
    hy = by + 24
    if lead:
        hf = F(SERIF_BOLD, fit_size(td, head, SERIF_BOLD, w - 2, 17))
        td.text((x + 1, hy), head, font=hf, fill=BLACK)
        hy += 22
        df, lines = fit_lines(td, deck, SANS, 11, w - 2, 3)
        for ln in lines:
            td.text((x + 1, hy), ln, font=df, fill=(40, 38, 34))
            hy += 14
    else:
        hf, lines = fit_lines(td, head, SERIF_BOLD, 13, w - 2, 2)
        for ln in lines:
            td.text((x + 1, hy), ln, font=hf, fill=BLACK)
            hy += 14
        df, lines = fit_lines(td, deck, SANS, 10, w - 2, 2)
        for ln in lines:
            td.text((x + 1, hy), ln, font=df, fill=(40, 38, 34))
            hy += 11.5


# ---------------------------------------------------------------- map

def _inside(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > lat) != (yj > lat)) and \
                (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def draw_map(page, x, y, w, h):
    d = ImageDraw.Draw(page)
    lon0, lon1, lat0, lat1 = -170.0, 180.0, 84.0, -58.0

    def px(lon):
        return x + (lon - lon0) / (lon1 - lon0) * w

    def py(lat):
        return y + (lat0 - lat) / (lat0 - lat1) * h

    step = 5
    yy = y + 2
    while yy < y + h - 1:
        lat = lat0 - (yy - y) / h * (lat0 - lat1)
        xx = x + 2
        while xx < x + w - 1:
            lon = lon0 + (xx - x) / w * (lon1 - lon0)
            for _name, (colour, polys) in CONTINENTS.items():
                if any(_inside(lon, lat, p) for p in polys):
                    d.ellipse([xx - 1.6, yy - 1.6, xx + 1.6, yy + 1.6],
                              fill=colour)
                    break
            xx += step
        yy += step
    # numbered pins for the 13 pictured stories
    offsets = {8: (8, 6), 10: (7, -7), 2: (-2, 7)}
    nf = F(SANS_BOLD, 8)
    for idx, card in enumerate(CARDS):
        lon, lat = card[6], card[7]
        cx, cy = px(lon), py(lat)
        ox, oy = offsets.get(idx, (0, 0))
        cx, cy = cx + ox, cy + oy
        d.ellipse([cx - 6.5, cy - 6.5, cx + 6.5, cy + 6.5],
                  fill=(255, 255, 255), outline=RED, width=2)
        num = str(idx + 1)
        d.text((cx - tw(d, num, nf) / 2, cy - 4.5), num, font=nf, fill=BLACK)
    # legend, two rows under the map
    ly = y + h + 4
    lx = x
    lf = F(SANS_BOLD, 9)
    items = [(name, CONTINENTS[name][0]) for name in
             ("EUROPE", "ASIA", "AMERICAS", "MIDEAST", "AFRICA", "OCEANIA")]
    items.append(("GLOBAL", (120, 120, 120)))
    for i, (name, colour) in enumerate(items):
        if i == 4:
            ly += 13
            lx = x
        d.rectangle([lx, ly + 1, lx + 8, ly + 9], fill=colour)
        d.text((lx + 11, ly), name, font=lf, fill=BLACK)
        lx += 11 + tw(d, name, lf) + 12


# ---------------------------------------------------------------- page

def build():
    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)

    # claims bar
    lf = F(SANS_BOLD, 15)
    d.text((MX, 7), "THE DAILY ATLAS", font=lf, fill=RED)
    claims = "40 STORIES \u00b7 13 DRAWN \u00b7 6 CONTINENTS \u00b7 ALL FROM 21 NOVEMBER"
    cf = F(SANS_BOLD, fit_size(d, claims, SANS_BOLD, 640, 13))
    d.text((RIGHT - tw(d, claims, cf), 8), claims, font=cf, fill=BLACK)
    d.rectangle([MX, 29, RIGHT, 31], fill=RED)

    # masthead: the date only, serif title case, natural width
    date = "Saturday 21 November 2026"
    msize = fit_size(d, date, SERIF_BOLD, 950, 78)
    mf = F(SERIF_BOLD, msize)
    cap = mf.getmask("S").getbbox()[3]
    d.text(((W - tw(d, date, mf)) / 2, 40), date, font=mf, fill=BLACK)
    print("masthead size", msize, "cap px", cap, "width",
          round(tw(d, date, mf)))

    # day-parts bar
    py0, py1 = 122, 180
    d.rectangle([MX, py0, MX + 118, py1], fill=RED)
    pf = F(SANS_BOLD, 13)
    d.text((MX + 10, py0 + 9), "THE DAY IN", font=pf, fill=(255, 255, 255))
    d.text((MX + 10, py0 + 28), "PARTS", font=pf, fill=(255, 255, 255))
    seg_x = MX + 126
    seg_w = (RIGHT - seg_x) // 5
    for i, (label, head) in enumerate(DAYPARTS):
        sx = seg_x + i * seg_w
        if i:
            d.line([sx - 5, py0 + 4, sx - 5, py1 - 4], fill=HAIR, width=1)
        d.text((sx, py0 + 3), label, font=F(SANS_BOLD, 11), fill=RED)
        hf, lines = fit_lines(d, head, SANS, 11, seg_w - 12, 2)
        yy = py0 + 19
        for ln in lines:
            d.text((sx, yy), ln, font=hf, fill=BLACK)
            yy += 13

    # leads: three equal columns
    lead_y, lead_h = 190, 187
    lead_w = (CW - 16) // 3
    for i in range(3):
        draw_card(page, MX + i * (lead_w + 8), lead_y, lead_w, lead_h,
                  i, True)
    d = ImageDraw.Draw(page)

    # minis: 2 rows x 5
    mini_w = (CW - 32) // 5
    for r in range(2):
        for c in range(5):
            idx = 3 + r * 5 + c
            draw_card(page, MX + c * (mini_w + 8), 386 + r * 164,
                      mini_w, 158, idx, False)
    d = ImageDraw.Draw(page)

    # section header
    hy = 722
    d.text((MX, hy), "WHERE IT HAPPENED", font=F(SANS_BOLD, 15), fill=BLACK)
    also = "ALSO ON SATURDAY 21 NOVEMBER"
    af = F(SANS_BOLD, 13)
    d.text((RIGHT - tw(d, also, af), hy + 1), also, font=af, fill=RED)
    d.line([MX, hy + 20, RIGHT, hy + 20], fill=HAIR, width=1)

    # map bottom-left, ~40% width
    draw_map(page, MX, 748, 396, 118)
    d = ImageDraw.Draw(page)

    # briefs: two columns, hard one line each, pitch 10.5
    bx = [425, 722]
    col_w = [288, 288]
    per_col = [BRIEFS[:14], BRIEFS[14:]]
    nf = F(SANS_BOLD, 10)
    bf = F(SANS_BOLD, 10)
    rf = F(SANS, 10)
    for ci, col in enumerate(per_col):
        for ri, (num, lead_in, tail) in enumerate(col):
            yy = 748 + ri * 10.5
            x0 = bx[ci]
            ns = str(num)
            d.text((x0, yy), ns, font=nf, fill=RED)
            x1 = x0 + tw(d, ns, nf) + 4
            d.text((x1, yy), lead_in, font=bf, fill=BLACK)
            x2 = x1 + tw(d, lead_in, bf) + 3
            avail = bx[ci] + col_w[ci] - x2
            t = tail
            while t and tw(d, t, rf) > avail:
                t = t.rsplit(" ", 1)[0] if " " in t else t[:-1]
            d.text((x2, yy), t, font=rf, fill=(30, 28, 26))

    # date check
    dy0, dy1 = 916, 986
    d.rectangle([MX, dy0, RIGHT, dy1], outline=RED, width=2)
    d.rectangle([MX, dy0, MX + 92, dy1], fill=RED)
    df2 = F(SANS_BOLD, 14)
    d.text((MX + 12, dy0 + 14), "DATE", font=df2, fill=(255, 255, 255))
    d.text((MX + 12, dy0 + 34), "CHECK", font=df2, fill=(255, 255, 255))
    tf = F(SANS, 11)
    yy = dy0 + 7
    for raw in DATECHECK_LINES:
        for ln in wrap(d, raw, tf, RIGHT - (MX + 104) - 8):
            d.text((MX + 104, yy), ln, font=tf, fill=BLACK)
            yy += 14

    # footer
    d.line([MX, 994, RIGHT, 994], fill=BLACK, width=1)
    ff = F(SANS, fit_size(d, FOOTER, SANS, CW, 10))
    d.text((MX, 1000), FOOTER, font=ff, fill=BLACK)

    out = HERE / "entry.png"
    page.quantize(colors=256, method=Image.MEDIANCUT,
                  dither=Image.FLOYDSTEINBERG).save(out, optimize=True)
    small = page.resize((300, 300), Image.LANCZOS)
    small.quantize(colors=256, method=Image.MEDIANCUT).save(
        HERE / "entry-300.png", optimize=True)
    print("saved", out, out.stat().st_size, "bytes")
    return page


if __name__ == "__main__":
    build()
