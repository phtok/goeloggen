#!/usr/bin/env python3
import argparse
import csv
import html
import re
from pathlib import Path


NAME_RE = re.compile(r"^(philipp\s*tok|ph\.?\s*tok|phtok)\b", re.I)
EXACT_BYLINE_RE = re.compile(r"^von\s+(philipp\s*tok|ph\.?\s*tok|phtok)\s*$", re.I)
EXCLUDED = [
    "zeichnung",
    "zeichnungen",
    "zeichnerische",
    "farbstudie",
    "vektorisierte",
    "serie",
    "detail",
    "material",
    "heroine",
    "federzeichnungen",
]


def keep_marker(marker: str) -> bool:
    line = marker.split(":", 1)[1].strip() if ":" in marker else marker.strip()
    low = line.lower()
    if low.startswith("von "):
        return bool(EXACT_BYLINE_RE.match(low))
    if not NAME_RE.match(low):
        return False
    words = len([w for w in re.split(r"\s+", low.strip()) if w])
    if words > 8:
        return False
    if any(tok in low for tok in EXCLUDED):
        return False
    return True


def issue_sort_key(issue: str) -> int:
    m = re.search(r"\d+", issue or "")
    return int(m.group(0)) if m else 9999


def render_html(rows):
    posts = []
    for r in rows:
        text = r.get("text", "")
        paras = [p.strip() for p in text.split("\n\n") if p.strip()]
        paras_html = "\n".join(f"<p>{html.escape(p)}</p>" for p in paras)
        y = (r.get("jahr") or "").strip()
        h = (r.get("heft") or "").strip()
        posts.append(
            f"""<article class="post">
<h2>J{html.escape(y[-2:])}H{html.escape(h)} · {html.escape(r.get("titel",""))}</h2>
<p class="meta">{html.escape(r.get("erscheinung",""))} · Jahrgang {html.escape(y)} · Heft {html.escape(h)} · Seite {html.escape(r.get("seite",""))} · {html.escape(r.get("datei",""))} · Marker: {html.escape(r.get("marker",""))}</p>
{paras_html}
</article>"""
        )
    return f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Philipp Tok – Autorentexte (gefiltert)</title>
  <style>
    body {{ font-family: Georgia, "Times New Roman", serif; margin: 28px auto; max-width: 900px; color: #1f2937; line-height: 1.6; padding: 0 14px 40px; }}
    h1 {{ font-size: 34px; margin: 0 0 6px 0; }}
    p.lead {{ color: #6b7280; margin: 0 0 24px 0; }}
    article.post {{ border-top: 1px solid #e5e7eb; padding-top: 22px; margin-top: 22px; }}
    article.post h2 {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 22px; line-height: 1.25; margin: 0 0 8px 0; color: #111827; }}
    p.meta {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 13px; color: #6b7280; margin: 0 0 14px 0; }}
    article.post p {{ margin: 0 0 12px 0; font-size: 18px; }}
  </style>
</head>
<body>
  <h1>Philipp Tok – Autorentexte (gefiltert)</h1>
  <p class="lead">Treffer nach Marker-Filter · Einträge: {len(rows)}</p>
  {''.join(posts)}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="Filter author-text entries for Philipp Tok")
    ap.add_argument("input_csv")
    ap.add_argument("output_csv")
    ap.add_argument("output_html")
    args = ap.parse_args()

    in_csv = Path(args.input_csv)
    rows = list(csv.DictReader(in_csv.open("r", encoding="utf-8", newline="")))
    out_rows = [r for r in rows if keep_marker(r.get("marker", ""))]
    out_rows.sort(
        key=lambda r: (
            r.get("jahr", ""),
            issue_sort_key(r.get("heft", "")),
            r.get("heft", ""),
            int(r.get("seite", "0") or 0),
        )
    )

    with Path(args.output_csv).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["jahr", "heft", "erscheinung", "seite", "titel", "datei", "marker", "text"])
        w.writeheader()
        w.writerows(out_rows)

    Path(args.output_html).write_text(render_html(out_rows), encoding="utf-8")
    print(f"Input: {len(rows)}")
    print(f"Filtered: {len(out_rows)}")


if __name__ == "__main__":
    main()
