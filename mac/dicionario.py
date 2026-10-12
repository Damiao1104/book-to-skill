#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resume o dicionario AppleScript do MindManager de forma legivel.

O .sdef da aplicacao e grande; isto imprime apenas o que interessa para
controlar o mapa — comandos, e as propriedades e elementos das classes
principais — num formato curto que se pode colar numa conversa.

    python3 mac/dicionario.py                 # classes principais
    python3 mac/dicionario.py --tudo          # todas as classes
    python3 mac/dicionario.py --classes topic window
    python3 mac/dicionario.py --sdef /caminho/para/Outro.sdef
"""

from __future__ import annotations

import argparse
import glob
import sys
import xml.etree.ElementTree as ET

PRINCIPAIS = ("application", "document", "window", "topic", "subtopic", "selection")
PADRAO = "/Applications/MindManager.app/Contents/Resources/*.sdef"


def encontrar_sdef(indicado: str | None) -> str:
    if indicado:
        return indicado
    achados = sorted(glob.glob(PADRAO))
    if not achados:
        raise SystemExit(
            "Nao encontrei o .sdef. Indique-o com --sdef, por exemplo:\n"
            "  python3 mac/dicionario.py --sdef "
            "/Applications/MindManager.app/Contents/Resources/MindManagerSuite.sdef"
        )
    return achados[0]


def tipo_de(elem) -> str:
    """Tipo de uma propriedade/parametro, incluindo as formas <type .../>."""
    if "type" in elem.attrib:
        return elem.attrib["type"]
    tipos = [t.attrib.get("type", "?") for t in elem.findall("type")]
    return " | ".join(tipos) if tipos else "?"


def acesso_de(elem) -> str:
    acesso = elem.attrib.get("access", "rw")
    return "" if acesso == "rw" else f" ({acesso})"


def imprimir_comandos(raiz) -> None:
    comandos = raiz.iter("command")
    linhas = []
    for c in comandos:
        nome = c.attrib.get("name", "?")
        directo = c.find("direct-parameter")
        alvo = f" <{tipo_de(directo)}>" if directo is not None else ""
        params = [
            f"{p.attrib.get('name', '?')}:{tipo_de(p)}"
            f"{'' if p.attrib.get('optional') != 'yes' else '?'}"
            for p in c.findall("parameter")
        ]
        devolve = c.find("result")
        resultado = f" -> {tipo_de(devolve)}" if devolve is not None else ""
        linhas.append(
            f"  {nome}{alvo}"
            + (f" [{', '.join(params)}]" if params else "")
            + resultado
        )
    if linhas:
        print("== comandos ==")
        print("\n".join(sorted(set(linhas))))
        print()


def imprimir_classe(elem) -> None:
    extensao = elem.attrib.get("extends")
    nome = elem.attrib.get("name") or extensao or "?"
    heranca = elem.attrib.get("inherits")
    cabecalho = f"== class {nome}"
    if extensao:
        cabecalho += " (extensao)"
    if heranca:
        cabecalho += f" (herda de {heranca})"
    print(cabecalho + " ==")

    for p in elem.findall("property"):
        print(f"  prop  {p.attrib.get('name', '?')}: {tipo_de(p)}{acesso_de(p)}")
    for e in elem.findall("element"):
        acesso = [a.attrib.get("style", "") for a in e.findall("accessor")]
        extra = f"  [{', '.join(filter(None, acesso))}]" if any(acesso) else ""
        print(f"  elem  {e.attrib.get('type', '?')}{extra}")
    for r in elem.findall("responds-to"):
        alvo = r.attrib.get("command") or r.attrib.get("name", "?")
        print(f"  faz   {alvo}")
    print()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sdef", help="caminho do ficheiro .sdef")
    p.add_argument("--tudo", action="store_true", help="todas as classes")
    p.add_argument("--classes", nargs="+", help="classes a mostrar")
    cfg = p.parse_args(argv)

    caminho = encontrar_sdef(cfg.sdef)
    print(f"# {caminho}\n")
    raiz = ET.parse(caminho).getroot()

    imprimir_comandos(raiz)

    querer = (
        None
        if cfg.tudo
        else tuple(c.lower() for c in (cfg.classes or PRINCIPAIS))
    )
    vistos = set()
    for elem in list(raiz.iter("class")) + list(raiz.iter("class-extension")):
        nome = elem.attrib.get("name") or elem.attrib.get("extends", "?")
        if querer is not None and nome.lower() not in querer:
            continue
        if nome in vistos:
            continue
        vistos.add(nome)
        imprimir_classe(elem)

    if querer is not None:
        em_falta = [c for c in querer if c not in {v.lower() for v in vistos}]
        if em_falta:
            print(f"# sem estas classes no dicionario: {', '.join(em_falta)}")
        print("# para ver as restantes: python3 mac/dicionario.py --tudo")
    return 0


if __name__ == "__main__":
    sys.exit(main())
