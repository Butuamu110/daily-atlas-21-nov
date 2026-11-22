[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/Butuamu110/daily-atlas-21-nov/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/Butuamu110/daily-atlas-21-nov/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# THE DAILY ATLAS — The World in One Day, Saturday 21 November 2026

Round-4 challenger (d4): a GANTI-grade rebuild of the Daily Atlas page. Same paper, new "midnight atlas" design — an inverted navy Playfair masthead with the paper's name as the giant anchor (date demoted to the kicker bar), a gold hook band with the top-3 stories, and a wide world-map banner mid-page.

- All 40 stories happened, or were first reported, on Saturday 21 November 2026 — 13 pictured stories plus 27 briefs, across 7 regions. Every fact is drawn from the verified POOL21 pool: the EU **adopted** €1bn in military aid via the Peace Facility (Britain pledging 1,000+ drones), Wall Street's Nasdaq fell 5.28%, 372,000 people were moved after Akvan, and India stood at 159/1 on day **two**.
- Every pictured card carries a source tag and a data label inside its illustration strip; every deck carries at least two pool facts.
- The map banner plots real country polygons from longitude/latitude data, with numbered pins Ø18px for the 13 pictured stories and small region-coloured dots for the briefs.
- A UTC timeline (5 slots), a "Day in Numbers" strip (6 numbers, all bound to cards) and region counts frame the page; a DATE CHECK box names 6 Friday 20 November stories deliberately left out plus 3 not-yet-happened items.
- Duel record: three layouts were built and duelled on 300px readability + completeness. **C (wide map banner, two-column briefs) won** — A (map bottom-right, single-column briefs) and B (map plate beside stacked leads, pseudo-3D shaded plates/pins) both overflowed their briefs into the DATE CHECK box, and B's 3D-style shading added noise with no readability gain, so the flat 2D treatment is the entry and the shaded treatment is the noted backup.
- Original drawings throughout: every illustration is a flat geometric scene drawn by the program itself — no photographs, no AI images, no network.
- Deterministic: `draw.py` (Python stdlib + Pillow only) renders `entry.png` identically on every run; `main.py` copies it to the output directory named by `MAKEFUN_OUTPUT_DIR`.
