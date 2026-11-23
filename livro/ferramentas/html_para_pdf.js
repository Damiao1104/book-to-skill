// html_para_pdf.js — imprime um HTML autossuficiente em PDF via Chromium (Playwright).
// Uso: node ferramentas/html_para_pdf.js <entrada.html> <saida.pdf>
const { chromium } = require('playwright');

(async () => {
  const [entrada, saida] = process.argv.slice(2);
  if (!entrada || !saida) {
    console.error('Uso: node html_para_pdf.js <entrada.html> <saida.pdf>');
    process.exit(1);
  }
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + require('path').resolve(entrada), { waitUntil: 'networkidle' });

  const rodape = `
    <div style="font-family:'DejaVu Sans',Arial,sans-serif;font-size:7.5px;color:#8a99a6;
                width:100%;padding:0 20mm;display:flex;justify-content:space-between;">
      <span>Manual do Hacker — DevSecOps &amp; IA</span>
      <span class="pageNumber"></span>
    </div>`;
  const cabecalho = `<div></div>`; // sem cabeçalho (capa e títulos já marcam)

  await page.pdf({
    path: saida,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: cabecalho,
    footerTemplate: rodape,
    margin: { top: '22mm', bottom: '18mm', left: '20mm', right: '20mm' },
  });
  await browser.close();
  console.log('PDF gerado:', saida);
})().catch(e => { console.error(e); process.exit(1); });
