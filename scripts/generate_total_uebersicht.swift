import Foundation

struct Entry {
    let year: String
    let issue: String
    let publicationDate: String
    let svgRelativePath: String
    let id: String
}

func usage() {
    let cmd = (CommandLine.arguments.first as NSString?)?.lastPathComponent ?? "generate_total_uebersicht.swift"
    print("Usage: \(cmd) <output_root>")
}

func parseCSVLine(_ line: String) -> [String] {
    var fields: [String] = []
    var current = ""
    var inQuotes = false
    let chars = Array(line)
    var i = 0

    while i < chars.count {
        let ch = chars[i]
        if ch == "\"" {
            if inQuotes && i + 1 < chars.count && chars[i + 1] == "\"" {
                current.append("\"")
                i += 1
            } else {
                inQuotes.toggle()
            }
        } else if ch == "," && !inQuotes {
            fields.append(current)
            current = ""
        } else {
            current.append(ch)
        }
        i += 1
    }
    fields.append(current)
    return fields
}

func shortYear(_ year: String) -> String {
    if year.count >= 2 { return String(year.suffix(2)) }
    return year
}

func normalizeDashes(_ value: String) -> String {
    return value
        .replacingOccurrences(of: "–", with: "-")
        .replacingOccurrences(of: "—", with: "-")
}

func extractIssueLabel(from value: String) -> String {
    let normalized = normalizeDashes(value).replacingOccurrences(of: "_", with: "-")
    let ns = normalized as NSString

    let rangeRe = try! NSRegularExpression(pattern: #"(?<!\d)(\d{1,2})-(\d{1,2})(?!\d)"#, options: [])
    if let m = rangeRe.firstMatch(in: normalized, options: [], range: NSRange(location: 0, length: ns.length)) {
        let a = ns.substring(with: m.range(at: 1))
        let b = ns.substring(with: m.range(at: 2))
        return "\(a)-\(b)"
    }

    let singleRe = try! NSRegularExpression(pattern: #"(?<!\d)(\d{1,2})(?!\d)"#, options: [])
    if let m = singleRe.firstMatch(in: normalized, options: [], range: NSRange(location: 0, length: ns.length)) {
        return ns.substring(with: m.range(at: 1))
    }

    return normalized
}

func compactIssue(_ issue: String) -> String {
    extractIssueLabel(from: issue).replacingOccurrences(of: " ", with: "")
}

func occurrenceSuffix(_ occurrence: Int) -> String {
    if occurrence <= 0 { return "" }
    let letters = "abcdefghijklmnopqrstuvwxyz"
    if occurrence - 1 < letters.count {
        let idx = letters.index(letters.startIndex, offsetBy: occurrence - 1)
        return String(letters[idx])
    }
    return "_\(occurrence)"
}

func sanitizeID(_ value: String) -> String {
    let trimmed = value.trimmingCharacters(in: .whitespacesAndNewlines)
    let cleaned = trimmed.replacingOccurrences(of: #"[^A-Za-z0-9._:-]+"#, with: "_", options: .regularExpression)
    let noEdgeUnderscores = cleaned.trimmingCharacters(in: CharacterSet(charactersIn: "_"))
    return noEdgeUnderscores.isEmpty ? "entry" : noEdgeUnderscores
}

func isPlaceholderID(_ value: String) -> Bool {
    return value.range(of: #"^row-\d+$"#, options: .regularExpression) != nil
}

func fallbackEntryID(year: String, issue: String, svgPath: String) -> String {
    let svgStem = URL(fileURLWithPath: svgPath).deletingPathExtension().lastPathComponent
    let base = "\(year)-\(issue)-\(svgStem)"
    return sanitizeID(base)
}

func htmlAttrEscape(_ value: String) -> String {
    return value
        .replacingOccurrences(of: "&", with: "&amp;")
        .replacingOccurrences(of: "\"", with: "&quot;")
        .replacingOccurrences(of: "<", with: "&lt;")
        .replacingOccurrences(of: ">", with: "&gt;")
}

func issueSortKey(_ issue: String) -> Int {
    let re = try! NSRegularExpression(pattern: #"\d+"#, options: [])
    let ns = issue as NSString
    if let m = re.firstMatch(in: issue, options: [], range: NSRange(location: 0, length: ns.length)) {
        return Int(ns.substring(with: m.range)) ?? 9999
    }
    return 9999
}

let args = CommandLine.arguments
guard args.count >= 2 else {
    usage()
    exit(1)
}

let root = URL(fileURLWithPath: args[1], isDirectory: true)
let fm = FileManager.default

let yearDirs = (try? fm.contentsOfDirectory(at: root, includingPropertiesForKeys: nil))?
    .filter { $0.hasDirectoryPath }
    .filter { $0.lastPathComponent.range(of: #"^\d{4}$"#, options: .regularExpression) != nil }
    .sorted { $0.lastPathComponent < $1.lastPathComponent } ?? []

var all: [Entry] = []

for dir in yearDirs {
    let csvURL = dir.appendingPathComponent("verzeichnis.csv")
    guard fm.fileExists(atPath: csvURL.path) else { continue }

    guard let data = try? String(contentsOf: csvURL, encoding: .utf8) else { continue }
    let lines = data.split(whereSeparator: \ .isNewline).map(String.init)
    guard lines.count > 1 else { continue }

    for line in lines.dropFirst() {
        let fields = parseCSVLine(line)
        if fields.count < 8 { continue }
        if fields.count >= 10 {
            let status = fields[9].trimmingCharacters(in: .whitespacesAndNewlines).lowercased()
            if status == "drop" || status == "delete" || status == "excluded" {
                continue
            }
        }

        let year = fields[0]
        let issue = fields[1]
        let publicationDate = fields[2]
        let svgPath = fields[6]
        let rawId = fields.count >= 9 ? fields[8].trimmingCharacters(in: .whitespacesAndNewlines) : ""
        let entryId = (!rawId.isEmpty && !isPlaceholderID(rawId)) ? sanitizeID(rawId) : fallbackEntryID(year: year, issue: issue, svgPath: svgPath)
        all.append(Entry(year: year, issue: issue, publicationDate: publicationDate, svgRelativePath: "\(year)/\(svgPath)", id: entryId))
    }
}

all.sort {
    if $0.year != $1.year { return $0.year < $1.year }
    let k0 = issueSortKey($0.issue)
    let k1 = issueSortKey($1.issue)
    if k0 != k1 { return k0 < k1 }
    return $0.issue < $1.issue
}

var idCounts: [String: Int] = [:]
var uniqueAll: [Entry] = []
uniqueAll.reserveCapacity(all.count)
for e in all {
    let base = sanitizeID(e.id)
    let seen = idCounts[base, default: 0]
    idCounts[base] = seen + 1
    let finalID = seen == 0 ? base : "\(base)-\(seen + 1)"
    uniqueAll.append(Entry(year: e.year, issue: e.issue, publicationDate: e.publicationDate, svgRelativePath: e.svgRelativePath, id: finalID))
}
all = uniqueAll

let grouped = Dictionary(grouping: all, by: { $0.year })
let years = grouped.keys.sorted()

let dateFormatter = DateFormatter()
dateFormatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
let generatedAt = dateFormatter.string(from: Date())

var nav = ""
for y in years {
    nav += "<a href=\"#y\(y)\">\(y)</a>"
}

var sections = ""
for y in years {
    let entries = (grouped[y] ?? []).sorted {
        let k0 = issueSortKey($0.issue)
        let k1 = issueSortKey($1.issue)
        if k0 != k1 { return k0 < k1 }
        return $0.issue < $1.issue
    }
    var issueOrder: [String] = []
    var seenIssues = Set<String>()
    for e in entries {
        let label = compactIssue(e.issue)
        if !seenIssues.contains(label) {
            seenIssues.insert(label)
            issueOrder.append(label)
        }
    }

    var rows = ""
    for issueLabel in issueOrder {
        let rowEntries = entries.filter { compactIssue($0.issue) == issueLabel }
        var cards = ""

        for (occ, e) in rowEntries.enumerated() {
            let tiny = "J\(shortYear(e.year))H\(issueLabel)\(occurrenceSuffix(occ))"
            let fileName = "\(tiny).svg"
            cards += """
            <article class="card" data-entry-id="\(htmlAttrEscape(e.id))" data-year="\(htmlAttrEscape(e.year))" data-issue="\(htmlAttrEscape(issueLabel))" data-svg="\(htmlAttrEscape(e.svgRelativePath))" data-file="\(htmlAttrEscape(fileName))">
              <img src="\(htmlAttrEscape(e.svgRelativePath))" alt="\(htmlAttrEscape(tiny))" loading="lazy">
              <div class="tiny">\(htmlAttrEscape(tiny))</div>
              <div class="card-actions">
                <label class="choice"><input class="entry-select" type="checkbox"> Auswahl</label>
                <a class="tool-btn small inline-dl" href="\(htmlAttrEscape(e.svgRelativePath))" download="\(htmlAttrEscape(fileName))">Download</a>
              </div>
            </article>
            """
        }

        rows += """
        <section class="issue-row" data-year="\(htmlAttrEscape(y))" data-issue="\(htmlAttrEscape(issueLabel))">
          <header class="issue-head">
            <div class="issue-title">H\(htmlAttrEscape(issueLabel)) <span>(\(rowEntries.count))</span></div>
            <div class="issue-tools">
              <label class="choice"><input class="row-select" type="checkbox"> Zeile</label>
              <button class="tool-btn small row-download" type="button">Download Zeile</button>
            </div>
          </header>
          <div class="grid">
            \(cards)
          </div>
        </section>
        """
    }

    sections += """
    <section class="year" id="y\(y)" data-year="\(htmlAttrEscape(y))">
      <div class="year-head">
        <h2>\(y) <span>(\(entries.count))</span></h2>
        <div class="year-tools">
          <label class="choice"><input class="year-select" type="checkbox"> Jahr</label>
          <button class="tool-btn small year-download" type="button">Download Jahr</button>
        </div>
      </div>
      <div class="rows">
        \(rows)
      </div>
    </section>
    """
}

let html = """
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Totalübersicht Zeichnungen</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 20px; color: #1f2937; }
    h1 { margin: 0 0 8px 0; font-size: 24px; }
    p.meta { margin: 0 0 14px 0; color: #6b7280; }
    .toolbar { position: sticky; top: 0; z-index: 5; background: rgba(255,255,255,0.95); backdrop-filter: blur(3px); border: 1px solid #e5e7eb; padding: 8px 10px; margin: 0 0 16px 0; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .toolbar a { font-size: 12px; text-decoration: none; color: #374151; border: 1px solid #d1d5db; padding: 2px 6px; border-radius: 3px; }
    .tool-btn { font-size: 12px; border: 1px solid #d1d5db; background: #fff; color: #374151; border-radius: 3px; padding: 3px 8px; cursor: pointer; text-decoration: none; line-height: 1.2; }
    .tool-btn:hover { background: #f3f4f6; }
    .tool-btn.small { padding: 2px 6px; font-size: 11px; }
    .choice { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; color: #374151; white-space: nowrap; }
    .choice input { margin: 0; }
    .tool-info { font-size: 12px; color: #6b7280; margin-left: auto; }
    .year { margin: 0 0 28px 0; }
    .year-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin: 0 0 10px 0; }
    .year-tools { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    h2 { margin: 0; font-size: 18px; }
    h2 span { color: #6b7280; font-size: 13px; font-weight: 400; }
    .rows { display: grid; gap: 16px; }
    .issue-row { border: 1px solid #e5e7eb; background: #f9fafb; border-radius: 4px; padding: 10px; }
    .issue-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin: 0 0 8px 0; }
    .issue-title { font-size: 13px; font-weight: 600; color: #111827; }
    .issue-title span { color: #6b7280; font-weight: 400; }
    .issue-tools { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap: 10px; }
    .card { border: 1px solid #e5e7eb; background: #fff; padding: 8px; border-radius: 4px; }
    .card.is-selected { border-color: #0284c7; background: #f0f9ff; }
    .card img { width: 100%; height: 92px; object-fit: contain; display: block; background: #fff; }
    .tiny { margin-top: 5px; font-size: 10px; color: #6b7280; letter-spacing: 0.02em; }
    .card-actions { margin-top: 7px; display: flex; align-items: center; justify-content: space-between; gap: 6px; }
    .card .choice { font-size: 11px; }
    .inline-dl { margin-left: auto; }
    @media (max-width: 720px) {
      body { margin: 12px; }
      .toolbar { top: 4px; }
      .year-head, .issue-head { align-items: flex-start; }
      .grid { grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); }
    }
  </style>
</head>
<body>
  <h1>Totalübersicht Zeichnungen</h1>
  <p class="meta">Erzeugt am \(generatedAt) · Jahrgänge: \(years.count) · Zeichnungen: \(all.count)</p>
  <div class="toolbar">
    \(nav)
    <a class="tool-btn" href="./galerie_tok.html">Zur Galerie</a>
    <button id="toggle-selected-view" class="tool-btn" type="button">Nur Auswahl zeigen</button>
    <button id="select-all" class="tool-btn" type="button">Alle wählen</button>
    <button id="clear-selection" class="tool-btn" type="button">Auswahl löschen</button>
    <button id="copy-selected-ids" class="tool-btn" type="button">Auswahl-IDs kopieren</button>
    <button id="download-selected-ids" class="tool-btn" type="button">Auswahl-IDs herunterladen</button>
    <button id="download-selected-svgs" class="tool-btn" type="button">Auswahl als TAR herunterladen</button>
    <span id="tool-info" class="tool-info">0 ausgewählt</span>
  </div>
  \(sections)
  <script>
    (() => {
      const storageKey = `tok_selected_ids_v1:${location.pathname}`;
      const legacyKey = `tok_keep_ids_v2:${location.pathname}`;
      const cards = Array.from(document.querySelectorAll(".card[data-entry-id]"));
      const rowSections = Array.from(document.querySelectorAll(".issue-row[data-year][data-issue]"));
      const yearSections = Array.from(document.querySelectorAll(".year[data-year]"));
      const infoEl = document.getElementById("tool-info");
      const toggleBtn = document.getElementById("toggle-selected-view");
      const selectAllBtn = document.getElementById("select-all");
      const clearBtn = document.getElementById("clear-selection");
      const copyIdsBtn = document.getElementById("copy-selected-ids");
      const downloadIdsBtn = document.getElementById("download-selected-ids");
      const downloadSvgBtn = document.getElementById("download-selected-svgs");
      const cardIDs = new Set(cards.map(card => card.getAttribute("data-entry-id")).filter(Boolean));
      let showOnlySelected = false;

      function parseStoredSet(raw) {
        if (!raw) return new Set();
        try {
          const arr = JSON.parse(raw);
          if (!Array.isArray(arr)) return new Set();
          return new Set(arr);
        } catch {
          return new Set();
        }
      }

      function loadSelected() {
        const current = parseStoredSet(localStorage.getItem(storageKey));
        if (current.size > 0) return current;
        return parseStoredSet(localStorage.getItem(legacyKey));
      }

      let selected = new Set(Array.from(loadSelected()).filter(id => cardIDs.has(id)));

      function saveSelected() {
        localStorage.setItem(storageKey, JSON.stringify(Array.from(selected).sort()));
      }

      function idsText() {
        return Array.from(selected).sort().join("\\n");
      }

      function cardsInScope(scope) {
        return Array.from(scope.querySelectorAll(".card[data-entry-id]"));
      }

      function setScopeSelection(scope, shouldSelect) {
        for (const card of cardsInScope(scope)) {
          const id = card.getAttribute("data-entry-id");
          if (!id) continue;
          if (shouldSelect) selected.add(id); else selected.delete(id);
        }
      }

      function selectionCount(scope) {
        let count = 0;
        for (const card of cardsInScope(scope)) {
          const id = card.getAttribute("data-entry-id");
          if (id && selected.has(id)) count += 1;
        }
        return count;
      }

      function applyScopeCheckbox(scope, selector) {
        const checkbox = scope.querySelector(selector);
        if (!checkbox) return;
        const cardsInThis = cardsInScope(scope);
        if (!cardsInThis.length) {
          checkbox.checked = false;
          checkbox.indeterminate = false;
          return;
        }
        const selCount = selectionCount(scope);
        checkbox.checked = selCount > 0 && selCount === cardsInThis.length;
        checkbox.indeterminate = selCount > 0 && selCount < cardsInThis.length;
      }

      function sanitizeFileName(value) {
        const cleaned = String(value || "").replace(/[^A-Za-z0-9._-]+/g, "_").replace(/^_+|_+$/g, "");
        return cleaned || "zeichnung";
      }

      function downloadBlob(blob, filename) {
        if (!blob) return;
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        if (filename) a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(() => URL.revokeObjectURL(a.href), 500);
      }

      async function fetchBytes(url) {
        try {
          const res = await fetch(url, { cache: "no-store" });
          if (!res.ok) throw new Error(`HTTP ${res.status}`);
          return new Uint8Array(await res.arrayBuffer());
        } catch {
          return await new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            xhr.open("GET", url, true);
            xhr.responseType = "arraybuffer";
            xhr.onload = () => {
              if ((xhr.status >= 200 && xhr.status < 300) || xhr.status === 0) {
                resolve(new Uint8Array(xhr.response || new ArrayBuffer(0)));
              } else {
                reject(new Error(`XHR ${xhr.status}`));
              }
            };
            xhr.onerror = () => reject(new Error("XHR failed"));
            xhr.send();
          });
        }
      }

      function writeString(buf, offset, length, value) {
        const bytes = new TextEncoder().encode(value || "");
        buf.set(bytes.slice(0, length), offset);
      }

      function writeOctal(buf, offset, length, value) {
        const maxLen = Math.max(1, length - 1);
        let oct = Math.max(0, Number(value) || 0).toString(8);
        if (oct.length > maxLen) oct = oct.slice(-maxLen);
        oct = oct.padStart(maxLen, "0");
        writeString(buf, offset, maxLen, oct);
        buf[offset + length - 1] = 0;
      }

      function buildTar(files) {
        const chunks = [];
        const now = Math.floor(Date.now() / 1000);

        for (const file of files) {
          const name = sanitizeFileName(file.name || "zeichnung.svg");
          const data = file.data instanceof Uint8Array ? file.data : new Uint8Array(0);
          const header = new Uint8Array(512);

          writeString(header, 0, 100, name);
          writeOctal(header, 100, 8, 0o644);
          writeOctal(header, 108, 8, 0);
          writeOctal(header, 116, 8, 0);
          writeOctal(header, 124, 12, data.length);
          writeOctal(header, 136, 12, now);
          for (let i = 148; i < 156; i += 1) header[i] = 0x20;
          header[156] = "0".charCodeAt(0);
          writeString(header, 257, 6, "ustar");
          writeString(header, 263, 2, "00");
          writeString(header, 265, 32, "codex");
          writeString(header, 297, 32, "staff");

          let checksum = 0;
          for (let i = 0; i < 512; i += 1) checksum += header[i];
          const chk = checksum.toString(8).padStart(6, "0");
          writeString(header, 148, 6, chk);
          header[154] = 0;
          header[155] = 0x20;

          chunks.push(header);
          chunks.push(data);

          const pad = (512 - (data.length % 512)) % 512;
          if (pad) chunks.push(new Uint8Array(pad));
        }

        chunks.push(new Uint8Array(1024));
        return new Blob(chunks, { type: "application/x-tar" });
      }

      async function downloadSingleByURL(url, filename) {
        try {
          const data = await fetchBytes(url);
          downloadBlob(new Blob([data], { type: "image/svg+xml;charset=utf-8" }), filename);
        } catch {
          const a = document.createElement("a");
          a.href = url;
          a.download = filename || "";
          a.target = "_blank";
          document.body.appendChild(a);
          a.click();
          a.remove();
        }
      }

      async function downloadCardsAsTar(cardsToDownload, prefix) {
        const items = cardsToDownload
          .map((card, idx) => {
            const href = card.getAttribute("data-svg") || "";
            const fallback = `${prefix}_${idx + 1}.svg`;
            const name = sanitizeFileName(card.getAttribute("data-file") || fallback);
            return { href, name };
          })
          .filter(item => !!item.href);

        if (!items.length) return;
        const files = [];
        for (const item of items) {
          const data = await fetchBytes(item.href);
          files.push({ name: item.name, data });
        }
        const tarName = `${sanitizeFileName(prefix || "auswahl")}.tar`;
        downloadBlob(buildTar(files), tarName);
      }

      function applyState() {
        for (const card of cards) {
          const id = card.getAttribute("data-entry-id");
          const checkbox = card.querySelector(".entry-select");
          const isSelected = id && selected.has(id);
          card.classList.toggle("is-selected", !!isSelected);
          if (checkbox) checkbox.checked = !!isSelected;
          card.style.display = (showOnlySelected && !isSelected) ? "none" : "";
        }

        for (const row of rowSections) {
          applyScopeCheckbox(row, ".row-select");
          const visibleInRow = cardsInScope(row).filter(card => card.style.display !== "none").length;
          row.style.display = (showOnlySelected && visibleInRow === 0) ? "none" : "";
        }

        for (const year of yearSections) {
          applyScopeCheckbox(year, ".year-select");
          const visibleInYear = cardsInScope(year).filter(card => card.style.display !== "none").length;
          year.style.display = (showOnlySelected && visibleInYear === 0) ? "none" : "";
        }

        const visible = cards.filter(c => c.style.display !== "none").length;
        infoEl.textContent = `${selected.size} ausgewählt · ${visible}/${cards.length} sichtbar`;
        toggleBtn.textContent = showOnlySelected ? "Alle zeigen" : "Nur Auswahl zeigen";
      }

      for (const card of cards) {
        const id = card.getAttribute("data-entry-id");
        const checkbox = card.querySelector(".entry-select");
        if (!id || !checkbox) continue;
        checkbox.addEventListener("change", () => {
          if (checkbox.checked) selected.add(id); else selected.delete(id);
          saveSelected();
          applyState();
        });
      }

      for (const row of rowSections) {
        const checkbox = row.querySelector(".row-select");
        const btn = row.querySelector(".row-download");
        if (checkbox) {
          checkbox.addEventListener("change", () => {
            setScopeSelection(row, checkbox.checked);
            saveSelected();
            applyState();
          });
        }
        if (btn) {
          btn.addEventListener("click", async () => {
            const year = row.getAttribute("data-year") || "jahr";
            const issue = row.getAttribute("data-issue") || "heft";
            btn.disabled = true;
            const original = btn.textContent;
            btn.textContent = "Erzeuge TAR...";
            try {
              await downloadCardsAsTar(cardsInScope(row), `${year}_H${issue}`);
            } finally {
              btn.textContent = original;
              btn.disabled = false;
            }
          });
        }
      }

      for (const year of yearSections) {
        const checkbox = year.querySelector(".year-select");
        const btn = year.querySelector(".year-download");
        if (checkbox) {
          checkbox.addEventListener("change", () => {
            setScopeSelection(year, checkbox.checked);
            saveSelected();
            applyState();
          });
        }
        if (btn) {
          btn.addEventListener("click", async () => {
            const yearLabel = year.getAttribute("data-year") || "jahr";
            btn.disabled = true;
            const original = btn.textContent;
            btn.textContent = "Erzeuge TAR...";
            try {
              await downloadCardsAsTar(cardsInScope(year), `${yearLabel}`);
            } finally {
              btn.textContent = original;
              btn.disabled = false;
            }
          });
        }
      }

      for (const link of document.querySelectorAll(".inline-dl")) {
        link.addEventListener("click", async (ev) => {
          ev.preventDefault();
          const card = link.closest(".card");
          const href = (card && card.getAttribute("data-svg")) || link.getAttribute("href") || "";
          const name = (card && card.getAttribute("data-file")) || link.getAttribute("download") || "zeichnung.svg";
          await downloadSingleByURL(href, sanitizeFileName(name));
        });
      }

      toggleBtn.addEventListener("click", () => {
        showOnlySelected = !showOnlySelected;
        applyState();
      });

      selectAllBtn.addEventListener("click", () => {
        for (const id of cardIDs) selected.add(id);
        saveSelected();
        applyState();
      });

      clearBtn.addEventListener("click", () => {
        if (!confirm("Aktuelle Auswahl löschen?")) return;
        selected.clear();
        saveSelected();
        applyState();
      });

      copyIdsBtn.addEventListener("click", async () => {
        const text = idsText();
        if (!text) return;
        try {
          await navigator.clipboard.writeText(text);
          copyIdsBtn.textContent = "Kopiert";
          setTimeout(() => copyIdsBtn.textContent = "Auswahl-IDs kopieren", 1200);
        } catch {
          alert("Kopieren fehlgeschlagen. Nutze stattdessen 'Auswahl-IDs herunterladen'.");
        }
      });

      downloadIdsBtn.addEventListener("click", () => {
        const text = idsText();
        const blob = new Blob([text ? text + "\\n" : ""], { type: "text/plain;charset=utf-8" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "selected_ids.txt";
        a.click();
        URL.revokeObjectURL(a.href);
      });

      downloadSvgBtn.addEventListener("click", async () => {
        const selectedCards = cards.filter(card => {
          const id = card.getAttribute("data-entry-id");
          return !!id && selected.has(id);
        });
        downloadSvgBtn.disabled = true;
        const original = downloadSvgBtn.textContent;
        downloadSvgBtn.textContent = "Erzeuge TAR...";
        try {
          await downloadCardsAsTar(selectedCards, "auswahl");
        } finally {
          downloadSvgBtn.textContent = original;
          downloadSvgBtn.disabled = false;
        }
      });

      saveSelected();
      applyState();
    })();
  </script>
</body>
</html>
"""

try html.write(to: root.appendingPathComponent("total_uebersicht.html"), atomically: true, encoding: .utf8)

var csv = "jahr,heft,erscheinung,svg,id\n"
for e in all {
    csv += "\(e.year),\(e.issue),\(e.publicationDate),\(e.svgRelativePath),\(e.id)\n"
}
try csv.write(to: root.appendingPathComponent("total_verzeichnis.csv"), atomically: true, encoding: .utf8)

print("Years: \(years.count)")
print("Entries: \(all.count)")
print("Output: \(root.path)")
