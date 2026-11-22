#!/usr/bin/env python3
"""THE DAILY ATLAS — round-4 challenger (d4) for News Image 20261121,
account @rojanon11. GANTI-grade rebuild of challenger-d2: same paper
name, wholly new page — an inverted navy "midnight atlas" masthead,
a gold hook band, and three duel layouts (A/B/C) sharing one verified
fact pool. Every fact comes ONLY from POOL21.md (Saturday 21 Nov 2026):
EU ADOPTED 1bn euro aid (never "8bn paid"), Wall Street -5.28%, the
400-drone/110-missile barrage, Akvan's 372,000 moved, Mongolia's
resignation, ANC 31%, India 159/1 on day TWO.
Run: python3 draw.py [A|B|C]  ->  writes entry.png (winner) beside
this file; variant renders go to variant-<X>.png.
Deterministic: stdlib + Pillow only, no network.
"""
import os, sys, math
from PIL import Image, ImageDraw, ImageFont
from mapdata import WORLD

HERE = os.path.dirname(os.path.abspath(__file__))
W = H = 1024
M = 24
CW = W - 2 * M

# ---- palette: midnight atlas (new identity for d4) ----
BG     = (246, 243, 236)   # warm white
PAPER  = (255, 253, 247)
INK    = (22, 30, 44)      # near-black navy ink
NAVY   = (16, 32, 56)      # masthead / map deep navy
NAVY2  = (24, 48, 80)
GOLD   = (198, 152, 46)
BURG   = (140, 47, 57)     # hook band / accents
RULE   = (190, 182, 160)
CARDB  = (198, 190, 168)
LAND   = (172, 198, 178)   # sage land on navy
CREAM  = (243, 236, 218)

REGIONS = {
    "EUROPE":   (176, 58, 46),
    "ASIA":     (29, 111, 184),
    "MIDEAST":  (125, 60, 152),
    "AFRICA":   (30, 132, 73),
    "AMERICAS": (202, 111, 30),
    "OCEANIA":  (20, 143, 119),
    "GLOBAL":   (93, 109, 126),
}

def _font(name, size):
    return ImageFont.truetype(os.path.join(HERE, "fonts", name), size)
_cache = {}
def PF(size): return _cache.setdefault(("pf", size), _font("PlayfairDisplay-900.ttf", size))
def AB(size): return _cache.setdefault(("ab", size), _font("Archivo-Bold.ttf", size))
def AM(size): return _cache.setdefault(("am", size), _font("Archivo-Medium.ttf", size))

# ---- POOL21 verbatim strips ----
NUMBERS = [
    ("3",       "weapons cross into Poland: two missiles and a jet drone"),
    ("42",      "injured in the Kryvyi Rih strike, four of them children"),
    ("-5.28%",  "Nasdaq's fall at Friday's close"),
    ("372,000", "people moved to shelters as Akvan hit"),
    ("\u20ac1BN", "EU military aid adopted for Ukraine"),
    ("159/1",   "India at stumps in Wellington"),
]
TIMELINE = [
    ("OVERNIGHT", "Kryvyi Rih strike: two killed, 42 injured"),
    ("MORNING",   "Rutte flies to Warsaw over the missiles"),
    ("MIDDAY",    "Antalya: third COP31 draft due after overnight talks"),
    ("AFTERNOON", "Denmark expels the Russian attache"),
    ("EVENING",   "Stumps in Wellington: India 159/1"),
]
REGION_COUNTS = [("EUROPE", 16), ("ASIA", 6), ("AMERICAS", 8), ("MIDEAST", 6),
                 ("AFRICA", 1), ("OCEANIA", 1), ("GLOBAL", 2)]

CARDS = [
 dict(no=1, place="WARSAW, POLAND", region="EUROPE", topic="WAR",
      headline="Rutte flies to Warsaw after missiles land",
      deck="Two missiles and a suspected jet drone came down in the south-east, a Kh-101 near Nowy Lipowiec. Rutte calls it a \u201cgrave violation\u201d; Tusk calls it a deliberate provocation. (AP)",
      tag="AP - SOFX", label="3 WEAPONS CROSS", caption="WARSAW \u00b7 MISSILES DOWN",
      lon=21.0, lat=52.2, scene="field"),
 dict(no=2, place="ANTALYA", region="GLOBAL", topic="CLIMATE",
      headline="COP31 runs into overtime with no deal yet",
      deck="Talks ran past Friday's scheduled close into Saturday. The draft drops every fossil-fuel reference and the $120bn finance target; a third draft is due this morning. (AP)",
      tag="Ongoing - AP", label="NO DEAL YET", caption="ANTALYA \u00b7 OVERTIME TALKS",
      lon=30.7, lat=36.9, scene="cop"),
 dict(no=3, place="NEW YORK", region="AMERICAS", topic="MARKETS",
      headline="Wall Street enters correction as AI rout deepens",
      deck="The S&P 500 fell about 3.7% on Friday, pushing it into correction territory. The Nasdaq dropped 5.28% as chip and AI shares plunged. (SimpleLife)",
      tag="Friday's close", label="NASDAQ -5.28%", caption="NEW YORK \u00b7 FRIDAY'S CLOSE",
      lon=-74.0, lat=40.7, scene="markets"),
 dict(no=4, place="KRYVYI RIH", region="EUROPE", topic="WAR",
      headline="Russian strike kills two, injures 42",
      deck="An overnight strike kills two and injures 42, four of them children, the city's military chief says. One of Russia's largest attacks of the war. (AppiStos)",
      tag="City chief says", label="2 DEAD - 42 HURT", caption="KRYVYI RIH \u00b7 OVERNIGHT STRIKE",
      lon=33.4, lat=47.9, scene="blast"),
 dict(no=5, place="COPENHAGEN", region="EUROPE", topic="SECURITY",
      headline="Denmark exposes 'assassination plot'",
      deck="Russia 'planned and initiated' a bid to kill a Ukrainian-American rapper near Copenhagen, Denmark says. The Russian attache is expelled. (BBC)",
      tag="Denmark says - BBC", label="ATTACHE EXPELLED", caption="COPENHAGEN \u00b7 PLOT EXPOSED",
      lon=12.6, lat=55.7, scene="target"),
 dict(no=6, place="KYIV", region="EUROPE", topic="WAR",
      headline="Russia's barrage: 400 drones, 110 missiles",
      deck="At least eight dead across Ukraine in the overnight barrage. The Austrian embassy is hit in Kyiv; France calls for a UN Security Council meeting. (BBC)",
      tag="Officials' count", label="400 DRONES - 110 MISSILES", caption="KYIV \u00b7 OVERNIGHT BARRAGE",
      lon=30.5, lat=50.4, scene="intercept"),
 dict(no=7, place="ODISHA, INDIA", region="ASIA", topic="STORM",
      headline="After Akvan: 372,000 moved, no deaths",
      deck="A day after landfall, no deaths reported and relief is under way. The storm weakens to a depression; schools shut through Saturday. (Ridhu Times)",
      tag="Relief reports", label="372,000 MOVED", caption="ODISHA \u00b7 AFTER AKVAN",
      lon=84.9, lat=19.3, scene="cyclone"),
 dict(no=8, place="BRUSSELS", region="EUROPE", topic="DEFENCE",
      headline="EU adopts \u20ac1bn military aid for Ukraine",
      deck="Joint buying runs via the Peace Facility. Britain pledges 1,000+ drones in a \u00a3260m package alongside the EU deal. (Reuters)",
      tag="Adopted - EU", label="\u20ac1BN ADOPTED", caption="BRUSSELS \u00b7 AID ADOPTED",
      lon=4.3, lat=50.8, scene="flags"),
 dict(no=9, place="NEW YORK", region="AMERICAS", topic="CYBER",
      headline="JPMorgan, Visa, Mastercard hit by cyberattack",
      deck="The banks report incidents at third-party vendors. Their core payment networks are unaffected, they say. (Reuters)",
      tag="Banks say", label="3 NETWORKS HIT", caption="NEW YORK \u00b7 PAYMENT NETWORKS",
      lon=-73.9, lat=40.8, scene="cyber"),
 dict(no=10, place="ULAANBAATAR", region="ASIA", topic="POLITICS",
      headline="Mongolia's president resigns",
      deck="The resignation sets the stage for a snap election. It caps a week of political turmoil in the capital. (Reuters)",
      tag="Capital reports", label="SNAP ELECTION NEXT", caption="ULAANBAATAR \u00b7 RESIGNATION",
      lon=106.9, lat=47.9, scene="steppe"),
 dict(no=11, place="THE HAGUE", region="GLOBAL", topic="LAW",
      headline="Myanmar ruling rattles Israel's Gaza defence",
      deck="The world court's genocide verdict against Myanmar raises questions in Jerusalem over its own case, experts say. Ruling came on Thursday. (BBC)",
      tag="Experts say", label="GENOCIDE VERDICT", caption="THE HAGUE \u00b7 WORLD COURT",
      lon=4.3, lat=52.1, scene="court"),
 dict(no=12, place="JOHANNESBURG", region="AFRICA", topic="POLITICS",
      headline="ANC scrambles after worst result since 1994",
      deck="The ANC wins 31% of the vote, its worst since 1994. It now races for coalition deals to stay in government. (BBC)",
      tag="Count - BBC", label="ANC 31%", caption="JOHANNESBURG \u00b7 THE COUNT",
      lon=28.0, lat=-26.2, scene="ballot"),
 dict(no=13, place="WELLINGTON", region="OCEANIA", topic="CRICKET",
      headline="India fight back: 159/1 at stumps, day two",
      deck="India trail New Zealand by 209 in the first Test after the hosts made 368. Nicholls made 175 not out for the hosts. (ICC)",
      tag="Scorecard - ICC", label="159/1 - DAY TWO", caption="WELLINGTON \u00b7 DAY TWO",
      lon=174.8, lat=-41.3, scene="cricket"),
]

BRIEFS = [
 (14, "Kathmandu Nepal's new leader Balendra Shah faces an India test (BBC)", "ASIA", 85.3, 27.7),
 (15, "Washington US releases more UFO footage filmed in the Middle East (BBC)", "AMERICAS", -77.0, 38.9),
 (16, "Los Angeles Hyundai unveils the 2027 Elantra at the auto show (Fast Company)", "AMERICAS", -118.2, 34.1),
 (17, "Cardiff Lauren Price beats Kotaskova to become undisputed champion (BBC)", "EUROPE", -3.2, 51.5),
 (18, "Paris Three police are sentenced over the beating of Michel Zecler (BBC)", "EUROPE", 2.4, 48.9),
 (19, "Oxford Life, 22 years minimum, for the Thames drowning murder (BBC)", "EUROPE", -1.3, 51.8),
 (20, "New York Nikhil Gupta gets 19+ years over the Sikh murder plot (BBC)", "AMERICAS", -74.0, 40.7),
 (21, "Cincinnati Fiona the hippo dies after eating a hat (AP)", "AMERICAS", -84.5, 39.1),
 (22, "Washington US sanctions four Iranians over oil revenues (OFAC)", "MIDEAST", -77.1, 38.8),
 (23, "Hormuz A tanker is struck and on fire in the Strait of Hormuz (UKMTO)", "MIDEAST", 56.3, 26.6),
 (24, "Los Angeles A jury convicts the man who started the Palisades Fire (AP)", "AMERICAS", -118.3, 34.0),
 (25, "Frankfurt ECB names Boone and Brunnermeier for its Executive Board (Reuters)", "EUROPE", 8.7, 50.1),
 (26, "Buenos Aires Argentina's Senate backs a disability framework, 71-0 (AP)", "AMERICAS", -58.4, -34.6),
 (27, "Riyadh A Saudi coalition intercepts Houthi missiles over Riyadh (Reuters)", "MIDEAST", 46.7, 24.6),
 (28, "Barcelona A pill is hailed as a breakthrough for pancreatic cancer (Reuters)", "EUROPE", 2.2, 41.4),
 (29, "Gaza On World Children's Day, Palestinian children appeal for help (UN)", "MIDEAST", 34.3, 31.5),
 (30, "Madrid Amnesty says Spanish police used excess force in the strike (AP)", "EUROPE", -3.7, 40.4),
 (31, "Rome Italian workers and students march against Meloni's government (AFP)", "EUROPE", 12.5, 41.9),
 (32, "Jeddah Saudi Arabia warns of thunderstorms through Tuesday (SPA)", "MIDEAST", 39.2, 21.5),
 (33, "Kuala Lumpur Malaysia to send 10,000 Rohingya to Turkey for training (Reuters)", "ASIA", 101.7, 3.1),
 (34, "Kharkiv Ukraine says it has finished a \u201cBear Trap\u201d in the Kharkiv area (Ukrinform)", "EUROPE", 36.2, 49.9),
 (35, "Islamabad Pakistan's minerals are worth $8-10 trillion, its minister says (Reuters)", "ASIA", 73.1, 33.7),
 (36, "Singapore US presses Singapore and Malaysia on Iran sanctions (Reuters)", "ASIA", 103.8, 1.35),
 (37, "Paris France seeks a UN council meeting on the Kyiv strikes (AFP)", "EUROPE", 2.3, 48.8),
 (38, "Kyiv The war tally: 771 Ukrainians killed, 2,300+ missing (homevo)", "EUROPE", 30.6, 50.5),
 (39, "Ankara Turkey welcomes the World Court's Myanmar ruling (Anadolu)", "MIDEAST", 32.9, 39.9),
 (40, "Turin ATP semis are set: Alcaraz v Shelton, Zverev v Medvedev (ATP)", "EUROPE", 7.7, 45.1),
]

DATE_CHECK = ("Left out as Friday 20 November's news: Kyiv's three bridges hit, Cyclone Akvan's "
 "landfall at Gopalpur, COP31's final day ending with no deal, Asia's AI sell-off (Taipei -6.2%), "
 "the UK-EU reset deal and Phillips's 118 in the first innings. Not yet happened, so not shown: "
 "any final COP31 text, the ATP semi-final results and BepiColombo's entry into orbit around "
 "Mercury (due today).")
FOOTER_L = "Every story here happened, or was first reported, on Saturday 21 November 2026. Contested claims are attributed."
FOOTER_R = "Sources named beside each story \u00b7 original drawings"

# ---- text helpers ----
def tw(d, s, f): return d.textlength(s, font=f)
def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, f) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines
def fit(d, s, start, maxw, floor=8):
    size = start
    while size > floor and tw(d, s, AB(size)) > maxw: size -= 1
    return AB(size)
def ctext(d, cx, y, s, f, fill): d.text((cx - tw(d, s, f) / 2, y), s, font=f, fill=fill)

# ---- flat scene illustrations (fresh compositions for the POOL21 cards) ----
def sc_field(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(140, 170, 100))
    for i in range(4):
        fy = y + int(h*(0.30+0.17*i)); d.line([x, fy, x+w, fy-int(h*0.05)], fill=(110, 140, 74), width=2)
    mx, my = x+int(w*0.58), y+int(h*0.30)
    d.polygon([(mx, my), (mx+int(w*0.26), my+int(h*0.20)), (mx+int(w*0.23), my+int(h*0.30)), (mx-int(w*0.03), my+int(h*0.10))], fill=(150, 152, 156))
    d.ellipse([mx+int(w*0.16), my+int(h*0.30), mx+int(w*0.30), my+int(h*0.40)], outline=(90, 80, 60), width=2)
    dx, dy = x+int(w*0.16), y+int(h*0.36)  # drone silhouette
    d.polygon([(dx-9, dy), (dx+9, dy), (dx+4, dy+5), (dx-4, dy+5)], fill=(40, 44, 48))
    d.line([dx-13, dy-3, dx+13, dy-3], fill=(40, 44, 48), width=2)

def sc_cop(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(86, 128, 156))
    gx, gy, gr = x+int(w*0.30), y+int(h*0.48), int(h*0.34)
    d.ellipse([gx-gr, gy-gr, gx+gr, gy+gr], fill=(70, 130, 90))
    d.ellipse([gx-int(gr*0.55), gy-int(gr*0.5), gx-int(gr*0.05), gy-int(gr*0.05)], fill=(120, 160, 90))
    tx = x+int(w*0.68); tw_ = max(5, int(w*0.05))
    d.rectangle([tx, y+int(h*0.14), tx+tw_, y+int(h*0.66)], outline=(240, 240, 240), width=2)
    d.rectangle([tx+1, y+int(h*0.40), tx+tw_-1, y+int(h*0.66)], fill=(220, 70, 50))
    d.rectangle([x, y+int(h*0.86), x+w, y+h], fill=(60, 96, 120))

def sc_markets(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(29, 33, 43))
    for i in range(1, 4):
        gy = y+int(h*i/4); d.line([x+3, gy, x+w-3, gy], fill=(58, 66, 80), width=1)
    pts = [(0.04, 0.22), (0.24, 0.30), (0.42, 0.26), (0.60, 0.48), (0.78, 0.55), (0.96, 0.78)]
    xy = [(x+int(w*fx), y+int(h*fy)) for fx, fy in pts]
    d.line(xy, fill=(232, 76, 60), width=2)
    for px, py in xy: d.ellipse([px-2, py-2, px+2, py+2], fill=(232, 76, 60))

def sc_blast(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(52, 54, 74))
    for i, bh in enumerate((0.34, 0.48, 0.28, 0.42, 0.32, 0.52, 0.30)):
        bx = x+int(w*(0.02+0.14*i)); bw = int(w*0.12)
        d.rectangle([bx, y+h-int(h*bh), bx+bw, y+h], fill=(26, 27, 38))
    cx, cy = x+int(w*0.60), y+int(h*0.34)
    for k in range(12):
        a = 2*math.pi*k/12; r = int(h*(0.30 if k % 2 == 0 else 0.16))
        d.line([cx, cy, cx+r*math.cos(a), cy+r*0.72*math.sin(a)], fill=(255, 170, 60), width=2)
    d.ellipse([cx-int(h*0.13), cy-int(h*0.10), cx+int(h*0.13), cy+int(h*0.10)], fill=(255, 196, 84))

def sc_target(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(126, 148, 168))
    for i, rh in enumerate((0.26, 0.36, 0.22, 0.32, 0.27)):
        rx = x+int(w*(0.03+0.19*i)); rw = int(w*0.17); ry = y+h-int(h*rh)
        d.rectangle([rx, ry+int(h*0.10), rx+rw, y+h], fill=(104, 92, 84))
    cx, cy = x+int(w*0.56), y+int(h*0.42); r = int(h*0.30)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(198, 44, 40), width=2)
    d.line([cx-r-5, cy, cx-r+7, cy], fill=(198, 44, 40), width=2)
    d.line([cx+r-7, cy, cx+r+5, cy], fill=(198, 44, 40), width=2)
    d.ellipse([cx-2, cy-2, cx+2, cy+2], fill=(198, 44, 40))

def sc_intercept(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(26, 30, 52))
    for i, bh in enumerate((0.30, 0.44, 0.26, 0.38, 0.30, 0.48, 0.28)):
        bx = x+int(w*(0.02+0.14*i)); bw = int(w*0.12)
        d.rectangle([bx, y+h-int(h*bh), bx+bw, y+h], fill=(12, 14, 26))
    for fx, fy in ((0.30, 0.30), (0.58, 0.22), (0.80, 0.36)):
        cx, cy = x+int(w*fx), y+int(h*fy)
        for a in range(8):
            ang = 2*math.pi*a/8; r = int(h*0.13)
            d.line([cx, cy, cx+r*math.cos(ang), cy+r*0.8*math.sin(ang)], fill=(255, 190, 90), width=1)
        d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(255, 220, 140))
    # drone + missile counts as tiny silhouettes along the top
    for i in range(6):
        dx = x+int(w*(0.06+0.15*i)); dy = y+int(h*0.10)
        d.polygon([(dx-5, dy), (dx+5, dy), (dx, dy+4)], fill=(200, 200, 210))

def sc_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(84, 118, 148))
    d.rectangle([x, y+int(h*0.66), x+w, y+h], fill=(46, 84, 110))
    cx, cy = x+int(w*0.62), y+int(h*0.40)
    for r in (int(h*0.34), int(h*0.24), int(h*0.14)):
        d.arc([cx-r, cy-int(r*0.62), cx+r, cy+int(r*0.62)], 20, 300, fill=(235, 240, 244), width=2)
    d.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(255, 255, 255))
    shore = y+int(h*0.66)
    for i in range(3):
        tx = x+int(w*(0.06+0.13*i)); tw_ = max(10, int(w*0.10))
        d.polygon([(tx, shore), (tx+tw_//2, shore-int(h*0.16)), (tx+tw_, shore)], fill=(240, 200, 120))

def sc_flags(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(112, 146, 186))
    d.rectangle([x, y+int(h*0.80), x+w, y+h], fill=(90, 120, 84))
    def flag(fx, fw, fh, eu):
        fy = y+int(h*0.16)
        d.line([fx, fy, fx, y+int(h*0.82)], fill=(60, 54, 44), width=2)
        d.rectangle([fx+2, fy, fx+2+fw, fy+fh], fill=(36, 52, 120))
        if eu:
            ccx, ccy, rr = fx+2+fw/2, fy+fh/2, fh*0.30
            for k in range(8):
                a = 2*math.pi*k/8; sx, sy = ccx+rr*math.cos(a), ccy+rr*math.sin(a)
                d.ellipse([sx-1.5, sy-1.5, sx+1.5, sy+1.5], fill=(245, 197, 24))
        else:
            d.line([fx+2, fy, fx+2+fw, fy+fh], fill=(240, 240, 240), width=2)
            d.line([fx+2, fy+fh, fx+2+fw, fy], fill=(240, 240, 240), width=2)
            d.rectangle([fx+2+fw//2-2, fy, fx+2+fw//2+2, fy+fh], fill=(200, 40, 50))
            d.rectangle([fx+2, fy+fh//2-2, fx+2+fw, fy+fh//2+2], fill=(200, 40, 50))
    fw, fh = int(w*0.30), int(h*0.40)
    flag(x+int(w*0.10), fw, fh, eu=False); flag(x+int(w*0.56), fw, fh, eu=True)

def sc_cyber(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(24, 30, 44))
    cw_, ch_ = int(w*0.24), int(h*0.52)
    for i, col in enumerate(((196, 204, 214), (88, 130, 190), (178, 58, 52))):
        cx = x+int(w*(0.05+0.27*i)); cy = y+int(h*0.16)
        d.rounded_rectangle([cx, cy, cx+cw_, cy+ch_], radius=4, fill=col)
        d.rectangle([cx, cy+int(ch_*0.24), cx+cw_, cy+int(ch_*0.40)], fill=(40, 44, 54))

def sc_steppe(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+int(h*0.60)], fill=(120, 168, 208))
    d.rectangle([x, y+int(h*0.60), x+w, y+h], fill=(140, 160, 84))
    gx, gy = x+int(w*0.30), y+int(h*0.62); gw, gh = int(w*0.30), int(h*0.30)
    d.rectangle([gx, gy, gx+gw, gy+gh], fill=(244, 242, 236))
    d.pieslice([gx-2, gy-int(gh*0.55), gx+gw+2, gy+int(gh*0.45)], 180, 360, fill=(238, 234, 226))
    fx = x+int(w*0.76)
    d.line([fx, y+int(h*0.16), fx, y+int(h*0.86)], fill=(70, 60, 50), width=2)
    fw, fh = int(w*0.17), int(h*0.30); fy = y+int(h*0.16)
    for i, col in enumerate(((206, 42, 48), (0, 96, 160), (206, 42, 48))):
        d.rectangle([fx+2+i*fw//3, fy, fx+2+(i+1)*fw//3, fy+fh], fill=col)

def sc_court(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(104, 116, 138))
    cx = x+w//2
    d.polygon([(cx-int(w*0.34), y+int(h*0.30)), (cx+int(w*0.34), y+int(h*0.30)), (cx, y+int(h*0.08))], fill=(226, 222, 208))
    for i in range(4):
        cxx = cx-int(w*0.27)+i*int(w*0.18)
        d.rectangle([cxx, y+int(h*0.40), cxx+int(w*0.07), y+int(h*0.78)], fill=(238, 236, 226))
    d.rectangle([cx-int(w*0.36), y+int(h*0.80), cx+int(w*0.36), y+int(h*0.88)], fill=(226, 222, 208))

def sc_ballot(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(96, 118, 96))
    bx0, bx1 = x+int(w*0.30), x+int(w*0.72); by0, by1 = y+int(h*0.44), y+int(h*0.86)
    d.rectangle([bx0, by0, bx1, by1], fill=(226, 220, 200))
    d.rectangle([bx0+int(w*0.06), by0+int(h*0.08), bx1-int(w*0.06), by0+int(h*0.15)], fill=(52, 48, 44))
    px0 = x+int(w*0.40)
    d.polygon([(px0, by0-int(h*0.26)), (px0+int(w*0.20), by0-int(h*0.30)), (px0+int(w*0.20), by0-int(h*0.02)), (px0, by0+int(h*0.02))], fill=(250, 250, 246))
    # 31% tally bars
    d.rectangle([x+int(w*0.06), y+int(h*0.20), x+int(w*0.06)+int(w*0.31), y+int(h*0.30)], fill=(245, 197, 24))
    d.rectangle([x+int(w*0.06), y+int(h*0.34), x+int(w*0.06)+int(w*0.69), y+int(h*0.42)], fill=(200, 200, 200))

def sc_cricket(d, x, y, w, h):
    d.rectangle([x, y, x+w, y+h], fill=(92, 142, 82))
    d.rectangle([x+int(w*0.28), y, x+int(w*0.72), y+h], fill=(198, 172, 112))
    sx = x+int(w*0.60)
    for i in range(3):
        d.line([sx+i*4-4, y+int(h*0.30), sx+i*4-4, y+int(h*0.72)], fill=(240, 230, 190), width=2)
    bx, by = x+int(w*0.82), y+int(h*0.34)
    d.ellipse([bx-4, by-4, bx+4, by+4], fill=(196, 40, 44))

SCENES = {"field": sc_field, "cop": sc_cop, "markets": sc_markets, "blast": sc_blast,
          "target": sc_target, "intercept": sc_intercept, "cyclone": sc_cyclone,
          "flags": sc_flags, "cyber": sc_cyber, "steppe": sc_steppe, "court": sc_court,
          "ballot": sc_ballot, "cricket": sc_cricket}

# ---- card rendering ----
def draw_strip(d, card, x, y, w, h, lead=False, shaded=False):
    if shaded:  # pseudo-3D treatment: offset shadow plate under the strip
        d.rectangle([x+3, y+3, x+w+3, y+h+3], fill=(160, 152, 132))
    SCENES[card["scene"]](d, x, y, w, h)
    rc = REGIONS[card["region"]]
    d.rectangle([x, y, x+w, y+3], fill=rc)
    band_h = 15 if lead else 12
    d.rectangle([x, y+h-band_h, x+w, y+h], fill=NAVY)
    cf = fit(d, card["caption"], 10 if lead else 9, w-10)
    ctext(d, x+w/2, y+h-band_h+1, card["caption"], cf, CREAM)
    # Source tag chip (top-right) and data label chip (bottom-left) are
    # stacked zones: with mini strips at 42px the tag ends exactly where
    # the label begins, so even card 6's long label cannot collide.
    tag_f = AB(9 if lead else 8)
    tag_w = tw(d, card["tag"], tag_f) + 8
    tag_h = 13 if lead else 12
    d.rectangle([x+w-tag_w-3, y+4, x+w-3, y+4+tag_h], fill=NAVY)
    d.text((x+w-tag_w+1, y+5), card["tag"], font=tag_f, fill=CREAM)
    lab_f = fit(d, card["label"], 11 if lead else 10, w-12)
    lab_w = tw(d, card["label"], lab_f) + 9
    ly = y+h-band_h-14
    d.rectangle([x+3, ly, x+3+lab_w, ly+13], fill=BURG)
    d.text((x+7, ly+1), card["label"], font=lab_f, fill=(255, 255, 255))

def draw_card(d, card, x, y, w, strip_h, lead=False, shaded=False):
    d.rectangle([x, y, x+w, y+strip_h], outline=CARDB, width=1)
    draw_strip(d, card, x, y, w, strip_h, lead, shaded)
    rc = REGIONS[card["region"]]
    ry = y + strip_h + 4
    d.text((x+1, ry), "%d  %s \u00b7 %s \u00b7 %s" % (card["no"], card["place"], card["region"], card["topic"]),
           font=AB(10 if lead else 9), fill=rc)
    hy = ry + (14 if lead else 12)
    hf = PF(20 if lead else 13)
    for ln in wrap(d, card["headline"], hf, w-2)[:2]:
        d.text((x+1, hy), ln, font=hf, fill=INK); hy += 20 if lead else 15
    df, dlh = (AM(11), 12) if lead else (AM(10), 10.5)
    for ln in wrap(d, card["deck"], df, w-2):
        d.text((x+1, hy+1), ln, font=df, fill=(64, 74, 62)); hy += dlh
    return hy

# ---- shared head: inverted masthead, hook, timeline, numbers, regions ----
def draw_head(d, variant):
    d.rectangle([0, 0, W, 96], fill=NAVY)
    d.text((M, 6), "THE WORLD'S NEWS IN ONE PICTURE", font=AB(11), fill=GOLD)
    r = "40 STORIES \u00b7 7 REGIONS \u00b7 EVERY ONE DATED SATURDAY 21 NOVEMBER 2026"
    d.text((W-M-tw(d, r, AB(11)), 6), r, font=AB(11), fill=CREAM)
    if variant == "B":
        d.text((M, 24), "The Daily Atlas", font=PF(52), fill=(255, 255, 255))
        dl = "SATURDAY 21 NOVEMBER 2026"
        d.text((W-M-tw(d, dl, AB(15)), 40), dl, font=AB(15), fill=GOLD)
        d.text((W-M-tw(d, "Midnight atlas edition", AM(11)), 62), "Midnight atlas edition", font=AM(11), fill=CREAM)
    else:
        ctext(d, W/2, 22, "The Daily Atlas", PF(56), (255, 255, 255))
    d.line([M, 92, W-M, 92], fill=GOLD, width=2)
    sub = "Missiles land in Poland \u00b7 COP31 slips into overtime \u00b7 Wall Street falls into correction \u00b7 Denmark exposes a plot"
    ctext(d, W/2, 100, sub, fit(d, sub, 11, CW-16), INK)
    # hook band (gold for d4, distinct from d2 burgundy band)
    d.rectangle([M, 112, W-M, 136], fill=GOLD)
    hook = "TOP OF THE DAY \u2014 1 RUTTE FLIES TO WARSAW AFTER MISSILES LAND  \u00b7  2 COP31 RUNS INTO OVERTIME, NO DEAL YET  \u00b7  3 WALL STREET ENTERS CORRECTION, NASDAQ -5.28%"
    ctext(d, W/2, 118, hook, fit(d, hook, 12, CW-20), NAVY)
    # timeline
    cw5 = CW/5
    for i, (lab, ev) in enumerate(TIMELINE):
        cx = M + i*cw5
        if i: d.line([cx, 144, cx, 170], fill=RULE, width=1)
        d.text((cx+8, 141), lab, font=AB(10), fill=BURG)
        ey = 152
        for ln in wrap(d, ev, AM(9), cw5-14)[:2]:
            d.text((cx+8, ey), ln, font=AM(9), fill=INK); ey += 10
    d.line([M, 172, W-M, 172], fill=RULE, width=1)
    # numbers
    d.text((M, 176), "THE DAY IN NUMBERS", font=AB(10), fill=NAVY)
    cw6 = CW/6
    for i, (num, cap) in enumerate(NUMBERS):
        cx = M + i*cw6
        ctext(d, cx+cw6/2, 187, num, PF(23), BURG)
        cy = 213
        for ln in wrap(d, cap, AM(9), cw6-8)[:2]:
            ctext(d, cx+cw6/2, cy, ln, AM(9), (84, 92, 76)); cy += 10
    # region chips
    cw7 = (CW - 6*6)/7
    for i, (name, n) in enumerate(REGION_COUNTS):
        cx = M + i*(cw7+6)
        d.rectangle([cx, 234, cx+cw7, 250], fill=REGIONS[name])
        ctext(d, cx+cw7/2, 237, "%s %d" % (name, n), AB(9), (255, 255, 255))
    d.line([M, 254, W-M, 254], fill=RULE, width=1)
    return 258

# ---- map panel ----
def draw_map(d, x0, top, x1, bottom, shaded=False):
    if shaded:
        d.rectangle([x0+4, top+4, x1+4, bottom+4], fill=(150, 142, 122))
    d.rectangle([x0, top, x1, bottom], fill=NAVY)
    d.text((x0+12, top+7), "WHERE IT HAPPENED", font=AB(12), fill=CREAM)
    mx0, mx1, my0, my1 = x0+10, x1-10, top+28, bottom-26
    def px(lon): return mx0 + (lon+180)/360*(mx1-mx0)
    def py(lat): return my0 + (82-lat)/140*(my1-my0)
    for glon in range(-150, 181, 30):
        d.line([px(glon), my0, px(glon), my1], fill=NAVY2, width=1)
    for glat in range(-45, 76, 15):
        d.line([mx0, py(glat), mx1, py(glat)], fill=NAVY2, width=1)
    for rings in WORLD.values():
        for ring in rings.split("|"):
            pts = []
            for pair in ring.split(","):
                lo, la = pair.split(":"); pts.append((px(float(lo)), py(float(la))))
            if len(pts) >= 3: d.polygon(pts, fill=LAND)
    for no, _t, region, lon, lat in BRIEFS:
        cx, cy = px(lon), py(lat)
        d.ellipse([cx-2.6, cy-2.6, cx+2.6, cy+2.6], fill=REGIONS[region])
    for card in CARDS:
        cx, cy = px(card["lon"]), py(card["lat"]); r = 9
        if shaded:
            d.ellipse([cx-r+2, cy-r+2, cx+r+2, cy+r+2], fill=(10, 18, 30))
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=REGIONS[card["region"]], outline=CREAM, width=2)
        s = str(card["no"]); f = AB(10)
        d.text((cx-tw(d, s, f)/2, cy-5), s, font=f, fill=(255, 255, 255))
    d.text((x0+12, bottom-17), "Numbered pins = pictured stories \u00b7 small dots = briefs",
           font=AM(9), fill=CREAM)

# ---- briefs ----
def draw_briefs(d, x, top, w, items, lh=10.5, fsize=9):
    y = top
    for no, text, region, _lon, _lat in items:
        ns = str(no)
        d.text((x, y), ns, font=AB(fsize), fill=REGIONS[region])
        off = tw(d, ns, AB(fsize)) + 5
        for j, ln in enumerate(wrap(d, text, AM(fsize), w-off)):
            d.text((x+off, y+j*10), ln, font=AM(fsize), fill=(52, 62, 54))
        y += lh * max(1, len(wrap(d, text, AM(fsize), w-off)))
    return y

def briefs_header(d, x, top, w):
    d.text((x, top), "ALSO ON SATURDAY 21 NOVEMBER \u2014 27 MORE STORIES", font=AB(11), fill=NAVY)
    d.line([x, top+14, x+w, top+14], fill=NAVY, width=1)
    return top + 18

# ---- bottom bands ----
def draw_bottom(d):
    y0, y1 = 968, 1006
    d.rectangle([M, y0, W-M, y1], fill=PAPER, outline=BURG, width=2)
    lab = "DATE CHECK"
    d.text((M+8, y0+5), lab, font=AB(10), fill=BURG)
    tx = M + 8 + tw(d, lab, AB(10)) + 8
    words = DATE_CHECK.split(); cur = ""
    for w_ in words:
        t = (cur+" "+w_).strip()
        if tw(d, t, AM(9)) <= (W-M-8)-tx: cur = t
        else: break
    d.text((tx, y0+5), cur, font=AM(9), fill=INK)
    rest = DATE_CHECK[len(cur):].strip(); yy = y0+16
    for ln in wrap(d, rest, AM(9), CW-16)[:2]:
        d.text((M+8, yy), ln, font=AM(9), fill=INK); yy += 11
    d.text((M, 1011), FOOTER_L, font=AM(8), fill=(84, 92, 76))
    d.text((W-M-tw(d, FOOTER_R, AM(8)), 1011), FOOTER_R, font=AM(8), fill=(84, 92, 76))

# ---- layouts ----
def layout_A(d):
    """Leads on top, map bottom-RIGHT, briefs bottom-left (swap of d2)."""
    top = draw_head(d, "A")
    lead_w = (CW-2*12)/3; end = 0
    for i, card in enumerate(CARDS[:3]):
        end = max(end, draw_card(d, card, M+i*(lead_w+12), top+4, lead_w, 52, lead=True))
    fy = end + 6
    feat_w = (CW-4*10)/5
    for r in range(2):
        end = 0
        for c in range(5):
            end = max(end, draw_card(d, CARDS[3+r*5+c], M+c*(feat_w+10), fy, feat_w, 32))
        fy = end + 6
    draw_map(d, W-M-430, fy, W-M, 962)
    bw = 430 + 16
    by = briefs_header(d, M, fy+2, CW-bw)
    draw_briefs(d, M, by, CW-bw, BRIEFS, lh=10.2, fsize=9)
    return fy

def layout_B(d):
    """Map as a raised (pseudo-3D shaded) plate beside two stacked leads."""
    top = draw_head(d, "B")
    left_w = 540
    y = top + 4
    for card in CARDS[:2]:
        y = draw_card(d, card, M, y, left_w, 46, lead=True, shaded=True) + 8
    draw_map(d, M+left_w+16, top+4, W-M, y-8, shaded=True)
    fy = y + 2
    feat_w = (CW-4*10)/5
    end = 0
    for c in range(5):
        end = max(end, draw_card(d, CARDS[2+c], M+c*(feat_w+10), fy, feat_w, 32, shaded=True))
    fy = end + 6
    end = 0
    for c in range(5):
        end = max(end, draw_card(d, CARDS[7+c], M+c*(feat_w+10), fy, feat_w, 32, shaded=True))
    fy = end + 6
    end = max(end, draw_card(d, CARDS[12], M, fy, feat_w, 32, shaded=True))
    by = briefs_header(d, M+feat_w+16, fy+2, CW-feat_w-16)
    draw_briefs(d, M+feat_w+16, by, CW-feat_w-16, BRIEFS, lh=10.2, fsize=9)
    return fy

def layout_C(d):
    """Wide map banner mid-page; briefs in two columns at the foot."""
    top = draw_head(d, "C")
    lead_w = (CW-2*12)/3; end = 0
    for i, card in enumerate(CARDS[:3]):
        end = max(end, draw_card(d, card, M+i*(lead_w+12), top+4, lead_w, 42, lead=True))
    my0 = end + 6
    draw_map(d, M, my0, W-M, my0+126)
    fy = my0 + 134
    feat_w = (CW-4*10)/5
    for r in range(2):
        end = 0
        for c in range(5):
            end = max(end, draw_card(d, CARDS[3+r*5+c], M+c*(feat_w+10), fy, feat_w, 42))
        fy = end + 6
    by = briefs_header(d, M, fy+2, CW)
    half = (len(BRIEFS)+1)//2
    colw = (CW-16)/2
    draw_briefs(d, M, by, colw, BRIEFS[:half], lh=9.4, fsize=9)
    draw_briefs(d, M+colw+16, by, colw, BRIEFS[half:], lh=9.4, fsize=9)
    return fy

LAYOUTS = {"A": layout_A, "B": layout_B, "C": layout_C}

def build(variant="C", out="entry.png"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    LAYOUTS[variant](d)
    draw_bottom(d)
    path = os.path.join(HERE, out)
    q = img.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.Dither.NONE)
    q.save(path, optimize=True)
    print(variant, "saved", path, os.path.getsize(path), "bytes")
    return path

if __name__ == "__main__":
    v = sys.argv[1] if len(sys.argv) > 1 else "C"
    if v == "ALL":
        for k in "ABC": build(k, "variant-%s.png" % k)
    else:
        build(v, "entry.png")
