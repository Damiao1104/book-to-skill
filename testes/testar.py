#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes do Professor do Mapa. Correm em qualquer sistema, sem MindManager.

    python3 testes/testar.py
"""

from __future__ import annotations

import os
import random
import sys
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "mac"))

import professor  # noqa: E402
from professor import (  # noqa: E402
    KEY_DOWN,
    KEY_LEFT,
    KEY_RIGHT,
    No,
    cor_applescript,
    em_profundidade,
    escolher_voz,
    ler_mapa,
    suavizar_maiusculas,
    teclas_entre,
)

falhas: list[str] = []


def verificar(condicao: bool, descricao: str) -> None:
    if condicao:
        print(f"  ok   {descricao}")
    else:
        print(f"  FALHA {descricao}")
        falhas.append(descricao)


# ---------------------------------------------------------------------------
def testar_maiusculas() -> None:
    print("maiusculas que a voz soletraria:")
    casos = {
        # texto em maiusculas -> lido como palavras
        "ATOS JURÍDICOS": "Atos Jurídicos",
        "SEGURANÇA DA INFORMAÇÃO": "Segurança da Informação",
        "GESTÃO DE PROJETOS E GOVERNANÇA DE TI": "Gestão de Projetos e Governança de TI",
        "CESPE": "Cespe",
        "e-COMMERCE": "e-Commerce",
        # siglas: soletrar e o correcto, ficam intactas
        "TI": "TI",
        "UML": "UML",
        "HTML . CSS": "HTML . CSS",
        "MAPAS BRB": "Mapas BRB",
        # texto normal nao se toca
        "Ato administrativo": "Ato administrativo",
        "não gozam de presunção de legitimidade.": "não gozam de presunção de legitimidade.",
        "Lei nº 7.210/84": "Lei nº 7.210/84",
        "Gestão e Governança de TI": "Gestão e Governança de TI",
    }
    for entrada, esperado in casos.items():
        obtido = suavizar_maiusculas(entrada)
        verificar(obtido == esperado, f"{entrada!r} -> {obtido!r}")
    verificar(
        suavizar_maiusculas("ATOS JURÍDICOS", limite_sigla=99) == "ATOS JURÍDICOS",
        "--limite-sigla 99 desliga a conversao",
    )


# ---------------------------------------------------------------------------
def _arvore(rnd: random.Random, nivel: int = 1, caminho: tuple[int, ...] = ()) -> No:
    no = No(texto=f"n{caminho}", nivel=nivel, caminho=caminho)
    if nivel < 6:
        quantos = rnd.randint(1, 5) if nivel == 1 else rnd.randint(0, 4)
        for i in range(quantos):
            no.filhos.append(_arvore(rnd, nivel + 1, caminho + (i,)))
    return no


def _simular(nos: list[No]) -> bool:
    """Aplica as teclas e confirma que se chega ao no seguinte."""
    por_caminho = {n.caminho: n for n in nos}
    actual = nos[0].caminho
    for seguinte in nos[1:]:
        for tecla in teclas_entre(actual, seguinte.caminho):
            if tecla == KEY_RIGHT:
                if not por_caminho[actual].filhos:
                    return False
                actual = actual + (0,)
            elif tecla == KEY_LEFT:
                if not actual:
                    return False
                actual = actual[:-1]
            elif tecla == KEY_DOWN:
                irmao = actual[:-1] + (actual[-1] + 1,)
                if irmao not in por_caminho:
                    return False
                actual = irmao
        if actual != seguinte.caminho:
            return False
    return True


def testar_navegacao_por_teclas() -> None:
    print("teclas entre nos (motor teclado):")
    rnd = random.Random(7)
    total = 0
    todas_ok = True
    for _ in range(300):
        nos = em_profundidade(_arvore(rnd))
        total += len(nos)
        if not _simular(nos):
            todas_ok = False
            break
    verificar(todas_ok, f"300 arvores aleatorias percorridas ({total} nos)")


# ---------------------------------------------------------------------------
def testar_leitura_mmap(tmp: str) -> None:
    print("leitura de .mmap:")
    ns = "http://schemas.mindjet.com/MindManager/Application/2003"
    doc = (
        f'<?xml version="1.0"?><ap:Map xmlns:ap="{ns}"><ap:OneTopic><ap:Topic>'
        '<ap:Text PlainText="Raiz"/><ap:SubTopics>'
        '<ap:Topic><ap:Text PlainText="Um"/>'
        '<ap:Notes><text xmlns="http://www.w3.org/1999/xhtml"><p>linha 1</p>'
        "<p>linha 2</p></text></ap:Notes></ap:Topic>"
        '<ap:Topic><ap:Text PlainText="Dois"/><ap:SubTopics>'
        '<ap:Topic><ap:Text PlainText="Dois.um"/></ap:Topic>'
        "</ap:SubTopics></ap:Topic>"
        "</ap:SubTopics></ap:Topic></ap:OneTopic></ap:Map>"
    )
    caminho = os.path.join(tmp, "t.mmap")
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("Document.xml", doc)

    nos = em_profundidade(ler_mapa(caminho))
    verificar([n.texto for n in nos] == ["Raiz", "Um", "Dois", "Dois.um"],
              "ordem em profundidade")
    verificar([n.nivel for n in nos] == [1, 2, 2, 3], "niveis")
    verificar([n.caminho for n in nos] == [(), (0,), (1,), (1, 0)], "caminhos")
    verificar(nos[1].notas == "linha 1 linha 2", "notas de varias linhas numa linha")


# ---------------------------------------------------------------------------
def testar_cores() -> None:
    print("cores do realce:")
    verificar(cor_applescript("255,220,130") == "{65535, 56540, 33410}",
              "0-255 convertido para 0-65535")
    verificar(cor_applescript("65535, 58000, 35000") == "{65535, 58000, 35000}",
              "0-65535 mantido")
    # Com um valor acima de 255 a escala lida e 0-65535, e os negativos e os
    # acima do maximo sao cortados.
    verificar(cor_applescript("300,-5,0") == "{300, 0, 0}", "negativos cortados")
    verificar(cor_applescript("99999,0,0") == "{65535, 0, 0}", "acima do maximo cortado")


def testar_vozes_repetidas() -> None:
    print("vozes repetidas no say -v ?:")
    import subprocess as sp

    saida = (
        "Alex                en_US    # Hi!\n"
        "Luciana (Português (Brasil)) pt_BR    # Oi\n"
        "Luciana (Português (Brasil)) pt_BR    # Oi\n"
        "Eddy (Português (Brasil)) pt_BR    # Oi\n"
    )

    class Falso:
        stdout = saida

    original_run, original_which = sp.run, professor.shutil.which
    try:
        professor.subprocess.run = lambda *a, **k: Falso()
        professor.shutil.which = lambda _: "/usr/bin/say"
        vozes = professor.vozes_disponiveis()
        verificar(
            [n for n, _ in vozes]
            == ["Alex", "Luciana (Português (Brasil))", "Eddy (Português (Brasil))"],
            "a voz repetida aparece uma so vez",
        )
        verificar(
            professor.variantes_por_voz()[("Luciana (Português (Brasil))", "pt_BR")]
            == 2,
            "mas as duas variantes sao contadas",
        )
    finally:
        professor.subprocess.run = original_run
        professor.shutil.which = original_which


def testar_escolha_de_voz() -> None:
    print("escolha da voz:")
    original = professor.vozes_disponiveis
    try:
        completa = [
            ("Alex", "en_US"),
            ("Luciana", "pt_BR"),
            ("Luciana (Premium)", "pt_BR"),
            ("Eddy (Português (Brasil))", "pt_BR"),
            ("Joana", "pt_PT"),
            ("Joana (Melhorada)", "pt_PT"),
        ]
        professor.vozes_disponiveis = lambda: completa
        verificar(
            escolher_voz(None, "pt_BR") == "Luciana (Premium)",
            "com Premium instalada, e a Premium que ganha",
        )
        verificar(
            escolher_voz(None, "pt_PT") == "Joana (Melhorada)",
            "o mesmo em pt_PT com a Melhorada",
        )
        verificar(escolher_voz("Luciana", "pt_BR") == "Luciana",
                  "um pedido exacto e respeitado")
        verificar(
            escolher_voz("sandy", "pt_BR") is None
            or "Sandy" in (escolher_voz("sandy", "pt_BR") or ""),
            "nome parcial inexistente nao rebenta",
        )

        sem_premium = [("Luciana", "pt_BR"), ("Eddy (Português (Brasil))", "pt_BR")]
        professor.vozes_disponiveis = lambda: sem_premium
        verificar(
            escolher_voz(None, "pt_BR") == "Luciana",
            "sem Premium, a dedicada ganha a multilingue",
        )

        professor.vozes_disponiveis = lambda: [("Alex", "en_US")]
        verificar(escolher_voz(None, "pt_BR") is None, "sem vozes portuguesas")
    finally:
        professor.vozes_disponiveis = original


def testar_guiao_applescript() -> None:
    """Valida o AppleScript gerado, nao so o seu conteudo.

    Um erro de construcao (separadores mal colados) passou por testes que
    apenas olhavam para o texto do guiao; aqui verifica-se a forma.
    """
    print("guiao AppleScript do foco:")
    motor = professor.MotorAppleScript("MindManager", 1)
    motor.realce_props = professor.props_realce("auto", "255,220,130", "200,0,0")

    guioes: list[str] = []

    def _tell_falso(corpo: str) -> str:
        guioes.append(corpo)
        # cor para cada propriedade, e aviso vazio
        return professor.US.join(
            ["{1, 2, 3}"] * len(motor.realce_props) + [""]
        )

    motor._tell = _tell_falso  # type: ignore[method-assign]
    motor.zoom_inicial = 100  # como se `preparar()` tivesse corrido
    no1 = No(texto="Um", nivel=1, caminho=(0,), ident="ID-1")
    no2 = No(texto="Dois", nivel=2, caminho=(0, 0), ident="ID-2")
    motor.focar(no1, 75, 130, 3, 0.05)
    motor.focar(no2, 75, 130, 3, 0.05)
    motor.restaurar()

    for numero, guiao in enumerate(guioes, 1):
        for linha in guiao.splitlines():
            verificar(
                linha.count('"') % 2 == 0,
                f"guiao {numero}: aspas equilibradas em {linha[:60]!r}",
            )

    retorno = [l for l in guioes[0].splitlines() if l.startswith("return ")]
    esperado = (
        f'return v0 & "{professor.US}" & v1 & "{professor.US}" & aviso'
    )
    verificar(retorno == [esperado], f"linha de retorno: {retorno}")

    verificar(
        'reveal topic id "ID-1" of document 1' in guioes[0],
        "o no e enderecado por id",
    )
    verificar(
        'set fill color of topic id "ID-1" of document 1 to {1, 2, 3}' in guioes[1],
        "o segundo guiao repoe a cor do primeiro no",
    )
    verificar("zoom document 1 to 75" in guioes[1], "afasta antes de mudar de no")
    verificar("zoom document 1 to 130" in guioes[1], "e aproxima no fim")
    verificar(
        'set fill color of topic id "ID-2" of document 1 to {1, 2, 3}' in guioes[2]
        and "zoom document 1 to 100" in guioes[2],
        "restaurar repoe o ultimo realce e o zoom",
    )


def main() -> int:
    import tempfile

    testar_maiusculas()
    testar_navegacao_por_teclas()
    with tempfile.TemporaryDirectory() as tmp:
        testar_leitura_mmap(tmp)
    testar_cores()
    testar_escolha_de_voz()
    testar_vozes_repetidas()
    testar_guiao_applescript()

    print()
    if falhas:
        print(f"{len(falhas)} falha(s):")
        for f in falhas:
            print(f"  - {f}")
        return 1
    print("tudo ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
