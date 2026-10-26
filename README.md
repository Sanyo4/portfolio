# sanay.space, paper edition

The portfolio site, built as a paper-cut travel scrapbook around one line: "I took 43 flights in 45 weeks doing street photography during my year abroad in Singapore." A push to `main` updates GitHub Pages and Vercel (sanay.space).

Static HTML, one stylesheet, one small script. No framework, no build step for the pages, no tracking.

## Run it

```bash
npx serve -l 5173 .
```

or `python3 -m http.server 5173`. To view it on a phone on the same wifi, use the machine's LAN address.

## Pages

- `index.html`: hero with boarding-pass links, the story as a route of six stops ending at Vedas, work, photography, case studies, footer.
- `map/index.html`: the full map. Every role, win, course and build, linked from the top nav and under the hero passes. Generated from `tools/map_data.py`.
- `flights/index.html`: the flight log, linked from "43 flights in 45 weeks" in the hero. A seatback in-flight map driven by a reel of boarding stubs, one per flight. Generated, see below.
- `hi/index.html`: the meetup card at `sanay.space/hi`. The lockscreen QR code points here, so keep the path. One screen on a phone, no scrolling.
- `case-studies/`: one page per piece plus the hub. Generated, see below. Keep every file name: CVs and LinkedIn link to them.

## Case studies

`python3 tools/build-case-studies.py` builds every page in `case-studies/` from `case-studies/src/*.md`, builds `map/index.html` from `tools/map_data.py`, and refreshes the list on the main page between the `case-studies:list` markers. The vault (`Projects/Substack`) stays the source of truth for the words; the script only restyles them. Beau and Gonzo sit under "Things I made" (the `MADE` set in the script), with Natter linked out to its own page.

## Flights

`python3 tools/build-flights.py` builds `flights/index.html` from `tools/flights.csv`. The map is drawn at build time (plate carree, land from `tools/land-110m.json`, Natural Earth 110m via world-atlas 2.0.2), so the page ships ready-made SVG paths and `assets/js/flights.js` only moves the camera, draws the current route and flies the plane. The same build writes the passport (one stamp per country, in order of first landing, filled in by the script as the reel moves) and the "Stats for nerds" drawer, a plain `<details>` whose numbers are all worked out at build time.

`tools/flights.csv` is the public copy of the vault's `Resources/Flight Log.csv`. Refresh it with `python3 tools/flights_data.py` (it reads the vault by default, or pass the CSV path). It keeps public fields only: no booking references, email links, seats, notes or other passengers, and no cancelled, undated or future flights. Trip titles on the site come from the `TRIPS` table in that script, keyed by the vault ID of each trip's first flight, so the vault's own trip names never reach the repo; a new trip needs a line there. A new airport needs a line in `AIRPORTS`.

## Assets

- `assets/css/site.css`: the design system. Cool paper, sage and slate card stock, vermilion stamp ink. Fraunces for text, IBM Plex Mono for labels, both self-hosted in `assets/fonts/`.
- `assets/css/case-study.css` and `assets/css/hi.css`: page-specific layers on top.
- `assets/js/site.js`: pointer and scroll parallax on the hero paper layers (768px and up only), the route line that fills as you read, the reading progress plane on case studies, and scroll-in for prints. All of it is off under `prefers-reduced-motion`, and the page reads the same without JS.
- `assets/img/`: WebP exports, cropped and resized only. `tools/make-images.sh` rebuilds them from `Pictures/` in this repo and `~/Pictures/portfolio` (set `PHOTOS=` to point elsewhere). Captions are the month each frame was shot, from the camera's EXIF.
- `assets/img/og.jpg`: the link preview. Its source is `tools/og.html`; render that at 1200x630 to update it.

## Adding things

- A photo: export it with a line in `tools/make-images.sh`, then copy a `<figure class="print corners rise">` block in the Photography section.
- A role, win or course: add it to `tools/map_data.py` and rerun the build.
- A story stop: copy an `<li class="beat">` in the route.
- The site shows the first name only ("Sanay"), including page titles and the case-study bylines in `tools/build-case-studies.py`. Keep it that way.
