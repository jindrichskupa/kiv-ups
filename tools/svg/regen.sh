#!/usr/bin/env bash
# Přegeneruje SVG obrázky všech cvičení. Usage: tools/svg/regen.sh [root]  (root = kam psát, výchozí kořen repa)
set -euo pipefail
cd "$(dirname "$0")"
R=${1:-../..}
img() { mkdir -p "$R/$1/slides/images"; echo "$R/$1/slides/images"; }
python3 -I gen_svg.py   "$(img ex05)"
python3 -I gen_svg02.py "$(img ex02)"
python3 -I gen_svg04.py "$(img ex04)"
python3 -I gen_svg06.py "$(img ex06)"
python3 -I gen_svg07.py "$(img ex07)"
python3 -I gen_svg08.py "$(img ex08)"
python3 -I gen_svg09.py "$(img ex09)" "$(img ex10)"
python3 -I gen_svg11.py "$(img ex11)"
python3 -I gen_svg12.py "$(img ex12)" "$(img ex13)"
