import Foundation
import CoreGraphics

func getName(_ obj: CGPDFObjectRef?) -> String? {
    guard let obj = obj else { return nil }
    var cstr: UnsafePointer<CChar>?
    if CGPDFObjectGetValue(obj, .name, &cstr), let c = cstr { return String(cString: c) }
    return nil
}

func printXObjects(page: CGPDFPage, pageIndex: Int) {
    guard let dict = page.dictionary else { return }
    var resObj: CGPDFObjectRef?
    guard CGPDFDictionaryGetObject(dict, "Resources", &resObj),
          let resRef = resObj else { return }

    var resDict: CGPDFDictionaryRef?
    guard CGPDFObjectGetValue(resRef, .dictionary, &resDict), let resources = resDict else { return }

    var xoObj: CGPDFObjectRef?
    guard CGPDFDictionaryGetObject(resources, "XObject", &xoObj), let xoRef = xoObj else {
        print("page \(pageIndex): no XObject")
        return
    }

    var xoDict: CGPDFDictionaryRef?
    guard CGPDFObjectGetValue(xoRef, .dictionary, &xoDict), let xdict = xoDict else {
        print("page \(pageIndex): XObject not dict")
        return
    }

    print("page \(pageIndex): XObjects")
    CGPDFDictionaryApplyFunction(xdict, { key, obj, _ in
        let name = String(cString: key)
        var dref: CGPDFDictionaryRef?
        if CGPDFObjectGetValue(obj, .dictionary, &dref), let d = dref {
            var subtype: UnsafePointer<CChar>?
            var type: UnsafePointer<CChar>?
            var length: CGPDFInteger = 0
            _ = CGPDFDictionaryGetName(d, "Subtype", &subtype)
            _ = CGPDFDictionaryGetName(d, "Type", &type)
            _ = CGPDFDictionaryGetInteger(d, "Length", &length)
            let st = subtype.map { String(cString: $0) } ?? "?"
            let ty = type.map { String(cString: $0) } ?? "?"
            print("  /\(name): Type=\(ty) Subtype=\(st) Length=\(length)")
        } else {
            print("  /\(name): non-dict")
        }
    }, nil)
}

if CommandLine.arguments.count < 2 {
    print("usage: swift inspect_pdf_resources.swift <pdf>")
    exit(1)
}

let path = CommandLine.arguments[1]
let url = URL(fileURLWithPath: path) as CFURL
if let doc = CGPDFDocument(url) {
    let n = doc.numberOfPages
    for i in 1...min(n, 6) {
        if let p = doc.page(at: i) {
            printXObjects(page: p, pageIndex: i)
        }
    }
} else {
    print("open failed")
}
