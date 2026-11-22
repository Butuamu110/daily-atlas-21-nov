#!/usr/bin/env python3
"""THE DAILY ATLAS — News Image 20261121, round-4 page for @rojanon11.

One self-contained renderer: it paints a full broadsheet front page —
"THE WORLD IN ONE DAY, SATURDAY 21 NOVEMBER 2026" — onto a 1024x1024
canvas and saves it as entry.png next to this file. The design is a
"midnight atlas": a deep-navy masthead carrying the paper's name as the
visual anchor, a gold hook band with the day's top three stories, and
(layout C, the duel winner) a wide world-map banner across the middle
of the page with the briefs in two columns at the foot.

Every fact on the page comes from the verified POOL21 pool for
Saturday 21 November 2026 and from nowhere else. In particular the EU
ADOPTED €1bn of military aid for Ukraine through the Peace Facility —
the pool is explicit that the figure is one billion, adopted, and any
larger "paid" figure is a known drift to keep off the page.

Usage: python3 draw.py [A|B|C]   (default C; A and B are the losing
duel layouts, kept so the duel can be re-run; ALL writes all three)
Deterministic: Python stdlib + Pillow only, no network, no clock.
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

from mapdata import WORLD

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- canvas
PAGE = 1024                 # the page is square: width == height
EDGE = 24                   # outer margin on every side
SPAN = PAGE - 2 * EDGE      # usable width inside the margins

# ---------------------------------------------------------------- palette
PAPER_BG  = (246, 243, 236)  # warm off-white page background
CARD_FACE = (255, 253, 247)  # near-white panel fill (date-check box)
INK_DARK  = (22, 30, 44)     # body ink, a near-black navy
DEEP_NAVY = (16, 32, 56)     # masthead and map sea
NAVY_SOFT = (24, 48, 80)     # graticule lines on the map
GOLDEN    = (198, 152, 46)   # hook band, masthead rule
BURGUNDY  = (140, 47, 57)    # accents, data labels, big figures
RULE_GREY = (190, 182, 160)  # hairlines between bands
CARD_EDGE = (198, 190, 168)  # outline around each story strip
LAND_SAGE = (172, 198, 178)  # continent fill on the navy map
CREAM_TXT = (243, 236, 218)  # light text on navy

REGION_TINTS = {
    "EUROPE":   (176, 58, 46),
    "ASIA":     (29, 111, 184),
    "MIDEAST":  (125, 60, 152),
    "AFRICA":   (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA":  (20, 143, 119),
    "GLOBAL":   (93, 109, 126),
}

# ---------------------------------------------------------------- type
class TypeKit:
    """Lazy font loader with a (file, size) cache.

    The page uses three faces: Playfair Display 900 for headlines and
    big figures, Archivo Bold for kickers/labels, Archivo Medium for
    body text. Fonts live in the fonts/ folder beside this file.
    """

    def __init__(self, folder):
        self._folder = folder
        self._loaded = {}

    def _face(self, filename, size):
        key = (filename, size)
        if key not in self._loaded:
            path = os.path.join(self._folder, filename)
            self._loaded[key] = ImageFont.truetype(path, size)
        return self._loaded[key]

    def playfair(self, size):
        return self._face("PlayfairDisplay-900.ttf", size)

    def bold(self, size):
        return self._face("Archivo-Bold.ttf", size)

    def medium(self, size):
        return self._face("Archivo-Medium.ttf", size)


TYPE = TypeKit(os.path.join(HERE, "fonts"))


# ---------------------------------------------------------------- text maths
def measure(d, s, f):
    """Pixel width of string s set in font f."""
    return d.textlength(s, font=f)


def wrap_lines(d, s, f, maxw):
    """Greedy word wrap: pack words until the next would exceed maxw."""
    lines = []
    current = ""
    for word in s.split():
        trial = (current + " " + word).strip()
        if measure(d, trial, f) <= maxw or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def shrink_font(d, s, start, maxw, floor=8):
    """Largest Archivo Bold at or below `start` that fits s in maxw."""
    size = start
    while size > floor and measure(d, s, TYPE.bold(size)) > maxw:
        size -= 1
    return TYPE.bold(size)


def centred(d, cx, y, s, f, fill):
    """Draw s horizontally centred on cx at height y."""
    d.text((cx - measure(d, s, f) / 2, y), s, font=f, fill=fill)


# ---------------------------------------------------------------- page data
# The "Day in Numbers" strip: (big figure, caption). Every figure is
# bound to one of the pictured stories below.
FIGURE_STRIP = [
    ("3",       "weapons cross into Poland: two missiles and a jet drone"),
    ("42",      "injured in the Kryvyi Rih strike, four of them children"),
    ("-5.28%",  "Nasdaq's fall at Friday's close"),
    ("372,000", "people moved to shelters as Akvan hit"),
    ("€1BN",    "EU military aid adopted for Ukraine"),
    ("159/1",   "India at stumps in Wellington"),
]

# The UTC day timeline across the top of the page: (slot, event).
DAY_TIMELINE = [
    ("OVERNIGHT", "Kryvyi Rih strike: two killed, 42 injured"),
    ("MORNING",   "Rutte flies to Warsaw over the missiles"),
    ("MIDDAY",    "Antalya: third COP31 draft due after overnight talks"),
    ("AFTERNOON", "Denmark expels the Russian attache"),
    ("EVENING",   "Stumps in Wellington: India 159/1"),
]

# Story counts per region, shown as the coloured chip row.
REGION_TALLY = [("EUROPE", 16), ("ASIA", 6), ("AMERICAS", 8), ("MIDEAST", 6),
                ("AFRICA", 1), ("OCEANIA", 1), ("GLOBAL", 2)]


# ---------------------------------------------------------------- stories
def story(no, place, region, topic, headline, deck, tag, label, caption,
          lon, lat, scene):
    """One pictured story card, as a named-field record."""
    return {
        "no": no, "place": place, "region": region, "topic": topic,
        "headline": headline, "deck": deck, "tag": tag, "label": label,
        "caption": caption, "lon": lon, "lat": lat, "scene": scene,
    }


STORIES = [
    story(1, "WARSAW, POLAND", "EUROPE", "WAR",
          "Rutte flies to Warsaw after missiles land",
          "Two missiles and a suspected jet drone came down in the south-east, a Kh-101 near Nowy Lipowiec. Rutte calls it a “grave violation”; Tusk calls it a deliberate provocation. (AP)",
          "AP - SOFX", "3 WEAPONS CROSS", "WARSAW · MISSILES DOWN",
          21.0, 52.2, "field"),
    story(2, "ANTALYA", "GLOBAL", "CLIMATE",
          "COP31 runs into overtime with no deal yet",
          "Talks ran past Friday's scheduled close into Saturday. The draft drops every fossil-fuel reference and the $120bn finance target; a third draft is due this morning. (AP)",
          "Ongoing - AP", "NO DEAL YET", "ANTALYA · OVERTIME TALKS",
          30.7, 36.9, "cop"),
    story(3, "NEW YORK", "AMERICAS", "MARKETS",
          "Wall Street enters correction as AI rout deepens",
          "The S&P 500 fell about 3.7% on Friday, pushing it into correction territory. The Nasdaq dropped 5.28% as chip and AI shares plunged. (SimpleLife)",
          "Friday's close", "NASDAQ -5.28%", "NEW YORK · FRIDAY'S CLOSE",
          -74.0, 40.7, "markets"),
    story(4, "KRYVYI RIH", "EUROPE", "WAR",
          "Russian strike kills two, injures 42",
          "An overnight strike kills two and injures 42, four of them children, the city's military chief says. One of Russia's largest attacks of the war. (AppiStos)",
          "City chief says", "2 DEAD - 42 HURT", "KRYVYI RIH · OVERNIGHT STRIKE",
          33.4, 47.9, "blast"),
    story(5, "COPENHAGEN", "EUROPE", "SECURITY",
          "Denmark exposes 'assassination plot'",
          "Russia 'planned and initiated' a bid to kill a Ukrainian-American rapper near Copenhagen, Denmark says. The Russian attache is expelled. (BBC)",
          "Denmark says - BBC", "ATTACHE EXPELLED", "COPENHAGEN · PLOT EXPOSED",
          12.6, 55.7, "target"),
    story(6, "KYIV", "EUROPE", "WAR",
          "Russia's barrage: 400 drones, 110 missiles",
          "At least eight dead across Ukraine in the overnight barrage. The Austrian embassy is hit in Kyiv; France calls for a UN Security Council meeting. (BBC)",
          "Officials' count", "400 DRONES - 110 MISSILES", "KYIV · OVERNIGHT BARRAGE",
          30.5, 50.4, "intercept"),
    story(7, "ODISHA, INDIA", "ASIA", "STORM",
          "After Akvan: 372,000 moved, no deaths",
          "A day after landfall, no deaths reported and relief is under way. The storm weakens to a depression; schools shut through Saturday. (Ridhu Times)",
          "Relief reports", "372,000 MOVED", "ODISHA · AFTER AKVAN",
          84.9, 19.3, "cyclone"),
    story(8, "BRUSSELS", "EUROPE", "DEFENCE",
          "EU adopts €1bn military aid for Ukraine",
          "Joint buying runs via the Peace Facility. Britain pledges 1,000+ drones in a £260m package alongside the EU deal. (Reuters)",
          "Adopted - EU", "€1BN ADOPTED", "BRUSSELS · AID ADOPTED",
          4.3, 50.8, "flags"),
    story(9, "NEW YORK", "AMERICAS", "CYBER",
          "JPMorgan, Visa, Mastercard hit by cyberattack",
          "The banks report incidents at third-party vendors. Their core payment networks are unaffected, they say. (Reuters)",
          "Banks say", "3 NETWORKS HIT", "NEW YORK · PAYMENT NETWORKS",
          -73.9, 40.8, "cyber"),
    story(10, "ULAANBAATAR", "ASIA", "POLITICS",
          "Mongolia's president resigns",
          "The resignation sets the stage for a snap election. It caps a week of political turmoil in the capital. (Reuters)",
          "Capital reports", "SNAP ELECTION NEXT", "ULAANBAATAR · RESIGNATION",
          106.9, 47.9, "steppe"),
    story(11, "THE HAGUE", "GLOBAL", "LAW",
          "Myanmar ruling rattles Israel's Gaza defence",
          "The world court's genocide verdict against Myanmar raises questions in Jerusalem over its own case, experts say. Ruling came on Thursday. (BBC)",
          "Experts say", "GENOCIDE VERDICT", "THE HAGUE · WORLD COURT",
          4.3, 52.1, "court"),
    story(12, "JOHANNESBURG", "AFRICA", "POLITICS",
          "ANC scrambles after worst result since 1994",
          "The ANC wins 31% of the vote, its worst since 1994. It now races for coalition deals to stay in government. (BBC)",
          "Count - BBC", "ANC 31%", "JOHANNESBURG · THE COUNT",
          28.0, -26.2, "ballot"),
    story(13, "WELLINGTON", "OCEANIA", "CRICKET",
          "India fight back: 159/1 at stumps, day two",
          "India trail New Zealand by 209 in the first Test after the hosts made 368. Nicholls made 175 not out for the hosts. (ICC)",
          "Scorecard - ICC", "159/1 - DAY TWO", "WELLINGTON · DAY TWO",
          174.8, -41.3, "cricket"),
]


# ---------------------------------------------------------------- briefs
def brief(no, text, region, lon, lat):
    """One unpictured brief: a line of text plus its map dot position."""
    return {"no": no, "text": text, "region": region, "lon": lon, "lat": lat}


BRIEFS = [
    brief(14, "Kathmandu Nepal's new leader Balendra Shah faces an India test (BBC)", "ASIA", 85.3, 27.7),
    brief(15, "Washington US releases more UFO footage filmed in the Middle East (BBC)", "AMERICAS", -77.0, 38.9),
    brief(16, "Los Angeles Hyundai unveils the 2027 Elantra at the auto show (Fast Company)", "AMERICAS", -118.2, 34.1),
    brief(17, "Cardiff Lauren Price beats Kotaskova to become undisputed champion (BBC)", "EUROPE", -3.2, 51.5),
    brief(18, "Paris Three police are sentenced over the beating of Michel Zecler (BBC)", "EUROPE", 2.4, 48.9),
    brief(19, "Oxford Life, 22 years minimum, for the Thames drowning murder (BBC)", "EUROPE", -1.3, 51.8),
    brief(20, "New York Nikhil Gupta gets 19+ years over the Sikh murder plot (BBC)", "AMERICAS", -74.0, 40.7),
    brief(21, "Cincinnati Fiona the hippo dies after eating a hat (AP)", "AMERICAS", -84.5, 39.1),
    brief(22, "Washington US sanctions four Iranians over oil revenues (OFAC)", "MIDEAST", -77.1, 38.8),
    brief(23, "Hormuz A tanker is struck and on fire in the Strait of Hormuz (UKMTO)", "MIDEAST", 56.3, 26.6),
    brief(24, "Los Angeles A jury convicts the man who started the Palisades Fire (AP)", "AMERICAS", -118.3, 34.0),
    brief(25, "Frankfurt ECB names Boone and Brunnermeier for its Executive Board (Reuters)", "EUROPE", 8.7, 50.1),
    brief(26, "Buenos Aires Argentina's Senate backs a disability framework, 71-0 (AP)", "AMERICAS", -58.4, -34.6),
    brief(27, "Riyadh A Saudi coalition intercepts Houthi missiles over Riyadh (Reuters)", "MIDEAST", 46.7, 24.6),
    brief(28, "Barcelona A pill is hailed as a breakthrough for pancreatic cancer (Reuters)", "EUROPE", 2.2, 41.4),
    brief(29, "Gaza On World Children's Day, Palestinian children appeal for help (UN)", "MIDEAST", 34.3, 31.5),
    brief(30, "Madrid Amnesty says Spanish police used excess force in the strike (AP)", "EUROPE", -3.7, 40.4),
    brief(31, "Rome Italian workers and students march against Meloni's government (AFP)", "EUROPE", 12.5, 41.9),
    brief(32, "Jeddah Saudi Arabia warns of thunderstorms through Tuesday (SPA)", "MIDEAST", 39.2, 21.5),
    brief(33, "Kuala Lumpur Malaysia to send 10,000 Rohingya to Turkey for training (Reuters)", "ASIA", 101.7, 3.1),
    brief(34, "Kharkiv Ukraine says it has finished a “Bear Trap” in the Kharkiv area (Ukrinform)", "EUROPE", 36.2, 49.9),
    brief(35, "Islamabad Pakistan's minerals are worth $8-10 trillion, its minister says (Reuters)", "ASIA", 73.1, 33.7),
    brief(36, "Singapore US presses Singapore and Malaysia on Iran sanctions (Reuters)", "ASIA", 103.8, 1.35),
    brief(37, "Paris France seeks a UN council meeting on the Kyiv strikes (AFP)", "EUROPE", 2.3, 48.8),
    brief(38, "Kyiv The war tally: 771 Ukrainians killed, 2,300+ missing (homevo)", "EUROPE", 30.6, 50.5),
    brief(39, "Ankara Turkey welcomes the World Court's Myanmar ruling (Anadolu)", "MIDEAST", 32.9, 39.9),
    brief(40, "Turin ATP semis are set: Alcaraz v Shelton, Zverev v Medvedev (ATP)", "EUROPE", 7.7, 45.1),
]

# The DATE CHECK box copy: Friday 20 November stories deliberately left
# out, plus items that had not happened yet on Saturday — named so a
# reader can audit the date discipline of the page.
DATE_CHECK = ("Left out as Friday 20 November's news: Kyiv's three bridges hit, Cyclone Akvan's "
              "landfall at Gopalpur, COP31's final day ending with no deal, Asia's AI sell-off (Taipei -6.2%), "
              "the UK-EU reset deal and Phillips's 118 in the first innings. Not yet happened, so not shown: "
              "any final COP31 text, the ATP semi-final results and BepiColombo's entry into orbit around "
              "Mercury (due today).")

FOOTER_LEFT = "Every story here happened, or was first reported, on Saturday 21 November 2026. Contested claims are attributed."
FOOTER_RIGHT = "Sources named beside each story · original drawings"


# ---------------------------------------------------------------- scenes
# Thirteen small flat illustrations, one per pictured story. Each takes
# the draw context and the strip's (x, y, w, h) box and paints inside it.

def paint_skyline(d, x, y, w, h, heights, fill):
    """Seven flat building silhouettes standing along the bottom edge.

    Shared by the two night scenes (cards 4 and 6), which differ only
    in their height profile and silhouette colour.
    """
    for i, bh in enumerate(heights):
        bx = x + int(w * (0.02 + 0.14 * i))
        bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * bh), bx + bw, y + h], fill=fill)


def paint_field(d, x, y, w, h):
    """Card 1 — Polish farmland, a missile shape, a drone silhouette."""
    d.rectangle([x, y, x + w, y + h], fill=(140, 170, 100))
    for i in range(4):
        fy = y + int(h * (0.30 + 0.17 * i))
        d.line([x, fy, x + w, fy - int(h * 0.05)], fill=(110, 140, 74), width=2)
    mx, my = x + int(w * 0.58), y + int(h * 0.30)
    d.polygon([(mx, my), (mx + int(w * 0.26), my + int(h * 0.20)),
               (mx + int(w * 0.23), my + int(h * 0.30)),
               (mx - int(w * 0.03), my + int(h * 0.10))], fill=(150, 152, 156))
    d.ellipse([mx + int(w * 0.16), my + int(h * 0.30),
               mx + int(w * 0.30), my + int(h * 0.40)], outline=(90, 80, 60), width=2)
    dx, dy = x + int(w * 0.16), y + int(h * 0.36)  # drone silhouette
    d.polygon([(dx - 9, dy), (dx + 9, dy), (dx + 4, dy + 5), (dx - 4, dy + 5)], fill=(40, 44, 48))
    d.line([dx - 13, dy - 3, dx + 13, dy - 3], fill=(40, 44, 48), width=2)


def paint_summit(d, x, y, w, h):
    """Card 2 — a globe and a thermometer for the COP31 talks."""
    d.rectangle([x, y, x + w, y + h], fill=(86, 128, 156))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.48), int(h * 0.34)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 90))
    d.ellipse([gx - int(gr * 0.55), gy - int(gr * 0.5),
               gx - int(gr * 0.05), gy - int(gr * 0.05)], fill=(120, 160, 90))
    tx = x + int(w * 0.68)
    tube_w = max(5, int(w * 0.05))
    d.rectangle([tx, y + int(h * 0.14), tx + tube_w, y + int(h * 0.66)],
                outline=(240, 240, 240), width=2)
    d.rectangle([tx + 1, y + int(h * 0.40), tx + tube_w - 1, y + int(h * 0.66)],
                fill=(220, 70, 50))
    d.rectangle([x, y + int(h * 0.86), x + w, y + h], fill=(60, 96, 120))


def paint_chart(d, x, y, w, h):
    """Card 3 — a falling red line on a dark market grid."""
    d.rectangle([x, y, x + w, y + h], fill=(29, 33, 43))
    for i in range(1, 4):
        gy = y + int(h * i / 4)
        d.line([x + 3, gy, x + w - 3, gy], fill=(58, 66, 80), width=1)
    trace = [(0.04, 0.22), (0.24, 0.30), (0.42, 0.26),
             (0.60, 0.48), (0.78, 0.55), (0.96, 0.78)]
    xy = [(x + int(w * fx), y + int(h * fy)) for fx, fy in trace]
    d.line(xy, fill=(232, 76, 60), width=2)
    for px, py in xy:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(232, 76, 60))


def paint_strike(d, x, y, w, h):
    """Card 4 — night skyline with a star-burst explosion."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 54, 74))
    paint_skyline(d, x, y, w, h, (0.34, 0.48, 0.28, 0.42, 0.32, 0.52, 0.30), (26, 27, 38))
    cx, cy = x + int(w * 0.60), y + int(h * 0.34)
    for k in range(12):
        a = 2 * math.pi * k / 12
        r = int(h * (0.30 if k % 2 == 0 else 0.16))
        d.line([cx, cy, cx + r * math.cos(a), cy + r * 0.72 * math.sin(a)],
               fill=(255, 170, 60), width=2)
    d.ellipse([cx - int(h * 0.13), cy - int(h * 0.10),
               cx + int(h * 0.13), cy + int(h * 0.10)], fill=(255, 196, 84))


def paint_crosshair(d, x, y, w, h):
    """Card 5 — rooftops under a red targeting reticle."""
    d.rectangle([x, y, x + w, y + h], fill=(126, 148, 168))
    for i, rh in enumerate((0.26, 0.36, 0.22, 0.32, 0.27)):
        rx = x + int(w * (0.03 + 0.19 * i))
        rw = int(w * 0.17)
        ry = y + h - int(h * rh)
        d.rectangle([rx, ry + int(h * 0.10), rx + rw, y + h], fill=(104, 92, 84))
    cx, cy = x + int(w * 0.56), y + int(h * 0.42)
    r = int(h * 0.30)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(198, 44, 40), width=2)
    d.line([cx - r - 5, cy, cx - r + 7, cy], fill=(198, 44, 40), width=2)
    d.line([cx + r - 7, cy, cx + r + 5, cy], fill=(198, 44, 40), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(198, 44, 40))


def paint_barrage(d, x, y, w, h):
    """Card 6 — night skyline, interception bursts, drone silhouettes."""
    d.rectangle([x, y, x + w, y + h], fill=(26, 30, 52))
    paint_skyline(d, x, y, w, h, (0.30, 0.44, 0.26, 0.38, 0.30, 0.48, 0.28), (12, 14, 26))
    for fx, fy in ((0.30, 0.30), (0.58, 0.22), (0.80, 0.36)):
        cx, cy = x + int(w * fx), y + int(h * fy)
        for a in range(8):
            ang = 2 * math.pi * a / 8
            r = int(h * 0.13)
            d.line([cx, cy, cx + r * math.cos(ang), cy + r * 0.8 * math.sin(ang)],
                   fill=(255, 190, 90), width=1)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 140))
    # drone silhouettes strung along the top edge
    for i in range(6):
        dx = x + int(w * (0.06 + 0.15 * i))
        dy = y + int(h * 0.10)
        d.polygon([(dx - 5, dy), (dx + 5, dy), (dx, dy + 4)], fill=(200, 200, 210))


def paint_storm(d, x, y, w, h):
    """Card 7 — a cyclone spiral over the sea, tents on the shore."""
    d.rectangle([x, y, x + w, y + h], fill=(84, 118, 148))
    d.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=(46, 84, 110))
    cx, cy = x + int(w * 0.62), y + int(h * 0.40)
    for r in (int(h * 0.34), int(h * 0.24), int(h * 0.14)):
        d.arc([cx - r, cy - int(r * 0.62), cx + r, cy + int(r * 0.62)],
              20, 300, fill=(235, 240, 244), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    shore = y + int(h * 0.66)
    for i in range(3):
        tx = x + int(w * (0.06 + 0.13 * i))
        tent_w = max(10, int(w * 0.10))
        d.polygon([(tx, shore), (tx + tent_w // 2, shore - int(h * 0.16)),
                   (tx + tent_w, shore)], fill=(240, 200, 120))


def paint_flags(d, x, y, w, h):
    """Card 8 — two flags on poles: a union-style flag and the EU flag."""
    d.rectangle([x, y, x + w, y + h], fill=(112, 146, 186))
    d.rectangle([x, y + int(h * 0.80), x + w, y + h], fill=(90, 120, 84))

    def one_flag(fx, fw, fh, eu):
        fy = y + int(h * 0.16)
        d.line([fx, fy, fx, y + int(h * 0.82)], fill=(60, 54, 44), width=2)
        d.rectangle([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(36, 52, 120))
        if eu:
            ccx, ccy, rr = fx + 2 + fw / 2, fy + fh / 2, fh * 0.30
            for k in range(8):
                a = 2 * math.pi * k / 8
                sx, sy = ccx + rr * math.cos(a), ccy + rr * math.sin(a)
                d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(245, 197, 24))
        else:
            d.line([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(240, 240, 240), width=2)
            d.line([fx + 2, fy + fh, fx + 2 + fw, fy], fill=(240, 240, 240), width=2)
            d.rectangle([fx + 2 + fw // 2 - 2, fy, fx + 2 + fw // 2 + 2, fy + fh],
                        fill=(200, 40, 50))
            d.rectangle([fx + 2, fy + fh // 2 - 2, fx + 2 + fw, fy + fh // 2 + 2],
                        fill=(200, 40, 50))

    fw, fh = int(w * 0.30), int(h * 0.40)
    one_flag(x + int(w * 0.10), fw, fh, eu=False)
    one_flag(x + int(w * 0.56), fw, fh, eu=True)


def paint_bankcards(d, x, y, w, h):
    """Card 9 — three payment cards standing on a dark ground."""
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 44))
    cw_, ch_ = int(w * 0.24), int(h * 0.52)
    for i, col in enumerate(((196, 204, 214), (88, 130, 190), (178, 58, 52))):
        cx = x + int(w * (0.05 + 0.27 * i))
        cy = y + int(h * 0.16)
        d.rounded_rectangle([cx, cy, cx + cw_, cy + ch_], radius=4, fill=col)
        d.rectangle([cx, cy + int(ch_ * 0.24), cx + cw_, cy + int(ch_ * 0.40)],
                    fill=(40, 44, 54))


def paint_ger(d, x, y, w, h):
    """Card 10 — a Mongolian ger on the steppe, flag beside it."""
    d.rectangle([x, y, x + w, y + int(h * 0.60)], fill=(120, 168, 208))
    d.rectangle([x, y + int(h * 0.60), x + w, y + h], fill=(140, 160, 84))
    gx, gy = x + int(w * 0.30), y + int(h * 0.62)
    gw, gh = int(w * 0.30), int(h * 0.30)
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=(244, 242, 236))
    d.pieslice([gx - 2, gy - int(gh * 0.55), gx + gw + 2, gy + int(gh * 0.45)],
               180, 360, fill=(238, 234, 226))
    fx = x + int(w * 0.76)
    d.line([fx, y + int(h * 0.16), fx, y + int(h * 0.86)], fill=(70, 60, 50), width=2)
    fw, fh = int(w * 0.17), int(h * 0.30)
    fy = y + int(h * 0.16)
    for i, col in enumerate(((206, 42, 48), (0, 96, 160), (206, 42, 48))):
        d.rectangle([fx + 2 + i * fw // 3, fy, fx + 2 + (i + 1) * fw // 3, fy + fh],
                    fill=col)


def paint_court(d, x, y, w, h):
    """Card 11 — a courthouse: pediment, four columns, steps."""
    d.rectangle([x, y, x + w, y + h], fill=(104, 116, 138))
    cx = x + w // 2
    d.polygon([(cx - int(w * 0.34), y + int(h * 0.30)),
               (cx + int(w * 0.34), y + int(h * 0.30)),
               (cx, y + int(h * 0.08))], fill=(226, 222, 208))
    for i in range(4):
        cxx = cx - int(w * 0.27) + i * int(w * 0.18)
        d.rectangle([cxx, y + int(h * 0.40), cxx + int(w * 0.07), y + int(h * 0.78)],
                    fill=(238, 236, 226))
    d.rectangle([cx - int(w * 0.36), y + int(h * 0.80),
                 cx + int(w * 0.36), y + int(h * 0.88)], fill=(226, 222, 208))


def paint_ballotbox(d, x, y, w, h):
    """Card 12 — a ballot box, a paper going in, the 31% tally bars."""
    d.rectangle([x, y, x + w, y + h], fill=(96, 118, 96))
    bx0, bx1 = x + int(w * 0.30), x + int(w * 0.72)
    by0, by1 = y + int(h * 0.44), y + int(h * 0.86)
    d.rectangle([bx0, by0, bx1, by1], fill=(226, 220, 200))
    d.rectangle([bx0 + int(w * 0.06), by0 + int(h * 0.08),
                 bx1 - int(w * 0.06), by0 + int(h * 0.15)], fill=(52, 48, 44))
    px0 = x + int(w * 0.40)
    d.polygon([(px0, by0 - int(h * 0.26)), (px0 + int(w * 0.20), by0 - int(h * 0.30)),
               (px0 + int(w * 0.20), by0 - int(h * 0.02)), (px0, by0 + int(h * 0.02))],
              fill=(250, 250, 246))
    # tally bars: the winner's 31% against the rest
    d.rectangle([x + int(w * 0.06), y + int(h * 0.20),
                 x + int(w * 0.06) + int(w * 0.31), y + int(h * 0.30)], fill=(245, 197, 24))
    d.rectangle([x + int(w * 0.06), y + int(h * 0.34),
                 x + int(w * 0.06) + int(w * 0.69), y + int(h * 0.42)], fill=(200, 200, 200))


def paint_pitch(d, x, y, w, h):
    """Card 13 — a cricket pitch strip, stumps and a red ball."""
    d.rectangle([x, y, x + w, y + h], fill=(92, 142, 82))
    d.rectangle([x + int(w * 0.28), y, x + int(w * 0.72), y + h], fill=(198, 172, 112))
    sx = x + int(w * 0.60)
    for i in range(3):
        d.line([sx + i * 4 - 4, y + int(h * 0.30), sx + i * 4 - 4, y + int(h * 0.72)],
               fill=(240, 230, 190), width=2)
    bx, by = x + int(w * 0.82), y + int(h * 0.34)
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(196, 40, 44))


SCENE_PAINTERS = {
    "field": paint_field, "cop": paint_summit, "markets": paint_chart,
    "blast": paint_strike, "target": paint_crosshair,
    "intercept": paint_barrage, "cyclone": paint_storm, "flags": paint_flags,
    "cyber": paint_bankcards, "steppe": paint_ger, "court": paint_court,
    "ballot": paint_ballotbox, "cricket": paint_pitch,
}


# ---------------------------------------------------------------- cards
def paint_chip(d, rx, ry, text, font, back, fore, height, extra):
    """One small filled chip: a rectangle with its text inset 4px from
    the left edge and 1px from the top. `extra` is the horizontal
    padding folded into the chip's width beyond the text itself."""
    w = measure(d, text, font) + extra
    d.rectangle([rx, ry, rx + w, ry + height], fill=back)
    d.text((rx + 4, ry + 1), text, font=font, fill=fore)
    return w


def paint_strip(d, card, x, y, w, h, lead=False, shaded=False):
    """The illustration strip at the top of a card.

    Paints the scene, a region-colour rule along the top, a navy caption
    band along the bottom, a source-tag chip top-right and a burgundy
    data-label chip bottom-left. The two chips sit in stacked zones:
    with a 42px mini strip the tag ends exactly where the label begins,
    so even card 6's long label cannot collide with the tag.
    """
    if shaded:  # pseudo-3D duel treatment: offset shadow plate beneath
        d.rectangle([x + 3, y + 3, x + w + 3, y + h + 3], fill=(160, 152, 132))
    SCENE_PAINTERS[card["scene"]](d, x, y, w, h)
    tint = REGION_TINTS[card["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=tint)
    band_h = 15 if lead else 12
    d.rectangle([x, y + h - band_h, x + w, y + h], fill=DEEP_NAVY)
    cap_font = shrink_font(d, card["caption"], 10 if lead else 9, w - 10)
    centred(d, x + w / 2, y + h - band_h + 1, card["caption"], cap_font, CREAM_TXT)
    tag_font = TYPE.bold(9 if lead else 8)
    tag_w = measure(d, card["tag"], tag_font) + 8
    paint_chip(d, x + w - tag_w - 3, y + 4, card["tag"], tag_font,
               DEEP_NAVY, CREAM_TXT, 13 if lead else 12, 8)
    lab_font = shrink_font(d, card["label"], 11 if lead else 10, w - 12)
    ly = y + h - band_h - 14
    paint_chip(d, x + 3, ly, card["label"], lab_font,
               BURGUNDY, (255, 255, 255), 13, 9)


def paint_card(d, card, x, y, w, strip_h, lead=False, shaded=False):
    """A full story card: strip, kicker line, headline, deck.

    Returns the y just below the deck, so rows can stack tightly.
    """
    d.rectangle([x, y, x + w, y + strip_h], outline=CARD_EDGE, width=1)
    paint_strip(d, card, x, y, w, strip_h, lead, shaded)
    tint = REGION_TINTS[card["region"]]
    ry = y + strip_h + 4
    kicker = "%d  %s · %s · %s" % (card["no"], card["place"], card["region"], card["topic"])
    d.text((x + 1, ry), kicker, font=TYPE.bold(10 if lead else 9), fill=tint)
    hy = ry + (14 if lead else 12)
    head_font = TYPE.playfair(20 if lead else 13)
    for ln in wrap_lines(d, card["headline"], head_font, w - 2)[:2]:
        d.text((x + 1, hy), ln, font=head_font, fill=INK_DARK)
        hy += 20 if lead else 15
    deck_font, deck_step = (TYPE.medium(11), 12) if lead else (TYPE.medium(10), 10.5)
    for ln in wrap_lines(d, card["deck"], deck_font, w - 2):
        d.text((x + 1, hy + 1), ln, font=deck_font, fill=(64, 74, 62))
        hy += deck_step
    return hy


# ---------------------------------------------------------------- head block
def paint_head(d, variant):
    """Masthead, standfirst, hook band, timeline, figures, region chips.

    Returns the y where the body layouts begin (258).
    """
    d.rectangle([0, 0, PAGE, 96], fill=DEEP_NAVY)
    d.text((EDGE, 6), "THE WORLD'S NEWS IN ONE PICTURE", font=TYPE.bold(11), fill=GOLDEN)
    r = "40 STORIES · 7 REGIONS · EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((PAGE - EDGE - measure(d, r, TYPE.bold(11)), 6), r, font=TYPE.bold(11), fill=CREAM_TXT)
    if variant == "B":
        d.text((EDGE, 24), "The Daily Atlas", font=TYPE.playfair(52), fill=(255, 255, 255))
        dl = "SATURDAY 21 NOVEMBER 2026"
        d.text((PAGE - EDGE - measure(d, dl, TYPE.bold(15)), 40), dl, font=TYPE.bold(15), fill=GOLDEN)
        tag = "Midnight atlas edition"
        d.text((PAGE - EDGE - measure(d, tag, TYPE.medium(11)), 62), tag,
               font=TYPE.medium(11), fill=CREAM_TXT)
    else:
        centred(d, PAGE / 2, 22, "The Daily Atlas", TYPE.playfair(56), (255, 255, 255))
    d.line([EDGE, 92, PAGE - EDGE, 92], fill=GOLDEN, width=2)
    sub = "Missiles land in Poland · COP31 slips into overtime · Wall Street falls into correction · Denmark exposes a plot"
    centred(d, PAGE / 2, 100, sub, shrink_font(d, sub, 11, SPAN - 16), INK_DARK)
    # hook band: gold here (the d2 paper used burgundy; gold is d4's own)
    d.rectangle([EDGE, 112, PAGE - EDGE, 136], fill=GOLDEN)
    hook = "TOP OF THE DAY — 1 RUTTE FLIES TO WARSAW AFTER MISSILES LAND  ·  2 COP31 RUNS INTO OVERTIME, NO DEAL YET  ·  3 WALL STREET ENTERS CORRECTION, NASDAQ -5.28%"
    centred(d, PAGE / 2, 118, hook, shrink_font(d, hook, 12, SPAN - 20), DEEP_NAVY)
    # day timeline, five slots across the width
    slot_w = SPAN / 5
    for i, (lab, ev) in enumerate(DAY_TIMELINE):
        cx = EDGE + i * slot_w
        if i:
            d.line([cx, 144, cx, 170], fill=RULE_GREY, width=1)
        d.text((cx + 8, 141), lab, font=TYPE.bold(10), fill=BURGUNDY)
        ey = 152
        for ln in wrap_lines(d, ev, TYPE.medium(9), slot_w - 14)[:2]:
            d.text((cx + 8, ey), ln, font=TYPE.medium(9), fill=INK_DARK)
            ey += 10
    d.line([EDGE, 172, PAGE - EDGE, 172], fill=RULE_GREY, width=1)
    # the day in numbers, six bound figures
    d.text((EDGE, 176), "THE DAY IN NUMBERS", font=TYPE.bold(10), fill=DEEP_NAVY)
    fig_w = SPAN / 6
    for i, (num, cap) in enumerate(FIGURE_STRIP):
        cx = EDGE + i * fig_w
        centred(d, cx + fig_w / 2, 187, num, TYPE.playfair(23), BURGUNDY)
        cy = 213
        for ln in wrap_lines(d, cap, TYPE.medium(9), fig_w - 8)[:2]:
            centred(d, cx + fig_w / 2, cy, ln, TYPE.medium(9), (84, 92, 76))
            cy += 10
    # region tally chips
    chip_w = (SPAN - 6 * 6) / 7
    for i, (name, n) in enumerate(REGION_TALLY):
        cx = EDGE + i * (chip_w + 6)
        d.rectangle([cx, 234, cx + chip_w, 250], fill=REGION_TINTS[name])
        centred(d, cx + chip_w / 2, 237, "%s %d" % (name, n), TYPE.bold(9), (255, 255, 255))
    d.line([EDGE, 254, PAGE - EDGE, 254], fill=RULE_GREY, width=1)
    return 258


# ---------------------------------------------------------------- map panel
def paint_map(d, x0, top, x1, bottom, shaded=False):
    """The world map: real polygons, graticule, brief dots, story pins."""
    if shaded:
        d.rectangle([x0 + 4, top + 4, x1 + 4, bottom + 4], fill=(150, 142, 122))
    d.rectangle([x0, top, x1, bottom], fill=DEEP_NAVY)
    d.text((x0 + 12, top + 7), "WHERE IT HAPPENED", font=TYPE.bold(12), fill=CREAM_TXT)
    mx0, mx1, my0, my1 = x0 + 10, x1 - 10, top + 28, bottom - 26

    def px(lon):
        return mx0 + (lon + 180) / 360 * (mx1 - mx0)

    def py(lat):
        return my0 + (82 - lat) / 140 * (my1 - my0)

    for glon in range(-150, 181, 30):
        d.line([px(glon), my0, px(glon), my1], fill=NAVY_SOFT, width=1)
    for glat in range(-45, 76, 15):
        d.line([mx0, py(glat), mx1, py(glat)], fill=NAVY_SOFT, width=1)
    for rings in WORLD.values():
        for ring in rings.split("|"):
            pts = []
            for pair in ring.split(","):
                lo, la = pair.split(":")
                pts.append((px(float(lo)), py(float(la))))
            if len(pts) >= 3:
                d.polygon(pts, fill=LAND_SAGE)
    for b in BRIEFS:
        cx, cy = px(b["lon"]), py(b["lat"])
        d.ellipse([cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6], fill=REGION_TINTS[b["region"]])
    for card in STORIES:
        cx, cy = px(card["lon"]), py(card["lat"])
        r = 9
        if shaded:
            d.ellipse([cx - r + 2, cy - r + 2, cx + r + 2, cy + r + 2], fill=(10, 18, 30))
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=REGION_TINTS[card["region"]], outline=CREAM_TXT, width=2)
        s = str(card["no"])
        f = TYPE.bold(10)
        d.text((cx - measure(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))
    d.text((x0 + 12, bottom - 17), "Numbered pins = pictured stories · small dots = briefs",
           font=TYPE.medium(9), fill=CREAM_TXT)


# ---------------------------------------------------------------- briefs block
def paint_briefs(d, x, top, w, items, lh=10.5, fsize=9):
    """A column of numbered briefs; returns the y below the last one."""
    y = top
    for b in items:
        ns = str(b["no"])
        d.text((x, y), ns, font=TYPE.bold(fsize), fill=REGION_TINTS[b["region"]])
        off = measure(d, ns, TYPE.bold(fsize)) + 5
        wrapped = wrap_lines(d, b["text"], TYPE.medium(fsize), w - off)
        for j, ln in enumerate(wrapped):
            d.text((x + off, y + j * 10), ln, font=TYPE.medium(fsize), fill=(52, 62, 54))
        y += lh * max(1, len(wrapped))
    return y


def briefs_heading(d, x, top, w):
    d.text((x, top), "ALSO ON SATURDAY 21 NOVEMBER — 27 MORE STORIES",
           font=TYPE.bold(11), fill=DEEP_NAVY)
    d.line([x, top + 14, x + w, top + 14], fill=DEEP_NAVY, width=1)
    return top + 18


# ---------------------------------------------------------------- foot block
def paint_foot(d):
    """The DATE CHECK box and the two footer lines."""
    y0, y1 = 968, 1006
    d.rectangle([EDGE, y0, PAGE - EDGE, y1], fill=CARD_FACE, outline=BURGUNDY, width=2)
    lab = "DATE CHECK"
    d.text((EDGE + 8, y0 + 5), lab, font=TYPE.bold(10), fill=BURGUNDY)
    tx = EDGE + 8 + measure(d, lab, TYPE.bold(10)) + 8
    # first line: greedily take whole words while they fit beside the label
    cur = ""
    for word in DATE_CHECK.split():
        trial = (cur + " " + word).strip()
        if measure(d, trial, TYPE.medium(9)) <= (PAGE - EDGE - 8) - tx:
            cur = trial
        else:
            break
    d.text((tx, y0 + 5), cur, font=TYPE.medium(9), fill=INK_DARK)
    rest = DATE_CHECK[len(cur):].strip()
    yy = y0 + 16
    for ln in wrap_lines(d, rest, TYPE.medium(9), SPAN - 16)[:2]:
        d.text((EDGE + 8, yy), ln, font=TYPE.medium(9), fill=INK_DARK)
        yy += 11
    d.text((EDGE, 1011), FOOTER_LEFT, font=TYPE.medium(8), fill=(84, 92, 76))
    d.text((PAGE - EDGE - measure(d, FOOTER_RIGHT, TYPE.medium(8)), 1011),
           FOOTER_RIGHT, font=TYPE.medium(8), fill=(84, 92, 76))


# ---------------------------------------------------------------- layouts
def paint_lead_row(d, top, strip_h):
    """The three lead stories in a row directly under the head block.
    Returns the y just below the deepest lead deck."""
    lead_w = (SPAN - 2 * 12) / 3
    end = 0
    for i, card in enumerate(STORIES[:3]):
        end = max(end, paint_card(d, card, EDGE + i * (lead_w + 12), top + 4,
                                  lead_w, strip_h, lead=True))
    return end


def paint_feature_rows(d, fy, strip_h):
    """The ten remaining pictured stories, in two rows of five starting
    at fy. Returns the y just below the second row, plus its gap."""
    feat_w = (SPAN - 4 * 10) / 5
    for r in range(2):
        end = 0
        for c in range(5):
            end = max(end, paint_card(d, STORIES[3 + r * 5 + c],
                                      EDGE + c * (feat_w + 10), fy, feat_w, strip_h))
        fy = end + 6
    return fy


def page_layout_a(d):
    """Duel layout A: leads on top, map bottom-right, briefs bottom-left."""
    top = paint_head(d, "A")
    fy = paint_lead_row(d, top, 52) + 6
    fy = paint_feature_rows(d, fy, 32)
    paint_map(d, PAGE - EDGE - 430, fy, PAGE - EDGE, 962)
    bw = 430 + 16
    by = briefs_heading(d, EDGE, fy + 2, SPAN - bw)
    paint_briefs(d, EDGE, by, SPAN - bw, BRIEFS, lh=10.2, fsize=9)
    return fy


def page_layout_b(d):
    """Duel layout B: map as a raised shaded plate beside two stacked leads."""
    top = paint_head(d, "B")
    left_w = 540
    y = top + 4
    for card in STORIES[:2]:
        y = paint_card(d, card, EDGE, y, left_w, 46, lead=True, shaded=True) + 8
    paint_map(d, EDGE + left_w + 16, top + 4, PAGE - EDGE, y - 8, shaded=True)
    fy = y + 2
    feat_w = (SPAN - 4 * 10) / 5
    end = 0
    for c in range(5):
        end = max(end, paint_card(d, STORIES[2 + c], EDGE + c * (feat_w + 10),
                                  fy, feat_w, 32, shaded=True))
    fy = end + 6
    end = 0
    for c in range(5):
        end = max(end, paint_card(d, STORIES[7 + c], EDGE + c * (feat_w + 10),
                                  fy, feat_w, 32, shaded=True))
    fy = end + 6
    end = max(end, paint_card(d, STORIES[12], EDGE, fy, feat_w, 32, shaded=True))
    by = briefs_heading(d, EDGE + feat_w + 16, fy + 2, SPAN - feat_w - 16)
    paint_briefs(d, EDGE + feat_w + 16, by, SPAN - feat_w - 16, BRIEFS,
                 lh=10.2, fsize=9)
    return fy


def page_layout_c(d):
    """Duel layout C (the winner): wide map banner mid-page, briefs in
    two columns at the foot of the page."""
    top = paint_head(d, "C")
    end = paint_lead_row(d, top, 42)
    my0 = end + 6
    paint_map(d, EDGE, my0, PAGE - EDGE, my0 + 126)
    fy = paint_feature_rows(d, my0 + 134, 42)
    by = briefs_heading(d, EDGE, fy + 2, SPAN)
    half = (len(BRIEFS) + 1) // 2
    colw = (SPAN - 16) / 2
    paint_briefs(d, EDGE, by, colw, BRIEFS[:half], lh=9.4, fsize=9)
    paint_briefs(d, EDGE + colw + 16, by, colw, BRIEFS[half:], lh=9.4, fsize=9)
    return fy


LAYOUTS = {"A": page_layout_a, "B": page_layout_b, "C": page_layout_c}


# ---------------------------------------------------------------- render
def render(variant="C", out="entry.png"):
    """Paint one layout and save it as a 256-colour PNG beside this file."""
    img = Image.new("RGB", (PAGE, PAGE), PAPER_BG)
    d = ImageDraw.Draw(img)
    LAYOUTS[variant](d)
    paint_foot(d)
    path = os.path.join(HERE, out)
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(path, optimize=True)
    print(variant, "saved", path, os.path.getsize(path), "bytes")
    return path


if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else "C"
    if v == "ALL":
        for k in "ABC":
            render(k, "variant-%s.png" % k)
    else:
        render(v, "entry.png")
