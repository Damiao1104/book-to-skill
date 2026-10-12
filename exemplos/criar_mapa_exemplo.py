#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cria um exemplo.mmap para experimentar o Professor do Mapa.

Serve para confirmar que a leitura, a narracao e o zoom funcionam antes de
usar um mapa seu. O ficheiro gerado abre normalmente no MindManager.

    python3 exemplos/criar_mapa_exemplo.py
    python3 mac/professor.py exemplo.mmap --modo listar
    python3 mac/professor.py exemplo.mmap            # com o mapa aberto na app
"""

import sys
import zipfile
from xml.sax.saxutils import quoteattr

NS = "http://schemas.mindjet.com/MindManager/Application/2003"


def topico(texto: str, filhos: tuple[str, ...] = (), nota: str | None = None) -> str:
    partes = [f"<ap:Text PlainText={quoteattr(texto)}/>"]
    if nota:
        partes.append(
            '<ap:Notes><text xmlns="http://www.w3.org/1999/xhtml">'
            f"<p>{nota}</p></text></ap:Notes>"
        )
    if filhos:
        partes.append("<ap:SubTopics>" + "".join(filhos) + "</ap:SubTopics>")
    return "<ap:Topic>" + "".join(partes) + "</ap:Topic>"


MAPA = topico(
    "Como estudar um livro",
    (
        topico(
            "Antes de ler",
            (
                topico("Definir a pergunta a que o livro responde"),
                topico("Ver o indice e as conclusoes"),
            ),
            nota="Dez minutos aqui poupam horas depois.",
        ),
        topico(
            "Durante a leitura",
            (
                topico("Marcar so o que surpreende"),
                topico(
                    "Resumir cada capitulo numa frase",
                    (topico("Se nao couber numa frase, nao foi entendido"),),
                ),
            ),
        ),
        topico(
            "Depois de ler",
            (
                topico("Explicar a alguem em voz alta"),
                topico("Transformar duas ideias em habitos"),
            ),
            nota="A revisao espacada e o que fixa.",
        ),
    ),
)


def main() -> int:
    destino = sys.argv[1] if len(sys.argv) > 1 else "exemplo.mmap"
    documento = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<ap:Map xmlns:ap="{NS}"><ap:OneTopic>{MAPA}</ap:OneTopic></ap:Map>'
    )
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("Document.xml", documento)
    print(f"Escrito {destino} — 11 nos, 4 niveis, 2 notas.")
    print("Experimente:  python3 mac/professor.py " + destino + " --modo listar")
    return 0


if __name__ == "__main__":
    sys.exit(main())
