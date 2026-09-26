#!/usr/bin/env bash
# Exports the site photos as sized WebP files in assets/img.
# Crops and resizes only; the look of each photo is left as shot.
# Sources: Pictures/ in this repo and ~/Pictures/portfolio (not in the repo).
set -euo pipefail
cd "$(dirname "$0")/.."
SRC="${PHOTOS:-$HOME/Pictures/portfolio}"
P="Pictures"
OUT="assets/img"
mkdir -p "$OUT"

# name source crop(WxH+X+Y or -) widths...
exp() {
  local name="$1" src="$2" crop="$3"; shift 3
  for w in "$@"; do
    if [ "$crop" = "-" ]; then
      magick "$src" -auto-orient -resize "${w}x>" -strip -quality 74 "$OUT/$name-$w.webp"
    else
      magick "$src" -auto-orient -crop "$crop" +repage -resize "${w}x>" -strip -quality 74 "$OUT/$name-$w.webp"
    fi
  done
}

# Hero and /hi
exp bromo      "$SRC/me/DSCF1179.jpg"            -  420 760
exp tower      "$SRC/street/DSCF0464~2.jpg"      -  240 360 640
exp portrait   "$SRC/me/DSC06863~2.jpg"          -  240 480
exp mirror     "$SRC/me/DSCF2284.jpg"            -  420 760

# The year abroad strip
exp sanoai     "$SRC/me/PXL_20250118_061221115.MP~2.jpg" 2030x3045+0+280 260 360 640
exp steps      "$SRC/me/DSCF3993.jpg"            -  260 360 640
exp books      "$SRC/me/DSCF4906.jpg"            -  260 360 640
exp monorail   "$SRC/me/DSCF7114_exported_16316.jpg" 1080x1620+0+120 260 360 640
exp mural      "$SRC/me/DSCF6420.jpg"            -  480 820

# Street photography
for f in DSCF0582 DSCF1951 DSCF3232 DSCF7328 DSCF6740 DSCF7145 DSCF1552 DSCF3685 DSCF0721 DSCF6403 DSCF1948 DSCF6667; do
  exp "st-${f#DSCF}" "$SRC/street/$f.jpg" - 400 800
done

# Story prints from the repo originals
exp play       "$P/5. Awards & Extracurriculars/performer/play performance.jpg" 633x791+290+0 320 440 560
exp rowing     "$P/5. Awards & Extracurriculars/rowing national finals/rowing national finals.jpg" 840x420+360+154 360 640
exp steamunity "$P/3. Leadership & Mentorship/Foundational Design Mentor, steamunity/steamunity group with dpm heng.jpeg" - 400 560 720
exp innovi     "$P/1. Professional & Industry Experience/Automation Project Manager  Innovi Advisors Ltd/innovi advisors presentation.jpg" - 400 560 720

# The logbook: earlier work and wins
H="$P/2. Hackathons & Competitions"
exp cam-stage  "$H/grand finalist and tooling winner, hack the law llm x law winner, university of cambridge/cambridge hackathon presenting stage.jpg" - 360 640
exp web3       "$H/finalist web3 hackthon easy a vchain/easya vchain hackathon selfie.jpg" 960x720+0+260 360 640
exp glasses    "$H/Golden Glasses Award for Most Engaging Presentation, future interaction of smart glasses bootcamp/smart glasses group winning.JPG" - 360 640
exp treehouse  "$P/1. Professional & Industry Experience/Builder & Facilitator  Treehouse Innovation/legal tech talk group.jpeg" - 360 640
