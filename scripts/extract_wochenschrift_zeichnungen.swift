import Foundation
import PDFKit
import CoreGraphics

struct IssueMeta {
    let year: String
    let issue: String
    let title: String
}

struct Record {
    let entryId: String
    let sourceFile: String
    let year: String
    let issue: String
    let title: String
    let publicationDate: String
    let pageIndex: Int
    let imageRelativePath: String
    let note: String
}

struct PDFColor {
    var r: Double
    var g: Double
    var b: Double

    static let black = PDFColor(r: 0, g: 0, b: 0)

    func hex() -> String {
        func clamp255(_ v: Double) -> Int {
            return max(0, min(255, Int((max(0, min(1, v)) * 255.0).rounded())))
        }
        return String(format: "#%02X%02X%02X", clamp255(r), clamp255(g), clamp255(b))
    }

    static func fromGray(_ gray: Double) -> PDFColor {
        let v = max(0, min(1, gray))
        return PDFColor(r: v, g: v, b: v)
    }

    static func fromCMYK(c: Double, m: Double, y: Double, k: Double) -> PDFColor {
        let cc = max(0, min(1, c))
        let mm = max(0, min(1, m))
        let yy = max(0, min(1, y))
        let kk = max(0, min(1, k))
        let r = 1.0 - min(1.0, cc + kk)
        let g = 1.0 - min(1.0, mm + kk)
        let b = 1.0 - min(1.0, yy + kk)
        return PDFColor(r: r, g: g, b: b)
    }
}

struct PDFMatrix {
    var a: Double
    var b: Double
    var c: Double
    var d: Double
    var e: Double
    var f: Double

    static let identity = PDFMatrix(a: 1, b: 0, c: 0, d: 1, e: 0, f: 0)

    func apply(_ p: CGPoint) -> CGPoint {
        let x = a * Double(p.x) + c * Double(p.y) + e
        let y = b * Double(p.x) + d * Double(p.y) + f
        return CGPoint(x: x, y: y)
    }

    func multiplied(leftBy m: PDFMatrix) -> PDFMatrix {
        return PDFMatrix(
            a: m.a * a + m.c * b,
            b: m.b * a + m.d * b,
            c: m.a * c + m.c * d,
            d: m.b * c + m.d * d,
            e: m.a * e + m.c * f + m.e,
            f: m.b * e + m.d * f + m.f
        )
    }

    var approxScale: Double {
        let sx = hypot(a, b)
        let sy = hypot(c, d)
        return max(0.001, (sx + sy) / 2.0)
    }
}

struct GraphicsState {
    var ctm: PDFMatrix = .identity
    var strokeColor: PDFColor = .black
    var fillColor: PDFColor = .black
    var lineWidth: Double = 1.0
    var lineCap: Int = 0
    var lineJoin: Int = 0
    var miterLimit: Double = 10.0
}

enum PathSegment {
    case move(CGPoint)
    case line(CGPoint)
    case curve(CGPoint, CGPoint, CGPoint)
    case close
}

struct VectorPath {
    let segments: [PathSegment]
    let bbox: CGRect
    let stroke: Bool
    let fill: Bool
    let evenOddFill: Bool
    let strokeColor: PDFColor
    let fillColor: PDFColor
    let lineWidth: Double
    let lineCap: Int
    let lineJoin: Int
    let miterLimit: Double
}

final class PathBuilder {
    var segments: [PathSegment] = []
    var points: [CGPoint] = []
    var currentPoint: CGPoint?

    func clear() {
        segments.removeAll(keepingCapacity: true)
        points.removeAll(keepingCapacity: true)
        currentPoint = nil
    }

    func move(_ p: CGPoint) {
        segments.append(.move(p))
        points.append(p)
        currentPoint = p
    }

    func line(_ p: CGPoint) {
        if currentPoint == nil {
            move(p)
            return
        }
        segments.append(.line(p))
        points.append(p)
        currentPoint = p
    }

    func curve(_ c1: CGPoint, _ c2: CGPoint, _ p: CGPoint) {
        if currentPoint == nil {
            move(p)
            return
        }
        segments.append(.curve(c1, c2, p))
        points.append(c1)
        points.append(c2)
        points.append(p)
        currentPoint = p
    }

    func close() {
        segments.append(.close)
    }

    func appendRect(_ p1: CGPoint, _ p2: CGPoint, _ p3: CGPoint, _ p4: CGPoint) {
        move(p1)
        line(p2)
        line(p3)
        line(p4)
        close()
    }

    var isEmpty: Bool { segments.isEmpty || points.isEmpty }

    var bbox: CGRect {
        guard let first = points.first else { return .null }
        var minX = first.x
        var minY = first.y
        var maxX = first.x
        var maxY = first.y
        for p in points.dropFirst() {
            minX = min(minX, p.x)
            minY = min(minY, p.y)
            maxX = max(maxX, p.x)
            maxY = max(maxY, p.y)
        }
        return CGRect(x: minX, y: minY, width: max(0.001, maxX - minX), height: max(0.001, maxY - minY))
    }
}

final class ScannerContext {
    var stateStack: [GraphicsState] = [GraphicsState()]
    let path = PathBuilder()
    var results: [VectorPath] = []

    var state: GraphicsState {
        get { stateStack[stateStack.count - 1] }
        set { stateStack[stateStack.count - 1] = newValue }
    }

    func pushState() {
        stateStack.append(state)
    }

    func popState() {
        if stateStack.count > 1 {
            _ = stateStack.popLast()
        }
    }

    func transform(x: Double, y: Double) -> CGPoint {
        return state.ctm.apply(CGPoint(x: x, y: y))
    }

    func paint(stroke: Bool, fill: Bool, evenOddFill: Bool, closeBeforePaint: Bool) {
        if closeBeforePaint {
            path.close()
        }
        defer { path.clear() }

        if path.isEmpty {
            return
        }

        let b = path.bbox
        let lw = max(0.1, state.lineWidth * state.ctm.approxScale)
        results.append(VectorPath(
            segments: path.segments,
            bbox: b,
            stroke: stroke,
            fill: fill,
            evenOddFill: evenOddFill,
            strokeColor: state.strokeColor,
            fillColor: state.fillColor,
            lineWidth: lw,
            lineCap: state.lineCap,
            lineJoin: state.lineJoin,
            miterLimit: state.miterLimit
        ))
    }

    func endPath() {
        path.clear()
    }
}

func withContext(_ info: UnsafeMutableRawPointer?) -> ScannerContext? {
    guard let info else { return nil }
    return Unmanaged<ScannerContext>.fromOpaque(info).takeUnretainedValue()
}

func popNumber(_ scanner: CGPDFScannerRef?) -> Double? {
    guard let scanner else { return nil }
    var n: CGPDFReal = 0
    if CGPDFScannerPopNumber(scanner, &n) {
        return Double(n)
    }
    var i: CGPDFInteger = 0
    if CGPDFScannerPopInteger(scanner, &i) {
        return Double(i)
    }
    return nil
}

func popAllNumbers(_ scanner: CGPDFScannerRef?) -> [Double] {
    guard scanner != nil else { return [] }
    var values: [Double] = []
    while let n = popNumber(scanner) {
        values.append(n)
    }
    return values.reversed()
}

func colorFromComponents(_ values: [Double]) -> PDFColor? {
    switch values.count {
    case 1:
        return PDFColor.fromGray(values[0])
    case 3:
        return PDFColor(r: values[0], g: values[1], b: values[2])
    case 4:
        return PDFColor.fromCMYK(c: values[0], m: values[1], y: values[2], k: values[3])
    default:
        return nil
    }
}

let cb_q: CGPDFOperatorCallback = { _, info in
    withContext(info)?.pushState()
}

let cb_Q: CGPDFOperatorCallback = { _, info in
    withContext(info)?.popState()
}

let cb_cm: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let f = popNumber(scanner),
          let e = popNumber(scanner),
          let d = popNumber(scanner),
          let c = popNumber(scanner),
          let b = popNumber(scanner),
          let a = popNumber(scanner) else { return }
    let m = PDFMatrix(a: a, b: b, c: c, d: d, e: e, f: f)
    var s = ctx.state
    s.ctm = s.ctm.multiplied(leftBy: m)
    ctx.state = s
}

let cb_w: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let w = popNumber(scanner) else { return }
    var s = ctx.state
    s.lineWidth = max(0.001, w)
    ctx.state = s
}

let cb_J: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let cap = popNumber(scanner) else { return }
    var s = ctx.state
    s.lineCap = Int(cap.rounded())
    ctx.state = s
}

let cb_j: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let join = popNumber(scanner) else { return }
    var s = ctx.state
    s.lineJoin = Int(join.rounded())
    ctx.state = s
}

let cb_M: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let ml = popNumber(scanner) else { return }
    var s = ctx.state
    s.miterLimit = ml
    ctx.state = s
}

let cb_RG: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let b = popNumber(scanner),
          let g = popNumber(scanner),
          let r = popNumber(scanner) else { return }
    var s = ctx.state
    s.strokeColor = PDFColor(r: r, g: g, b: b)
    ctx.state = s
}

let cb_rg: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let b = popNumber(scanner),
          let g = popNumber(scanner),
          let r = popNumber(scanner) else { return }
    var s = ctx.state
    s.fillColor = PDFColor(r: r, g: g, b: b)
    ctx.state = s
}

let cb_G: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let gray = popNumber(scanner) else { return }
    var s = ctx.state
    s.strokeColor = PDFColor.fromGray(gray)
    ctx.state = s
}

let cb_g: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info), let gray = popNumber(scanner) else { return }
    var s = ctx.state
    s.fillColor = PDFColor.fromGray(gray)
    ctx.state = s
}

let cb_K: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let k = popNumber(scanner),
          let y = popNumber(scanner),
          let m = popNumber(scanner),
          let c = popNumber(scanner) else { return }
    var s = ctx.state
    s.strokeColor = PDFColor.fromCMYK(c: c, m: m, y: y, k: k)
    ctx.state = s
}

let cb_k: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let k = popNumber(scanner),
          let y = popNumber(scanner),
          let m = popNumber(scanner),
          let c = popNumber(scanner) else { return }
    var s = ctx.state
    s.fillColor = PDFColor.fromCMYK(c: c, m: m, y: y, k: k)
    ctx.state = s
}

let cb_SC: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info) else { return }
    let values = popAllNumbers(scanner)
    guard let color = colorFromComponents(values) else { return }
    var s = ctx.state
    s.strokeColor = color
    ctx.state = s
}

let cb_sc: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info) else { return }
    let values = popAllNumbers(scanner)
    guard let color = colorFromComponents(values) else { return }
    var s = ctx.state
    s.fillColor = color
    ctx.state = s
}

let cb_SCN: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info) else { return }
    let values = popAllNumbers(scanner)
    guard let color = colorFromComponents(values) else { return }
    var s = ctx.state
    s.strokeColor = color
    ctx.state = s
}

let cb_scn: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info) else { return }
    let values = popAllNumbers(scanner)
    guard let color = colorFromComponents(values) else { return }
    var s = ctx.state
    s.fillColor = color
    ctx.state = s
}

let cb_m: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let y = popNumber(scanner),
          let x = popNumber(scanner) else { return }
    ctx.path.move(ctx.transform(x: x, y: y))
}

let cb_l: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let y = popNumber(scanner),
          let x = popNumber(scanner) else { return }
    ctx.path.line(ctx.transform(x: x, y: y))
}

let cb_c: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let y3 = popNumber(scanner),
          let x3 = popNumber(scanner),
          let y2 = popNumber(scanner),
          let x2 = popNumber(scanner),
          let y1 = popNumber(scanner),
          let x1 = popNumber(scanner) else { return }
    let p1 = ctx.transform(x: x1, y: y1)
    let p2 = ctx.transform(x: x2, y: y2)
    let p3 = ctx.transform(x: x3, y: y3)
    ctx.path.curve(p1, p2, p3)
}

let cb_v: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let y3 = popNumber(scanner),
          let x3 = popNumber(scanner),
          let y2 = popNumber(scanner),
          let x2 = popNumber(scanner),
          let cp = ctx.path.currentPoint else { return }
    let p2 = ctx.transform(x: x2, y: y2)
    let p3 = ctx.transform(x: x3, y: y3)
    ctx.path.curve(cp, p2, p3)
}

let cb_y: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let y3 = popNumber(scanner),
          let x3 = popNumber(scanner),
          let y1 = popNumber(scanner),
          let x1 = popNumber(scanner) else { return }
    let p1 = ctx.transform(x: x1, y: y1)
    let p3 = ctx.transform(x: x3, y: y3)
    ctx.path.curve(p1, p3, p3)
}

let cb_h: CGPDFOperatorCallback = { _, info in
    withContext(info)?.path.close()
}

let cb_re: CGPDFOperatorCallback = { scanner, info in
    guard let ctx = withContext(info),
          let h = popNumber(scanner),
          let w = popNumber(scanner),
          let y = popNumber(scanner),
          let x = popNumber(scanner) else { return }
    let p1 = ctx.transform(x: x, y: y)
    let p2 = ctx.transform(x: x + w, y: y)
    let p3 = ctx.transform(x: x + w, y: y + h)
    let p4 = ctx.transform(x: x, y: y + h)
    ctx.path.appendRect(p1, p2, p3, p4)
}

let cb_S: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: false, evenOddFill: false, closeBeforePaint: false)
}

let cb_s: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: false, evenOddFill: false, closeBeforePaint: true)
}

let cb_f: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: false, fill: true, evenOddFill: false, closeBeforePaint: false)
}

let cb_fStar: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: false, fill: true, evenOddFill: true, closeBeforePaint: false)
}

let cb_B: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: true, evenOddFill: false, closeBeforePaint: false)
}

let cb_BStar: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: true, evenOddFill: true, closeBeforePaint: false)
}

let cb_b: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: true, evenOddFill: false, closeBeforePaint: true)
}

let cb_bStar: CGPDFOperatorCallback = { _, info in
    withContext(info)?.paint(stroke: true, fill: true, evenOddFill: true, closeBeforePaint: true)
}

let cb_n: CGPDFOperatorCallback = { _, info in
    withContext(info)?.endPath()
}

func createOperatorTable() -> CGPDFOperatorTableRef {
    let t = CGPDFOperatorTableCreate()!

    CGPDFOperatorTableSetCallback(t, "q", cb_q)
    CGPDFOperatorTableSetCallback(t, "Q", cb_Q)
    CGPDFOperatorTableSetCallback(t, "cm", cb_cm)

    CGPDFOperatorTableSetCallback(t, "w", cb_w)
    CGPDFOperatorTableSetCallback(t, "J", cb_J)
    CGPDFOperatorTableSetCallback(t, "j", cb_j)
    CGPDFOperatorTableSetCallback(t, "M", cb_M)

    CGPDFOperatorTableSetCallback(t, "RG", cb_RG)
    CGPDFOperatorTableSetCallback(t, "rg", cb_rg)
    CGPDFOperatorTableSetCallback(t, "G", cb_G)
    CGPDFOperatorTableSetCallback(t, "g", cb_g)
    CGPDFOperatorTableSetCallback(t, "K", cb_K)
    CGPDFOperatorTableSetCallback(t, "k", cb_k)
    CGPDFOperatorTableSetCallback(t, "SC", cb_SC)
    CGPDFOperatorTableSetCallback(t, "sc", cb_sc)
    CGPDFOperatorTableSetCallback(t, "SCN", cb_SCN)
    CGPDFOperatorTableSetCallback(t, "scn", cb_scn)

    CGPDFOperatorTableSetCallback(t, "m", cb_m)
    CGPDFOperatorTableSetCallback(t, "l", cb_l)
    CGPDFOperatorTableSetCallback(t, "c", cb_c)
    CGPDFOperatorTableSetCallback(t, "v", cb_v)
    CGPDFOperatorTableSetCallback(t, "y", cb_y)
    CGPDFOperatorTableSetCallback(t, "h", cb_h)
    CGPDFOperatorTableSetCallback(t, "re", cb_re)

    CGPDFOperatorTableSetCallback(t, "S", cb_S)
    CGPDFOperatorTableSetCallback(t, "s", cb_s)
    CGPDFOperatorTableSetCallback(t, "f", cb_f)
    CGPDFOperatorTableSetCallback(t, "F", cb_f)
    CGPDFOperatorTableSetCallback(t, "f*", cb_fStar)
    CGPDFOperatorTableSetCallback(t, "B", cb_B)
    CGPDFOperatorTableSetCallback(t, "B*", cb_BStar)
    CGPDFOperatorTableSetCallback(t, "b", cb_b)
    CGPDFOperatorTableSetCallback(t, "b*", cb_bStar)
    CGPDFOperatorTableSetCallback(t, "n", cb_n)

    return t
}

func extractPaintedPaths(page: CGPDFPage) -> [VectorPath] {
    let cs = CGPDFContentStreamCreateWithPage(page)
    let table = createOperatorTable()
    let ctx = ScannerContext()
    let scanner = CGPDFScannerCreate(cs, table, Unmanaged.passUnretained(ctx).toOpaque())
    _ = CGPDFScannerScan(scanner)
    return ctx.results
}

func usage() {
    let cmd = (CommandLine.arguments.first as NSString?)?.lastPathComponent ?? "extract_wochenschrift_zeichnungen.swift"
    print("Usage: \(cmd) <input_pdf_dir> <output_dir>")
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
        let title = titleRaw.isEmpty ? rawBase : titleRaw.replacingOccurrences(of: "_", with: " ")
        return IssueMeta(year: year, issue: issue, title: title)
    }

    let genericRe = try! NSRegularExpression(pattern: #".*?(\d{4})[_-](.+)$"#, options: [])
    if let m = genericRe.firstMatch(in: base, options: [], range: NSRange(location: 0, length: ns.length)) {
        let year = ns.substring(with: m.range(at: 1))
        let rest = ns.substring(with: m.range(at: 2))
        let issue = extractIssueLabel(from: rest)
        return IssueMeta(year: year, issue: issue, title: rawBase)
    }

    return IssueMeta(year: fallbackYear, issue: extractIssueLabel(from: rawBase), title: rawBase)
}

func csvEscape(_ value: String) -> String {
    if value.contains(",") || value.contains("\n") || value.contains("\"") {
        return "\"" + value.replacingOccurrences(of: "\"", with: "\"\"") + "\""
    }
    return value
}

func issueSortKey(_ issue: String) -> Int {
    let regex = try! NSRegularExpression(pattern: #"\d+"#, options: [])
    let ns = issue as NSString
    if let m = regex.firstMatch(in: issue, options: [], range: NSRange(location: 0, length: ns.length)) {
        return Int(ns.substring(with: m.range)) ?? 9999
    }
    return 9999
}

func sanitizeFileStem(_ value: String) -> String {
    let cleaned = value.replacingOccurrences(of: #"[^A-Za-z0-9._-]+"#, with: "_", options: .regularExpression)
    return cleaned.trimmingCharacters(in: CharacterSet(charactersIn: "_"))
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

func lowerText(_ page: PDFPage?) -> String {
    return page?.string?.lowercased() ?? ""
}

func findTargetPageIndex(doc: PDFDocument) -> Int? {
    let preferred = [3, 2].filter { $0 < doc.pageCount }

    for idx in preferred {
        if lowerText(doc.page(at: idx)).contains("wort der woche") {
            return idx
        }
    }

    for idx in preferred {
        if lowerText(doc.page(at: idx)).contains("zeichnung") {
            return idx
        }
    }

    let limit = min(doc.pageCount, 8)
    for idx in 0..<limit {
        if lowerText(doc.page(at: idx)).contains("wort der woche") {
            return idx
        }
    }

    return preferred.first
}

func findHeaderBounds(page: PDFPage, phrase: String) -> CGRect? {
    guard let text = page.string else { return nil }
    let lower = text.lowercased()
    guard let r = lower.range(of: phrase.lowercased()) else { return nil }
    let ns = NSRange(r, in: lower)
    guard let sel = page.selection(for: ns) else { return nil }
    return sel.bounds(for: page)
}

func clamp(_ rect: CGRect, to bounds: CGRect) -> CGRect {
    let x = max(bounds.minX, min(rect.minX, bounds.maxX))
    let y = max(bounds.minY, min(rect.minY, bounds.maxY))
    let maxW = bounds.maxX - x
    let maxH = bounds.maxY - y
    let w = max(1, min(rect.width, maxW))
    let h = max(1, min(rect.height, maxH))
    return CGRect(x: x, y: y, width: w, height: h).integral
}

func computeVectorWindow(page: PDFPage) -> (CGRect, String) {
    let box = page.bounds(for: .mediaBox)

    if let header = findHeaderBounds(page: page, phrase: "Wort der Woche") {
        let rect = CGRect(
            x: header.minX - box.width * 0.02,
            y: header.minY - box.height * 0.27,
            width: box.width * 0.33,
            height: box.height * 0.21
        )
        return (clamp(rect, to: box), "anchor:wort-der-woche")
    }

    let fallback = CGRect(
        x: box.width * 0.04,
        y: box.height * 0.62,
        width: box.width * 0.30,
        height: box.height * 0.22
    )
    return (clamp(fallback, to: box), "fallback:fixed-left-top")
}

func rectArea(_ r: CGRect) -> Double {
    return max(0, Double(r.width * r.height))
}

func selectIconPaths(from paths: [VectorPath], window: CGRect) -> [VectorPath] {
    let wArea = rectArea(window)

    var candidates = paths.filter { p in
        p.bbox.intersects(window) && p.bbox.width > 0.5 && p.bbox.height > 0.5
    }

    candidates = candidates.filter { p in
        let b = p.bbox
        let area = rectArea(b)
        if area > wArea * 0.45 { return false }
        if b.width > window.width * 0.92 { return false }
        if b.height > window.height * 0.92 { return false }
        return true
    }

    if candidates.isEmpty {
        candidates = paths.filter { p in
            p.bbox.intersects(window) && rectArea(p.bbox) < wArea * 0.8
        }
    }

    if candidates.count > 32 {
        candidates.sort { rectArea($0.bbox) > rectArea($1.bbox) }
        candidates = Array(candidates.prefix(32))
    }

    return candidates
}

struct PathComponent {
    let paths: [VectorPath]
    let bbox: CGRect
}

func tokRegex() -> NSRegularExpression {
    return try! NSRegularExpression(
        pattern: #"(?i)(philipp\s*tok|ph\.?\s*tok|zeichnung\s*[:\-]?\s*(philipp\s*tok|ph\.?\s*tok|tok\b)|\btok\b)"#,
        options: []
    )
}

func hasTokReference(_ text: String) -> Bool {
    let ns = text as NSString
    let r = NSRange(location: 0, length: ns.length)
    return tokRegex().firstMatch(in: text, options: [], range: r) != nil
}

func tokReferencePageIndices(doc: PDFDocument) -> [Int] {
    var out: [Int] = []
    for idx in 0..<doc.pageCount {
        guard let text = doc.page(at: idx)?.string else { continue }
        if hasTokReference(text.lowercased()) {
            out.append(idx)
        }
    }
    return out
}

func expanded(_ rect: CGRect, by value: CGFloat) -> CGRect {
    return rect.insetBy(dx: -value, dy: -value)
}

func selectTokComponents(from paths: [VectorPath], pageBounds: CGRect) -> [PathComponent] {
    let pageArea = rectArea(pageBounds)
    if pageArea <= 0 { return [] }

    var filtered: [VectorPath] = []
    for p in paths {
        let b = p.bbox
        let area = rectArea(b)
        if area < pageArea * 0.00004 { continue }
        if area > pageArea * 0.22 { continue }
        if b.width < pageBounds.width * 0.01 || b.height < pageBounds.height * 0.01 { continue }
        if b.width > pageBounds.width * 0.78 || b.height > pageBounds.height * 0.78 { continue }
        filtered.append(p)
    }
    if filtered.isEmpty { return [] }

    let n = filtered.count
    let bboxes = filtered.map { $0.bbox }
    let linkPad = max(pageBounds.width, pageBounds.height) * 0.004

    var adj = Array(repeating: [Int](), count: n)
    for i in 0..<n {
        for j in (i + 1)..<n {
            if expanded(bboxes[i], by: linkPad).intersects(expanded(bboxes[j], by: linkPad)) {
                adj[i].append(j)
                adj[j].append(i)
            }
        }
    }

    var visited = Array(repeating: false, count: n)
    var components: [PathComponent] = []

    for start in 0..<n {
        if visited[start] { continue }
        var stack = [start]
        visited[start] = true
        var indices: [Int] = []

        while let cur = stack.popLast() {
            indices.append(cur)
            for nxt in adj[cur] where !visited[nxt] {
                visited[nxt] = true
                stack.append(nxt)
            }
        }

        let compPaths = indices.map { filtered[$0] }
        if compPaths.isEmpty { continue }
        guard let box = unionBBox(of: compPaths) else { continue }
        let area = rectArea(box)
        if area < pageArea * 0.00008 { continue }
        if area > pageArea * 0.16 { continue }
        if box.width < pageBounds.width * 0.02 || box.height < pageBounds.height * 0.02 { continue }
        if compPaths.count > 180 { continue }

        components.append(PathComponent(paths: compPaths, bbox: box))
    }

    components.sort { rectArea($0.bbox) > rectArea($1.bbox) }
    if components.count > 8 {
        components = Array(components.prefix(8))
    }
    return components
}

func signatureForComponent(pageIndex: Int, bbox: CGRect) -> String {
    return "\(pageIndex)-\(Int(bbox.minX.rounded()))-\(Int(bbox.minY.rounded()))-\(Int(bbox.width.rounded()))-\(Int(bbox.height.rounded()))"
}

func rightTopWindow(page: PDFPage) -> CGRect {
    let box = page.bounds(for: .mediaBox)
    let rect = CGRect(
        x: box.width * 0.53,
        y: box.height * 0.56,
        width: box.width * 0.43,
        height: box.height * 0.40
    )
    return clamp(rect, to: box)
}

func selectComponentsInWindow(from paths: [VectorPath], pageBounds: CGRect, window: CGRect) -> [PathComponent] {
    let base = selectTokComponents(from: paths, pageBounds: pageBounds)
    if base.isEmpty { return [] }

    let windowArea = rectArea(window)
    var out: [PathComponent] = []

    for comp in base {
        let inter = comp.bbox.intersection(window)
        if inter.isNull || inter.isEmpty { continue }

        let interArea = rectArea(inter)
        let compArea = rectArea(comp.bbox)
        if interArea < max(8.0, compArea * 0.08) { continue }
        if compArea > windowArea * 0.98 { continue }

        out.append(comp)
    }

    out.sort {
        let i0 = rectArea($0.bbox.intersection(window))
        let i1 = rectArea($1.bbox.intersection(window))
        if i0 != i1 { return i0 > i1 }
        return rectArea($0.bbox) > rectArea($1.bbox)
    }
    if out.count > 6 {
        out = Array(out.prefix(6))
    }
    return out
}

func selectAllPageComponents(from paths: [VectorPath], pageBounds: CGRect) -> [PathComponent] {
    let pageArea = rectArea(pageBounds)
    if pageArea <= 0 { return [] }

    var out = selectTokComponents(from: paths, pageBounds: pageBounds).filter { comp in
        let area = rectArea(comp.bbox)
        if area < pageArea * 0.00012 { return false }
        if area > pageArea * 0.045 { return false }
        return true
    }

    out.sort { rectArea($0.bbox) > rectArea($1.bbox) }
    if out.count > 6 {
        out = Array(out.prefix(6))
    }
    return out
}

func unionBBox(of paths: [VectorPath]) -> CGRect? {
    guard let first = paths.first else { return nil }
    var u = first.bbox
    for p in paths.dropFirst() {
        u = u.union(p.bbox)
    }
    return u
}

func fmt(_ v: Double) -> String {
    let s = String(format: "%.3f", v)
    var out = s
    while out.contains(".") && (out.hasSuffix("0") || out.hasSuffix(".")) {
        if out.hasSuffix("0") {
            out.removeLast()
        } else if out.hasSuffix(".") {
            out.removeLast()
            break
        }
    }
    if out.isEmpty { return "0" }
    return out
}

func svgPoint(_ p: CGPoint, minX: Double, maxY: Double) -> String {
    let x = Double(p.x) - minX
    let y = maxY - Double(p.y)
    return "\(fmt(x)) \(fmt(y))"
}

func capName(_ v: Int) -> String {
    switch v {
    case 1: return "round"
    case 2: return "square"
    default: return "butt"
    }
}

func joinName(_ v: Int) -> String {
    switch v {
    case 1: return "round"
    case 2: return "bevel"
    default: return "miter"
    }
}

func pathToSvgD(_ path: VectorPath, minX: Double, maxY: Double) -> String {
    var parts: [String] = []
    for seg in path.segments {
        switch seg {
        case .move(let p):
            parts.append("M \(svgPoint(p, minX: minX, maxY: maxY))")
        case .line(let p):
            parts.append("L \(svgPoint(p, minX: minX, maxY: maxY))")
        case .curve(let c1, let c2, let p):
            parts.append("C \(svgPoint(c1, minX: minX, maxY: maxY)) \(svgPoint(c2, minX: minX, maxY: maxY)) \(svgPoint(p, minX: minX, maxY: maxY))")
        case .close:
            parts.append("Z")
        }
    }
    return parts.joined(separator: " ")
}

func writeSVG(paths: [VectorPath], to outURL: URL) throws {
    guard let bounds = unionBBox(of: paths) else {
        throw NSError(domain: "extract", code: 1, userInfo: [NSLocalizedDescriptionKey: "no bounds"])
    }

    let pad = 4.0
    let minX = Double(bounds.minX) - pad
    let maxY = Double(bounds.maxY) + pad
    let width = Double(bounds.width) + pad * 2.0
    let height = Double(bounds.height) + pad * 2.0

    var body = ""
    for p in paths {
        let d = pathToSvgD(p, minX: minX, maxY: maxY)
        var attrs: [String] = []
        attrs.append("d=\"\(d)\"")
        if p.fill {
            attrs.append("fill=\"#000000\"")
            if p.evenOddFill {
                attrs.append("fill-rule=\"evenodd\"")
            }
        } else {
            attrs.append("fill=\"none\"")
        }
        if p.stroke {
            attrs.append("stroke=\"#000000\"")
            attrs.append("stroke-width=\"\(fmt(p.lineWidth))\"")
            attrs.append("stroke-linecap=\"\(capName(p.lineCap))\"")
            attrs.append("stroke-linejoin=\"\(joinName(p.lineJoin))\"")
            attrs.append("stroke-miterlimit=\"\(fmt(p.miterLimit))\"")
        } else {
            attrs.append("stroke=\"none\"")
        }
        body += "  <path \(attrs.joined(separator: " ")) />\n"
    }

    let svg = """
    <svg xmlns="http://www.w3.org/2000/svg" width="\(fmt(width))" height="\(fmt(height))" viewBox="0 0 \(fmt(width)) \(fmt(height))">
    \(body)</svg>
    """
    try svg.write(to: outURL, atomically: true, encoding: .utf8)
}

func shortYear(_ year: String) -> String {
    if year.count >= 2 {
        return String(year.suffix(2))
    }
    return year
}

func compactIssueLabel(_ issue: String) -> String {
    return extractIssueLabel(from: issue).replacingOccurrences(of: " ", with: "")
}

func compactRecordLabel(_ r: Record) -> String {
    return "J\(shortYear(r.year))H\(compactIssueLabel(r.issue))"
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

func generateHtml(records: [Record], title: String) -> String {
    let dateFormatter = DateFormatter()
    dateFormatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
    let generatedAt = dateFormatter.string(from: Date())

    var rows = ""
    for r in records {
        rows += """
        <tr>
          <td>\(r.year)</td>
          <td>\(r.issue)</td>
          <td>\(r.publicationDate)</td>
          <td>\(r.pageIndex + 1)</td>
          <td>\(r.title)</td>
          <td class="drawing-cell"><img src="\(r.imageRelativePath)" alt="\(r.sourceFile)" loading="lazy"></td>
          <td><code>\(r.sourceFile)</code><br><small>\(r.note)</small></td>
        </tr>
        """
    }

    return """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>\(title)</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #1f2937; }
        h1 { margin: 0 0 8px 0; font-size: 24px; }
        p.meta { margin: 0 0 20px 0; color: #6b7280; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #e5e7eb; padding: 12px; vertical-align: top; }
        th { background: #f9fafb; text-align: left; }
        td.drawing-cell { min-width: 280px; }
        img { width: 220px; height: auto; display: block; background: #fff; border: 1px solid #e5e7eb; padding: 16px; }
        code { font-size: 12px; }
        small { color: #6b7280; }
      </style>
    </head>
    <body>
      <h1>\(title)</h1>
      <p class="meta">Erzeugt am \(generatedAt) · Treffer: \(records.count)</p>
      <table>
        <thead>
          <tr>
            <th>Jahr</th>
            <th>Heft</th>
            <th>Erscheinung</th>
            <th>Seite</th>
            <th>Titel</th>
            <th>Zeichnung (SVG)</th>
            <th>Quelle</th>
          </tr>
        </thead>
        <tbody>
          \(rows)
        </tbody>
      </table>
    </body>
    </html>
    """
}

func generateYearOverviewHtml(year: String, records: [Record]) -> String {
    let dateFormatter = DateFormatter()
    dateFormatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
    let generatedAt = dateFormatter.string(from: Date())

    var cards = ""
    var seen: [String: Int] = [:]
    for r in records {
        let key = "\(r.year)|\(compactIssueLabel(r.issue))"
        let occ = seen[key, default: 0]
        seen[key] = occ + 1
        let tiny = compactRecordLabel(r) + occurrenceSuffix(occ)
        cards += """
        <article class="card">
          <img src="\(r.imageRelativePath)" alt="\(r.sourceFile)" loading="lazy">
          <div class="tiny">\(tiny)</div>
        </article>
        """
    }

    return """
    <!doctype html>
    <html lang="de">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Jahresübersicht \(year)</title>
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 28px; color: #1f2937; }
        h1 { margin: 0 0 8px 0; font-size: 24px; }
        p.meta { margin: 0 0 22px 0; color: #6b7280; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 18px; }
        .card { border: 1px solid #e5e7eb; background: #fff; padding: 12px 12px 10px; }
        .card img { width: 100%; height: 140px; object-fit: contain; display: block; background: #fff; }
        .tiny { margin-top: 8px; font-size: 11px; color: #6b7280; letter-spacing: 0.02em; }
      </style>
    </head>
    <body>
      <h1>Jahresübersicht \(year)</h1>
      <p class="meta">Erzeugt am \(generatedAt) · Zeichnungen: \(records.count)</p>
      <section class="grid">
        \(cards)
      </section>
    </body>
    </html>
    """
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    usage()
    exit(1)
}

let inputDir = URL(fileURLWithPath: args[1], isDirectory: true)
let outputDir = URL(fileURLWithPath: args[2], isDirectory: true)
let imagesDir = outputDir.appendingPathComponent("images", isDirectory: true)
let extraTokScan = ProcessInfo.processInfo.environment["EXTRA_TOK_SCAN"] == "1"
let extraPage3RightScan = ProcessInfo.processInfo.environment["EXTRA_PAGE3_RIGHT_SCAN"] == "1"
let extraAllPagesScan = ProcessInfo.processInfo.environment["EXTRA_ALL_PAGES_SCAN"] == "1"

let fm = FileManager.default
try fm.createDirectory(at: outputDir, withIntermediateDirectories: true)
try fm.createDirectory(at: imagesDir, withIntermediateDirectories: true)

let fallbackYear = inputDir.lastPathComponent
let pdfFiles = try fm.contentsOfDirectory(at: inputDir, includingPropertiesForKeys: nil)
    .filter { $0.pathExtension.lowercased() == "pdf" }
    .sorted { $0.lastPathComponent.localizedStandardCompare($1.lastPathComponent) == .orderedAscending }

var records: [Record] = []
var failures: [String] = []

for fileURL in pdfFiles {
    autoreleasepool {
        let fileName = fileURL.lastPathComponent
        let meta = parseMeta(from: fileName, fallbackYear: fallbackYear)

        guard let doc = PDFDocument(url: fileURL) else {
            failures.append("OPEN_FAIL: \(fileName)")
            return
        }

        guard let cgDoc = CGPDFDocument(fileURL as CFURL) else {
            failures.append("CGPDF_OPEN_FAIL: \(fileName)")
            return
        }

        let stem = sanitizeFileStem((fileName as NSString).deletingPathExtension)
        let publicationDate = findDate(in: doc)
        var seenComponents: Set<String> = []
        var mainPageIndex: Int? = nil

        if let pageIndex = findTargetPageIndex(doc: doc),
           let pdfKitPage = doc.page(at: pageIndex),
           let cgPage = cgDoc.page(at: pageIndex + 1) {
            mainPageIndex = pageIndex

            let allPaths = extractPaintedPaths(page: cgPage)
            if allPaths.isEmpty {
                failures.append("NO_PATHS: \(fileName)")
            } else {
                let (window, anchorNote) = computeVectorWindow(page: pdfKitPage)
                let iconPaths = selectIconPaths(from: allPaths, window: window)

                if iconPaths.isEmpty {
                    failures.append("NO_ICON_PATHS: \(fileName)")
                } else {
                    do {
                        let imageName = "\(stem)_zeichnung.svg"
                        let imageURL = imagesDir.appendingPathComponent(imageName)
                        try writeSVG(paths: iconPaths, to: imageURL)

                        if let b = unionBBox(of: iconPaths) {
                            seenComponents.insert(signatureForComponent(pageIndex: pageIndex, bbox: b))
                        }

                        records.append(Record(
                            entryId: "\(stem)-p\(pageIndex + 1)-main",
                            sourceFile: fileName,
                            year: meta.year,
                            issue: meta.issue,
                            title: meta.title,
                            publicationDate: publicationDate,
                            pageIndex: pageIndex,
                            imageRelativePath: "images/\(imageName)",
                            note: "\(anchorNote);paths=\(iconPaths.count)"
                        ))
                    } catch {
                        failures.append("SVG_WRITE_FAIL: \(fileName): \(error.localizedDescription)")
                    }
                }
            }
        } else {
            failures.append("PAGE_NOT_FOUND: \(fileName)")
        }

        if extraPage3RightScan && doc.pageCount > 2 {
            let p3 = 2
            if let p3PdfPage = doc.page(at: p3), let p3CgPage = cgDoc.page(at: p3 + 1) {
                let p3Paths = extractPaintedPaths(page: p3CgPage)
                let p3Window = rightTopWindow(page: p3PdfPage)
                let p3Comps = selectComponentsInWindow(from: p3Paths, pageBounds: p3PdfPage.bounds(for: .mediaBox), window: p3Window)

                var localIdx = 0
                for comp in p3Comps {
                    let sig = signatureForComponent(pageIndex: p3, bbox: comp.bbox)
                    if seenComponents.contains(sig) { continue }
                    seenComponents.insert(sig)

                    localIdx += 1
                    let imageName = "\(stem)_p\(p3 + 1)_rt_\(localIdx).svg"
                    let imageURL = imagesDir.appendingPathComponent(imageName)

                    do {
                        try writeSVG(paths: comp.paths, to: imageURL)
                        records.append(Record(
                            entryId: "\(stem)-p\(p3 + 1)-rt\(localIdx)",
                            sourceFile: fileName,
                            year: meta.year,
                            issue: meta.issue,
                            title: meta.title,
                            publicationDate: publicationDate,
                            pageIndex: p3,
                            imageRelativePath: "images/\(imageName)",
                            note: "page3-right-top;paths=\(comp.paths.count)"
                        ))
                    } catch {
                        failures.append("P3_RIGHT_SVG_WRITE_FAIL: \(fileName):p\(p3 + 1):\(error.localizedDescription)")
                    }
                }
            }
        }

        if extraTokScan {
            let tokPages = tokReferencePageIndices(doc: doc)

            for tokPageIndex in tokPages {
                if let mainPageIndex, tokPageIndex == mainPageIndex { continue }
                guard let tokPdfPage = doc.page(at: tokPageIndex),
                      let tokCgPage = cgDoc.page(at: tokPageIndex + 1) else { continue }

                let tokPaths = extractPaintedPaths(page: tokCgPage)
                if tokPaths.isEmpty { continue }

                let components = selectTokComponents(from: tokPaths, pageBounds: tokPdfPage.bounds(for: .mediaBox))
                if components.isEmpty { continue }

                var localIdx = 0
                for comp in components {
                    let sig = signatureForComponent(pageIndex: tokPageIndex, bbox: comp.bbox)
                    if seenComponents.contains(sig) { continue }
                    seenComponents.insert(sig)

                    localIdx += 1
                    let imageName = "\(stem)_p\(tokPageIndex + 1)_tok_\(localIdx).svg"
                    let imageURL = imagesDir.appendingPathComponent(imageName)

                    do {
                        try writeSVG(paths: comp.paths, to: imageURL)
                        records.append(Record(
                            entryId: "\(stem)-p\(tokPageIndex + 1)-tok\(localIdx)",
                            sourceFile: fileName,
                            year: meta.year,
                            issue: meta.issue,
                            title: meta.title,
                            publicationDate: publicationDate,
                            pageIndex: tokPageIndex,
                            imageRelativePath: "images/\(imageName)",
                            note: "tok-scan;paths=\(comp.paths.count)"
                        ))
                    } catch {
                        failures.append("TOK_SVG_WRITE_FAIL: \(fileName):p\(tokPageIndex + 1):\(error.localizedDescription)")
                    }
                }
            }
        }

        if extraAllPagesScan {
            for scanPageIndex in 0..<doc.pageCount {
                guard let scanPdfPage = doc.page(at: scanPageIndex),
                      let scanCgPage = cgDoc.page(at: scanPageIndex + 1) else { continue }

                let scanPaths = extractPaintedPaths(page: scanCgPage)
                if scanPaths.isEmpty { continue }

                let comps = selectAllPageComponents(from: scanPaths, pageBounds: scanPdfPage.bounds(for: .mediaBox))
                if comps.isEmpty { continue }

                var localIdx = 0
                for comp in comps {
                    let sig = signatureForComponent(pageIndex: scanPageIndex, bbox: comp.bbox)
                    if seenComponents.contains(sig) { continue }
                    seenComponents.insert(sig)

                    localIdx += 1
                    let imageName = "\(stem)_p\(scanPageIndex + 1)_all_\(localIdx).svg"
                    let imageURL = imagesDir.appendingPathComponent(imageName)

                    do {
                        try writeSVG(paths: comp.paths, to: imageURL)
                        records.append(Record(
                            entryId: "\(stem)-p\(scanPageIndex + 1)-all\(localIdx)",
                            sourceFile: fileName,
                            year: meta.year,
                            issue: meta.issue,
                            title: meta.title,
                            publicationDate: publicationDate,
                            pageIndex: scanPageIndex,
                            imageRelativePath: "images/\(imageName)",
                            note: "all-pages-scan;paths=\(comp.paths.count)"
                        ))
                    } catch {
                        failures.append("ALL_SCAN_SVG_WRITE_FAIL: \(fileName):p\(scanPageIndex + 1):\(error.localizedDescription)")
                    }
                }
            }
        }
    }
}

records.sort {
    if $0.year != $1.year { return $0.year < $1.year }
    let k0 = issueSortKey($0.issue)
    let k1 = issueSortKey($1.issue)
    if k0 != k1 { return k0 < k1 }
    return $0.issue < $1.issue
}

let reportTitle = "Verzeichnis Zeichnungen (SVG, \(fallbackYear))"
let html = generateHtml(records: records, title: reportTitle)
try html.write(to: outputDir.appendingPathComponent("index.html"), atomically: true, encoding: .utf8)

let groupedByYear = Dictionary(grouping: records, by: { $0.year })
for year in groupedByYear.keys.sorted() {
    var yearRecords = groupedByYear[year] ?? []
    yearRecords.sort {
        let k0 = issueSortKey($0.issue)
        let k1 = issueSortKey($1.issue)
        if k0 != k1 { return k0 < k1 }
        return $0.issue < $1.issue
    }
    let yearHtml = generateYearOverviewHtml(year: year, records: yearRecords)
    let outName = "jahr_\(year)_uebersicht.html"
    try yearHtml.write(to: outputDir.appendingPathComponent(outName), atomically: true, encoding: .utf8)
}

var csv = "jahr,heft,erscheinung,seite,titel,datei,svg,hinweis,id,status\n"
for r in records {
    csv += [r.year, r.issue, r.publicationDate, String(r.pageIndex + 1), r.title, r.sourceFile, r.imageRelativePath, r.note, r.entryId, "keep"].map(csvEscape).joined(separator: ",") + "\n"
}
try csv.write(to: outputDir.appendingPathComponent("verzeichnis.csv"), atomically: true, encoding: .utf8)

if !failures.isEmpty {
    let failText = failures.joined(separator: "\n") + "\n"
    try failText.write(to: outputDir.appendingPathComponent("failures.log"), atomically: true, encoding: .utf8)
}

print("PDF files: \(pdfFiles.count)")
print("Records (SVG): \(records.count)")
print("Output: \(outputDir.path)")
if !failures.isEmpty {
    print("Failures: \(failures.count) (see failures.log)")
}
