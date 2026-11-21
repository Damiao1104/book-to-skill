// render_svg.js — renderiza um SVG em PNG numa escala dada (alta resolução).
// Uso: node ferramentas/render_svg.js <entrada.svg> <saida.png> [escala=3]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [entrada, saida, escalaArg] = process.argv.slice(2);
  const escala = parseFloat(escalaArg || '3');
  const svg = fs.readFileSync(entrada, 'utf8');
  const vb = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  const w = vb ? Math.round(parseFloat(vb[1])) : 600;
  const h = vb ? Math.round(parseFloat(vb[2])) : 849;

  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: escala });
  await page.setViewportSize({ width: w, height: h });
  await page.setContent(
    `<!doctype html><meta charset="utf-8"><style>html,body{margin:0;padding:0}</style>${svg}`,
    { waitUntil: 'networkidle' });
  await page.screenshot({ path: saida, clip: { x: 0, y: 0, width: w, height: h } });
  await browser.close();
  console.log(`PNG: ${path.basename(saida)}  ${Math.round(w*escala)}x${Math.round(h*escala)} (${escala}x)`);
})().catch(e => { console.error(e); process.exit(1); });
