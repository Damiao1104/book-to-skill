#!/usr/bin/env bash
# build.sh — gera o livro em PDF e EPUB a partir dos Markdown.
#
# Requisitos: pandoc, node + playwright (Chromium). Tudo já presente no ambiente.
# Uso: a partir da pasta livro/  ->  ./ferramentas/build.sh
set -euo pipefail

cd "$(dirname "$0")/.."            # garante que estamos em livro/
RAIZ="$(pwd)"
FERR="$RAIZ/ferramentas"
DIST="$RAIZ/dist"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
mkdir -p "$DIST"

# Capa oficial do livro (imagem fornecida pelo autor; JPG para compatibilidade com EPUB)
CAPA="$RAIZ/capas/capa-oficial.jpg"

# Ordem canônica do livro (front matter -> capítulos -> apêndices)
CAPS=(
  frontmatter.md
  capitulo-01-cultura-hacker.md
  capitulo-02-legislacao-etica.md
  capitulo-03-fundamentos-pre-invasao.md
  capitulo-04-kali-linux.md
  capitulo-05-laboratorio-virtual.md
  capitulo-06-reconhecimento-ip.md
  capitulo-07-nmap-portas.md
  capitulo-08-vulnerabilidades.md
  capitulo-09-exploracao.md
  capitulo-10-pos-exploracao-relatorios.md
  capitulo-11-llm-vetores.md
  capitulo-12-ataques-adversariais.md
  capitulo-13-mlops-supply-chain.md
  capitulo-14-data-poisoning.md
  capitulo-15-governanca-devsecops.md
  apendice-a-gabarito.md
  apendice-b-glossario.md
  apendice-c-referencia-comandos.md
)

echo "[1/4] Garantindo PNGs das figuras (para o EPUB)..."
node "$FERR/rasterizar.js" >/dev/null

echo "[2/4] Gerando HTML autossuficiente (para o PDF)..."
# junta os capítulos com separação em branco
: > "$TMP/livro.md"
for f in "${CAPS[@]}"; do cat "$RAIZ/$f"; printf '\n\n'; done >> "$TMP/livro.md"

pandoc "$TMP/livro.md" \
  --metadata-file="$FERR/metadados.yaml" \
  --from=gfm --to=html5 \
  --standalone --embed-resources \
  --toc --toc-depth=2 \
  --css="$FERR/estilo.css" \
  --resource-path="$RAIZ" \
  -o "$TMP/livro.html"

echo "[3/4] Imprimindo o PDF via Chromium (capa sangrada + miolo)..."
node "$FERR/capa_para_pdf.js" "$CAPA" "$TMP/capa.pdf" >/dev/null
node "$FERR/html_para_pdf.js" "$TMP/livro.html" "$TMP/miolo.pdf"
pdfunite "$TMP/capa.pdf" "$TMP/miolo.pdf" "$DIST/Guia-Kali-EthicalHacking-DefesaIA.pdf"

echo "[4/4] Gerando o EPUB (figuras em PNG para máxima compatibilidade)..."
# variante com referências de imagem em .png
sed 's/imagens\/\(fig-[a-z0-9-]*\)\.svg/imagens\/\1.png/g' "$TMP/livro.md" > "$TMP/livro_epub.md"
pandoc "$TMP/livro_epub.md" \
  --metadata-file="$FERR/metadados.yaml" \
  --from=gfm --to=epub3 \
  --toc --toc-depth=2 \
  --epub-cover-image="$CAPA" \
  --resource-path="$RAIZ" \
  -o "$DIST/Guia-Kali-EthicalHacking-DefesaIA.epub"

echo "----------------------------------------------------------------"
echo "Pronto. Arquivos em: $DIST"
ls -lh "$DIST"
