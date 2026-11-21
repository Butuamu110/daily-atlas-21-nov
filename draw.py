#!/usr/bin/env python3
"""THE DAILY ATLAS — variant D of the make.fun News Image entry for
Saturday 21 November 2026. Challenger-d2 revision (22 Nov 2026, AKUN.md
section 22): name-first Playfair masthead with a burgundy hook band,
decks at the 12px floor, map pins at the 18px standard, and second
facts restored on the Brussels and Hague cards. Deterministic Pillow
composition, stdlib + PIL only, no network. Draws a 1024x1024
gazetteer-style page: masthead,
UTC timeline, the day in numbers, region counts, 13 pictured stories,
a wide hero map of real country polygons with numbered pins, 27 briefs,
a date-check box and a footer. Every fact comes from the shared pool.
Run: python3 draw.py  ->  writes entry.png beside this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont
from mapdata import WORLD

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 24                      # page margin
CW = W - 2 * M              # content width = 976

# ---- palette (atlas / gazetteer identity) ----
BG     = (243, 234, 211)    # parchment
PAPER  = (250, 246, 233)    # card paper
INK    = (38, 51, 42)       # ink green-black
FOREST = (31, 81, 48)       # forest green
BURG   = (123, 45, 38)      # burgundy
RULE   = (178, 164, 128)    # hairline tan
CARDB  = (196, 184, 152)    # card border
MAPBG  = (24, 54, 38)       # deep green map panel
LAND   = (168, 191, 165)    # sage land
PARCH  = (243, 234, 211)    # parchment text on dark
GOLD   = (201, 162, 39)

REGIONS = {
    "EUROPE":   (176, 58, 46),
    "ASIA":     (29, 111, 184),
    "MIDEAST":  (125, 60, 152),
    "AFRICA":   (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA":  (20, 143, 119),
    "GLOBAL":   (93, 109, 126),
}

# ---- fonts ----
def _font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)

_cache = {}
def PF(size):   # Playfair Display 900 — headlines, masthead, numbers
    return _cache.setdefault(("pf", size), _font("PlayfairDisplay-900.ttf", size))
def AB(size):   # Archivo Bold — labels, chips, briefs heads
    return _cache.setdefault(("ab", size), _font("Archivo-Bold.ttf", size))
def AM(size):   # Archivo Medium — decks, body
    return _cache.setdefault(("am", size), _font("Archivo-Medium.ttf", size))

# ---- pool data: numbers strip + timeline + region counts (verbatim) ----
NUMBERS = [
    ("3",        "weapons cross into Poland: two missiles and a jet drone"),
    ("42",       "injured in the Kryvyi Rih strike, four of them children"),
    ("900,000",  "AI chips cleared by the US for China"),
    ("$94.65",   "Brent crude as Iran crews its Kharg tanker convoy"),
    ("€8BN",     "paid out by the EU to Kyiv"),
    ("159/1",    "India at stumps in Wellington, day three"),
]
TIMELINE = [
    ("OVERNIGHT", "Kryvyi Rih strike: two killed, 42 injured"),
    ("MORNING",   "Rutte flies to Warsaw over the missiles"),
    ("MIDDAY",    "Antalya: third COP31 draft due after overnight talks"),
    ("AFTERNOON", "Denmark expels the Russian attache"),
    ("EVENING",   "BepiColombo reaches Mercury: burn at 19:24 CET"),
]
REGION_COUNTS = [
    ("EUROPE", 15), ("ASIA", 6), ("MIDEAST", 5), ("AFRICA", 1),
    ("AMERICAS", 9), ("OCEANIA", 1), ("GLOBAL", 3),
]

# ---- pool data: the 13 pictured stories ----
# deck = pool deck (leads verbatim incl. sources; feature decks trimmed
# only where the column cannot hold them, always keeping >= 2 facts).
CARDS = [
 dict(no=1, place="WARSAW, POLAND", region="EUROPE", topic="WAR",
      headline="Rutte flies to Warsaw after missiles land",
      deck="Two missiles and a suspected jet drone came down, a Kh-101 near Nowy Lipowiec. Rutte: a \"grave violation\"; Tusk: a deliberate provocation. (AP)",
      tag="AP - SOFX", label="3 WEAPONS CROSS",
      caption="WARSAW - MISSILES DOWN", lon=21.0, lat=52.2, scene="field"),
 dict(no=2, place="ANTALYA", region="GLOBAL", topic="CLIMATE",
      headline="COP31 runs into overtime with no deal yet",
      deck="Talks ran past Friday's close into Saturday - 92,000 accredited. The draft drops every fossil-fuel reference and the $120bn finance target. (AP)",
      tag="Ongoing - AP", label="NO DEAL YET",
      caption="ANTALYA - OVERTIME TALKS", lon=30.7, lat=36.9, scene="cop"),
 dict(no=3, place="WASHINGTON", region="AMERICAS", topic="TECH",
      headline="US clears 900,000 AI chips for China",
      deck="Washington cleared roughly 900,000 advanced AI chips for export to China. The licences land while the wider tech freeze between the two powers stays in place. (Reuters)",
      tag="Cleared - Washington", label="900,000 CHIPS",
      caption="WASHINGTON - CHIPS CLEARED", lon=-77.0, lat=38.9, scene="chip"),
 dict(no=4, place="KRYVYI RIH", region="EUROPE", topic="WAR",
      headline="Russian strike kills two, injures 42",
      deck="An overnight strike kills two and injures 42, four of them children. Ukraine's day toll: 12 killed, 82 wounded, officials say. (AppiStos)",
      tag="City chief says", label="2 DEAD - 42 HURT",
      caption="KRYVYI RIH - OVERNIGHT STRIKE", lon=33.4, lat=47.9, scene="blast"),
 dict(no=5, place="COPENHAGEN", region="EUROPE", topic="SECURITY",
      headline="Denmark exposes 'assassination plot'",
      deck="Russia 'planned and initiated' a bid to kill a Ukrainian-American rapper near Copenhagen. The attache is expelled. (BBC)",
      tag="Denmark says - BBC", label="ATTACHE EXPELLED",
      caption="COPENHAGEN - PLOT EXPOSED", lon=12.6, lat=55.7, scene="target"),
 dict(no=6, place="KYIV", region="EUROPE", topic="WAR",
      headline="Kyiv rations power as 50 settlements go dark",
      deck="A kindergarten in Zaporizhzhia was struck; 50 Rivne settlements lost power. Kyiv is rationing. (BBC)",
      tag="Officials' count", label="50 SETTLEMENTS DARK",
      caption="KYIV - POWER RATIONED", lon=30.5, lat=50.4, scene="kyiv"),
 dict(no=7, place="KHARG ISLAND", region="MIDEAST", topic="ENERGY",
      headline="Iran crews Kharg tanker convoy",
      deck="Iran crewed 14+ tankers into a convoy at Kharg to test the US blockade. Brent jumped 4.6% to $94.65. (Reuters)",
      tag="Convoy sailing", label="BRENT $94.65",
      caption="KHARG ISLAND - TANKER CONVOY", lon=50.3, lat=29.2, scene="tanker"),
 dict(no=8, place="BRUSSELS", region="EUROPE", topic="DEFENCE",
      headline="EU pays out nearly €8bn to Kyiv",
      deck="Brussels paid nearly €8bn to Kyiv for budget and war; Britain adds 1,000+ drones in a £260m package. (Reuters)",
      tag="Paid out - EU", label="EUR 8BN PAID OUT",
      caption="BRUSSELS - PAYOUT TO KYIV", lon=4.3, lat=50.8, scene="flags"),
 dict(no=9, place="NEW YORK", region="AMERICAS", topic="CYBER",
      headline="JPMorgan, Visa, Mastercard hit by cyberattack",
      deck="Incidents reported at third-party vendors. Core payment networks are unaffected, the banks say. (Reuters)",
      tag="Banks say", label="3 NETWORKS HIT",
      caption="NEW YORK - PAYMENT NETWORKS", lon=-73.9, lat=40.8, scene="cyber"),
 dict(no=10, place="RIYADH", region="MIDEAST", topic="WAR",
      headline="Coalition destroys Houthi workshops",
      deck="Coalition strikes destroyed six Houthi workshops in Sana'a overnight. Three missiles over Riyadh were downed. (Reuters)",
      tag="Coalition says", label="3 MISSILES DOWNED",
      caption="RIYADH - THIRD NIGHT OF ALERTS", lon=46.7, lat=24.6, scene="intercept"),
 dict(no=11, place="THE HAGUE", region="GLOBAL", topic="LAW",
      headline="Myanmar ruling rattles Israel's Gaza defence",
      deck="The Myanmar genocide verdict raises questions over Israel's own case, experts say; it was ruled Thursday. (BBC)",
      tag="Experts say", label="GENOCIDE VERDICT",
      caption="THE HAGUE - WORLD COURT", lon=4.3, lat=52.1, scene="court"),
 dict(no=12, place="MERCURY", region="GLOBAL", topic="SPACE",
      headline="BepiColombo reaches Mercury tonight",
      deck="Eight years in flight, ESA-JAXA's BepiColombo reaches Mercury tonight. Thrusters fire at 19:24 CET to enter orbit. (ESA)",
      tag="Tonight - ESA", label="8 YEARS IN FLIGHT",
      caption="MERCURY - ARRIVAL TONIGHT", lon=None, lat=None, scene="mercury"),
 dict(no=13, place="WELLINGTON", region="OCEANIA", topic="CRICKET",
      headline="India fight back: 159/1, day three",
      deck="India resume at 159/1 on day three, trailing by 209 after the hosts made 368. Nicholls made 175 not out. (ICC)",
      tag="Scorecard - ICC", label="159/1 - DAY THREE",
      caption="WELLINGTON - DAY THREE", lon=174.8, lat=-41.3, scene="cricket"),
]

# ---- pool data: briefs 14-40 (text verbatim, source in parens) ----
# region is used only for the colour of the brief's dot on the map.
BRIEFS = [
 (14, "Cardiff Lauren Price beats Kotaskova to become undisputed champion (BBC)", "EUROPE", -3.2, 51.5),
 (15, "Paris Three police are sentenced over the beating of Michel Zecler (BBC)", "EUROPE", 2.4, 48.9),
 (16, "New York Nikhil Gupta gets 19+ years over the Sikh murder plot (BBC)", "AMERICAS", -74.0, 40.7),
 (17, "Washington US sanctions four Iranians over oil revenues (OFAC)", "MIDEAST", -77.1, 38.8),
 (18, "Los Angeles A jury convicts the man who started the Palisades Fire (AP)", "AMERICAS", -118.3, 34.0),
 (19, "Frankfurt ECB names Boone and Brunnermeier for its Executive Board (Reuters)", "EUROPE", 8.7, 50.1),
 (20, "Buenos Aires Argentina's Senate backs a disability framework, 71-0 (AP)", "AMERICAS", -58.4, -34.6),
 (21, "Barcelona A pill is hailed as a breakthrough for pancreatic cancer (Reuters)", "EUROPE", 2.2, 41.4),
 (22, "Gaza On World Children's Day, Palestinian children appeal for help (UN)", "MIDEAST", 34.3, 31.5),
 (23, "Johannesburg Sixty murders a day make Joburg's homicide rate the world's worst (Reuters)", "AFRICA", 28.0, -26.2),
 (24, "Kharkiv Ukraine says it has finished a \"Bear Trap\" in the Kharkiv area (Ukrinform)", "EUROPE", 36.2, 49.9),
 (25, "Singapore US presses Singapore and Malaysia on Iran sanctions (Reuters)", "ASIA", 103.8, 1.35),
 (26, "Paris France seeks a UN council meeting on the Kyiv strikes (AFP)", "EUROPE", 2.3, 48.8),
 (27, "Kyiv The war tally: 771 Ukrainians killed, 2,300+ missing (homevo)", "EUROPE", 30.6, 50.5),
 (28, "Ankara Turkey welcomes the World Court's Myanmar ruling (Anadolu)", "MIDEAST", 32.9, 39.9),
 (29, "Sacramento California subpoenas Nvidia in its AI-chips inquiry (Reuters)", "AMERICAS", -121.5, 38.6),
 (30, "New Delhi India launches its first H5N1 bird-flu vaccine (Reuters)", "ASIA", 77.2, 28.6),
 (31, "Imphal Manipur clashes kill 11, with 181 in hospital (Reuters)", "ASIA", 93.9, 24.8),
 (32, "Atlanta Measles costs the US its WHO elimination status (AP)", "AMERICAS", -84.4, 33.7),
 (33, "Pasadena Voyager 1 is now one light-day from Earth (NASA)", "AMERICAS", -118.1, 34.1),
 (34, "Tokyo Japan to buy up to 8m barrels of Saudi crude (Reuters)", "ASIA", 139.7, 35.7),
 (35, "Leverkusen Bayer agrees a $7.25bn Roundup settlement (Reuters)", "EUROPE", 7.0, 51.0),
 (36, "Sumy A HIMARS strike wipes out 20 Russian commanders (Ukrinform)", "EUROPE", 34.8, 50.9),
 (37, "London Britain hit Moscow with cyberattacks, its chief confirms (BBC)", "EUROPE", -0.1, 51.5),
 (38, "Jakarta Indonesia asks Google why 19,000 YouTube accounts vanished (Reuters)", "ASIA", 106.8, -6.2),
 (39, "Las Vegas Grand Prix qualifying runs under the lights tonight (AP)", "AMERICAS", -115.1, 36.1),
 (40, "New Delhi Modi opens an SCO dialogue forum (Reuters)", "ASIA", 77.2, 28.6),
]

DATE_CHECK = ("Left out as earlier news: Kyiv's three bridges hit (Friday 20 November), Cyclone Akvan's "
 "landfall at Gopalpur (Friday), Asia's AI sell-off - Taipei -6.2% (Friday), Wall Street's AI sell-off "
 "at Friday's close, the UK-EU reset deal (Friday), Mongolia's president quits (Friday), COP31's "
 "scheduled Friday close, the Shenzhen three-leader summit (Thursday 19 November), Anthropic's "
 "$81.3bn IPO filing (Thursday) and the World Court's Myanmar ruling itself (Thursday). Not yet "
 "happened, so not shown: any final COP31 text.")
FOOTER_L = "Every story here happened, or was first reported, on Saturday 21 November 2026. Contested claims are attributed."
FOOTER_R = "Sources named beside each story - original drawings"

# ---- text helpers ----
def tw(d, s, f):
    return d.textlength(s, font=f)

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines

def fit(d, s, name, start, maxw, floor=8):
    """Largest Archivo-Bold size <= start whose width fits maxw."""
    size = start
    while size > floor and tw(d, s, AB(size)) > maxw:
        size -= 1
    return AB(size)

def ctext(d, cx, y, s, f, fill):
    d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)

# ---- flat illustration scenes (drawn inside the strip box) ----
def sc_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(43, 56, 84))
    river_y = y + int(h * 0.72)
    d.rectangle([x, river_y, x + w, y + h], fill=(52, 92, 122))
    for i in range(3):  # three bridges: deck + arc + piers
        bx = x + int(w * (0.10 + 0.30 * i)); bw = int(w * 0.24)
        by = river_y - int(h * (0.10 + 0.07 * i))
        d.line([bx, by, bx + bw, by], fill=(232, 220, 180), width=2)
        d.arc([bx, by - int(h * 0.16), bx + bw, by + int(h * 0.16)], 180, 360, fill=(232, 220, 180), width=1)
        d.line([bx + bw // 2, by, bx + bw // 2, river_y + 4], fill=(200, 190, 160), width=1)
    for i in range(3):  # missile arcs + bursts
        sx = x + int(w * (0.62 + 0.12 * i)); sy = y + 3
        ex = x + int(w * (0.24 + 0.26 * i)); ey = river_y - int(h * 0.22)
        for t in range(0, 11, 2):
            px = sx + (ex - sx) * t / 10; py = sy + (ey - sy) * t / 10 - int(h * 0.18) * (1 - abs(t / 5 - 1))
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(255, 190, 90))
        d.polygon([(ex - 4, ey), (ex, ey - 5), (ex + 4, ey), (ex, ey + 5)], fill=(255, 160, 60))

def sc_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(84, 118, 148))
    d.rectangle([x, y + int(h * 0.66), x + w, y + h], fill=(46, 84, 110))
    cx, cy = x + int(w * 0.62), y + int(h * 0.40)
    for r in (int(h * 0.34), int(h * 0.24), int(h * 0.14)):
        d.arc([cx - r, cy - int(r * 0.62), cx + r, cy + int(r * 0.62)], 20, 300, fill=(235, 240, 244), width=2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255))
    for i in range(9):  # rain streaks
        rx = x + 6 + i * (w - 12) // 9; ry = y + int(h * (0.12 + 0.09 * (i % 3)))
        d.line([rx, ry, rx - 3, ry + 6], fill=(200, 220, 235), width=1)
    shore = y + int(h * 0.66)
    for i in range(3):  # shelter tents on the shore
        tx = x + int(w * (0.06 + 0.13 * i)); tw_ = max(10, int(w * 0.10))
        d.polygon([(tx, shore), (tx + tw_ // 2, shore - int(h * 0.16)), (tx + tw_, shore)], fill=(240, 200, 120))

def sc_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(29, 33, 43))
    for i in range(1, 4):
        gy = y + int(h * i / 4)
        d.line([x + 3, gy, x + w - 3, gy], fill=(58, 66, 80), width=1)
    pts = [(0.04, 0.22), (0.24, 0.30), (0.42, 0.26), (0.60, 0.48), (0.78, 0.55), (0.96, 0.78)]
    xy = [(x + int(w * fx), y + int(h * fy)) for fx, fy in pts]
    d.line(xy, fill=(232, 76, 60), width=2)
    for px, py in xy:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(232, 76, 60))
    ax, ay = xy[-1]
    d.polygon([(ax - 4, ay - 5), (ax + 5, ay - 4), (ax, ay + 4)], fill=(232, 76, 60))

def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(112, 146, 186))
    d.rectangle([x, y + int(h * 0.80), x + w, y + h], fill=(90, 120, 84))
    def flag(fx, fw, fh, eu):
        fy = y + int(h * 0.16)
        d.line([fx, fy, fx, y + int(h * 0.82)], fill=(60, 54, 44), width=2)
        d.rectangle([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(36, 52, 120))
        if eu:
            import math
            ccx, ccy, rr = fx + 2 + fw / 2, fy + fh / 2, fh * 0.30
            for k in range(8):
                a = 2 * math.pi * k / 8
                sx, sy = ccx + rr * math.cos(a), ccy + rr * math.sin(a)
                d.ellipse([sx - 1.5, sy - 1.5, sx + 1.5, sy + 1.5], fill=(245, 197, 24))
        else:
            d.line([fx + 2, fy, fx + 2 + fw, fy + fh], fill=(240, 240, 240), width=2)
            d.line([fx + 2, fy + fh, fx + 2 + fw, fy], fill=(240, 240, 240), width=2)
            d.rectangle([fx + 2 + fw // 2 - 2, fy, fx + 2 + fw // 2 + 2, fy + fh], fill=(200, 40, 50))
            d.rectangle([fx + 2, fy + fh // 2 - 2, fx + 2 + fw, fy + fh // 2 + 2], fill=(200, 40, 50))
    fw, fh = int(w * 0.30), int(h * 0.40)
    flag(x + int(w * 0.10), fw, fh, eu=False)
    flag(x + int(w * 0.56), fw, fh, eu=True)

def sc_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(86, 128, 156))
    gx, gy, gr = x + int(w * 0.30), y + int(h * 0.48), int(h * 0.34)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 90))
    d.ellipse([gx - gr * 0.55, gy - gr * 0.5, gx - gr * 0.05, gy - gr * 0.05], fill=(120, 160, 90))
    d.ellipse([gx + gr * 0.1, gy + gr * 0.05, gx + gr * 0.6, gy + gr * 0.55], fill=(120, 160, 90))
    tx = x + int(w * 0.68); tw_ = max(5, int(w * 0.05))
    d.rectangle([tx, y + int(h * 0.14), tx + tw_, y + int(h * 0.66)], outline=(240, 240, 240), width=2)
    d.rectangle([tx + 1, y + int(h * 0.40), tx + tw_ - 1, y + int(h * 0.66)], fill=(220, 70, 50))
    d.ellipse([tx - 3, y + int(h * 0.62), tx + tw_ + 3, y + int(h * 0.62) + tw_ + 6], fill=(220, 70, 50))
    d.rectangle([x, y + int(h * 0.86), x + w, y + h], fill=(60, 96, 120))

def sc_field(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(140, 170, 100))
    for i in range(4):
        fy = y + int(h * (0.30 + 0.17 * i))
        d.line([x, fy, x + w, fy - int(h * 0.05)], fill=(110, 140, 74), width=2)
    mx, my = x + int(w * 0.60), y + int(h * 0.34)  # fallen missile, diagonal
    d.polygon([(mx, my), (mx + int(w * 0.26), my + int(h * 0.20)), (mx + int(w * 0.23), my + int(h * 0.30)), (mx - int(w * 0.03), my + int(h * 0.10))], fill=(150, 152, 156))
    d.polygon([(mx - int(w * 0.03), my + int(h * 0.10)), (mx - int(w * 0.09), my + int(h * 0.02)), (mx - int(w * 0.08), my + int(h * 0.16))], fill=(110, 112, 118))
    d.ellipse([mx + int(w * 0.16), my + int(h * 0.30), mx + int(w * 0.30), my + int(h * 0.40)], outline=(90, 80, 60), width=2)

def sc_iraq(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(206, 178, 128))
    d.rectangle([x, y + int(h * 0.62), x + w, y + h], fill=(188, 152, 96))
    def vehicle(vx, vy, s):
        d.rectangle([vx, vy, vx + int(34 * s), vy + int(10 * s)], fill=(96, 96, 70))
        d.rectangle([vx + int(22 * s), vy - int(6 * s), vx + int(32 * s), vy], fill=(80, 80, 58))
        for wx in (vx + int(7 * s), vx + int(26 * s)):
            d.ellipse([wx - int(4 * s), vy + int(7 * s), wx + int(4 * s), vy + int(15 * s)], fill=(40, 40, 36))
    s = max(0.5, h / 90)
    vehicle(x + int(w * 0.14), y + int(h * 0.44), s)
    vehicle(x + int(w * 0.55), y + int(h * 0.50), s * 0.85)

def sc_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(168, 108, 92))
    bx0, bx1 = x + int(w * 0.30), x + int(w * 0.78)  # plain banner
    d.rectangle([bx0, y + int(h * 0.14), bx1, y + int(h * 0.40)], fill=(246, 240, 220))
    d.line([bx0, y + int(h * 0.14), bx0, y + h], fill=(70, 54, 44), width=1)
    d.line([bx1, y + int(h * 0.14), bx1, y + h], fill=(70, 54, 44), width=1)
    for i in range(7):  # crowd silhouettes
        hx = x + int(w * (0.05 + 0.135 * i)); hy = y + int(h * 0.66)
        r = max(3, int(h * 0.10))
        d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(52, 44, 40))
        d.rectangle([hx - r - 1, hy + r - 1, hx + r + 1, y + h], fill=(52, 44, 40))

def sc_bars(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(38, 46, 56))
    base = y + int(h * 0.84)
    d.line([x + 4, base, x + w - 4, base], fill=(200, 200, 200), width=1)
    for i, fh in enumerate((0.34, 0.52, 0.72)):
        bx = x + int(w * (0.18 + 0.26 * i)); bw = int(w * 0.16)
        d.rectangle([bx, base - int(h * fh), bx + bw, base], fill=(226, 110, 60) if i < 2 else (232, 76, 60))

def sc_court(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(104, 116, 138))
    cx = x + w // 2
    d.polygon([(cx - int(w * 0.34), y + int(h * 0.30)), (cx + int(w * 0.34), y + int(h * 0.30)), (cx, y + int(h * 0.08))], fill=(226, 222, 208))
    d.rectangle([cx - int(w * 0.34), y + int(h * 0.32), cx + int(w * 0.34), y + int(h * 0.38)], fill=(226, 222, 208))
    for i in range(4):
        cxx = cx - int(w * 0.27) + i * int(w * 0.18)
        d.rectangle([cxx, y + int(h * 0.40), cxx + int(w * 0.07), y + int(h * 0.78)], fill=(238, 236, 226))
    d.rectangle([cx - int(w * 0.36), y + int(h * 0.80), cx + int(w * 0.36), y + int(h * 0.88)], fill=(226, 222, 208))

def sc_oil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 164, 108))
    d.rectangle([x, y + int(h * 0.78), x + w, y + h], fill=(120, 92, 58))
    cx = x + int(w * 0.42); top = y + int(h * 0.10); bot = y + int(h * 0.80); hw = int(w * 0.20)
    d.line([cx - hw, bot, cx, top], fill=(52, 48, 44), width=2)
    d.line([cx + hw, bot, cx, top], fill=(52, 48, 44), width=2)
    d.line([cx - hw * 0.6, y + int(h * 0.52), cx + hw * 0.6, y + int(h * 0.52)], fill=(52, 48, 44), width=1)
    d.line([cx - hw * 0.6, y + int(h * 0.52), cx, top], fill=(52, 48, 44), width=1)
    d.line([cx + hw * 0.6, y + int(h * 0.52), cx, top], fill=(52, 48, 44), width=1)
    d.rectangle([cx - 3, top - 3, cx + 3, top + 3], fill=(52, 48, 44))
    d.rectangle([x + int(w * 0.68), y + int(h * 0.60), x + int(w * 0.84), y + int(h * 0.78)], fill=(90, 74, 50))

def sc_ballot(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 118, 96))
    bx0, bx1 = x + int(w * 0.30), x + int(w * 0.72)
    by0, by1 = y + int(h * 0.44), y + int(h * 0.86)
    d.rectangle([bx0, by0, bx1, by1], fill=(226, 220, 200))
    d.rectangle([bx0 + int(w * 0.06), by0 + int(h * 0.08), bx1 - int(w * 0.06), by0 + int(h * 0.15)], fill=(52, 48, 44))
    px0 = x + int(w * 0.40)  # ballot paper sliding into the slot
    d.polygon([(px0, by0 - int(h * 0.26)), (px0 + int(w * 0.20), by0 - int(h * 0.30)), (px0 + int(w * 0.20), by0 - int(h * 0.02)), (px0, by0 + int(h * 0.02))], fill=(250, 250, 246))
    d.line([px0 + int(w * 0.04), by0 - int(h * 0.16), px0 + int(w * 0.09), by0 - int(h * 0.08)], fill=(31, 81, 48), width=2)
    d.line([px0 + int(w * 0.09), by0 - int(h * 0.08), px0 + int(w * 0.17), by0 - int(h * 0.22)], fill=(31, 81, 48), width=2)

def sc_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(92, 142, 82))
    d.rectangle([x + int(w * 0.28), y, x + int(w * 0.72), y + h], fill=(198, 172, 112))
    sx = x + int(w * 0.60)  # stumps
    for i in range(3):
        d.line([sx + i * 4 - 4, y + int(h * 0.30), sx + i * 4 - 4, y + int(h * 0.72)], fill=(240, 230, 190), width=2)
    d.line([sx - 5, y + int(h * 0.28), sx + 5, y + int(h * 0.28)], fill=(240, 230, 190), width=1)
    d.polygon([(x + int(w * 0.10), y + int(h * 0.78)), (x + int(w * 0.20), y + int(h * 0.74)), (x + int(w * 0.34), y + int(h * 0.30)), (x + int(w * 0.28), y + int(h * 0.26))], fill=(214, 178, 120))
    bx, by = x + int(w * 0.82), y + int(h * 0.34)  # ball
    d.ellipse([bx - 4, by - 4, bx + 4, by + 4], fill=(196, 40, 44))
    d.arc([bx - 3, by - 3, bx + 3, by + 3], 100, 260, fill=(250, 220, 220), width=1)

def sc_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(52, 54, 74))
    for i, bh in enumerate((0.34, 0.48, 0.28, 0.42, 0.32, 0.52, 0.30)):  # skyline
        bx = x + int(w * (0.02 + 0.14 * i)); bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * bh), bx + bw, y + h], fill=(26, 27, 38))
    import math
    cx, cy = x + int(w * 0.60), y + int(h * 0.34)  # explosion burst
    for k in range(12):
        a = 2 * math.pi * k / 12
        r = int(h * (0.30 if k % 2 == 0 else 0.16))
        px_, py_ = cx + r * math.cos(a), cy + r * 0.72 * math.sin(a)
        d.line([cx, cy, px_, py_], fill=(255, 170, 60), width=2)
    d.ellipse([cx - int(h * 0.13), cy - int(h * 0.10), cx + int(h * 0.13), cy + int(h * 0.10)], fill=(255, 196, 84))
    for i, (dx, dy, r) in enumerate(((0.16, -0.30, 0.10), (0.26, -0.42, 0.13), (-0.14, -0.34, 0.08))):
        sx, sy = cx + int(w * dx), cy + int(h * dy); rr = int(h * r)
        d.ellipse([sx - rr, sy - rr * 0.7, sx + rr, sy + rr * 0.7], fill=(150, 148, 158))

def sc_target(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(126, 148, 168))
    for i, rh in enumerate((0.26, 0.36, 0.22, 0.32, 0.27)):  # rooftops
        rx = x + int(w * (0.03 + 0.19 * i)); rw = int(w * 0.17)
        ry = y + h - int(h * rh)
        d.polygon([(rx, ry + int(h * 0.10)), (rx + rw // 2, ry), (rx + rw, ry + int(h * 0.10))], fill=(84, 62, 54))
        d.rectangle([rx, ry + int(h * 0.10), rx + rw, y + h], fill=(104, 92, 84))
    cx, cy = x + int(w * 0.56), y + int(h * 0.42)  # reticle
    r = int(h * 0.30)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(198, 44, 40), width=2)
    d.line([cx - r - 5, cy, cx - r + 7, cy], fill=(198, 44, 40), width=2)
    d.line([cx + r - 7, cy, cx + r + 5, cy], fill=(198, 44, 40), width=2)
    d.line([cx, cy - r - 5, cx, cy - r + 7], fill=(198, 44, 40), width=2)
    d.line([cx, cy + r - 7, cx, cy + r + 5], fill=(198, 44, 40), width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(198, 44, 40))

def sc_cyber(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 44))
    cw_, ch_ = int(w * 0.24), int(h * 0.52)
    for i, col in enumerate(((196, 204, 214), (88, 130, 190), (178, 58, 52))):
        cx = x + int(w * (0.05 + 0.27 * i)); cy = y + int(h * 0.16)
        d.rounded_rectangle([cx, cy, cx + cw_, cy + ch_], radius=4, fill=col)
        d.rectangle([cx, cy + int(ch_ * 0.24), cx + cw_, cy + int(ch_ * 0.40)], fill=(40, 44, 54))
        d.rectangle([cx + 5, cy + int(ch_ * 0.62), cx + int(cw_ * 0.55), cy + int(ch_ * 0.72)], fill=(240, 240, 240))
    tx, ty = x + int(w * 0.90), y + int(h * 0.52)  # warning triangle
    tr = int(h * 0.26)
    d.polygon([(tx, ty - tr), (tx - tr * 0.9, ty + tr * 0.7), (tx + tr * 0.9, ty + tr * 0.7)], fill=(245, 197, 24), outline=(24, 30, 44))
    d.text((tx - 2, ty - int(tr * 0.28)), "!", font=AB(max(9, int(h * 0.30))), fill=(24, 30, 44))

def sc_steppe(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + int(h * 0.60)], fill=(120, 168, 208))
    d.rectangle([x, y + int(h * 0.60), x + w, y + h], fill=(140, 160, 84))
    gx, gy = x + int(w * 0.34), y + int(h * 0.62)  # ger tent
    gw, gh = int(w * 0.30), int(h * 0.30)
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=(244, 242, 236))
    d.pieslice([gx - 2, gy - int(gh * 0.55), gx + gw + 2, gy + int(gh * 0.45)], 180, 360, fill=(238, 234, 226))
    d.polygon([(gx + gw // 2 - 4, gy - int(gh * 0.52)), (gx + gw // 2 + 4, gy - int(gh * 0.52)), (gx + gw // 2, gy - int(gh * 0.78))], fill=(198, 110, 44))
    d.rectangle([gx + gw // 2 - 4, gy + int(gh * 0.30), gx + gw // 2 + 4, gy + gh], fill=(150, 84, 48))
    fx = x + int(w * 0.76)  # Mongolian flag on a pole
    d.line([fx, y + int(h * 0.16), fx, y + int(h * 0.86)], fill=(70, 60, 50), width=2)
    fw, fh = int(w * 0.17), int(h * 0.30)
    fy = y + int(h * 0.16)
    for i, col in enumerate(((206, 42, 48), (0, 96, 160), (206, 42, 48))):
        d.rectangle([fx + 2 + i * fw // 3, fy, fx + 2 + (i + 1) * fw // 3, fy + fh], fill=col)
    d.rectangle([fx + 4, fy + 3, fx + 7, fy + 8], fill=(250, 200, 40))

def sc_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 34, 40))
    cw_, ch_ = int(w * 0.34), int(h * 0.56)  # the chip package
    cx, cy = x + (w - cw_) // 2, y + (h - ch_) // 2
    for i in range(5):  # pins left and right
        py_ = cy + int(ch_ * (0.12 + 0.19 * i))
        d.line([x + int(w * 0.06), py_, cx, py_], fill=(120, 200, 210), width=2)
        d.line([cx + cw_, py_, x + w - int(w * 0.06), py_], fill=(120, 200, 210), width=2)
    for i in range(4):  # pins top and bottom
        px_ = cx + int(cw_ * (0.16 + 0.23 * i))
        d.line([px_, y + int(h * 0.06), px_, cy], fill=(120, 200, 210), width=2)
        d.line([px_, cy + ch_, px_, y + h - int(h * 0.06)], fill=(120, 200, 210), width=2)
    d.rectangle([cx, cy, cx + cw_, cy + ch_], fill=(30, 90, 104), outline=(150, 220, 228), width=2)
    iw, ih = int(cw_ * 0.52), int(ch_ * 0.48)
    ix, iy = cx + (cw_ - iw) // 2, cy + (ch_ - ih) // 2
    d.rectangle([ix, iy, ix + iw, iy + ih], outline=(240, 200, 90), width=2)
    d.line([ix + 4, iy + ih - 4, ix + iw // 2, iy + 5], fill=(240, 200, 90), width=1)
    d.line([ix + iw // 2, iy + 5, ix + iw - 4, iy + ih - 4], fill=(240, 200, 90), width=1)

def sc_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + int(h * 0.52)], fill=(238, 178, 110))  # dusk sky
    d.rectangle([x, y + int(h * 0.52), x + w, y + h], fill=(38, 84, 110))  # sea
    d.ellipse([x + int(w * 0.80), y + int(h * 0.08), x + int(w * 0.92), y + int(h * 0.08) + int(h * 0.22)], fill=(250, 214, 130))
    def tanker(tx, ty, s, col):
        hl = int(64 * s); hh = int(13 * s)
        d.polygon([(tx, ty), (tx + hl, ty), (tx + hl - int(8 * s), ty + hh), (tx + int(6 * s), ty + hh)], fill=col)
        d.rectangle([tx + int(8 * s), ty - int(6 * s), tx + hl - int(14 * s), ty], fill=(222, 226, 228))
        d.rectangle([tx + hl - int(12 * s), ty - int(13 * s), tx + hl - int(6 * s), ty], fill=(240, 240, 238))
        d.line([tx + int(20 * s), ty - int(6 * s), tx + int(20 * s), ty], fill=(120, 40, 36), width=max(1, int(2 * s)))
    s = max(0.6, h / 95)
    tanker(x + int(w * 0.06), y + int(h * 0.56), s, (30, 34, 40))
    tanker(x + int(w * 0.46), y + int(h * 0.64), s * 0.82, (44, 48, 54))
    tanker(x + int(w * 0.70), y + int(h * 0.54), s * 0.66, (56, 60, 66))
    for i in range(6):  # wave ticks
        wx = x + int(w * (0.05 + 0.16 * i)); wy = y + int(h * (0.86 if i % 2 else 0.80))
        d.line([wx, wy, wx + int(w * 0.07), wy], fill=(120, 170, 196), width=1)

def sc_intercept(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(26, 30, 52))
    for i, bh in enumerate((0.30, 0.44, 0.26, 0.38, 0.30, 0.48, 0.28)):  # night skyline
        bx = x + int(w * (0.02 + 0.14 * i)); bw = int(w * 0.12)
        d.rectangle([bx, y + h - int(h * bh), bx + bw, y + h], fill=(12, 14, 26))
        d.rectangle([bx + 3, y + h - int(h * bh) + 4, bx + 6, y + h - int(h * bh) + 7], fill=(250, 200, 90))
    import math
    for k, (fx, fy) in enumerate(((0.30, 0.30), (0.58, 0.22), (0.80, 0.36))):  # intercept bursts
        cx, cy = x + int(w * fx), y + int(h * fy)
        for a in range(8):
            ang = 2 * math.pi * a / 8
            r = int(h * 0.13)
            d.line([cx, cy, cx + r * math.cos(ang), cy + r * 0.8 * math.sin(ang)], fill=(255, 190, 90), width=1)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 220, 140))
    for sx, sy in ((0.10, 0.62), (0.42, 0.70), (0.68, 0.60)):  # rising trails
        d.arc([x + int(w * sx), y + int(h * sy) - int(h * 0.30), x + int(w * (sx + 0.22)), y + int(h * sy) + int(h * 0.10)], 200, 320, fill=(200, 120, 90), width=1)

def sc_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(8, 10, 20))
    import random
    rng = random.Random(21)
    for _ in range(46):  # star field (fixed seed: deterministic)
        sx, sy = x + rng.randint(2, max(2, int(w) - 3)), y + rng.randint(2, max(2, int(h) - 3))
        d.ellipse([sx, sy, sx + 1.4, sy + 1.4], fill=(230, 234, 244))
    pr = int(h * 0.34)  # Mercury: grey cratered disc, lower right
    pcx, pcy = x + int(w * 0.68), y + int(h * 0.60)
    d.ellipse([pcx - pr, pcy - pr, pcx + pr, pcy + pr], fill=(168, 160, 148))
    d.ellipse([pcx - pr, pcy - pr, pcx + int(pr * 0.2), pcy + pr], fill=(140, 132, 120))
    for dx, dy, r in ((-0.3, -0.2, 0.16), (0.25, 0.3, 0.12), (0.05, -0.45, 0.09), (-0.45, 0.35, 0.10)):
        cx, cy = pcx + int(pr * dx), pcy + int(pr * dy); rr = max(2, int(pr * r))
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=(110, 102, 92), width=1)
    ox, oy = x + int(w * 0.20), y + int(h * 0.30)  # the orbiter: bus + two wings
    d.rectangle([ox - 5, oy - 4, ox + 5, oy + 4], fill=(226, 228, 232))
    d.rectangle([ox - 20, oy - 3, ox - 6, oy + 3], fill=(52, 84, 168))
    d.rectangle([ox + 6, oy - 3, ox + 20, oy + 3], fill=(52, 84, 168))
    d.line([ox + 5, oy, ox + 12, oy - 9], fill=(226, 228, 232), width=1)
    d.ellipse([ox + 11, oy - 11, ox + 15, oy - 7], fill=(240, 200, 90))
    for t in range(0, 9):  # dashed approach path toward the planet
        px_ = ox + (pcx - pr - ox) * t / 8; py_ = oy + (pcy - 10 - oy) * t / 8
        if t % 2 == 0:
            d.ellipse([px_ - 1, py_ - 1, px_ + 1, py_ + 1], fill=(250, 200, 90))

SCENES = {"kyiv": sc_kyiv, "cyclone": sc_cyclone, "markets": sc_markets,
          "flags": sc_flags, "cop": sc_cop, "field": sc_field, "iraq": sc_iraq,
          "strike": sc_strike, "bars": sc_bars, "court": sc_court,
          "oil": sc_oil, "ballot": sc_ballot, "cricket": sc_cricket,
          "blast": sc_blast, "target": sc_target, "cyber": sc_cyber,
          "steppe": sc_steppe, "chip": sc_chip, "tanker": sc_tanker,
          "intercept": sc_intercept, "mercury": sc_mercury}

# ---- strip furniture: accent rule, source tag (top-right), data label
# chip (bottom-left), caption band (bottom edge). Zones never overlap. ----
def draw_strip(d, card, x, y, w, h, lead=False):
    SCENES[card["scene"]](d, x, y, w, h)
    rc = REGIONS[card["region"]]
    d.rectangle([x, y, x + w, y + 3], fill=rc)
    band_h = 16 if lead else 12
    d.rectangle([x, y + h - band_h, x + w, y + h], fill=INK)
    cf = fit(d, card["caption"], "ab", 10 if lead else 9, w - 10)
    ctext(d, x + w / 2, y + h - band_h + (1 if lead else 0), card["caption"], cf, PARCH)
    tag_f = AB(10 if lead else 9)
    tag_w = tw(d, card["tag"], tag_f) + 8
    ty = y + 5 if lead else y + 2
    d.rectangle([x + w - tag_w - 3, ty, x + w - 3, ty + (14 if lead else 13)], fill=INK)
    d.text((x + w - tag_w + 1, ty + 1), card["tag"], font=tag_f, fill=PARCH)
    lab_f = fit(d, card["label"], "ab", 12 if lead else 10, w - 12)
    lab_w = tw(d, card["label"], lab_f) + 9
    lab_h = 16 if lead else 13
    ly = y + h - band_h - lab_h - 2
    d.rectangle([x + 3, ly, x + 3 + lab_w, ly + lab_h], fill=BURG)
    d.text((x + 7, ly + 2), card["label"], font=lab_f, fill=(255, 255, 255))

def draw_card(d, card, x, y, w, strip_h, lead=False):
    d.rectangle([x, y, x + w, y + strip_h], outline=CARDB, width=1)
    draw_strip(d, card, x, y, w, strip_h, lead)
    rc = REGIONS[card["region"]]
    ry = y + strip_h + (5 if lead else 3)
    d.text((x + 1, ry), "%d  %s - %s - %s" % (card["no"], card["place"], card["region"], card["topic"]),
           font=AB(11 if lead else 9), fill=rc)
    hy = ry + (15 if lead else 12)
    hf = PF(22 if lead else 14)
    for ln in wrap(d, card["headline"], hf, w - 2)[:2]:
        d.text((x + 1, hy), ln, font=hf, fill=INK)
        hy += 24 if lead else 15
    df = AM(12)
    for ln in wrap(d, card["deck"], df, w - 2):
        d.text((x + 1, hy + 1), ln, font=df, fill=(64, 74, 62))
        hy += 13 if lead else 12.5
    return hy

# ---- page head ----
def draw_top(d):
    # kicker bar: series line left, coverage promise right
    d.rectangle([0, 0, W, 24], fill=FOREST)
    d.text((M, 5), "THE WORLD IN ONE DAY  ·  GAZETTEER EDITION", font=AB(12), fill=PARCH)
    right = "40 STORIES - 7 REGIONS - EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((W - M - tw(d, right, AB(11)), 6), right, font=AB(11), fill=PARCH)
    # masthead: the name is the giant serif anchor; the date block sits right
    d.text((M, 29), "The Daily Atlas", font=PF(44), fill=INK)
    date1 = "SATURDAY 21 NOVEMBER 2026"
    d.text((W - M - tw(d, date1, AB(14)), 34), date1, font=AB(14), fill=FOREST)
    date2 = "Atlas edition - one page, the whole day"
    d.text((W - M - tw(d, date2, AM(11)), 54), date2, font=AM(11), fill=(84, 92, 76))
    d.line([M, 78, W - M, 78], fill=BURG, width=3)
    # HOOK band: the day's biggest stories + their numbers, first-glance read
    d.rectangle([M, 84, W - M, 108], fill=BURG)
    hook = "MISSILES LAND IN POLAND  -  900,000 AI CHIPS CLEARED FOR CHINA  -  BRENT $94.65 AS IRAN CREWS ITS KHARG CONVOY"
    ctext(d, W / 2, 90, hook, fit(d, hook, "ab", 13, CW - 24), (255, 255, 255))
    # UTC timeline strip
    cw5 = CW / 5
    for i, (lab, ev) in enumerate(TIMELINE):
        cx = M + i * cw5
        if i:
            d.line([cx, 114, cx, 144], fill=RULE, width=1)
        d.text((cx + 8, 109), lab, font=AB(10), fill=FOREST)
        ey = 120
        for ln in wrap(d, ev, AM(10), cw5 - 14)[:2]:
            d.text((cx + 8, ey), ln, font=AM(10), fill=INK)
            ey += 11
    d.line([M, 144, W - M, 144], fill=RULE, width=1)
    # THE DAY IN NUMBERS
    d.text((M, 148), "THE DAY IN NUMBERS", font=AB(10), fill=FOREST)
    cw6 = CW / 6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i * cw6
        ctext(d, cx + cw6 / 2, 160, num, PF(25), BURG)
        cy = 189
        for ln in wrap(d, cap, AM(10), cw6 - 8)[:2]:
            ctext(d, cx + cw6 / 2, cy, ln, AM(10), (84, 92, 76))
            cy += 11
    # region count chips
    cw7 = (CW - 6 * 6) / 7
    for i, (name, n) in enumerate(REGION_COUNTS):
        cx = M + i * (cw7 + 6)
        d.rectangle([cx, 213, cx + cw7, 231], fill=REGIONS[name])
        ctext(d, cx + cw7 / 2, 217, "%s %d" % (name, n), AB(10), (255, 255, 255))
    d.line([M, 236, W - M, 236], fill=RULE, width=1)

def draw_cards(d):
    lead_w = (CW - 2 * 12) / 3
    end = 0
    for i, card in enumerate(CARDS[:3]):
        end = max(end, draw_card(d, card, M + i * (lead_w + 12), 240, lead_w, 54, lead=True))
    fy = end + 8
    feat_w = (CW - 4 * 10) / 5
    for r in range(2):
        end = 0
        for c in range(5):
            card = CARDS[3 + r * 5 + c]
            end = max(end, draw_card(d, card, M + c * (feat_w + 10), fy, feat_w, 32, lead=False))
        fy = end + 8
    return fy

# ---- hero map panel (bottom-left, 430 wide) ----
def draw_map(d, top, bottom=960):
    x0, x1 = M, M + 430
    d.rectangle([x0, top, x1, bottom], fill=MAPBG)
    d.text((x0 + 12, top + 7), "WHERE IT HAPPENED", font=AB(12), fill=PARCH)
    mx0, mx1, my0, my1 = x0 + 10, x1 - 10, top + 28, bottom - 30
    def px(lon):
        return mx0 + (lon + 180) / 360 * (mx1 - mx0)
    def py(lat):
        return my0 + (82 - lat) / 140 * (my1 - my0)
    for glon in range(-150, 181, 30):
        d.line([px(glon), my0, px(glon), my1], fill=(36, 74, 52), width=1)
    for glat in range(-45, 76, 15):
        d.line([mx0, py(glat), mx1, py(glat)], fill=(36, 74, 52), width=1)
    for rings in WORLD.values():
        for ring in rings.split("|"):
            pts = []
            for pair in ring.split(","):
                lo, la = pair.split(":")
                pts.append((px(float(lo)), py(float(la))))
            if len(pts) >= 3:
                d.polygon(pts, fill=LAND)
    for no, _t, region, lon, lat in BRIEFS:  # brief dots under the pins
        if lon is not None:
            cx, cy = px(lon), py(lat)
            d.ellipse([cx - 2.6, cy - 2.6, cx + 2.6, cy + 2.6], fill=REGIONS[region])
    for card in CARDS:  # numbered pins for the pictured stories (12 is in space)
        if card["lon"] is None:
            continue
        cx, cy = px(card["lon"]), py(card["lat"])
        r = 9
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=REGIONS[card["region"]], outline=PARCH, width=2)
        s = str(card["no"])
        f = AB(10)
        d.text((cx - tw(d, s, f) / 2, cy - 5), s, font=f, fill=(255, 255, 255))
    d.text((x0 + 12, bottom - 18), "Pins = pictured stories - dots = briefs - no. 12 is in space (Mercury)",
           font=AM(9), fill=PARCH)

# ---- briefs column (bottom-right) ----
def draw_briefs(d, top):
    x = M + 430 + 16
    w = W - M - x
    d.text((x, top + 5), "ALSO ON SATURDAY 21 NOVEMBER - 27 MORE STORIES", font=AB(12), fill=FOREST)
    d.line([x, top + 21, W - M, top + 21], fill=FOREST, width=1)
    y0 = top + 26
    lh = (960 - y0) / len(BRIEFS)
    y = y0
    for no, text, region, _lon, _lat in BRIEFS:
        ns = str(no)
        d.text((x, y), ns, font=AB(10), fill=REGIONS[region])
        off = tw(d, ns, AB(10)) + 5
        lines = wrap(d, text, AM(10), w - off)
        for j, ln in enumerate(lines):
            d.text((x + off if j == 0 else x + off, y + j * 11), ln, font=AM(10), fill=(52, 62, 54))
        y += lh
    return lh

# ---- date check + footer ----
def draw_bottom_bands(d):
    y0, y1 = 966, 1004
    d.rectangle([M, y0, W - M, y1], fill=PAPER, outline=BURG, width=2)
    lab = "DATE CHECK"
    d.text((M + 8, y0 + 5), lab, font=AB(10), fill=BURG)
    tx = M + 8 + tw(d, lab, AB(10)) + 8
    lines = wrap(d, DATE_CHECK, AM(9), (W - M - 8) - tx)[:1]
    rest = wrap(d, DATE_CHECK, AM(9), CW - 16)
    # first line beside the label, remainder full width below
    words = DATE_CHECK.split()
    first, cur = [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, AM(9)) <= (W - M - 8) - tx:
            cur = t
        else:
            break
    first = cur
    remainder = DATE_CHECK[len(first):].strip()
    d.text((tx, y0 + 5), first, font=AM(9), fill=INK)
    yy = y0 + 16
    for ln in wrap(d, remainder, AM(9), CW - 16)[:2]:
        d.text((M + 8, yy), ln, font=AM(9), fill=INK)
        yy += 11
    d.text((M, 1010), FOOTER_L, font=AM(9), fill=(84, 92, 76))
    d.text((W - M - tw(d, FOOTER_R, AM(9)), 1010), FOOTER_R, font=AM(9), fill=(84, 92, 76))

def build():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_top(d)
    bottom_top = draw_cards(d)
    lh = draw_briefs(d, bottom_top)
    draw_map(d, bottom_top)
    draw_bottom_bands(d)
    out = os.path.join(HERE, "entry.png")
    # Palette-quantize (no dither, flat-illustration palette) to win the
    # byte tie-break against the 181-198 KB leaders without hurting the
    # 300 px read: text edges stay on palette colours.
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(out, optimize=True)
    print("bottom_top:", bottom_top, "brief leading: %.2f" % lh)
    print("saved", out, os.path.getsize(out), "bytes")

if __name__ == "__main__":
    build()
