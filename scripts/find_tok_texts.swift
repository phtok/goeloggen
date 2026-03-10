import Foundation
import PDFKit

struct IssueMeta {
    let year: String
    let issue: String
    let title: String
}

struct AuthorEntry {
    let year: String
    let issue: String
    let title: String
    let publicationDate: String
    let fileName: String
    let pageIndex: Int
    let marker: String
    let text: String
}

struct MentionEntry {
    let year: String
    let issue: String
    let title: String
    let publicationDate: String
    let fileName: String
    let pageIndex: Int
    let term: String
    let context: String
}

func usage() {
    let cmd = (CommandLine.arguments.first as NSString?)?.lastPathComponent ?? "find_tok_texts.swift"
    print("Usage: \(cmd) <input_pdf_root> <output_dir>")
}

func normalizeDashes(_ value: String) -> String {
    return value
        .replacingOccurrences(of: "–", with: "-")
        .replacingOccurrences(of: "—", with: "-")
}

func parseMeta(from fileName: String, fallbackYear: String) -> IssueMeta {
    let rawBase = (fileName as NSString).deletingPathExtension
    let base = normalizeDashes(rawBase)
    let ns = base as NSString

    let mainRe = try! NSRegularExpression(pattern: #"^G(\d{4})[_-](\d{1,2})(?:[_-](\d{1,2}))?(?:[_-](.+))?$"#, options: [])
    if let m = mainRe.firstMatch(in: base, options: [], range: NSRange(location: 0, length: ns.length)) {
        let year = ns.substring(with: m.range(at: 1))
        let a = ns.substring(with: m.range(at: 2))
        let b = m.range(at: 3).location != NSNotFound ? ns.substring(with: m.range(at: 3)) : ""
        let issue = b.isEmpty ? a : "\(a)-\(b)"
        let titleRaw = m.range(at: 4).location != NSNotFound ? ns.substring(with: m.range(at: 4)) : ""
        let title = titleRaw.replacingOccurrences(of: "_", with: " ").trimmingCharacters(in: .whitespacesAndNewlines)
        return IssueMeta(year: year, issue: issue, title: title.isEmpty ? base : title)
    }

    let genericRe = try! NSRegularExpression(pattern: #".*?(\d{4})[_-](.+)$"#, options: [])
    if let m = genericRe.firstMatch(in: base, options: [], range: NSRange(location: 0, length: ns.length)) {
        let year = ns.substring(with: m.range(at: 1))
        let tail = ns.substring(with: m.range(at: 2))
        let tailNS = tail as NSString
        let issueRe = try! NSRegularExpression(pattern: #"^(\d{1,2}(?:-\d{1,2})?)"#, options: [])
        if let i = issueRe.firstMatch(in: tail, options: [], range: NSRange(location: 0, length: tailNS.length)) {
            let issue = tailNS.substring(with: i.range(at: 1))
            let restStart = i.range.location + i.range.length
            let rest = restStart < tailNS.length ? tailNS.substring(from: restStart) : ""
            let title = rest.replacingOccurrences(of: "_", with: " ").trimmingCharacters(in: CharacterSet(charactersIn: "-_ ").union(.whitespacesAndNewlines))
            return IssueMeta(year: year, issue: issue, title: title.isEmpty ? base : title)
        }
        return IssueMeta(year: year, issue: tail, title: base)
    }

    let yRe = try! NSRegularExpression(pattern: #"(19|20)\d{2}"#, options: [])
    let yRange = NSRange(location: 0, length: ns.length)
    let year = yRe.firstMatch(in: base, options: [], range: yRange).map { ns.substring(with: $0.range) } ?? fallbackYear
    return IssueMeta(year: year, issue: "?", title: base)
}

func issueSortKey(_ issue: String) -> Int {
    let regex = try! NSRegularExpression(pattern: #"\d+"#, options: [])
    let ns = issue as NSString
    if let m = regex.firstMatch(in: issue, options: [], range: NSRange(location: 0, length: ns.length)) {
        return Int(ns.substring(with: m.range)) ?? 9999
    }
    return 9999
}

func compactSpaces(_ s: String) -> String {
    return s.replacingOccurrences(of: #"\s+"#, with: " ", options: .regularExpression).trimmingCharacters(in: .whitespacesAndNewlines)
}

func regexReplace(_ value: String, pattern: String, with replacement: String, options: NSRegularExpression.Options = []) -> String {
    let re = try! NSRegularExpression(pattern: pattern, options: options)
    return re.stringByReplacingMatches(in: value, options: [], range: NSRange(location: 0, length: (value as NSString).length), withTemplate: replacement)
}

func cleanText(_ raw: String) -> String {
    var text = raw
        .replacingOccurrences(of: "\u{00AD}", with: "")
        .replacingOccurrences(of: "\r\n", with: "\n")
        .replacingOccurrences(of: "\r", with: "\n")

    // Merge hyphenated words split across line breaks.
    for _ in 0..<3 {
        let replaced = regexReplace(text, pattern: #"(\p{L})-\s*\n\s*(\p{Ll})"#, with: "$1$2")
        if replaced == text { break }
        text = replaced
    }

    let dropLinePatterns: [String] = [
        #"^\d+\s*$"#,
        #"^\s*\d+\s+DAS GOETHEANUM.*$"#,
        #"^\s*DAS GOETHEANUM.*$"#,
        #"^\s*Impressum\b.*$"#,
        #"^\s*Redaktion@.*$"#
    ]
    let dropRes = dropLinePatterns.map { try! NSRegularExpression(pattern: $0, options: [.caseInsensitive]) }

    let lines = text.components(separatedBy: "\n").map {
        compactSpaces($0)
    }

    var paragraphs: [[String]] = []
    var current: [String] = []

    for line in lines {
        if line.isEmpty {
            if !current.isEmpty {
                paragraphs.append(current)
                current.removeAll(keepingCapacity: true)
            }
            continue
        }

        let ns = line as NSString
        let r = NSRange(location: 0, length: ns.length)
        let shouldDrop = dropRes.contains { $0.firstMatch(in: line, options: [], range: r) != nil }
        if shouldDrop { continue }
        current.append(line)
    }
    if !current.isEmpty {
        paragraphs.append(current)
    }

    var out: [String] = []
    for p in paragraphs {
        var joined = p.joined(separator: " ")
        joined = regexReplace(joined, pattern: #"\s+([,.;:!?])"#, with: "$1")
        joined = regexReplace(joined, pattern: #"\(\s+"#, with: "(")
        joined = regexReplace(joined, pattern: #"\s+\)"#, with: ")")
        joined = compactSpaces(joined)
        if !joined.isEmpty {
            out.append(joined)
        }
    }
    return out.joined(separator: "\n\n")
}

func findDate(in doc: PDFDocument) -> String {
    let monthPattern = #"(Januar|Februar|März|Maerz|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)"#
    let pattern = #"\b(\d{1,2})\.\s*"# + monthPattern + #"\s+(\d{4})\b"#
    let re = try! NSRegularExpression(pattern: pattern, options: [.caseInsensitive])

    let pagesToCheck = min(doc.pageCount, 8)
    for idx in 0..<pagesToCheck {
        guard let page = doc.page(at: idx), let text = page.string else { continue }
        let ns = text as NSString
        let range = NSRange(location: 0, length: ns.length)
        if let m = re.firstMatch(in: text, options: [], range: range) {
            let day = ns.substring(with: m.range(at: 1))
            let month = ns.substring(with: m.range(at: 2))
            let year = ns.substring(with: m.range(at: 3))
            return "\(day). \(month) \(year)"
        }
    }
    return "unbekannt"
}

let mentionRegex = try! NSRegularExpression(
    pattern: #"(?i)\bphilipp\s*tok\b|\bph\.?\s*tok\b|\bphtok\b|(?<![A-Za-zÄÖÜäöü])tok(?!yo|io|en|[A-Za-zÄÖÜäöü])"#,
    options: []
)
let authorLineRegex = try! NSRegularExpression(
    pattern: #"(?i)^\s*(von\s+)?(philipp\s*tok|ph\.?\s*tok|phtok)\s*$"#,
    options: []
)
let explicitBylineLineRegex = try! NSRegularExpression(
    pattern: #"(?i)^\s*von\s+(philipp\s*tok|ph\.?\s*tok|phtok)\s*$"#,
    options: []
)
let speakerLineRegex = try! NSRegularExpression(
    pattern: #"(?i)^\s*(philipp\s*tok|ph\.?\s*tok|phtok)\s*[:\-–]\s*$"#,
    options: []
)
let bylineInlineRegex = try! NSRegularExpression(
    pattern: #"(?i)\bvon\s+(philipp\s*tok|ph\.?\s*tok|phtok)\b"#,
    options: []
)
let creditRegex = try! NSRegularExpression(
    pattern: #"(?i)\b(zeichnung|bild|foto|fotos|illustration|grafik|layout|produktion|kontakt|redaktion)\b"#,
    options: []
)
let sentenceRegex = try! NSRegularExpression(pattern: #"[^.!?…]+[.!?…]+|[^.!?…]+$"#, options: [])

func hasMatch(_ re: NSRegularExpression, in s: String) -> Bool {
    return re.firstMatch(in: s, options: [], range: NSRange(location: 0, length: (s as NSString).length)) != nil
}

func normalizedLinesForDetection(_ raw: String) -> [String] {
    let text = raw
        .replacingOccurrences(of: "\u{00AD}", with: "")
        .replacingOccurrences(of: "\r\n", with: "\n")
        .replacingOccurrences(of: "\r", with: "\n")
    let dropLinePatterns: [String] = [
        #"^\d+\s*$"#,
        #"^\s*\d+\s+DAS GOETHEANUM.*$"#,
        #"^\s*DAS GOETHEANUM.*$"#,
        #"^\s*Impressum\b.*$"#,
        #"^\s*Redaktion@.*$"#
    ]
    let dropRes = dropLinePatterns.map { try! NSRegularExpression(pattern: $0, options: [.caseInsensitive]) }
    return text.components(separatedBy: "\n").map { compactSpaces($0) }.filter { line in
        if line.isEmpty { return false }
        let ns = line as NSString
        let r = NSRange(location: 0, length: ns.length)
        return !dropRes.contains { $0.firstMatch(in: line, options: [], range: r) != nil }
    }
}

func detectAuthorMarker(raw: String, cleaned: String) -> String? {
    if cleaned.count < 450 { return nil }
    let lines = normalizedLinesForDetection(raw)
    let head = Array(lines.prefix(18))
    let excludedTokens = [
        "beitrag", "gespräch", "interview", "kuratorium", "ausstellung", "titelzeichnung",
        "gestaltung", "redaktion", "kontakt", "zeichnungen", "zeichnerische", "vektorisierte",
        "serie", "detail", "material", "federzeichnungen"
    ]
    for (idx, line) in head.enumerated() {
        let lower = line.lowercased()
        if !hasMatch(mentionRegex, in: lower) { continue }
        if hasMatch(creditRegex, in: lower) { continue }
        if excludedTokens.contains(where: { lower.contains($0) }) { continue }

        if hasMatch(authorLineRegex, in: lower) { return "line\(idx + 1):\(line)" }
        if hasMatch(explicitBylineLineRegex, in: lower) { return "line\(idx + 1):\(line)" }
        if hasMatch(speakerLineRegex, in: lower) { return "line\(idx + 1):\(line)" }
        if hasMatch(bylineInlineRegex, in: lower) {
            let words = lower.split(whereSeparator: { $0.isWhitespace }).count
            if words <= 7 {
                return "line\(idx + 1):\(line)"
            }
        }
    }
    return nil
}

func extractContexts(_ cleaned: String) -> [(String, String)] {
    let flat = compactSpaces(cleaned.replacingOccurrences(of: "\n", with: " "))
    let ns = flat as NSString
    let fullRange = NSRange(location: 0, length: ns.length)
    let sentenceMatches = sentenceRegex.matches(in: flat, options: [], range: fullRange)
    if sentenceMatches.isEmpty { return [] }

    var contexts: [(String, String)] = []
    var seen: Set<String> = []
    let mentionMatches = mentionRegex.matches(in: flat, options: [], range: fullRange)
    for m in mentionMatches {
        let term = ns.substring(with: m.range).trimmingCharacters(in: .whitespacesAndNewlines)
        guard !term.isEmpty else { continue }

        var sentIdx: Int? = nil
        for (idx, s) in sentenceMatches.enumerated() {
            if NSLocationInRange(m.range.location, s.range) {
                sentIdx = idx
                break
            }
        }
        guard let i = sentIdx else { continue }
        let start = max(0, i - 1)
        let end = min(sentenceMatches.count - 1, i + 1)
        let parts = (start...end).map {
            compactSpaces(ns.substring(with: sentenceMatches[$0].range))
        }.filter { !$0.isEmpty }
        let context = parts.joined(separator: " ")
        if context.isEmpty { continue }

        let key = "\(term.lowercased())::\(context.lowercased())"
        if seen.contains(key) { continue }
        seen.insert(key)
        contexts.append((term, context))
    }
    return contexts
}

func htmlEscape(_ s: String) -> String {
    return s
        .replacingOccurrences(of: "&", with: "&amp;")
        .replacingOccurrences(of: "<", with: "&lt;")
        .replacingOccurrences(of: ">", with: "&gt;")
        .replacingOccurrences(of: "\"", with: "&quot;")
}

func issueCompact(_ issue: String) -> String {
    return normalizeDashes(issue).replacingOccurrences(of: " ", with: "")
}

func renderAuthorHtml(_ entries: [AuthorEntry]) -> String {
    let generatedAt = ISO8601DateFormatter().string(from: Date())
    var body = ""
    for e in entries {
        let paras = e.text.components(separatedBy: "\n\n").map { p in
            "<p>\(htmlEscape(p))</p>"
        }.joined(separator: "\n")
        body += """
        <article class="post">
          <h2>J\(String(e.year.suffix(2)))H\(issueCompact(e.issue)) · \(htmlEscape(e.title))</h2>
          <p class="meta">\(htmlEscape(e.publicationDate)) · Jahrgang \(htmlEscape(e.year)) · Heft \(htmlEscape(e.issue)) · Seite \(e.pageIndex + 1) · \(htmlEscape(e.fileName)) · Marker: \(htmlEscape(e.marker))</p>
          \(paras)
        </article>
        """
    }

    return """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Philipp Tok – Autorentexte</title>
      <style>
        body { font-family: Georgia, "Times New Roman", serif; margin: 28px auto; max-width: 900px; color: #1f2937; line-height: 1.6; padding: 0 14px 40px; }
        h1 { font-size: 34px; margin: 0 0 6px 0; }
        p.lead { color: #6b7280; margin: 0 0 24px 0; }
        article.post { border-top: 1px solid #e5e7eb; padding-top: 22px; margin-top: 22px; }
        article.post h2 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 22px; line-height: 1.25; margin: 0 0 8px 0; color: #111827; }
        p.meta { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; font-size: 13px; color: #6b7280; margin: 0 0 14px 0; }
        article.post p { margin: 0 0 12px 0; font-size: 18px; }
      </style>
    </head>
    <body>
      <h1>Philipp Tok – Autorentexte</h1>
      <p class="lead">Gefunden in allen verfügbaren Jahrgängen · Erzeugt: \(generatedAt) · Treffer: \(entries.count)</p>
      \(body)
    </body>
    </html>
    """
}

func renderMentionHtml(_ entries: [MentionEntry]) -> String {
    let generatedAt = ISO8601DateFormatter().string(from: Date())
    var rows = ""
    for e in entries {
        rows += """
        <article class="hit">
          <h3>J\(String(e.year.suffix(2)))H\(issueCompact(e.issue)) · \(htmlEscape(e.title))</h3>
          <p class="meta">\(htmlEscape(e.publicationDate)) · Jahrgang \(htmlEscape(e.year)) · Heft \(htmlEscape(e.issue)) · Seite \(e.pageIndex + 1) · \(htmlEscape(e.fileName))</p>
          <p class="term">Fund: <strong>\(htmlEscape(e.term))</strong></p>
          <blockquote>\(htmlEscape(e.context))</blockquote>
        </article>
        """
    }
    return """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Philipp Tok – Erwähnungen</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px auto; max-width: 920px; color: #1f2937; line-height: 1.45; padding: 0 14px 40px; }
        h1 { font-size: 30px; margin: 0 0 6px 0; }
        p.lead { color: #6b7280; margin: 0 0 20px 0; }
        article.hit { border: 1px solid #e5e7eb; border-radius: 8px; padding: 14px 14px 10px; margin: 0 0 12px 0; background: #fff; }
        article.hit h3 { margin: 0 0 6px 0; font-size: 18px; color: #111827; }
        p.meta { margin: 0 0 8px 0; font-size: 12px; color: #6b7280; }
        p.term { margin: 0 0 6px 0; font-size: 13px; color: #374151; }
        blockquote { margin: 0 0 2px 0; border-left: 3px solid #d1d5db; padding: 4px 10px; color: #111827; background: #f9fafb; }
      </style>
    </head>
    <body>
      <h1>Philipp Tok – Erwähnungen</h1>
      <p class="lead">Mit Kontext (vorheriger, aktueller, nächster Satz) · Erzeugt: \(generatedAt) · Treffer: \(entries.count)</p>
      \(rows)
    </body>
    </html>
    """
}

func csvEscape(_ value: String) -> String {
    if value.contains(",") || value.contains("\n") || value.contains("\"") {
        return "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
    }
    return value
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    usage()
    exit(1)
}

let inputRoot = URL(fileURLWithPath: args[1], isDirectory: true)
let outDir = URL(fileURLWithPath: args[2], isDirectory: true)
let fm = FileManager.default
try fm.createDirectory(at: outDir, withIntermediateDirectories: true)

let pdfFiles = try fm.enumerator(at: inputRoot, includingPropertiesForKeys: nil)?
    .compactMap { $0 as? URL }
    .filter { $0.pathExtension.lowercased() == "pdf" }
    .sorted { $0.path.localizedStandardCompare($1.path) == .orderedAscending } ?? []

var authorEntries: [AuthorEntry] = []
var mentionEntries: [MentionEntry] = []
var failures: [String] = []
let startedAt = Date()

for (fileIdx, fileURL) in pdfFiles.enumerated() {
    if (fileIdx + 1) % 25 == 0 || fileIdx == 0 {
        let elapsed = Int(Date().timeIntervalSince(startedAt))
        print("[\(fileIdx + 1)/\(pdfFiles.count)] \(fileURL.lastPathComponent) · elapsed \(elapsed)s")
        fflush(stdout)
    }
    autoreleasepool {
        let fileName = fileURL.lastPathComponent
        let parentYear = fileURL.deletingLastPathComponent().lastPathComponent
        let fallbackYear = parentYear.range(of: #"^\d{4}$"#, options: .regularExpression) != nil ? parentYear : "?"
        let meta = parseMeta(from: fileName, fallbackYear: fallbackYear)

        guard let doc = PDFDocument(url: fileURL) else {
            failures.append("OPEN_FAIL: \(fileName)")
            return
        }
        let publicationDate = findDate(in: doc)

        var seenAuthorPage = Set<String>()
        var seenMentionContext = Set<String>()
        for idx in 0..<doc.pageCount {
            guard let page = doc.page(at: idx), let raw = page.string, !raw.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { continue }
            let cleaned = cleanText(raw)
            if cleaned.isEmpty { continue }

            if let marker = detectAuthorMarker(raw: raw, cleaned: cleaned) {
                let key = "\(meta.year)|\(meta.issue)|\(fileName)|\(idx)|\(cleaned.prefix(140))"
                if !seenAuthorPage.contains(key) {
                    seenAuthorPage.insert(key)
                    authorEntries.append(AuthorEntry(
                        year: meta.year,
                        issue: meta.issue,
                        title: meta.title,
                        publicationDate: publicationDate,
                        fileName: fileName,
                        pageIndex: idx,
                        marker: marker,
                        text: cleaned
                    ))
                }
            }

            let ctx = extractContexts(cleaned)
            if !ctx.isEmpty {
                for (term, context) in ctx {
                    let key = "\(meta.year)|\(meta.issue)|\(fileName)|\(idx)|\(term.lowercased())|\(context.lowercased())"
                    if seenMentionContext.contains(key) { continue }
                    seenMentionContext.insert(key)
                    mentionEntries.append(MentionEntry(
                        year: meta.year,
                        issue: meta.issue,
                        title: meta.title,
                        publicationDate: publicationDate,
                        fileName: fileName,
                        pageIndex: idx,
                        term: term,
                        context: context
                    ))
                }
            }
        }
    }
}

authorEntries.sort {
    if $0.year != $1.year { return $0.year < $1.year }
    let k0 = issueSortKey($0.issue)
    let k1 = issueSortKey($1.issue)
    if k0 != k1 { return k0 < k1 }
    if $0.issue != $1.issue { return $0.issue < $1.issue }
    return $0.pageIndex < $1.pageIndex
}

mentionEntries.sort {
    if $0.year != $1.year { return $0.year < $1.year }
    let k0 = issueSortKey($0.issue)
    let k1 = issueSortKey($1.issue)
    if k0 != k1 { return k0 < k1 }
    if $0.issue != $1.issue { return $0.issue < $1.issue }
    if $0.pageIndex != $1.pageIndex { return $0.pageIndex < $1.pageIndex }
    return $0.term.localizedCaseInsensitiveCompare($1.term) == .orderedAscending
}

let authorHtml = renderAuthorHtml(authorEntries)
try authorHtml.write(to: outDir.appendingPathComponent("tok_autorentexte_onepager.html"), atomically: true, encoding: .utf8)

let mentionHtml = renderMentionHtml(mentionEntries)
try mentionHtml.write(to: outDir.appendingPathComponent("tok_erwaehnungen_onepager.html"), atomically: true, encoding: .utf8)

var authorCSV = "jahr,heft,erscheinung,seite,titel,datei,marker,text\n"
for e in authorEntries {
    authorCSV += [e.year, e.issue, e.publicationDate, String(e.pageIndex + 1), e.title, e.fileName, e.marker, e.text].map(csvEscape).joined(separator: ",") + "\n"
}
try authorCSV.write(to: outDir.appendingPathComponent("tok_autorentexte.csv"), atomically: true, encoding: .utf8)

var mentionCSV = "jahr,heft,erscheinung,seite,titel,datei,term,kontext\n"
for e in mentionEntries {
    mentionCSV += [e.year, e.issue, e.publicationDate, String(e.pageIndex + 1), e.title, e.fileName, e.term, e.context].map(csvEscape).joined(separator: ",") + "\n"
}
try mentionCSV.write(to: outDir.appendingPathComponent("tok_erwaehnungen.csv"), atomically: true, encoding: .utf8)

if !failures.isEmpty {
    try (failures.joined(separator: "\n") + "\n").write(to: outDir.appendingPathComponent("failures.log"), atomically: true, encoding: .utf8)
}

let totalElapsed = Int(Date().timeIntervalSince(startedAt))
print("PDF files: \(pdfFiles.count)")
print("Author entries: \(authorEntries.count)")
print("Mention entries: \(mentionEntries.count)")
print("Output: \(outDir.path)")
print("Elapsed: \(totalElapsed)s")
if !failures.isEmpty {
    print("Failures: \(failures.count) (see failures.log)")
}
