#!/usr/bin/env python3
"""Build the case study pages from case-studies/src/*.md.

Run from anywhere:  python tools/build-case-studies.py

Writes:
  case-studies/<slug>.html   one page per source file, in file order
  case-studies/index.html    the hub page
  index.html                 the list between the case-studies:list markers

The vault (Projects/Substack) is the source of truth for the text. Copy a
post here when it changes, then rerun this script. The script only restyles:
it never changes the words. Standard library only.

Every link is relative, so the pages work on sanay.space (Vercel) and on the
GitHub Pages project path. The hub links through ../case-studies/ so it also
works when a host serves /case-studies without the trailing slash.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "case-studies" / "src"
OUT = ROOT / "case-studies"
INDEX = ROOT / "index.html"
SITE = "https://sanay.space"

DISCLOSURE = (
    "This piece was written with AI assistance, which I use as a dyslexia "
    "adjustment first provided through my Disabled Students' Allowance. Every "
    "fact in it comes from my own maintained record and has been checked by me."
)

# Which shelf each piece sits on. Anything not listed is Work.
MADE = {"beau", "gonzo"}

# Natter has no write-up yet, so it links out to its own page.
NATTER = {
    "href": "https://natter-landing.vercel.app",
    "kind": "App · Android",
    "title": "Natter: a voice journal that writes the entry for you, on the phone, with nothing sent anywhere",
    "standfirst": "You talk about your day and a small toad asks up to three questions, then writes the page from your own sentences. Beau and Gonzo are folding into it.",
    "meta": "natter-landing.vercel.app ↗",
}

SPRITE = """  <svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
    <defs>
      <filter id="ink" x="-5%" y="-5%" width="110%" height="110%">
        <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4" result="n" />
        <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8" xChannelSelector="R" yChannelSelector="G" result="d" />
        <feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -2.2 0 0 0 2" result="m" />
        <feComposite in="d" in2="m" operator="in" />
      </filter>
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
  </svg>"""


def parse(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path.name}: missing frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        meta[k.strip()] = v
    meta["body"] = m.group(2).strip()
    meta["short_title"] = meta.get("short_title") or meta["title"]
    meta["start_here"] = meta.get("start_here", "false").lower() == "true"
    meta["group"] = "made" if meta["slug"] in MADE else "work"
    words = len(re.findall(r"\w+", meta["body"]))
    meta["minutes"] = max(1, round(words / 220))
    return meta


def link(m):
    text, href = m.group(1), m.group(2)
    if href.startswith("/case-studies/"):
        return f'<a href="{href[len("/case-studies/"):]}">{text}</a>'
    return f'<a href="{href}" target="_blank" rel="noopener">{text}</a>'


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_to_html(body):
    out = []
    para = []
    n = 0
    # A post with its own numbered list keeps only those numbers.
    has_numbers = bool(re.search(r"^#{2,3} \d+\.\s", body, re.M))

    def flush():
        if para:
            out.append("        <p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    for line in body.splitlines():
        if line.startswith("### ") or line.startswith("## "):
            flush()
            text = line[4:].strip() if line.startswith("### ") else line[3:].strip()
            num = re.match(r"^(\d+)\.\s+(.*)$", text)
            if num:
                out.append(f'        <h2><span class="prose__n" aria-hidden="true">{int(num.group(1)):02d}</span><span class="sr-only">{num.group(1)}. </span>{inline(num.group(2))}</h2>')
            elif has_numbers:
                out.append(f'        <h2 class="prose__plain">{inline(text)}</h2>')
            else:
                n += 1
                out.append(f'        <h2><span class="prose__n" aria-hidden="true">{n:02d}</span>{inline(text)}</h2>')
        elif line.strip() == "":
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def head(title, description, url, prefix):
    t = html.escape(title)
    d = html.escape(description, quote=True)
    return f"""<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <script>document.documentElement.classList.replace("no-js", "js");</script>
  <title>{t}</title>
  <meta name="description" content="{d}" />
  <link rel="canonical" href="{url}" />
  <meta name="theme-color" content="#d7e3e3" />
  <meta property="og:type" content="article" />
  <meta property="og:site_name" content="sanay.space" />
  <meta property="og:url" content="{url}" />
  <meta property="og:title" content="{t}" />
  <meta property="og:description" content="{d}" />
  <meta property="og:image" content="{SITE}/assets/img/og.jpg" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{t}" />
  <meta name="twitter:description" content="{d}" />
  <meta name="twitter:image" content="{SITE}/assets/img/og.jpg" />
  <link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="preload" href="{prefix}assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin />
  <link rel="stylesheet" href="{prefix}assets/css/site.css" />
  <link rel="stylesheet" href="{prefix}assets/css/case-study.css" />
  <script src="{prefix}assets/js/site.js" defer></script>
</head>
"""


def topbar(prefix, active):
    cur = ' aria-current="page"' if active == "hub" else ""
    mcur = ' aria-current="page"' if active == "map" else ""
    return f"""  <a class="skip" href="#main">Skip to content</a>
{SPRITE}
  <header class="cs-top">
    <div class="wrap topbar">
      <a class="wordmark" href="{prefix}"><span>sanay<b>.</b>space</span></a>
      <nav class="topnav" aria-label="Site">
        <a class="topnav__extra" href="{prefix}#story">Story</a>
        <a href="{prefix}map/"{mcur}>Full map</a>
        <a href="{prefix}case-studies/"{cur}>Case studies</a>
        <a class="topnav__extra" href="{prefix}#contact">Contact</a>
      </nav>
    </div>
  </header>
"""


def pass_link(cls, href, label, dest, icon="go", external=True):
    ext = ' target="_blank" rel="noopener"' if external else ""
    return (f'<a class="pass {cls}" href="{href}"{ext}><span class="pass__paper"><span class="pass__body">'
            f'<span class="pass__label">{label}</span><span class="pass__dest">{dest}</span></span>'
            f'<span class="pass__stub" aria-hidden="true"><span class="pass__bar"></span><svg><use href="#{icon}" /></svg></span></span></a>')


def footer(prefix):
    return f"""  <footer class="section torn foot foot--small" id="contact">
    <div class="wrap">
      <div class="foot__grid">
        <div>
          <p class="label">Contact</p>
          <h2 class="foot__title">Say hello</h2>
          <p class="foot__where">Based in London.</p>
        </div>
        <ul class="passes" aria-label="Find me elsewhere">
          <li>{pass_link("pass--li", "https://www.linkedin.com/in/sanay-shah/", "LinkedIn", "sanay-shah")}</li>
          <li>{pass_link("pass--ig", "https://www.instagram.com/_s4nay/", "Instagram", "@_s4nay")}</li>
          <li>{pass_link("pass--ph", "https://www.instagram.com/sanay.photography/", "Photography", "@sanay<wbr>.photography")}</li>
          <li>{pass_link("pass--mail", "mailto:sanays.mail@gmail.com", "Email", "sanays.mail<wbr>@gmail.com", "mail", False)}</li>
        </ul>
      </div>
      <div class="foot__small">
        <p class="mono">Sanay Shah · 2026 · <a href="{prefix}">sanay.space</a></p>
      </div>
    </div>
  </footer>
"""


def entry(p, href, with_sf, date=True):
    pill = " · start here" if p.get("start_here") else ""
    sf = f'\n              <span class="entry__sf">{html.escape(p["standfirst"])}</span>' if with_sf else ""
    kind = f'{html.escape(p["kind"])}{" · " + html.escape(p["date"]) if date and p.get("date") else ""}{pill}'
    return f"""          <li>
            <a class="entry rise" href="{href}">
              <span class="entry__kind">{kind}</span>
              <span class="entry__title">{html.escape(p['title'])}</span>{sf}
              <span class="entry__meta">{p['minutes']} min read</span>
            </a>
          </li>"""


def natter_entry(with_sf):
    sf = f'\n              <span class="entry__sf">{html.escape(NATTER["standfirst"])}</span>' if with_sf else ""
    return f"""          <li>
            <a class="entry rise" href="{NATTER['href']}" target="_blank" rel="noopener">
              <span class="entry__kind">{html.escape(NATTER['kind'])}</span>
              <span class="entry__title">{html.escape(NATTER['title'])}</span>{sf}
              <span class="entry__meta">{html.escape(NATTER['meta'])}</span>
            </a>
          </li>"""


def groups(posts, href_prefix, with_sf, heading="h3"):
    work = "\n".join(entry(p, f"{href_prefix}{p['slug']}.html", with_sf) for p in posts if p["group"] == "work")
    made = "\n".join(entry(p, f"{href_prefix}{p['slug']}.html", with_sf) for p in posts if p["group"] == "made")
    made += "\n" + natter_entry(with_sf)
    return f"""        <div class="group">
          <{heading} class="group__title">Work</{heading}>
          <ul class="entries">
{work}
          </ul>
        </div>
        <div class="group">
          <{heading} class="group__title">Things I made</{heading}>
          <ul class="entries">
{made}
          </ul>
        </div>"""


def article_page(p, i, posts):
    n = len(posts)
    prev_p = posts[i - 2] if i > 1 else None
    next_p = posts[i] if i < n else None
    url = f"{SITE}/case-studies/{p['slug']}.html"
    intro = f'\n        <p class="cs-intro">{inline(p["intro"])}</p>' if p.get("intro") else ""
    ext = ""
    if p.get("link_url"):
        ext = "\n        <div class=\"cs-ext\">" + pass_link("pass--ph", p["link_url"], "Visit", html.escape(p["link_label"])) + "</div>"
    shelf = "Things I made" if p["group"] == "made" else "Work"

    def card(q, kind):
        if not q:
            return '      <span class="cs-pager__card is-empty" aria-hidden="true"></span>'
        lab = "Next" if kind == "next" else "Previous"
        arrow = "&rarr;" if kind == "next" else "&larr;"
        return f"""      <a class="cs-pager__card is-{kind}" href="{q['slug']}.html">
        <span class="label">{lab} <span aria-hidden="true">{arrow}</span></span>
        <span class="cs-pager__title">{html.escape(q['short_title'])}</span>
      </a>"""

    return head(f"{p['short_title']} · Sanay Shah", p["standfirst"], url, "../") + f"""<body class="cs-page">
{topbar("../", "article")}  <div class="cs-progress" aria-hidden="true"><span></span><svg><use href="#plane" /></svg></div>

  <main id="main">
    <article class="cs">
      <header class="cs-head">
        <div class="wrap cs-head__inner">
          <p class="cs-head__row">
            <span class="stamp" style="--rot: -5deg">{html.escape(p['kind'])}<strong>{i:02d}/{n:02d}</strong>{html.escape(p['date'])}</span>
            <a class="cs-back" href="./">&larr; All case studies</a>
          </p>
          <p class="label">{shelf}{" · start here" if p["start_here"] else ""}</p>
          <h1 class="cs-title">{html.escape(p['title'])}</h1>
          <p class="cs-standfirst">{html.escape(p['standfirst'])}</p>
          <p class="cs-meta">
            <img src="../assets/img/portrait-240.webp" alt="" width="40" height="40" />
            <span class="mono">Sanay Shah · {html.escape(p['date'])} · {p['minutes']} min read</span>
          </p>
        </div>
      </header>

      <div class="wrap">
        <div class="sheet tape">{intro}
          <div class="prose">
{md_to_html(p["body"])}
          </div>{ext}
          <p class="cs-disclosure">{html.escape(DISCLOSURE)}</p>
        </div>

        <nav class="cs-pager" aria-label="More case studies">
{card(prev_p, "prev")}
{card(next_p, "next")}
        </nav>
        <p class="cs-all"><a class="more-link" href="./">All case studies <span aria-hidden="true">&rarr;</span></a></p>
      </div>
    </article>
  </main>

{footer("../")}</body>
</html>
"""


def hub_page(posts):
    desc = ("Case studies by Sanay Shah on putting AI into real work at an accountancy "
            "practice and a national pharmacy group, plus the things he's built.")
    return head("Case studies · Sanay Shah", desc, f"{SITE}/case-studies/", "../") + f"""<body class="cs-page">
{topbar("../", "hub")}
  <main id="main">
    <header class="cs-head cs-head--hub">
      <div class="wrap cs-head__inner">
        <p class="label">Stamped entries</p>
        <h1 class="cs-title">Case studies</h1>
        <p class="cs-standfirst">Longer write-ups of the work and the things I've built, in my own words. Firms stay unnamed.</p>
      </div>
    </header>

    <section class="section torn writing hub" aria-label="All case studies">
      <div class="wrap">
{groups(posts, "../case-studies/", True, "h2")}
      </div>
    </section>
  </main>

{footer("../")}</body>
</html>
"""


def stub(item):
    paras = "".join(f"\n                <p class=\"stub__what\">{t}</p>" for t in item["text"])
    link = ""
    if item.get("link"):
        href, label = item["link"]
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        link = f'\n                <a class="stub__link" href="{href}"{ext}>{html.escape(label)} <span aria-hidden="true">{"↗" if ext else "→"}</span></a>'
    return f"""            <li class="stub rise">
              <p class="stub__when">{html.escape(item['when'])}</p>
              <div class="stub__body">
                <h3 class="stub__role">{html.escape(item['role'])}</h3>
                <p class="stub__org">{html.escape(item['org'])}</p>{paras}{link}
              </div>
            </li>"""


def map_page():
    import map_data as m

    def block(key, title, items):
        return f"""        <section class="map-group" id="{key}" aria-labelledby="{key}-title">
          <h2 class="group__title" id="{key}-title">{title}</h2>
          <ol class="stubs">
{chr(10).join(stub(i) for i in items)}
          </ol>
        </section>"""

    wins = "\n".join(f"""            <li class="win rise" style="--c: {c}; --rot: {rot}; --rad: {rad}">
              <span class="win__big">{html.escape(b)}{(" · " + html.escape(d)) if d else ""}</span>
              <span class="win__event">{html.escape(e)}</span>
              <span class="win__note">{html.escape(n)}</span>
            </li>""" for b, d, e, n, c, rot, rad in m.WINS)
    prints = "\n".join(f"""          <figure class="print{tape}" style="--r: {r}">
            <img src="../assets/img/{name}-360.webp" srcset="../assets/img/{name}-360.webp 360w, ../assets/img/{name}-640.webp 640w" sizes="(min-width: 960px) 270px, 220px" width="{w}" height="{h}" alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async" />
            <figcaption>{html.escape(cap)}</figcaption>
          </figure>""" for name, w, h, alt, cap, r, tape in m.PRINTS)
    made = "\n".join(f"""            <li>
              <a class="entry rise" href="{href}"{' target="_blank" rel="noopener"' if ext else ""}>
                <span class="entry__kind">{html.escape(kind)}</span>
                <span class="entry__title">{html.escape(title)}</span>
                <span class="entry__sf">{html.escape(sf)}</span>
                <span class="entry__meta">{html.escape(meta)}</span>
              </a>
            </li>""" for href, ext, kind, title, sf, meta in m.MADE)
    legend = [("work", "Work"), ("leadership", "Leadership and volunteering"), ("education", "Education"), ("wins", "Wins"), ("made", "Things I made")]
    chips = "\n".join(f'          <li><a href="#{k}">{t}</a></li>' for k, t in legend)
    desc = ("Everything Sanay Shah has done so far in one place: work, leadership and volunteering, "
            "education, hackathon wins, rowing, theatre and the things he's built.")
    return head("The full map · Sanay Shah", desc, f"{SITE}/map/", "../") + f"""<body class="cs-page map-page">
{topbar("../", "map")}
  <main id="main">
    <header class="cs-head cs-head--hub">
      <div class="wrap cs-head__inner">
        <p class="label">The full map</p>
        <h1 class="cs-title">Every stop so far</h1>
        <p class="cs-standfirst">The main page tells the story. This is the whole logbook: every role, prize and course, newest first.</p>
        <ul class="legend" aria-label="Jump to">
{chips}
        </ul>
      </div>
    </header>

    <div class="section torn logbook map">
      <div class="wrap">
{block("work", "Work", m.WORK)}
{block("leadership", "Leadership and volunteering", m.LEAD)}
{block("education", "Education", m.EDUCATION)}
        <section class="map-group" id="wins" aria-labelledby="wins-title">
          <h2 class="group__title" id="wins-title">Wins and other stamps</h2>
          <ul class="wins">
{wins}
          </ul>
          <div class="snaps" role="group" aria-label="Photos from hackathons and earlier work" tabindex="0">
{prints}
          </div>
        </section>
        <section class="map-group" id="made" aria-labelledby="made-title">
          <h2 class="group__title" id="made-title">Things I made</h2>
          <ul class="entries">
{made}
          </ul>
        </section>
        <p class="cs-all"><a class="more-link" href="../case-studies/">Read the case studies <span aria-hidden="true">&rarr;</span></a></p>
      </div>
    </div>
  </main>

{footer("../")}</body>
</html>
"""


def update_index(posts):
    text = INDEX.read_text(encoding="utf-8")
    start = "<!-- case-studies:list -->"
    end = "<!-- /case-studies:list -->"
    if start not in text or end not in text:
        print("index.html: markers not found, skipped")
        return
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    block = start + "\n" + groups(posts, "case-studies/", False) + "\n        " + end
    INDEX.write_text(before + block + after, encoding="utf-8")


def main():
    posts = [parse(p) for p in sorted(SRC.glob("*.md"))]
    for i, p in enumerate(posts, 1):
        (OUT / f"{p['slug']}.html").write_text(article_page(p, i, posts), encoding="utf-8")
        print(f"{i:02d} {p['slug']}.html  ({p['minutes']} min)")
    (OUT / "index.html").write_text(hub_page(posts), encoding="utf-8")
    print("case-studies/index.html")
    update_index(posts)
    print("index.html list updated")
    import sys
    sys.path.insert(0, str(ROOT / "tools"))
    (ROOT / "map").mkdir(exist_ok=True)
    (ROOT / "map" / "index.html").write_text(map_page(), encoding="utf-8")
    print("map/index.html")


if __name__ == "__main__":
    main()
