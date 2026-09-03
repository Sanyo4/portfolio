#!/usr/bin/env python3
"""Build the case study pages from case-studies/src/*.md.

Run from the site root:  python tools/build-case-studies.py

Writes:
  case-studies/<slug>.html   one page per source file, in file order
  case-studies/index.html    the hub page
  index.html                 the list between the case-studies:list markers

The vault (Projects/Substack) is the source of truth for the text. Copy a
post here when it changes, then rerun this script. Standard library only.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "case-studies" / "src"
OUT = ROOT / "case-studies"
INDEX = ROOT / "index.html"

DISCLOSURE = (
    "This piece was written with AI assistance, which I use as a dyslexia "
    "adjustment first provided through my Disabled Students' Allowance. Every "
    "fact in it comes from my own maintained record and has been checked by me."
)

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com" />\n'
    '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />\n'
    '  <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400'
    '&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,300;1,6..72,400'
    '&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet" />'
)

FAVICON = (
    '<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E'
    '%3Crect width=%2732%27 height=%2732%27 fill=%27%230d1110%27/%3E%3Ccircle cx=%2716%27 cy=%2716%27 r=%275%27 fill=%27%239db08c%27/%3E%3C/svg%3E" />'
)

THEME_BOOT = ('<script>try{var t=localStorage.getItem("theme");'
              'if(t==="light")document.documentElement.setAttribute("data-theme","light");}catch(e){}</script>')


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
    words = len(re.findall(r"\w+", meta["body"]))
    meta["minutes"] = max(1, round(words / 220))
    return meta


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"<em>\1</em>", s)
    return s


def md_to_html(body):
    out = []
    para = []
    n = 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    for line in body.splitlines():
        if line.startswith("### ") or line.startswith("## "):
            flush()
            text = line[4:].strip() if line.startswith("### ") else line[3:].strip()
            if re.match(r"^\d+\.\s", text):
                out.append(f'<h2>{inline(text)}</h2>')
            else:
                n += 1
                out.append(f'<h2><span class="cs-h2__n">{n:02d}</span>{inline(text)}</h2>')
        elif line.strip() == "":
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def head(title, description):
    return f"""<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
  <script>document.documentElement.classList.replace('no-js','js');</script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}" />
  <meta name="theme-color" content="#0d1110" />
  <meta name="color-scheme" content="dark light" />
  {THEME_BOOT}
  {FAVICON}
  {FONTS}
  <link rel="stylesheet" href="../assets/css/main.css" />
  <link rel="stylesheet" href="../assets/css/case-study.css" />
  <script src="../assets/js/case-study.js" defer></script>
</head>
"""


def nav(active):
    hub_cls = "cs-nav__link is-active" if active == "hub" else "cs-nav__link"
    return f"""  <div class="grain" aria-hidden="true"></div>
  <header class="nav is-in cs-nav" id="nav">
    <a class="nav__mark" href="../index.html">sanay<i>.</i>space</a>
    <nav class="cs-nav__links">
      <a class="{hub_cls}" href="index.html">Case studies</a>
      <a class="cs-nav__link" href="../index.html#building">Building</a>
      <a class="cs-nav__link" href="../index.html#contact">Contact</a>
    </nav>
    <button class="nav__theme" id="theme-btn" type="button" aria-pressed="false"><span class="nav__theme-label" data-dark="Light" data-light="Dark"></span><i class="nav__theme-dot"></i></button>
  </header>
"""


def footer():
    return """    <footer class="foot cs-foot-bar">
      <span class="mono">sanay<i>.</i>space</span>
      <span class="mono"><a href="mailto:sanays.mail@gmail.com">sanays.mail@gmail.com</a> <span class="dot"></span> <a href="https://www.linkedin.com/in/sanay-shah/" target="_blank" rel="noopener">LinkedIn</a></span>
      <span class="mono">2026</span>
    </footer>
"""


def list_items(posts, prefix, cls="reveal-up"):
    rows = []
    for i, p in enumerate(posts, 1):
        pill = ' <span class="dot"></span> start here' if p["start_here"] else ""
        rows.append(f"""        <li class="study {cls}">
          <a class="study__link" href="{prefix}{p['slug']}.html" data-cursor="link">
            <span class="study__num mono">{i:02d}</span>
            <span class="study__main">
              <span class="mono study__kind">{html.escape(p['kind'])}{pill}</span>
              <span class="study__title">{html.escape(p['title'])}</span>
              <span class="study__sf">{html.escape(p['standfirst'])}</span>
            </span>
            <span class="study__time mono">{p['minutes']} min</span>
          </a>
        </li>""")
    return "\n".join(rows)


def article_page(p, i, posts):
    n = len(posts)
    prev_p = posts[i - 2] if i > 1 else None
    next_p = posts[i] if i < n else None
    body_html = md_to_html(p["body"])
    intro = f'\n      <p class="cs-intro">{inline(p["intro"])}</p>' if p.get("intro") else ""
    links = ""
    if p.get("link_url"):
        links = f"""
        <a class="btn cs-foot__link" href="{p['link_url']}" target="_blank" rel="noopener"><span>{html.escape(p['link_label'])} &rarr;</span></a>"""

    def card(q, kind):
        if not q:
            return f'      <span class="cs-pager__card is-empty is-{kind}"></span>'
        lab = "Next" if kind == "next" else "Previous"
        return f"""      <a class="cs-pager__card is-{kind}" href="{q['slug']}.html">
        <span class="mono label">{lab}</span>
        <span class="cs-pager__title">{html.escape(q['short_title'])}</span>
      </a>"""

    return head(f"{p['short_title']} | Sanay Shah", p["standfirst"]) + f"""<body class="cs-page">
{nav("article")}
  <div class="progress" id="progress" aria-hidden="true"></div>

  <main class="cs">
    <article class="cs-article">
      <header class="cs-head">
        <div class="cs-head__top">
          <span class="mono label">{html.escape(p['kind'])} <span class="dot"></span> {i:02d} of {n:02d}</span>
          <a class="mono cs-back" href="index.html">&larr; All case studies</a>
        </div>
        <h1 class="cs-title" data-split="words">{html.escape(p['title'])}</h1>
        <p class="cs-standfirst reveal-up" style="--d:.5s">{html.escape(p['standfirst'])}</p>
        <div class="cs-meta reveal-up" style="--d:.6s">
          <img class="cs-meta__avatar" src="../assets/img/me-sm.webp" alt="Sanay Shah" width="32" height="32" />
          <span class="mono">Sanay Shah <span class="dot"></span> {html.escape(p['date'])} <span class="dot"></span> {p['minutes']} min read</span>
        </div>
      </header>{intro}

      <div class="cs-body">
{body_html}
      </div>

      <footer class="cs-foot">{links}
        <p class="cs-disclosure">{html.escape(DISCLOSURE)}</p>
      </footer>
    </article>

    <nav class="cs-pager" aria-label="More case studies">
{card(prev_p, "prev")}
{card(next_p, "next")}
    </nav>
    <div class="cs-pager__all">
      <a class="arrow-link" href="index.html">All seven case studies <i>&rarr;</i></a>
    </div>
  </main>
{footer()}
</body>
</html>
"""


def hub_page(posts):
    desc = ("Seven case studies from Sanay Shah on putting AI into real work: an accountancy firm's "
            "agent system, a pharmacy group, two products built solo, and the philosophy behind the 80% cap.")
    return head("Case studies | Sanay Shah", desc) + f"""<body class="cs-page">
{nav("hub")}

  <main class="hub">
    <header class="hub__head">
      <p class="mono label">Case studies</p>
      <h1 class="hub__title" data-split="words">Seven pieces on putting AI into real work, <em>written from the record.</em></h1>
      <p class="hub__lead reveal-up" style="--d:.5s">The evidence behind the one-liners on the front page, and the thinking that runs through all of it.</p>
      <p class="hub__body reveal-up" style="--d:.6s">Two firms, two products, one working paper and one essay. Start with the essay if you want the philosophy first. The rest are the incidents, decisions and numbers it came from. Firms are unnamed until they've agreed to be named.</p>
    </header>

    <ol class="studies__list hub__list reveal-up" style="--d:.7s">
{list_items(posts, "", cls="")}
    </ol>
  </main>
{footer()}
</body>
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
    block = start + "\n" + list_items(posts, "case-studies/") + "\n        " + end
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


if __name__ == "__main__":
    main()
