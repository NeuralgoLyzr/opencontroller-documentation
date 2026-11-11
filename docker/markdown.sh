#!/bin/sh
# Each page as Markdown beside its export, at the address the page's menu
# asks for: Copy page and View as Markdown fetch <page>.md, which Mintlify
# serves and the export leaves out. The page's title and description open
# it, then its source as written.
set -eu
src=$1 out=$2
find "$src" -name '*.mdx' -not -path "$src/snippets/*" -not -path "$src/node_modules/*" | while read -r f; do
  rel=${f#"$src"/}
  dest="$out/${rel%.mdx}.md"
  mkdir -p "$(dirname "$dest")"
  awk '
    NR == 1 && $0 == "---" { front = 1; next }
    front && $0 == "---" { front = 0; printf "# %s\n\n", title; if (desc != "") printf "%s\n\n", desc; next }
    front && /^title:/ { title = unquote(substr($0, 7)); next }
    front && /^description:/ { desc = unquote(substr($0, 13)); next }
    front { next }
    { print }
    function unquote(s) { sub(/^[ \t]+/, "", s); sub(/[ \t]+$/, "", s); gsub(/^"|"$/, "", s); return s }
  ' "$f" > "$dest"
done
