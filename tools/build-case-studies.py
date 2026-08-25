#!/usr/bin/env python3
"""Build the case study pages from case-studies/src/*.md.

Run from the repo root:  python3 tools/build-case-studies.py

Writes:
  case-studies/<slug>.html   one page per source file, in file order
  case-studies/index.html    the hub page
  index.html                 the list between the case-studies:list markers

The vault (Projects/Substack) is the source of truth for the text. Copy a
post here when it changes, then rerun this script. No dependencies beyond
the standard library.
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
    '  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
    '&family=Newsreader:ital,opsz,wght@0,6..72,300;0,6..72,400;0,6..72,500;1,6..72,400'
    '&family=Source+Sans+3:wght@400;500;600&display=swap" rel="stylesheet" />'
)


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

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    for line in body.splitlines():
        if line.startswith("### "):
            flush()
            out.append("<h2>" + inline(line[4:].strip()) + "</h2>")
        elif line.startswith("## "):
            flush()
            out.append("<h2>" + inline(line[3:].strip()) + "</h2>")
        elif line.strip() == "":
            flush()
        else:
            para.append(line.strip())
    flush()
    return "\n".join(out)


def nav(depth_prefix, active):
    hub = "index.html" if depth_prefix == "" else "case-studies/index.html"
    home = "../index.html" if depth_prefix == "" else "index.html"
    hub_cls = "nav__link is-active" if active == "hub" else "nav__link"
    return f"""  <header class="nav panel" id="main-nav">
    <div class="nav__inner">
      <a class="wordmark" href="{home}">Sanay Shah</a>
      <nav class="nav__links">
        <a class="{hub_cls}" href="{hub}">Case studies</a>
        <a class="nav__link nav__link--long" href="{home}#building">Building</a>
        <a class="nav__link nav__link--long" href="{home}#experience">Experience</a>
        <a class="nav__link" href="{home}#connect">Connect</a>
        <button class="theme-toggle" type="button" aria-pressed="false">Dark</button>
      </nav>
    </div>
  </header>"""


def head(title, description, css, canonical_hint=""):
    return f"""<!DOCTYPE html>
<html lang="en">

<head>
  <script>document.documentElement.classList.add('js');</script>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description, quote=True)}" />
  {FONTS}
  <link rel="stylesheet" href="{css}" />
</head>
"""


def stage(prefix):
    return f"""  <div class="stage" aria-hidden="true">
    <img class="stage__img" src="{prefix}assets/hero.jpg" alt="" />
    <div class="stage__veil"></div>
    <div class="stage__grain"></div>
  </div>
"""


def footer(prefix, wide=False):
    cls = "footer footer--wide" if wide else "footer"
    return f"""    <div class="{cls} reveal" style="--d:0.2s">
      <span class="footer__mark">Sanay Shah</span>
      <a href="mailto:sanays.mail@gmail.com">sanays.mail@gmail.com</a>
      <a href="https://www.linkedin.com/in/sanay-shah/" target="_blank" rel="noopener">LinkedIn</a>
      <span class="footer__spacer"></span>
      <span>London &middot; Singapore</span>
      <span>&copy; 2026</span>
    </div>
"""


def list_items(posts, prefix):
    rows = []
    for i, p in enumerate(posts, 1):
        pill = '<span class="status-pill">Start here</span>' if p["start_here"] else ""
        rows.append(f"""          <a class="cs-item" href="{prefix}{p['slug']}.html">
            <span class="cs-item__num">{i:02d}</span>
            <span>
              <span class="cs-item__kind"><span class="label">{html.escape(p['kind'])}</span>{pill}</span>
              <span class="cs-item__title" style="display:block">{html.escape(p['title'])}</span>
              <span class="cs-item__sf" style="display:block">{html.escape(p['standfirst'])}</span>
              <span class="cs-item__meta" style="display:block">{html.escape(p['date'])} &middot; {p['minutes']} min read</span>
            </span>
            <span class="cs-item__arrow" aria-hidden="true">&rarr;</span>
          </a>""")
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
        <div class="cs-foot__links">
          <a class="chip" href="{p['link_url']}" target="_blank" rel="noopener">{html.escape(p['link_label'])} <span aria-hidden="true">&rarr;</span></a>
        </div>"""

    def card(q, kind):
        if not q:
            return f'      <span class="panel cs-pager__card is-empty is-{kind}"></span>'
        lab = "Next" if kind == "next" else "Previous"
        return f"""      <a class="panel cs-pager__card is-{kind}" href="{q['slug']}.html">
        <span class="label">{lab}</span>
        <span class="cs-pager__title" style="display:block">{html.escape(q['short_title'])}</span>
      </a>"""

    desc = p["standfirst"]
    return head(f"{p['short_title']} | Sanay Shah", desc, "../assets/case-study.css") + f"""
<body>
{stage("../")}
  <div class="progress" id="progress" aria-hidden="true"></div>
{nav("", "article")}

  <main class="cs">
    <article class="panel cs-article reveal">
      <header class="cs-head">
        <div class="cs-head__top">
          <span class="label">{html.escape(p['kind'])} &middot; {i:02d} of {n:02d}</span>
          <a class="cs-back" href="index.html">&larr; All case studies</a>
        </div>
        <h1 class="cs-title">{html.escape(p['title'])}</h1>
        <p class="lead cs-standfirst">{html.escape(p['standfirst'])}</p>
        <div class="cs-meta">
          <img class="cs-meta__avatar" src="../Pictures/me.jpg" alt="Sanay Shah" />
          <span><b>Sanay Shah</b></span>
          <span class="cs-meta__dot">&middot;</span>
          <span>{html.escape(p['date'])}</span>
          <span class="cs-meta__dot">&middot;</span>
          <span>{p['minutes']} min read</span>
        </div>
      </header>{intro}

      <div class="cs-body">
{body_html}
      </div>

      <footer class="cs-foot">{links}
        <p class="cs-disclosure">{html.escape(DISCLOSURE)}</p>
      </footer>
    </article>

    <nav class="cs-pager reveal" style="--d:0.1s" aria-label="More case studies">
{card(prev_p, "prev")}
{card(next_p, "next")}
    </nav>
    <div class="cs-pager__all reveal" style="--d:0.15s">
      <a class="chip" href="index.html">All seven case studies</a>
    </div>

{footer("../")}
  </main>

  <script src="../assets/case-study.js"></script>
</body>

</html>
"""


def hub_page(posts):
    desc = ("Seven case studies from Sanay Shah on putting AI into real work: an accountancy firm's "
            "agent system, a pharmacy group, two products built solo, and the philosophy behind the 80% cap.")
    return head("Case studies | Sanay Shah", desc, "../assets/case-study.css") + f"""
<body>
{stage("../")}
{nav("", "hub")}

  <main class="hub">
    <div class="wrap">
      <div class="panel hub__head reveal">
        <p class="label">Case studies</p>
        <h1>Seven pieces on putting AI into real work, <i>written from the record.</i></h1>
        <p class="lead">The evidence behind the one-liners on the front page, and the thinking that runs through all of it.</p>
        <p class="bodytext">Two firms, two products, one working paper and one essay. Start with the essay if you want the philosophy first. The rest are the incidents, decisions and numbers it came from. Firms are unnamed until they've agreed to be named.</p>
      </div>

      <div class="panel cs-list reveal" style="--d:0.08s">
{list_items(posts, "")}
      </div>

{footer("../", wide=True)}
    </div>
  </main>

  <script src="../assets/case-study.js"></script>
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
    block = start + "\n" + list_items(posts, "case-studies/") + "\n          " + end
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
