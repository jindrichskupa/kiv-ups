#!/usr/bin/env bash
# Build GitHub Pages site: one Marp deck per exercise + index.html generated from README.md.
# Usage: .github/build-site.sh [out_dir]   (needs `marp` on PATH)
set -euo pipefail

OUT=${1:-_site}
REPO=https://github.com/jindrichskupa/kiv-ups/blob/master
mkdir -p "$OUT"

for md in ex*/slides/ex[0-9][0-9].md; do
    ex=${md%%/*}
    mkdir -p "$OUT/$ex"
    # Slidy s <!-- bonus --> jdou jen do plné verze (plna.html); index.html = co se stihne na cvičení.
    if grep -q '<!-- bonus -->' "$md"; then
        marp --no-stdin --html "$md" -o "$OUT/$ex/plna.html"
        python3 -c 'import sys; s = open(sys.argv[1], encoding="utf-8").read(); sys.stdout.write("\n---\n".join(x for x in s.split("\n---\n") if "<!-- bonus -->" not in x))' "$md" > "$OUT/$ex/cviceni.md"
        marp --no-stdin --html "$OUT/$ex/cviceni.md" -o "$OUT/$ex/index.html"
        rm "$OUT/$ex/cviceni.md"
    else
        marp --no-stdin --html "$md" -o "$OUT/$ex/index.html"
    fi
    [ -d "$ex/slides/images" ] && cp -r "$ex/slides/images" "$OUT/$ex/"
done

# Rozcestnik: polozky "N. [nazev](.../exNN/...)" z README; jen cviceni, ktera maji sestavene slidy.
items=""
while IFS= read -r line; do
    title=$(sed -E 's/^[0-9]+\. \[([^]]*)\].*/\1/' <<<"$line")
    ex=$(grep -oE 'ex[0-9]{2}' <<<"$line" | head -1)
    [ -f "$OUT/$ex/index.html" ] || continue
    n=$((10#${ex#ex}))
    extra=""
    [ -f "$OUT/$ex/plna.html" ] && extra+=" <a class=\"sub\" href=\"$ex/plna.html\">plná verze</a>"
    [ -f "$ex/slides/$ex-reseni.md" ] && extra+=" <a class=\"sub\" href=\"$REPO/$ex/slides/$ex-reseni.md\">řešení příkladů</a>"
    items+="<li><a href=\"$ex/\"><span class=\"n\">$n.</span> $title</a>$extra</li>"$'\n'
done < <(grep -E '^[0-9]+\. \[' README.md)

cat > "$OUT/index.html" <<EOF
<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>KIV/UPS cvičení</title>
<style>
  :root { --bg: #fff; --fg: #1f2328; --muted: #656d76; --link: #0969da; --line: #d0d7de; }
  @media (prefers-color-scheme: dark) { :root { --bg: #0d1117; --fg: #e6edf3; --muted: #8d96a0; --link: #4493f8; --line: #30363d; } }
  body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, sans-serif; }
  main { max-width: 760px; margin: 0 auto; padding: 32px 16px; }
  h1 { margin: 0 0 4px; }
  p { color: var(--muted); margin: 0 0 24px; }
  ul { list-style: none; padding: 0; margin: 0; }
  li { padding: 12px 0; border-bottom: 1px solid var(--line); }
  a { color: var(--link); text-decoration: none; }
  a:hover { text-decoration: underline; }
  .n { display: inline-block; min-width: 2em; color: var(--muted); }
  .sub { margin-left: 12px; font-size: 14px; }
</style>
</head>
<body>
<main>
<h1>KIV/UPS</h1>
<p>Slidy ke cvičením (verze na cvičení; plná verze obsahuje i bonusové příklady). Ovládání: šipky, F = celá obrazovka. Zdroj: <a href="https://github.com/jindrichskupa/kiv-ups">github.com/jindrichskupa/kiv-ups</a></p>
<ul>
$items</ul>
</main>
</body>
</html>
EOF
echo "built $OUT"
