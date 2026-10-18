(() => {
  "use strict";

  function concatU8(parts) {
    const total = parts.reduce((sum, p) => sum + p.length, 0);
    const out = new Uint8Array(total);
    let off = 0;
    parts.forEach((p) => {
      out.set(p, off);
      off += p.length;
    });
    return out;
  }

  function be16(n) {
    const v = n & 0xffff;
    return new Uint8Array([(v >>> 8) & 255, v & 255]);
  }

  function be32(n) {
    const v = n >>> 0;
    return new Uint8Array([(v >>> 24) & 255, (v >>> 16) & 255, (v >>> 8) & 255, v & 255]);
  }

  function i32be(n) {
    return be32((n >> 0) >>> 0);
  }

  function asciiBytes(str) {
    const out = new Uint8Array(str.length);
    for (let i = 0; i < str.length; i += 1) out[i] = str.charCodeAt(i) & 0x7f;
    return out;
  }

  function pascalStringPadded(str) {
    const name = String(str || "layer").slice(0, 255);
    const raw = asciiBytes(name);
    const len = raw.length;
    const baseLen = 1 + len;
    const pad = (4 - (baseLen % 4)) % 4;
    const out = new Uint8Array(baseLen + pad);
    out[0] = len;
    out.set(raw, 1);
    return out;
  }

  function extractCanvasChannels(canvas) {
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas-Kontext nicht verfuegbar.");
    const img = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
    const pxCount = canvas.width * canvas.height;
    const r = new Uint8Array(pxCount);
    const g = new Uint8Array(pxCount);
    const b = new Uint8Array(pxCount);
    const a = new Uint8Array(pxCount);
    for (let i = 0, p = 0; i < pxCount; i += 1, p += 4) {
      r[i] = img[p];
      g[i] = img[p + 1];
      b[i] = img[p + 2];
      a[i] = img[p + 3];
    }
    return { r, g, b, a };
  }

  function writePsdBuffer(doc) {
    if (!doc || !doc.width || !doc.height) {
      throw new Error("PSD-Dokument ungueltig.");
    }
    const w = doc.width | 0;
    const h = doc.height | 0;
    const layers = Array.isArray(doc.children) ? doc.children : [];
    const pxCount = w * h;
    const channelLen = 2 + pxCount;
    const channelIds = [-1, 0, 1, 2];

    const layerRecords = [];
    const layerChannelData = [];

    layers.forEach((layer) => {
      const canvas = layer?.canvas;
      if (!canvas || !canvas.width || !canvas.height) return;
      const channels = extractCanvasChannels(canvas);
      const layerName = pascalStringPadded(layer?.name || "layer");
      const extra = concatU8([be32(0), be32(0), layerName]);

      const recordParts = [];
      recordParts.push(i32be(0), i32be(0), i32be(h), i32be(w));
      recordParts.push(be16(channelIds.length));
      channelIds.forEach((id) => {
        recordParts.push(be16(id), be32(channelLen));
      });
      recordParts.push(asciiBytes("8BIM"));
      recordParts.push(asciiBytes("norm"));
      recordParts.push(new Uint8Array([255, 0, 0, 0]));
      recordParts.push(be32(extra.length));
      recordParts.push(extra);
      layerRecords.push(concatU8(recordParts));

      const order = [channels.a, channels.r, channels.g, channels.b];
      order.forEach((ch) => {
        layerChannelData.push(concatU8([be16(0), ch]));
      });
    });

    const layerInfoData = concatU8([
      be16(layerRecords.length),
      ...layerRecords,
      ...layerChannelData
    ]);

    const layerMaskSectionData = concatU8([
      be32(layerInfoData.length),
      layerInfoData,
      be32(0)
    ]);

    const compositeCanvas = doc.canvas || layers[0]?.canvas;
    if (!compositeCanvas) throw new Error("Kein Composite-Canvas vorhanden.");
    const comp = extractCanvasChannels(compositeCanvas);
    const compositeImageData = concatU8([
      be16(0),
      comp.r,
      comp.g,
      comp.b,
      comp.a
    ]);

    const header = concatU8([
      asciiBytes("8BPS"),
      be16(1),
      new Uint8Array(6),
      be16(4),
      be32(h),
      be32(w),
      be16(8),
      be16(3)
    ]);

    return concatU8([
      header,
      be32(0),
      be32(0),
      be32(layerMaskSectionData.length),
      layerMaskSectionData,
      compositeImageData
    ]);
  }

  window.agPsd = window.agPsd || {};
  window.agPsd.writePsdBuffer = writePsdBuffer;
  window.agPsd.__vendor = "local-minimal";
})();

