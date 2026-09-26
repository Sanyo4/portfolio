# sanay.space, paper edition

The portfolio site, built as a paper-cut travel scrapbook around one line: "I took 43 flights in 45 weeks doing street photography during my year abroad in Singapore." A push to `main` updates GitHub Pages and Vercel (sanay.space).

Static HTML, one stylesheet, one small script. No framework, no build step for the pages, no tracking.

## Run it

```bash
npx serve -l 5173 .
```

or `python3 -m http.server 5173`. To view it on a phone on the same wifi, use the machine's LAN address.

## Pages

- `index.html`: hero with boarding-pass links, the story as a route of five stops, work, photography, case studies, footer.
- `map/index.html`: the full map. Every role, win, course and build, linked from the top nav and under the hero passes. Generated from `tools/map_data.py`.
- `hi/index.html`: the meetup card at `sanay.space/hi`. The lockscreen QR code points here, so keep the path. One screen on a phone, no scrolling.
- `case-studies/`: one page per piece plus the hub. Generated, see below. Keep every file name: CVs and LinkedIn link to them.

## Case studies

`python3 tools/build-case-studies.py` builds every page in `case-studies/` from `case-studies/src/*.md`, builds `map/index.html` from `tools/map_data.py`, and refreshes the list on the main page between the `case-studies:list` markers. The vault (`Projects/Substack`) stays the source of truth for the words; the script only restyles them. Beau and Gonzo sit under "Things I made" (the `MADE` set in the script), with Natter linked out to its own page.

## Assets

- `assets/css/site.css`: the design system. Cool paper, sage and slate card stock, vermilion stamp ink. Fraunces for text, IBM Plex Mono for labels, both self-hosted in `assets/fonts/`.
- `assets/css/case-study.css` and `assets/css/hi.css`: page-specific layers on top.
- `assets/js/site.js`: pointer and scroll parallax on the hero paper layers (768px and up only), the route line that fills as you read, the reading progress plane on case studies, and scroll-in for prints. All of it is off under `prefers-reduced-motion`, and the page reads the same without JS.
- `assets/img/`: WebP exports, cropped and resized only. `tools/make-images.sh` rebuilds them from `Pictures/` in this repo and `~/Pictures/portfolio` (set `PHOTOS=` to point elsewhere). Captions are the month each frame was shot, from the camera's EXIF.
- `assets/img/og.jpg`: the link preview. Its source is `tools/og.html`; render that at 1200x630 to update it.

## Adding things

- A photo: export it with a line in `tools/make-images.sh`, then copy a `<figure class="print corners rise">` block in the Photography section.
- A role, win or course: add it to `tools/map_data.py` and rerun the build.
- A story stop: copy an `<li class="beat">` in the route. The India stop has a marked place after the graduation stop.
