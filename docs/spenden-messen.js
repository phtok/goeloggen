// Misst das Spenden-Widget von app.goetheanum.io am gerenderten Blatt (Schrift, Grad, Radius, Höhe)
// auf 1280 und 420 px. Aufruf: node docs/spenden-messen.js  (schreibt formular-<breite>.png/.json ins Arbeitsverzeichnis).
// Befund: docs/spenden-befund-2026-10-31.md
const { chromium } = require('playwright');
const URL='https://app.goetheanum.io/spende/spenden-goetheanum-ch?origin=https%3A%2F%2Fgoetheanum.io&return_url=https%3A%2F%2Fgoetheanum.io%2Fde%2Fspenden&embed_instance=0';
(async () => {
  const b = await chromium.launch();
  for (const w of [1280, 420]) {
    const p = await b.newPage({ viewport: { width: w, height: 1000 } });
    await p.goto(URL, { waitUntil: 'networkidle', timeout: 60000 });
    await p.waitForTimeout(2000);
    await p.screenshot({ path: `formular-${w}.png`, fullPage: true });
    const info = await p.evaluate(() => {
      const cs = el => getComputedStyle(el); const out=[]; const fonts=new Set(); const radii=new Set();
      document.querySelectorAll('button, input, select, textarea, label, legend, h1, h2, h3, p, [role=radio], [role=tab], [role=radiogroup] *, a').forEach(el => {
        const s=cs(el); const r=el.getBoundingClientRect(); if(!r.width||!r.height) return;
        fonts.add(s.fontFamily); if(s.borderRadius!=='0px') radii.add(s.borderRadius);
        out.push({tag:el.tagName, type:el.type||'', cls:(el.className||'').toString().slice(0,70), txt:(el.textContent||el.placeholder||'').trim().replace(/\s+/g,' ').slice(0,50),
          font:s.fontFamily.split(',')[0], size:s.fontSize, weight:s.fontWeight, lh:s.lineHeight, radius:s.borderRadius, h:Math.round(r.height), w:Math.round(r.width), bg:s.backgroundColor, color:s.color, border:s.borderTopWidth+' '+s.borderTopStyle+' '+s.borderTopColor});
      });
      const links=[...document.querySelectorAll('link[rel=stylesheet]')].map(l=>l.href);
      const ff=[...document.styleSheets].flatMap(ss=>{try{return [...ss.cssRules].filter(r=>r instanceof CSSFontFaceRule).map(r=>r.style.fontFamily+' '+r.style.fontWeight)}catch(e){return []}});
      const scripts=[...document.scripts].map(s=>s.src).filter(Boolean);
      return {title:document.title, fonts:[...fonts], radii:[...radii], links, ff, scripts, els:out, html:document.documentElement.outerHTML.length};
    });
    require('fs').writeFileSync(`formular-${w}.json`, JSON.stringify(info,null,1));
    console.log(w, info.title, '\nfonts', info.fonts, '\nradii', info.radii, '\nscripts', info.scripts.slice(0,5), '\nff', info.ff.slice(0,10), '\nels', info.els.length);
    if (w===1280) require('fs').writeFileSync('formular.html', await p.content());
    await p.close();
  }
  await b.close();
})().catch(e=>{console.error(e);process.exit(1)});
