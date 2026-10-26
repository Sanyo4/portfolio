"""Build flights/index.html: the in-flight map and the reel of boarding stubs.

    python3 tools/flights_data.py      # only when the vault's Flight Log changes
    python3 tools/build-flights.py

Reads tools/flights.csv (public fields only) and tools/land-110m.json. The map
is plate carree at 10 units a degree, cropped to lon -100..150, lat -38..74, so
the browser never projects anything: every route is a ready-made SVG path.
"""
import html
import json
from datetime import date
from pathlib import Path

import flights_data as data
import flights_geo as geo

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "flights" / "index.html"

WEST, EAST, SOUTH, NORTH = -100, 150, -38, 74
SEASON = ("2024-08-01", "2025-07-31")  # the 43 flights in 45 weeks: Madeira to Kalamata
SUFFIX = (" Heathrow", " Gatwick", " Stansted", " Narita", " Haneda", " Incheon", " Gimpo", " Pudong", " Hongqiao", " JFK")

e = html.escape

ISO = {"United Kingdom": "GB", "United States": "US", "Turkey": "TR", "Netherlands": "NL", "Singapore": "SG",
       "Indonesia": "ID", "France": "FR", "India": "IN", "Japan": "JP", "Portugal": "PT", "Malaysia": "MY",
       "Thailand": "TH", "Vietnam": "VN", "South Korea": "KR", "Australia": "AU", "China": "CN", "Taiwan": "TW",
       "Hong Kong": "HK", "Greece": "GR", "Luxembourg": "LU"}
WORDS = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve",
         "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen", "Twenty", "Twenty-one",
         "Twenty-two", "Twenty-three", "Twenty-four", "Twenty-five"]


def city(iata):
    name = data.AIRPORTS[iata][0]
    for s in SUFFIX:
        name = name.replace(s, "")
    return name


def day(iso, fmt="%d %b %y"):
    return date.fromisoformat(iso).strftime(fmt).upper()


def hours(m):
    m = int(m or 0)
    return f"{m // 60} h {m % 60:02d}" if m else ""


def build():
    flights = data.load()
    frame = geo.Frame(WEST, EAST, SOUTH, NORTH, 2500, project=geo.plate_carree)
    W, H = frame.width, round(frame.height)

    season_n = 0
    for i, f in enumerate(flights):
        f["i"] = i
        f["gold"] = f["cabin"] == "Business"
        f["season"] = 0
        if SEASON[0] <= f["date"] <= SEASON[1]:
            season_n += 1
            f["season"] = season_n
        a, b = data.AIRPORTS[f["from"]], data.AIRPORTS[f["to"]]
        pts = geo.great_circle(frame, (a[3], a[2]), (b[3], b[2]), seg_km=120)
        f["d"] = geo.route_path(pts, "{:.0f}")
        f["box"] = [round(min(x for x, _ in pts)), round(min(y for _, y in pts)), round(max(x for x, _ in pts)), round(max(y for _, y in pts))]

    # ---------- the screen ----------
    used = sorted({f["from"] for f in flights} | {f["to"] for f in flights})
    dots = "".join(
        f'<circle r="1.6" cx="{frame(data.AIRPORTS[c][3], data.AIRPORTS[c][2])[0]:.0f}" cy="{frame(data.AIRPORTS[c][3], data.AIRPORTS[c][2])[1]:.0f}" />'
        for c in used)
    sx, sy = frame(103.82, 1.35)
    routes = "\n".join(
        f'        <path id="r{f["i"]}" class="rt{" rt--gold" if f["gold"] else ""}" d="{f["d"]}" />' for f in flights)
    svg = f'''<svg class="screen__map" id="map" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid meet" role="img" aria-label="World map with the route of the selected flight">
        <rect class="sea" x="-2500" y="-2500" width="{W + 5000}" height="{H + 5000}" />
        <path class="grat" d="{geo.graticule(frame, WEST, EAST, SOUTH, NORTH, every=15)}" />
        <path class="land" d="{geo.land_path(frame, step=2, west=WEST - 10, east=EAST + 15)}" />
        <ellipse class="land" cx="{sx:.0f}" cy="{sy:.0f}" rx="2.6" ry="1.6" />
        <g class="dots">{dots}</g>
        <g class="routes">
{routes}
        </g>
        <path class="glow" id="glow" d="" />
        <g class="ends" aria-hidden="true">
          <circle class="end" id="endA" r="3" /><circle class="end" id="endB" r="3" />
          <text class="code" id="codeA"></text><text class="code" id="codeB"></text>
        </g>
        <g class="plane" id="jet"><use href="#plane" x="-16" y="-16" width="32" height="32" /></g>
      </svg>'''

    # ---------- the reel (a plain grouped list without JS) ----------
    groups, trip = [], None
    for f in flights:
        key = (f["trip"], f["date"][:7] if trip is None or trip[0] != f["trip"] else trip[1])
        if trip is None or f["trip"] != trip[0] or date.fromisoformat(f["date"]).toordinal() - date.fromisoformat(groups[-1][1][-1]["date"]).toordinal() > 21:
            trip = key
            groups.append((key, []))
        groups[-1][1].append(f)

    total = len(flights)
    reel = []
    for (name, ym), legs in groups:
        when = date.fromisoformat(legs[0]["date"]).strftime("%B %Y")
        first_season = legs[0]["season"] == 1
        last_season = legs[-1]["season"] == season_n and season_n
        mark = ' trip--start' if first_season else ''
        reel.append(f'''        <section class="trip{mark}" data-trip="{e(name)}" data-when="{when}">
          <h3 class="trip__name">{e(name)} <span class="trip__when">{when}</span></h3>
          <ol class="trip__legs">''')
        for f in legs:
            sub = f"{city(f['from'])} to {city(f['to'])}"
            cls = "leg" + (" leg--gold" if f["gold"] else " leg--season" if f["season"] else "")
            ident = f["flight"] or f["airline"]
            said = ", ".join(x for x in (
                date.fromisoformat(f["date"]).strftime("%d %B %Y").lstrip("0"),
                f"{f['airline']} {f['flight']}".strip(),
                f"{f['dep']} to {f['arr']}{' the next day' if f['next_day'] else ''}" if f["dep"] and f["arr"] else "",
                f"{int(f['km']):,} km",
                f["cabin"] if f["cabin"] != "Economy" else "") if x)
            reel.append(f'''            <li class="{cls}" data-i="{f["i"]}" id="leg{f["i"]}" aria-label="Flight {f["i"] + 1} of {len(flights)}, {e(name)}: {f["from"]} to {f["to"]}, {e(said)}">
              <span class="leg__top"><span>{day(f["date"])}</span><span>{e(ident)}</span></span>
              <span class="leg__codes">{f["from"]} <span aria-hidden="true">&rarr;</span><span class="sr-only">to</span> {f["to"]}</span>
              <span class="leg__cities">{e(sub)}</span>
              <span class="leg__meta">{e(f["airline"])} &middot; {int(f["km"]):,} km</span>
              <span class="leg__n" aria-hidden="true">{f["i"] + 1}</span>
            </li>''')
        reel.append('          </ol>')
        if last_season:
            reel.append('          <p class="trip__end" aria-hidden="true">45 weeks end</p>')
        reel.append('        </section>')

    km = sum(int(f["km"]) for f in flights)
    mins = sum(int(f["min"] or 0) for f in flights)
    countries = sorted({data.AIRPORTS[c][1] for c in used})
    payload = {
        "total": total, "season": season_n,
        "flights": [{
            "date": f["date"], "dep": f["dep"], "arr": f["arr"], "next": bool(f["next_day"]), "flight": f["flight"],
            "airline": f["airline"], "from": f["from"], "to": f["to"], "fromCity": city(f["from"]), "toCity": city(f["to"]),
            "country": data.AIRPORTS[f["to"]][1], "km": int(f["km"]), "min": int(f["min"] or 0), "cabin": f["cabin"],
            "aircraft": f["aircraft"], "trip": f["trip"], "season": f["season"], "gold": f["gold"],
            "a": [round(v) for v in frame(data.AIRPORTS[f["from"]][3], data.AIRPORTS[f["from"]][2])],
            "b": [round(v) for v in frame(data.AIRPORTS[f["to"]][3], data.AIRPORTS[f["to"]][2])],
            "box": f["box"],
        } for f in flights],
        "totals": {"km": km, "minutes": mins, "airports": len(used), "countries": countries},
        # every route with a little sea round it: the opening view
        "world": [min(f["box"][0] for f in flights) - 40, min(f["box"][1] for f in flights) - 30,
                  max(f["box"][2] for f in flights) + 40, max(f["box"][3] for f in flights) + 30],
    }

    first, last = flights[0]["date"], flights[-1]["date"]
    words = {76: "Seventy-six", 77: "Seventy-seven", 78: "Seventy-eight", 79: "Seventy-nine", 80: "Eighty"}
    count = words.get(total, str(total))
    standfirst = (f"{count} flights, {date.fromisoformat(first).strftime('%B %Y')} to {date.fromisoformat(last).strftime('%B %Y')}. "
                  f"The busy stretch is the year in Singapore: {season_n} flights between August 2024 and July 2025, "
                  "most of them short hops around East and Southeast Asia. Two legs are in gold: ANA business class to Tokyo and back, in spring 2024.")

    visas, n_countries = stamps(flights)
    page = TEMPLATE.format(
        standfirst=e(standfirst), svg=svg, reel="\n".join(reel), total=total,
        payload=json.dumps(payload, separators=(",", ":")).replace("</", "<\\/"),
        passes=passes(),
        stats=stats(flights), visas=visas, countries=WORDS[n_countries] if n_countries < len(WORDS) else n_countries,
    )
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"{OUT.relative_to(ROOT)}: {total} flights, {len(page) / 1024:.0f} KB")


def flag(country):
    """Regional-indicator flag emoji; a country missing from ISO just goes without."""
    return "".join(chr(0x1F1E6 + ord(c) - 65) for c in ISO.get(country, ""))


def stamps(flights):
    """The passport: one stamp per country, in order of first landing."""
    first, count = {}, {}
    for f in flights:
        c = data.AIRPORTS[f["to"]][1]
        count[c] = count.get(c, 0) + 1
        first.setdefault(c, f)
    shapes = ("round", "oval", "box")
    tilt = (-8, 5, -3, 9, -6, 3, -10, 7, -2, 6)
    out = []
    for n, (c, f) in enumerate(first.items()):
        ink = "ver" if f["season"] else ("slate" if n % 2 else "sage")
        k = count[c]
        out.append(f'''          <li class="visa visa--{shapes[n % 3]} visa--{ink}" style="--tilt:{tilt[n % len(tilt)]}deg" data-country="{e(c)}" data-first="{f["i"]}">
            <span class="visa__ink">
              <span class="visa__country">{e(c)}</span>
              <span class="visa__code">{f["to"]}</span>
              <span class="visa__date">{day(f["date"])}</span>
            </span>
            <span class="visa__tally"><span class="visa__flag" aria-hidden="true">{flag(c)}</span> <span class="visa__n">{k}</span> {"landing" if k == 1 else "landings"}</span>
          </li>''')
    return "\n".join(out), len(first)


def stats(flights):
    """Stats for nerds: totals, the 43 in 45 on its own, records, flights by year."""
    from collections import Counter

    flights = sorted(flights, key=lambda f: (f["date"], f["dep"] or "99:99"))

    def totals(fs):
        mins = sum(int(f["min"] or 0) for f in fs)
        return {
            "flights": len(fs),
            "km": sum(int(f["km"]) for f in fs),
            "hours": round(mins / 60),
            "untimed": sum(1 for f in fs if not f["min"]),
            "airports": len({f["from"] for f in fs} | {f["to"] for f in fs}),
            "countries": len({data.AIRPORTS[f["to"]][1] for f in fs}),
            "airlines": len({f["airline"] for f in fs}),
        }

    def cards(t, extra):
        rows = [
            ("Flights", f'{t["flights"]}', extra.get("flights", "")),
            ("Distance", f'{t["km"]:,} km', f'{t["km"] / 40075:.1f} times round the Earth'),
            ("In the air", f'{t["hours"]} hours', f'{t["hours"] / 24:.1f} days, gate to gate'
             + (f'; {t["untimed"]} flight{"s" if t["untimed"] > 1 else ""} with no times left out' if t["untimed"] else "")),
            ("Airports", f'{t["airports"]}', ""),
            ("Countries", f'{t["countries"]}', ""),
            ("Airlines", f'{t["airlines"]}', ""),
        ]
        return "".join(
            f'<div class="nerd__stat"><dt>{k}</dt><dd><strong>{v}</strong>{f"<span>{e(s)}</span>" if s else ""}</dd></div>'
            for k, v, s in rows)

    season = [f for f in flights if f["season"]]
    season_block = ""
    if season:
        first, last = date.fromisoformat(season[0]["date"]), date.fromisoformat(season[-1]["date"])
        weeks = round((last - first).days / 7)
        span = f"{first.strftime('%d %b %Y').lstrip('0')} to {last.strftime('%d %b %Y').lstrip('0')}"
        season_block = (f'\n            <h3 class="nerd__head">The {len(season)} flights in {weeks} weeks</h3>'
                        f'\n            <dl class="nerd__grid nerd__grid--season">{cards(totals(season), {"flights": span})}</dl>')

    def named(f, *rest):
        """'BA11 London to Singapore, 10,881 km' without gaps when a field is missing."""
        head = " ".join(x for x in (f["flight"], f"{city(f['from'])} to {city(f['to'])}") if x)
        return ", ".join(x for x in (head, *rest) if x)

    # ties go to the longer flight in time
    longest = max(flights, key=lambda f: (int(f["km"]), int(f["min"] or 0)))
    shortest = min(flights, key=lambda f: (int(f["km"]), int(f["min"] or 0)))
    ends = Counter()
    for f in flights:
        ends[f["from"]] += 1
        ends[f["to"]] += 1
    hub, hub_n = ends.most_common(1)[0]
    routes = Counter(tuple(sorted((f["from"], f["to"]))) for f in flights)
    top_n = routes.most_common(1)[0][1]
    tops = [f"{city(a)} and {city(b)}" for (a, b), k in routes.items() if k == top_n]
    top_routes = "; ".join(tops) + (f", {top_n} flights each" if len(tops) > 1 else f", {top_n} flights")
    months = Counter(f["date"][:7] for f in flights)
    m_n = months.most_common(1)[0][1]
    busy = " and ".join(date.fromisoformat(m + "-01").strftime("%B %Y") for m, k in sorted(months.items()) if k == m_n)
    red = sum(1 for f in flights if f["dep"] and (f["dep"] >= "22:00" or f["dep"] < "05:00"))
    airline, airline_n = Counter(f["airline"] for f in flights).most_common(1)[0]
    typed = [f for f in flights if f["aircraft"]]
    cabins = Counter(f["cabin"] for f in flights)
    cabin_line = ", ".join(f"{cabins[c]} {c.lower()}" for c in ("Economy", "Premium Economy", "Business") if cabins[c])

    records = [
        ("Longest", named(longest, f'{int(longest["km"]):,} km', hours(longest["min"]))),
        ("Shortest", named(shortest, f'{int(shortest["km"]):,} km')),
        ("Busiest airport", f"{ {'SIN': 'Singapore Changi'}.get(hub, data.AIRPORTS[hub][0])}, {hub_n} takeoffs and landings"),
        ("Most flown route", top_routes if top_n > 1 else ""),
        ("Red-eyes", f"{red} flights leaving between 10pm and 5am"),
        ("Busiest month", f"{busy}, {m_n} flights" + (" each" if " and " in busy else "")),
        ("Most flown airline", f"{airline}, {airline_n} flights"),
        ("Cabins", cabin_line),
    ]
    if typed:
        plane, plane_n = Counter(f["aircraft"] for f in typed).most_common(1)[0]
        records.insert(-1, ("Most flown aircraft", f"{plane}, {plane_n} of the {len(typed)} flights with a known type"))
    records = [(k, v) for k, v in records if v]
    years = Counter(f["date"][:4] for f in flights)
    top_year = max(years.values())
    bars = "".join(
        f'<li><span class="nerd__year">{y}</span><span class="nerd__bar" style="--w:{k / top_year:.3f}"></span><span class="nerd__count">{k}</span></li>'
        for y, k in sorted(years.items()))

    return f'''        <details class="nerd" id="stats">
          <summary class="nerd__tab"><span class="mono">Stats for nerds<span class="nerd__sign" aria-hidden="true"></span></span></summary>
          <div class="nerd__body">
            <h2 class="sr-only">Stats for nerds</h2>
            <h3 class="nerd__head">Since {flights[0]["date"][:4]}</h3>
            <dl class="nerd__grid">{cards(totals(flights), {})}</dl>{season_block}
            <h3 class="nerd__head">Records</h3>
            <dl class="nerd__records">{"".join(f"<div><dt>{k}</dt><dd>{e(v)}</dd></div>" for k, v in records)}</dl>
            <h3 class="nerd__head">Flights by year</h3>
            <ol class="nerd__years">{bars}</ol>
          </div>
        </details>'''


def passes():
    """The contact passes, copied from the full map page so the footers stay identical."""
    src = (ROOT / "map" / "index.html").read_text(encoding="utf-8")
    start = src.index('<ul class="passes"', src.index("<footer"))
    return src[start:src.index("</ul>", start) + 5]


TEMPLATE = '''<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <script>document.documentElement.classList.replace("no-js", "js");</script>
  <title>Flights · Sanay</title>
  <meta name="description" content="Every flight Sanay has taken since 2022 on an in-flight map, including the 43 flights in 45 weeks of the year in Singapore." />
  <link rel="canonical" href="https://sanay.space/flights/" />
  <meta name="theme-color" content="#d7e3e3" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="sanay.space" />
  <meta property="og:url" content="https://sanay.space/flights/" />
  <meta property="og:title" content="Flights · Sanay" />
  <meta property="og:description" content="Every flight since 2022 on an in-flight map, including 43 flights in 45 weeks." />
  <meta property="og:image" content="https://sanay.space/assets/img/og.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="../assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="preload" href="../assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="../assets/css/site.css" />
  <link rel="stylesheet" href="../assets/css/case-study.css" />
  <link rel="stylesheet" href="../assets/css/flights.css" />
  <script src="../assets/js/site.js" defer></script>
  <script src="../assets/js/flights.js" defer></script>
</head>
<body class="cs-page flights-page">
  <a class="skip" href="#main">Skip to content</a>
  <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <defs>
      <symbol id="plane" viewBox="0 0 32 32">
        <path d="M2 15 L30 3 L21 29 L15 19 Z" fill="#fbfbf8" stroke="#1b2528" stroke-width="1.5" stroke-linejoin="round" />
        <path d="M30 3 L15 19 L13.5 26.5 L17.8 22" fill="#d9e2e0" stroke="#1b2528" stroke-width="1.5" stroke-linejoin="round" />
      </symbol>
      <symbol id="go" viewBox="0 0 16 16">
        <path d="M4 12 L12 4 M6 4 H12 V10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
      </symbol>
      <symbol id="mail" viewBox="0 0 16 16">
        <path d="M2 4 H14 V12 H2 Z M2 4 L8 9 L14 4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
      </symbol>
    </defs>
  </svg>
  <header class="cs-top">
    <div class="wrap topbar">
      <a class="wordmark" href="../"><span>sanay<b>.</b>space</span></a>
      <nav class="topnav" aria-label="Site">
        <a class="topnav__extra" href="../#story">Story</a>
        <a href="../map/">Full map</a>
        <a href="../case-studies/">Case studies</a>
        <a class="topnav__extra" href="../#contact">Contact</a>
      </nav>
    </div>
  </header>

  <main id="main" class="flights">
    <header class="cs-head cs-head--hub">
      <div class="wrap cs-head__inner">
        <p class="label">Flight log</p>
        <h1 class="cs-title">Every flight since 2022</h1>
        <p class="cs-standfirst">{standfirst}</p>
      </div>
    </header>

    <div class="section torn logbook fl">
      <div class="wrap">
        <p class="label fl__label js-only">In-flight map</p>
        <figure class="screen-fig js-only">
          <div class="screen tape tape--corner">
          <div class="screen__glass">
      {svg}
            <div class="readout" id="readout" aria-hidden="true">
              <p class="readout__count mono"><span id="roCount"></span><span class="readout__season" id="roSeason"></span></p>
              <div class="readout__route">
                <p class="readout__codes" id="roCodes"></p>
                <p class="readout__meta mono" id="roMeta"></p>
              </div>
              <p class="readout__date mono" id="roDate"></p>
            </div>
          </div>
          </div>
          <figcaption class="screen__caption" id="caption"></figcaption>
        </figure>

        <h2 class="fl__list-title">Every flight, by trip</h2>
        <div class="reel" id="reel" aria-label="Flights, in order">
{reel}
        </div>
        <div class="belt js-only" id="belt" aria-hidden="true"><span class="belt__notch"></span></div>

{stats}

        <section class="passport" id="stamps" aria-labelledby="stamps-title">
          <div class="passport__head">
            <p class="label">Passport</p>
            <h2 class="passport__title" id="stamps-title">{countries} countries</h2>
            <p class="passport__lead">Every country I have landed in, stamped with the airport and date of the first landing. Red ink is the Singapore year.</p>
          </div>
          <ol class="passport__page">
{visas}
          </ol>
        </section>
      </div>
    </div>
  </main>

  <script type="application/json" id="flights">{payload}</script>

  <footer class="section torn foot foot--small" id="contact">
    <div class="wrap">
      <div class="foot__grid">
        <div>
          <p class="label">Contact</p>
          <h2 class="foot__title">Say hello</h2>
          <p class="foot__where">Based in London.</p>
        </div>
        {passes}
      </div>
      <div class="foot__small">
        <p class="mono">Sanay · 2026 · <a href="../">sanay.space</a></p>
      </div>
    </div>
  </footer>
</body>
</html>
'''

if __name__ == "__main__":
    build()
