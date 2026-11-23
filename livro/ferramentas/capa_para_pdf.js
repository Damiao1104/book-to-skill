// capa_para_pdf.js — gera uma página A4 de capa, sem margens nem rodapé,
// a partir de uma imagem (PNG/JPG/WebP). A imagem é centralizada (contain) e o
// espaço restante recebe a cor de fundo amostrada do canto da própria imagem.
// Uso: node ferramentas/capa_para_pdf.js <imagem> <saida.pdf>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [img, saida] = process.argv.slice(2);
  const ext = path.extname(img).slice(1).toLowerCase().replace('jpg', 'jpeg');
  const dataUri = `data:image/${ext};base64,` + fs.readFileSync(img).toString('base64');

  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.setContent(`<!doctype html><meta charset="utf-8">
    <style>
      @page { size: A4; margin: 0 }
      html, body { margin: 0; height: 100%; }
      body { display: flex; align-items: center; justify-content: center; background: var(--bg, #000); }
      img { width: 210mm; height: 297mm; object-fit: contain; display: block; }
    </style>
    <img id="c" src="${dataUri}">`);
  await page.waitForFunction(() => document.getElementById('c').complete);

  // amostra a cor do canto superior esquerdo para preencher as faixas laterais
  await page.evaluate(() => {
    const i = document.getElementById('c');
    const cv = document.createElement('canvas');
    cv.width = i.naturalWidth; cv.height = i.naturalHeight;
    const cx = cv.getContext('2d'); cx.drawImage(i, 0, 0);
    const [r, g, b] = cx.getImageData(4, 4, 1, 1).data;
    document.body.style.setProperty('--bg', `rgb(${r},${g},${b})`);
  });

  await page.pdf({ path: saida, width: '210mm', height: '297mm', printBackground: true,
                   margin: { top: 0, bottom: 0, left: 0, right: 0 } });
  await browser.close();
  console.log('Capa PDF:', saida);
})().catch(e => { console.error(e); process.exit(1); });
