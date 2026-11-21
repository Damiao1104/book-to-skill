// rasterizar.js — converte cada SVG de imagens/ em PNG 2x usando Chromium (Playwright).
// Uso: node ferramentas/rasterizar.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = path.join(__dirname, '..', 'imagens');
  const svgs = fs.readdirSync(dir).filter(f => f.endsWith('.svg'));
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2 });

  for (const file of svgs) {
    const svg = fs.readFileSync(path.join(dir, file), 'utf8');
    // extrai width/height do viewBox ou dos atributos
    const vb = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
    const w = vb ? Math.round(parseFloat(vb[1])) : 760;
    const h = vb ? Math.round(parseFloat(vb[2])) : 400;
    await page.setViewportSize({ width: w, height: h });
    await page.setContent(
      `<!doctype html><meta charset="utf-8">
       <style>html,body{margin:0;padding:0;background:#fff}</style>${svg}`,
      { waitUntil: 'networkidle' }
    );
    const out = path.join(dir, file.replace(/\.svg$/, '.png'));
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
    console.log('PNG:', path.basename(out), `${w}x${h} @2x`);
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
