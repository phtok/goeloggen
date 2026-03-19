#!/usr/bin/env python3
import csv
import html
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


YEAR_RE = re.compile(r"^\d{4}$")


def normalize_dashes(value: str) -> str:
    return value.replace("–", "-").replace("—", "-")


def extract_issue_label(value: str) -> str:
    normalized = normalize_dashes(value).replace("_", "-")
    m = re.search(r"(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)", normalized)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = re.search(r"(?<!\d)(\d{1,2})(?!\d)", normalized)
    if m:
        return m.group(1)
    return normalized


def short_year(year: str) -> str:
    return year[-2:] if len(year) >= 2 else year


def compact_issue(issue: str) -> str:
    return extract_issue_label(issue).replace(" ", "")


def occurrence_suffix(idx: int) -> str:
    if idx <= 0:
        return ""
    letters = "abcdefghijklmnopqrstuvwxyz"
    if idx - 1 < len(letters):
        return letters[idx - 1]
    return f"_{idx}"


def note_kind(note: str) -> str:
    prefix = (note or "").split(";", 1)[0]
    if prefix.startswith("anchor:") or prefix.startswith("fallback:"):
        return "main"
    if prefix.startswith("tok-scan"):
        return "tok"
    if prefix.startswith("page3-right-top"):
        return "rt"
    if prefix.startswith("all-pages-scan"):
        return "all"
    return "other"


def parse_mode_page(row: dict):
    rid = (row.get("id") or "").strip()
    m = re.search(r"-p(\d+)-(main|tok\d+|rt\d+|all\d+)$", rid)
    if m:
        page = int(m.group(1))
        part = m.group(2)
        if part == "main":
            return "main", page
        if part.startswith("tok"):
            return "tok", page
        if part.startswith("rt"):
            return "rt", page
        if part.startswith("all"):
            return "all", page
    page_raw = (row.get("seite") or "").strip()
    page = int(page_raw) if page_raw.isdigit() else None
    return note_kind(row.get("hinweis") or ""), page


def load_rows(root: Path):
    out = []
    for yd in sorted(root.iterdir()):
        if not yd.is_dir() or not YEAR_RE.fullmatch(yd.name):
            continue
        csv_path = yd / "verzeichnis.csv"
        if not csv_path.exists():
            continue
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                row = dict(row)
                row["_year_dir"] = yd.name
                out.append(row)
    return out


def train_rates(train_rows, min_year=2014):
    key_n = Counter()
    key_k = Counter()
    mode_n = Counter()
    mode_k = Counter()
    page_n = Counter()
    page_k = Counter()

    for r in train_rows:
        year_raw = (r.get("jahr") or r.get("_year_dir") or "").strip()
        if not year_raw.isdigit() or int(year_raw) < min_year:
            continue
        mode, page = parse_mode_page(r)
        if mode not in {"all", "tok", "rt"} or page is None:
            continue

        key = (mode, page)
        key_n[key] += 1
        mode_n[mode] += 1
        page_n[page] += 1

        status = (r.get("status") or "keep").strip().lower()
        if status not in {"drop", "delete", "excluded"}:
            key_k[key] += 1
            mode_k[mode] += 1
            page_k[page] += 1

    return {
        "key_n": key_n,
        "key_k": key_k,
        "mode_n": mode_n,
        "mode_k": mode_k,
        "page_n": page_n,
        "page_k": page_k,
    }


def predict_score(stats, mode: str, page: int):
    key_n = stats["key_n"]
    key_k = stats["key_k"]
    mode_n = stats["mode_n"]
    mode_k = stats["mode_k"]
    page_n = stats["page_n"]
    page_k = stats["page_k"]

    global_n = sum(mode_n.values())
    global_k = sum(mode_k.values())
    global_rate = (global_k + 2.0) / (global_n + 4.0) if global_n else 0.2

    mode_rate = (mode_k[mode] + 2.0) / (mode_n[mode] + 4.0) if mode_n[mode] else global_rate
    page_rate = (page_k[page] + 2.0) / (page_n[page] + 4.0) if page_n[page] else global_rate

    n = key_n[(mode, page)]
    k = key_k[(mode, page)]
    if n:
        # Shrink combo rate toward mode/page priors to avoid overfitting.
        return (k + 8.0 * mode_rate + 2.0 * page_rate) / (n + 10.0)
    return 0.8 * mode_rate + 0.2 * page_rate


def tier_for_score(score: float):
    if score >= 0.45:
        return "A"
    if score >= 0.28:
        return "B"
    return "C"


def issue_sort_key(issue: str) -> int:
    m = re.search(r"\d+", issue or "")
    return int(m.group(0)) if m else 9999


def generate(train_root: Path, cand_root: Path):
    train_rows = load_rows(train_root)
    cand_rows = load_rows(cand_root)
    stats = train_rates(train_rows, min_year=2014)

    entries = []
    for r in cand_rows:
        status = (r.get("status") or "keep").strip().lower()
        if status in {"drop", "delete", "excluded"}:
            continue
        mode, page = parse_mode_page(r)
        if mode not in {"all", "tok", "rt"} or page is None:
            continue
        score = predict_score(stats, mode, page)
        tier = tier_for_score(score)
        year = (r.get("jahr") or r.get("_year_dir") or "").strip()
        issue = (r.get("heft") or "").strip()
        entries.append(
            {
                "id": (r.get("id") or "").strip(),
                "year": year,
                "issue": issue,
                "date": (r.get("erscheinung") or "").strip(),
                "page": page,
                "mode": mode,
                "score": score,
                "tier": tier,
                "datei": (r.get("datei") or "").strip(),
                "hinweis": (r.get("hinweis") or "").strip(),
                "svg_rel": f"{year}/{(r.get('svg') or '').strip()}",
            }
        )

    entries.sort(
        key=lambda e: (
            {"A": 0, "B": 1, "C": 2}[e["tier"]],
            -e["score"],
            e["year"],
            issue_sort_key(e["issue"]),
            e["issue"],
            e["id"],
        )
    )
    return entries


def write_csv(out_csv: Path, entries):
    fieldnames = ["tier", "score", "mode", "page", "jahr", "heft", "erscheinung", "id", "svg", "datei", "hinweis"]
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for e in entries:
            w.writerow(
                {
                    "tier": e["tier"],
                    "score": f"{e['score']:.4f}",
                    "mode": e["mode"],
                    "page": e["page"],
                    "jahr": e["year"],
                    "heft": e["issue"],
                    "erscheinung": e["date"],
                    "id": e["id"],
                    "svg": e["svg_rel"],
                    "datei": e["datei"],
                    "hinweis": e["hinweis"],
                }
            )


def write_html(out_html: Path, entries):
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    counts = Counter(e["tier"] for e in entries)

    seen_tiny = defaultdict(int)
    cards = []
    for e in entries:
        key = (e["year"], compact_issue(e["issue"]))
        occ = seen_tiny[key]
        seen_tiny[key] += 1
        tiny = f"J{short_year(e['year'])}H{compact_issue(e['issue'])}{occurrence_suffix(occ)}"
        cards.append(
            f"""<article class="card tier-{e['tier']}" data-tier="{e['tier']}" data-entry-id="{html.escape(e['id'])}">
  <img src="{html.escape(e['svg_rel'])}" alt="{html.escape(tiny)}" loading="lazy">
  <div class="tiny">{html.escape(tiny)}</div>
  <div class="meta">{e['tier']} · {e['mode']} · S{e['page']} · Score {e['score']:.2f}</div>
  <button class="mark-btn" type="button">Behalten</button>
</article>"""
        )

    html_doc = f"""<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Ergänzungen Vorsortiert</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 20px; color: #1f2937; }}
    h1 {{ margin: 0 0 8px 0; font-size: 24px; }}
    p.meta-top {{ margin: 0 0 14px 0; color: #6b7280; }}
    .toolbar {{ position: sticky; top: 0; z-index: 5; background: rgba(255,255,255,0.96); border: 1px solid #e5e7eb; padding: 8px 10px; margin: 0 0 16px 0; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .tool-btn {{ font-size: 12px; border: 1px solid #d1d5db; background: #fff; color: #374151; border-radius: 3px; padding: 3px 8px; cursor: pointer; }}
    .tool-btn:hover {{ background: #f3f4f6; }}
    .tool-info {{ font-size: 12px; color: #6b7280; margin-left: auto; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(138px, 1fr)); gap: 10px; }}
    .card {{ border: 1px solid #e5e7eb; background: #fff; padding: 6px; }}
    .card.is-kept {{ border-color: #10b981; background: #f0fdf4; }}
    .card img {{ width: 100%; height: 92px; object-fit: contain; display: block; background: #fff; }}
    .tiny {{ margin-top: 5px; font-size: 10px; color: #6b7280; letter-spacing: 0.02em; }}
    .meta {{ margin-top: 3px; font-size: 10px; color: #4b5563; }}
    .mark-btn {{ width: 100%; margin-top: 6px; font-size: 11px; border: 1px solid #d1d5db; border-radius: 3px; background: #fff; padding: 3px 4px; cursor: pointer; }}
    .card.is-kept .mark-btn {{ border-color: #10b981; color: #065f46; background: #ecfdf5; }}
    .tier-A {{ box-shadow: inset 0 0 0 1px #c7f9e3; }}
    .tier-B {{ box-shadow: inset 0 0 0 1px #dbeafe; }}
    .tier-C {{ box-shadow: inset 0 0 0 1px #f3f4f6; }}
  </style>
</head>
<body>
  <h1>Ergänzungen Vorsortiert (ab 2018)</h1>
  <p class="meta-top">Erzeugt am {generated} · Kandidaten: {len(entries)} · A: {counts['A']} · B: {counts['B']} · C: {counts['C']} · Standard: A+B</p>
  <div class="toolbar">
    <button id="show-ab" class="tool-btn" type="button">A+B zeigen</button>
    <button id="show-a" class="tool-btn" type="button">Nur A</button>
    <button id="show-all" class="tool-btn" type="button">Alle (A+B+C)</button>
    <button id="copy-ids" class="tool-btn" type="button">Keep-IDs kopieren</button>
    <button id="download-ids" class="tool-btn" type="button">Keep-IDs herunterladen</button>
    <button id="reset-ids" class="tool-btn" type="button">Auswahl zurücksetzen</button>
    <span id="tool-info" class="tool-info">0 behalten</span>
  </div>
  <section class="grid">
    {"".join(cards)}
  </section>
  <script>
    (() => {{
      const storageKey = `tok_keep_ids_vorsort_v1:${{location.pathname}}`;
      const cards = Array.from(document.querySelectorAll(".card[data-entry-id]"));
      const infoEl = document.getElementById("tool-info");
      const btnShowAB = document.getElementById("show-ab");
      const btnShowA = document.getElementById("show-a");
      const btnShowAll = document.getElementById("show-all");
      const copyBtn = document.getElementById("copy-ids");
      const downloadBtn = document.getElementById("download-ids");
      const resetBtn = document.getElementById("reset-ids");
      let tierMode = "AB";

      function loadKept() {{
        try {{
          const raw = localStorage.getItem(storageKey);
          if (!raw) return new Set();
          const arr = JSON.parse(raw);
          if (!Array.isArray(arr)) return new Set();
          return new Set(arr);
        }} catch {{
          return new Set();
        }}
      }}

      let kept = loadKept();

      function saveKept() {{
        localStorage.setItem(storageKey, JSON.stringify(Array.from(kept).sort()));
      }}

      function idsText() {{
        return Array.from(kept).sort().join("\\n");
      }}

      function tierVisible(tier) {{
        if (tierMode === "ALL") return true;
        if (tierMode === "A") return tier === "A";
        return tier === "A" || tier === "B";
      }}

      function applyState() {{
        for (const card of cards) {{
          const id = card.getAttribute("data-entry-id");
          const tier = card.getAttribute("data-tier");
          const btn = card.querySelector(".mark-btn");
          const isKept = id && kept.has(id);
          card.classList.toggle("is-kept", !!isKept);
          if (btn) btn.textContent = isKept ? "Behalten ✓" : "Behalten";
          card.style.display = tierVisible(tier) ? "" : "none";
        }}
        const visible = cards.filter(c => c.style.display !== "none").length;
        infoEl.textContent = `${{kept.size}} behalten · ${{visible}}/${{cards.length}} sichtbar · Filter ${{tierMode}}`;
      }}

      for (const card of cards) {{
        const id = card.getAttribute("data-entry-id");
        const btn = card.querySelector(".mark-btn");
        if (!id || !btn) continue;
        btn.addEventListener("click", () => {{
          if (kept.has(id)) kept.delete(id); else kept.add(id);
          saveKept();
          applyState();
        }});
      }}

      btnShowAB.addEventListener("click", () => {{ tierMode = "AB"; applyState(); }});
      btnShowA.addEventListener("click", () => {{ tierMode = "A"; applyState(); }});
      btnShowAll.addEventListener("click", () => {{ tierMode = "ALL"; applyState(); }});

      copyBtn.addEventListener("click", async () => {{
        const text = idsText();
        if (!text) return;
        try {{
          await navigator.clipboard.writeText(text);
          copyBtn.textContent = "Kopiert";
          setTimeout(() => copyBtn.textContent = "Keep-IDs kopieren", 1200);
        }} catch {{
          alert("Kopieren fehlgeschlagen. Nutze stattdessen 'Keep-IDs herunterladen'.");
        }}
      }});

      downloadBtn.addEventListener("click", () => {{
        const text = idsText();
        const blob = new Blob([text ? text + "\\n" : ""], {{ type: "text/plain;charset=utf-8" }});
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "keep_ids_vorsortiert.txt";
        a.click();
        URL.revokeObjectURL(a.href);
      }});

      resetBtn.addEventListener("click", () => {{
        if (!confirm("Alle Behalten-Markierungen zurücksetzen?")) return;
        kept.clear();
        saveKept();
        applyState();
      }});

      applyState();
    }})();
  </script>
</body>
</html>
"""
    out_html.write_text(html_doc, encoding="utf-8")


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_vorsortierung.py <train_root> <candidates_root> [output_html] [output_csv]")
        sys.exit(1)
    train_root = Path(sys.argv[1])
    cand_root = Path(sys.argv[2])
    out_html = Path(sys.argv[3]) if len(sys.argv) >= 4 else cand_root / "total_vorsortiert.html"
    out_csv = Path(sys.argv[4]) if len(sys.argv) >= 5 else cand_root / "vorsortierung.csv"

    entries = generate(train_root=train_root, cand_root=cand_root)
    write_csv(out_csv, entries)
    write_html(out_html, entries)

    c = Counter(e["tier"] for e in entries)
    print(f"Entries: {len(entries)}")
    print(f"A: {c['A']}  B: {c['B']}  C: {c['C']}")
    print(f"HTML: {out_html}")
    print(f"CSV: {out_csv}")


if __name__ == "__main__":
    main()
