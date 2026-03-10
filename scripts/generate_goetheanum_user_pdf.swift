#!/usr/bin/env swift

import AppKit
import CoreText
import Foundation

struct RowMap: Decodable {
    let keycode: Int
    let lower_key: String
    let upper_key: String
    let codepoint: String
    let glyph: String
    let upper_codepoint: String
    let upper_glyph: String
    let label: String
}

struct MappingJSON: Decodable {
    let version: String
    let rows: [RowMap]
}

struct KeyRow {
    let offset: CGFloat
    let keys: [Int]
    let lower: [String]
    let upper: [String]
}

let keyboardRows: [KeyRow] = [
    KeyRow(offset: 0, keys: [18, 19, 20, 21, 23, 22, 26, 28, 25, 29, 27, 24], lower: ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "ß", "´"], upper: ["!", "\"", "§", "$", "%", "&", "/", "(", ")", "=", "?", "`"]),
    KeyRow(offset: 12, keys: [12, 13, 14, 15, 17, 16, 32, 34, 31, 35, 33, 30], lower: ["q", "w", "e", "r", "t", "z", "u", "i", "o", "p", "ü", "+"], upper: ["Q", "W", "E", "R", "T", "Z", "U", "I", "O", "P", "Ü", "*"]),
    KeyRow(offset: 24, keys: [0, 1, 2, 3, 5, 4, 38, 40, 37, 39, 41, 42], lower: ["a", "s", "d", "f", "g", "h", "j", "k", "l", "ö", "ä", "#"], upper: ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ö", "Ä", "'"]),
    KeyRow(offset: 36, keys: [10, 6, 7, 8, 9, 11, 45, 46, 43, 47, 44], lower: ["<", "y", "x", "c", "v", "b", "n", "m", ",", ".", "-"], upper: [">", "Y", "X", "C", "V", "B", "N", "M", ";", ":", "_"]),
]

enum KeyboardLayer {
    case upper
    case lower
    case option
}

let optionLayerCodepoints: [Int: UInt32] = [
    19: 0xE260, 12: 0xE263, 14: 0xE261, 1: 0xE262,
    22: 0xE264, 17: 0xE267, 32: 0xE265, 4: 0xE266,
    29: 0xE26C, 31: 0xE26F, 33: 0xE26D, 39: 0xE26E,
    6: 0xE203, 7: 0xE204, 8: 0xE205, 9: 0xE206,
]

struct Fonts {
    let leise: NSFont
    let klar: NSFont
    let laut: NSFont
    let variabel: NSFont
    let icons: NSFont
}

var currentPageHeight: CGFloat = 0

enum IconGroup {
    case logos
    case rules
    case orientation
    case places
    case wc
    case waste
    case free
}

func parseCodepoint(_ token: String) -> UInt32? {
    let cleaned = token.uppercased().replacingOccurrences(of: "U+", with: "")
    return UInt32(cleaned, radix: 16)
}

func iconGroup(for item: RowMap) -> IconGroup {
    if item.label.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        return .free
    }
    guard let cp = parseCodepoint(item.codepoint) else {
        return .free
    }
    switch cp {
    case 0xE100, 0xE101, 0xE102:
        return .logos
    case 0xE20A, 0xE20F, 0xE20E, 0xE210, 0xE207, 0xE216, 0xE208, 0xE215:
        return .rules
    case 0xE202, 0xE201, 0xE200, 0xE204, 0xE205, 0xE206, 0xE203:
        return .orientation
    case 0xE20B, 0xE214, 0xE20C, 0xE209, 0xE21E, 0xE211, 0xE217:
        return .places
    case 0xE218, 0xE21A, 0xE219, 0xE21B, 0xE21C, 0xE21D:
        return .wc
    case 0xE20D, 0xE212, 0xE213:
        return .waste
    default:
        return .free
    }
}

func groupStrokeColor(_ group: IconGroup) -> NSColor {
    _ = group
    return NSColor(calibratedWhite: 0.78, alpha: 1)
}

func groupFillColor(_ group: IconGroup) -> NSColor {
    _ = group
    return NSColor.white
}

func toCGRect(_ rect: CGRect) -> CGRect {
    CGRect(x: rect.origin.x, y: currentPageHeight - rect.origin.y - rect.size.height, width: rect.size.width, height: rect.size.height)
}

func toCGY(_ y: CGFloat) -> CGFloat {
    currentPageHeight - y
}

func registerFont(at path: String) -> NSFont? {
    let url = URL(fileURLWithPath: path)
    var error: Unmanaged<CFError>?
    CTFontManagerRegisterFontsForURL(url as CFURL, .process, &error)

    guard
        let provider = CGDataProvider(url: url as CFURL),
        let cgFont = CGFont(provider),
        let psName = cgFont.postScriptName as String?
    else {
        return nil
    }
    return NSFont(name: psName, size: 12)
}

func nsFont(_ base: NSFont, _ size: CGFloat) -> NSFont {
    NSFont(name: base.fontName, size: size) ?? base
}

func attrs(_ font: NSFont, _ color: NSColor) -> [NSAttributedString.Key: Any] {
    [.font: font, .foregroundColor: color]
}

func variableWeightRange(_ font: NSFont) -> (NSNumber, CGFloat, CGFloat)? {
    let ct = font as CTFont
    guard let axes = CTFontCopyVariationAxes(ct) as? [[CFString: Any]] else {
        return nil
    }
    for axis in axes {
        guard
            let identifier = axis[kCTFontVariationAxisIdentifierKey] as? NSNumber,
            let minValue = axis[kCTFontVariationAxisMinimumValueKey] as? NSNumber,
            let maxValue = axis[kCTFontVariationAxisMaximumValueKey] as? NSNumber
        else {
            continue
        }
        return (identifier, CGFloat(minValue.doubleValue), CGFloat(maxValue.doubleValue))
    }
    return nil
}

func variableFont(_ font: NSFont, _ size: CGFloat, _ axisIdentifier: NSNumber, _ weight: CGFloat) -> NSFont {
    let vars: [NSNumber: NSNumber] = [axisIdentifier: NSNumber(value: Double(weight))]
    let descriptor = font.fontDescriptor.addingAttributes(
        [NSFontDescriptor.AttributeName(rawValue: kCTFontVariationAttribute as String): vars]
    )
    return NSFont(descriptor: descriptor, size: size) ?? nsFont(font, size)
}

func drawText(_ text: String, in rect: CGRect, _ at: [NSAttributedString.Key: Any], _ align: NSTextAlignment = .left, lineSpacing: CGFloat = 0, clipToRect: Bool = false) {
    let p = NSMutableParagraphStyle()
    p.alignment = align
    p.lineSpacing = lineSpacing
    var aa = at
    aa[.paragraphStyle] = p
    if clipToRect, let cg = NSGraphicsContext.current?.cgContext {
        cg.saveGState()
        cg.addRect(toCGRect(rect))
        cg.clip()
        (text as NSString).draw(in: toCGRect(rect), withAttributes: aa)
        cg.restoreGState()
        return
    }
    (text as NSString).draw(in: toCGRect(rect), withAttributes: aa)
}

func drawTextVerticallyCentered(_ text: String, in rect: CGRect, _ at: [NSAttributedString.Key: Any], _ align: NSTextAlignment = .center, yOffset: CGFloat = 0, clipToRect: Bool = false) {
    let b = (text as NSString).boundingRect(
        with: NSSize(width: rect.width, height: .greatestFiniteMagnitude),
        options: [.usesLineFragmentOrigin, .usesFontLeading],
        attributes: at
    )
    let h = max(1, ceil(b.height))
    let y = rect.minY + max(0, (rect.height - h) * 0.5) + yOffset
    drawText(text, in: CGRect(x: rect.minX, y: y, width: rect.width, height: h + 1), at, align, clipToRect: clipToRect)
}

func roundedRect(_ rect: CGRect, radius: CGFloat, stroke: NSColor, fill: NSColor = .white, width: CGFloat = 1.0) {
    let path = NSBezierPath(roundedRect: toCGRect(rect), xRadius: radius, yRadius: radius)
    fill.setFill()
    path.fill()
    stroke.setStroke()
    path.lineWidth = width
    path.stroke()
}

func parseMapping(path: String) throws -> [Int: RowMap] {
    let data = try Data(contentsOf: URL(fileURLWithPath: path))
    let decoded = try JSONDecoder().decode(MappingJSON.self, from: data)
    var out: [Int: RowMap] = [:]
    for row in decoded.rows {
        out[row.keycode] = row
    }
    return out
}

func beginPage(_ ctx: CGContext, _ width: CGFloat, _ height: CGFloat) {
    let box = CGRect(x: 0, y: 0, width: width, height: height)
    let pageInfo: [CFString: Any] = [kCGPDFContextMediaBox: box]
    ctx.beginPDFPage(pageInfo as CFDictionary)
    currentPageHeight = height
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = ns
    NSColor.white.setFill()
    NSBezierPath(rect: CGRect(x: 0, y: 0, width: width, height: height)).fill()
}

func endPage(_ ctx: CGContext) {
    NSGraphicsContext.restoreGraphicsState()
    ctx.endPDFPage()
}

func drawIntroPage(_ pageW: CGFloat, _ pageH: CGFloat, _ fonts: Fonts, _ version: String, _ today: String) {
    let cMain = NSColor(calibratedWhite: 0.08, alpha: 1)
    let cSub = NSColor(calibratedWhite: 0.42, alpha: 1)
    let cHint = cSub
    let cRule = NSColor(calibratedWhite: 0.86, alpha: 1)
    let margin: CGFloat = 43 // ~1.5cm
    let colGap: CGFloat = 16

    let titleY: CGFloat = margin
    drawText("Goetheanum Schriften", in: CGRect(x: margin, y: titleY, width: pageW - margin * 2, height: 36), attrs(nsFont(fonts.laut, 28), cMain))

    let leftX = margin
    let leftW: CGFloat = 500
    let rightX = leftX + leftW + colGap
    let rightW = pageW - margin - rightX

    let contentTop: CGFloat = 96
    let textBoxH: CGFloat = 102
    let textGap: CGFloat = 12
    let sampleSize: CGFloat = 22

    let textRows: [(String, String, NSFont, String)] = [
        ("Goetheanum Laut", "‹Goetheanum Programm Heute›", nsFont(fonts.laut, sampleSize), "Für Titel, Wegleitung, Signaletik und Hervorhebungen."),
        ("Goetheanum Klar", "‹Goetheanum Kommunikation im Alltag›", nsFont(fonts.klar, sampleSize), "Standard für Korrespondenz, Formulare, Dokumente und Lauftext."),
        ("Goetheanum Leise", "‹Goetheanum Kultur und Dialog›", nsFont(fonts.leise, sampleSize), "Als Gegenstimme und Rhythmusgeber für Titel, nicht für Fließtext-Mengen."),
    ]

    var y = contentTop
    for row in textRows {
        roundedRect(CGRect(x: leftX, y: y, width: leftW, height: textBoxH), radius: 8, stroke: cRule)
        drawText(row.0, in: CGRect(x: leftX + 12, y: y + 10, width: leftW - 24, height: 18), attrs(nsFont(fonts.klar, 13), cMain))
        drawText(row.1, in: CGRect(x: leftX + 12, y: y + 38, width: leftW - 24, height: 30), attrs(row.2, cMain))
        drawText(row.3, in: CGRect(x: leftX + 12, y: y + 77, width: leftW - 24, height: 18), attrs(nsFont(fonts.klar, 12), cSub))
        y += textBoxH + textGap
    }

    let iconsBoxH: CGFloat = 190
    roundedRect(CGRect(x: rightX, y: contentTop, width: rightW, height: iconsBoxH), radius: 8, stroke: cRule)
    drawText("Goetheanum Icons", in: CGRect(x: rightX + 12, y: contentTop + 10, width: rightW - 24, height: 18), attrs(nsFont(fonts.klar, 13), cMain))

    let previewIcons = [
        "\u{E20A}", "\u{E20F}", "\u{E20E}",
        "\u{E210}", "\u{E208}", "\u{E215}",
        "\u{E209}", "\u{E20B}", "\u{E202}",
    ]
    let gridX = rightX + 14
    let gridY = contentTop + 44
    let gridW = rightW - 28
    let colW = gridW / 3
    let rowH: CGFloat = 38
    for r in 0..<3 {
        for c in 0..<3 {
            let idx = r * 3 + c
            let icon = previewIcons[idx]
            let rect = CGRect(
                x: gridX + CGFloat(c) * colW,
                y: gridY + CGFloat(r) * rowH,
                width: colW,
                height: rowH
            )
            drawText(icon, in: rect, attrs(nsFont(fonts.icons, 28), cMain), .center)
        }
    }
    drawText(
        "Enthält Piktogramme und Logos.\nSiehe Tastatur-Belegung auf Seite 2, 3 und 4.",
        in: CGRect(x: rightX + 12, y: contentTop + 152, width: rightW - 24, height: 32),
        attrs(nsFont(fonts.klar, 12), cHint),
        .left,
        lineSpacing: 1.2
    )

    let varY = contentTop + iconsBoxH + textGap
    let varH: CGFloat = 128
    roundedRect(CGRect(x: rightX, y: varY, width: rightW, height: varH), radius: 8, stroke: cRule)
    drawText("Goetheanum Variabel", in: CGRect(x: rightX + 12, y: varY + 10, width: rightW - 24, height: 18), attrs(nsFont(fonts.klar, 13), cMain))
    let sampleVarText = "‹Goetheanum flexibel›"
    if let (axis, minWeight, maxWeight) = variableWeightRange(fonts.variabel) {
        let thin = variableFont(fonts.variabel, 20, axis, minWeight)
        let thick = variableFont(fonts.variabel, 20, axis, maxWeight)
        drawText(sampleVarText, in: CGRect(x: rightX + 12, y: varY + 38, width: rightW - 24, height: 22), attrs(thin, cMain))
        drawText(sampleVarText, in: CGRect(x: rightX + 12, y: varY + 66, width: rightW - 24, height: 22), attrs(thick, cMain))
    } else {
        drawText(sampleVarText, in: CGRect(x: rightX + 12, y: varY + 38, width: rightW - 24, height: 22), attrs(nsFont(fonts.klar, 20), cMain))
        drawText(sampleVarText, in: CGRect(x: rightX + 12, y: varY + 66, width: rightW - 24, height: 22), attrs(nsFont(fonts.laut, 20), cMain))
    }
    drawText("Nur für Profis geeignet.", in: CGRect(x: rightX + 12, y: varY + 102, width: rightW - 24, height: 16), attrs(nsFont(fonts.klar, 12), cSub))

    let footerTextH: CGFloat = 46
    let footerLineY = pageH - margin - footerTextH - 10
    let lineRect = CGRect(x: margin, y: footerLineY, width: pageW - margin * 2, height: 1)
    NSColor(calibratedWhite: 0.88, alpha: 1).setFill()
    NSBezierPath(rect: toCGRect(lineRect)).fill()

    let footerLines = [
        "Goetheanum Schriften Version \(version).",
        "Erstellt am \(today) durch die Goetheanum Kommunikation, basierend auf der Schrift Titillium aus Urbino.",
        "Piktogramme und Icons u.a. von Severin Geißler und Philipp Tok.",
    ]
    var fy = footerLineY + 11
    for line in footerLines {
        drawText(line, in: CGRect(x: margin, y: fy, width: pageW - margin * 2, height: 14), attrs(nsFont(fonts.klar, 11), cSub))
        fy += 14
    }
}

func iconPreviewSize(_ scalar: UInt32, _ upper: Bool) -> CGFloat {
    if scalar == 0xE100 || scalar == 0xE140 { return upper ? 5.8 : 6.6 } // Goetheanum-Logo (mit Wortmarke)
    if upper {
        if scalar >= 0xE240 && scalar <= 0xE25F { return 58.0 }
        if scalar >= 0xE140 && scalar <= 0xE143 { return 44.0 }
        if scalar >= 0xE100 && scalar <= 0xE13F { return 44.0 }
        return 44.0
    }
    if scalar >= 0xE100 && scalar <= 0xE103 { return 24.0 }
    return 28.0
}

func fitFontSize(_ text: String, _ base: NSFont, min: CGFloat, max: CGFloat, width: CGFloat, height: CGFloat) -> CGFloat {
    var size = max
    while size >= min {
        let f = nsFont(base, size)
        let b = (text as NSString).boundingRect(
            with: NSSize(width: width, height: .greatestFiniteMagnitude),
            options: [.usesLineFragmentOrigin, .usesFontLeading],
            attributes: [.font: f]
        )
        if ceil(b.width) <= width && ceil(b.height) <= height {
            return size
        }
        size -= 0.5
    }
    return min
}

func drawGlyphFitted(
    _ glyph: String,
    in rect: CGRect,
    baseFont: NSFont,
    color: NSColor,
    minSize: CGFloat,
    maxSize: CGFloat,
    hPad: CGFloat = 2,
    vPad: CGFloat = 2,
    yNudge: CGFloat = 0,
    clipToRect: Bool = false
) {
    let innerW = max(1, rect.width - hPad * 2)
    let innerH = max(1, rect.height - vPad * 2)
    let size = fitFontSize(glyph, baseFont, min: minSize, max: maxSize, width: innerW, height: innerH)
    let font = nsFont(baseFont, size)
    let at = attrs(font, color)
    let b = (glyph as NSString).boundingRect(
        with: NSSize(width: innerW, height: .greatestFiniteMagnitude),
        options: [.usesLineFragmentOrigin, .usesFontLeading],
        attributes: at
    )
    let h = max(1, ceil(b.height))
    let y = rect.minY + vPad + max(0, (innerH - h) * 0.5) + yNudge
    drawText(
        glyph,
        in: CGRect(x: rect.minX + hPad, y: y, width: innerW, height: h + 1),
        at,
        .center,
        clipToRect: clipToRect
    )
}

func drawGlyphPathFitted(
    _ glyph: String,
    in rect: CGRect,
    baseFont: NSFont,
    color: NSColor,
    hPad: CGFloat = 2,
    vPad: CGFloat = 2,
    yNudge: CGFloat = 0
) -> Bool {
    guard
        let scalar = glyph.unicodeScalars.first,
        glyph.unicodeScalars.count == 1,
        let cg = NSGraphicsContext.current?.cgContext
    else {
        return false
    }

    let ctFont = CTFontCreateWithName(baseFont.fontName as CFString, 1000, nil)
    var ch = UniChar(scalar.value)
    var cgGlyph: CGGlyph = 0
    guard CTFontGetGlyphsForCharacters(ctFont, &ch, &cgGlyph, 1) else {
        return false
    }
    guard let path = CTFontCreatePathForGlyph(ctFont, cgGlyph, nil) else {
        return false
    }
    let bounds = path.boundingBoxOfPath
    if bounds.width <= 0 || bounds.height <= 0 {
        return false
    }

    let inner = CGRect(
        x: rect.minX + hPad,
        y: rect.minY + vPad + yNudge,
        width: max(1, rect.width - hPad * 2),
        height: max(1, rect.height - vPad * 2)
    )
    let target = toCGRect(inner)
    let sx = target.width / bounds.width
    let sy = target.height / bounds.height
    let scale = max(0.0001, min(sx, sy))

    cg.saveGState()
    cg.translateBy(x: target.midX, y: target.midY)
    cg.scaleBy(x: scale, y: scale)
    cg.translateBy(x: -bounds.midX, y: -bounds.midY)
    cg.addPath(path)
    cg.setFillColor(color.cgColor)
    cg.fillPath()
    cg.restoreGState()
    return true
}

func normalizedIconScalar(_ scalar: UInt32) -> UInt32 {
    if scalar >= 0xE240 && scalar <= 0xE25E { return scalar - 0x40 }
    return scalar
}

func keyScale(_ scalar: UInt32, _ isPlaceholder: Bool, _ layer: KeyboardLayer) -> CGFloat {
    if isPlaceholder { return 0.30 }
    let cp = normalizedIconScalar(scalar)
    if layer == .option {
        if cp >= 0xE203 && cp <= 0xE206 { return 0.90 } // Kompass etwas kleiner
        return 0.98
    }
    switch cp {
    case 0xE100, 0xE140:
        return 0.64 // Wortmarke
    case 0xE101, 0xE102:
        return 0.78 // Punkt/Square
    case 0xE20B, 0xE214:
        return 0.82 // Fahrstuhl/Treppe (schwarzlastig)
    case 0xE212, 0xE213, 0xE20D:
        return 0.86 // Müll
    case 0xE21A, 0xE219, 0xE21C, 0xE218, 0xE21B, 0xE211:
        return 0.92 // WC/Nursing
    case 0xE21E, 0xE209:
        return 0.86 // WLAN/Eintritt
    default:
        return 0.96
    }
}

func drawKeyboardPage(_ pageW: CGFloat, _ pageH: CGFloat, _ fonts: Fonts, _ mapping: [Int: RowMap], _ layer: KeyboardLayer) {
    let cMain = NSColor(calibratedWhite: 0.08, alpha: 1)
    let cSub = NSColor(calibratedWhite: 0.44, alpha: 1)
    let margin: CGFloat = 43

    let upper = (layer == .upper)
    let isOption = (layer == .option)
    let leadTitle: String
    let tailTitle: String
    if isOption {
        leadTitle = "Goetheanum Icons Pfeile und Kompass "
        tailTitle = "Option/Alt"
    } else {
        leadTitle = upper ? "Goetheanum Icons mit Text " : "Goetheanum Icons ohne Text "
        tailTitle = upper ? "Großbuchstaben" : "Kleinbuchstaben"
    }
    let leadFont = nsFont(fonts.laut, 26)
    let tailFont = nsFont(fonts.leise, 26)
    let leadWidth = ceil((leadTitle as NSString).size(withAttributes: [.font: leadFont]).width)
    let tailWidth = ceil((tailTitle as NSString).size(withAttributes: [.font: tailFont]).width)
    let titleGap: CGFloat = 3
    let titleStartX = (pageW - (leadWidth + titleGap + tailWidth)) * 0.5
    drawText(leadTitle, in: CGRect(x: titleStartX, y: margin, width: leadWidth, height: 36), attrs(leadFont, cMain))
    drawText(tailTitle, in: CGRect(x: titleStartX + leadWidth + titleGap, y: margin, width: tailWidth, height: 36), attrs(tailFont, cSub))

    let left: CGFloat = margin
    let top: CGFloat = 92
    let keyW: CGFloat = 60
    let keyH: CGFloat = 68
    let gapX: CGFloat = 4
    let gapY: CGFloat = 10

    for (rowIndex, row) in keyboardRows.enumerated() {
        let labels = upper ? row.upper : row.lower
        let x0 = left + row.offset * 0.56
        let y0 = top + CGFloat(rowIndex) * (keyH + gapY)
        for (idx, keycode) in row.keys.enumerated() {
            let x = x0 + CGFloat(idx) * (keyW + gapX)
            let rect = CGRect(x: x, y: y0, width: keyW, height: keyH)
            let group: IconGroup = isOption ? (optionLayerCodepoints[keycode] != nil ? .orientation : .free) : (mapping[keycode].map(iconGroup) ?? .free)
            roundedRect(rect, radius: 4, stroke: groupStrokeColor(group), fill: groupFillColor(group))

            let keyLabel = isOption ? "opt+\(row.lower[idx])" : labels[idx]
            let keySize: CGFloat = isOption ? 7 : 9
            drawText(keyLabel, in: CGRect(x: x + 4, y: y0 + 4, width: keyW - 8, height: 11), attrs(nsFont(fonts.klar, keySize), cMain))

            let iconRect = CGRect(x: x + 3, y: y0 + 16, width: keyW - 6, height: keyH - 23)
            if isOption {
                if let cp = optionLayerCodepoints[keycode], let scalar = UnicodeScalar(cp) {
                    let displayGlyph = String(scalar)
                    let scale = keyScale(cp, false, .option)
                    let scaledHPad = 2 + (iconRect.width * (1 - scale) * 0.5)
                    let scaledVPad = 2 + (iconRect.height * (1 - scale) * 0.5)
                    let drewPath = drawGlyphPathFitted(displayGlyph, in: iconRect, baseFont: fonts.icons, color: cMain, hPad: scaledHPad, vPad: scaledVPad, yNudge: 0)
                    if !drewPath {
                        drawGlyphFitted(displayGlyph, in: iconRect, baseFont: fonts.icons, color: cMain, minSize: 7.0, maxSize: 16.0, hPad: 1, vPad: 1, yNudge: 0, clipToRect: false)
                    }
                } else {
                    drawGlyphFitted("\u{E101}", in: iconRect, baseFont: fonts.icons, color: NSColor(calibratedWhite: 0.56, alpha: 1), minSize: 6.0, maxSize: 10.0, hPad: 1, vPad: 1, yNudge: 0, clipToRect: false)
                }
            } else if let item = mapping[keycode] {
                let displayGlyph = upper && !item.upper_glyph.isEmpty ? item.upper_glyph : item.glyph
                let scalar = displayGlyph.unicodeScalars.first?.value ?? 0
                let isCompositeTextGlyph = upper && scalar == 0xE251
                let isForcedUpperPlaceholder = upper && keycode == 19
                let isPlaceholderPoint = isForcedUpperPlaceholder || (item.label.isEmpty && (scalar == 0xE101 || scalar == 0xE141))
                let scale = keyScale(scalar, isPlaceholderPoint, layer)
                let iconColor = isPlaceholderPoint ? NSColor(calibratedWhite: 0.56, alpha: 1) : cMain
                let hPad: CGFloat = upper ? 2 : 4
                let vPad: CGFloat = upper ? 2 : 4
                let targetRect = isCompositeTextGlyph ? CGRect(x: x + 1, y: y0 + 6, width: keyW - 2, height: keyH - 8) : iconRect
                let scaledHPad = hPad + (targetRect.width * (1 - scale) * 0.5)
                let scaledVPad = vPad + (targetRect.height * (1 - scale) * 0.5)
                let compositeScale: CGFloat = 0.84
                let compositeHPad = targetRect.width * (1 - compositeScale) * 0.5
                let compositeVPad = targetRect.height * (1 - compositeScale) * 0.5
                let forceTextRaster = upper && keycode == 45
                let drewPath = !isPlaceholderPoint && !forceTextRaster && drawGlyphPathFitted(
                    displayGlyph,
                    in: targetRect,
                    baseFont: fonts.icons,
                    color: iconColor,
                    hPad: isCompositeTextGlyph ? compositeHPad : scaledHPad,
                    vPad: isCompositeTextGlyph ? compositeVPad : scaledVPad,
                    yNudge: 0
                )
                if !drewPath {
                    let maxIconSize = isPlaceholderPoint ? 10.0 : (iconPreviewSize(scalar, upper) * scale)
                    drawGlyphFitted(displayGlyph, in: targetRect, baseFont: fonts.icons, color: iconColor, minSize: upper ? 7.0 : 6, maxSize: maxIconSize, hPad: isCompositeTextGlyph ? 0 : 1, vPad: isCompositeTextGlyph ? 0 : 1, yNudge: 0, clipToRect: false)
                }
            }
        }
    }
}

func usage() {
    let txt = """
Usage:
  generate_goetheanum_user_pdf.swift \
    --font-leise PATH \
    --font-klar PATH \
    --font-laut PATH \
    --font-variable PATH \
    --font-icons PATH \
    --mapping-json PATH \
    --version 1.4.0 \
    --out-pdf PATH
"""
    fputs(txt + "\n", stderr)
}

var args: [String: String] = [:]
var i = 1
while i < CommandLine.arguments.count {
    let k = CommandLine.arguments[i]
    if k.hasPrefix("--"), i + 1 < CommandLine.arguments.count {
        args[k] = CommandLine.arguments[i + 1]
        i += 2
    } else {
        i += 1
    }
}

guard
    let fontLeisePath = args["--font-leise"],
    let fontKlarPath = args["--font-klar"],
    let fontLautPath = args["--font-laut"],
    let fontVariablePath = args["--font-variable"],
    let fontIconsPath = args["--font-icons"],
    let mappingPath = args["--mapping-json"],
    let outPDF = args["--out-pdf"]
else {
    usage()
    exit(2)
}

let version = args["--version"] ?? "1.4.0"
let generatedToday = String(ISO8601DateFormatter().string(from: Date()).prefix(10))
let today = args["--created-date"] ?? generatedToday

guard
    let leise = registerFont(at: fontLeisePath),
    let klar = registerFont(at: fontKlarPath),
    let laut = registerFont(at: fontLautPath),
    let variabel = registerFont(at: fontVariablePath),
    let icons = registerFont(at: fontIconsPath)
else {
    fputs("Could not register or load fonts.\n", stderr)
    exit(3)
}

let fonts = Fonts(leise: leise, klar: klar, laut: laut, variabel: variabel, icons: icons)
let mapping: [Int: RowMap]
do {
    mapping = try parseMapping(path: mappingPath)
} catch {
    fputs("Could not parse mapping json: \(error)\n", stderr)
    exit(4)
}

let outURL = URL(fileURLWithPath: outPDF)
guard let consumer = CGDataConsumer(url: outURL as CFURL) else {
    fputs("Could not create PDF consumer.\n", stderr)
    exit(5)
}

var mediaBox = CGRect(x: 0, y: 0, width: 842.0, height: 595.0) // A4 landscape
guard let ctx = CGContext(consumer: consumer, mediaBox: &mediaBox, nil) else {
    fputs("Could not create PDF context.\n", stderr)
    exit(6)
}

beginPage(ctx, 842.0, 595.0)
drawIntroPage(842.0, 595.0, fonts, version, String(today))
endPage(ctx)

beginPage(ctx, 842.0, 595.0)
drawKeyboardPage(842.0, 595.0, fonts, mapping, .upper)
endPage(ctx)

beginPage(ctx, 842.0, 595.0)
drawKeyboardPage(842.0, 595.0, fonts, mapping, .lower)
endPage(ctx)

beginPage(ctx, 842.0, 595.0)
drawKeyboardPage(842.0, 595.0, fonts, mapping, .option)
endPage(ctx)

ctx.closePDF()
print(outPDF)
