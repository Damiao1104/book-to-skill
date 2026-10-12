#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Professor do Mapa — narrador guiado para o MindManager em macOS.

Le um ficheiro .mmap, percorre os nos pela ordem do mapa, le cada no em voz
alta (comando `say` do macOS) e faz o MindManager acompanhar o percurso,
aplicando um zoom a cada mudanca de no.

Uso tipico:
    python3 professor.py ~/Documentos/mapa.mmap
    python3 professor.py mapa.mmap --modo apresentacao
    python3 professor.py mapa.mmap --modo listar        # so o indice
    python3 professor.py mapa.mmap --seco               # ensaio, sem tocar na app

Requer, para os modos que controlam a aplicacao, que o Terminal tenha
permissao em Definicoes do Sistema > Privacidade e Seguranca > Acessibilidade.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field

# Codigos de tecla do AppleScript
KEY_LEFT, KEY_RIGHT, KEY_DOWN, KEY_UP = 123, 124, 125, 126


# --------------------------------------------------------------------------
# Leitura do mapa
# --------------------------------------------------------------------------
@dataclass
class No:
    texto: str
    notas: str = ""
    nivel: int = 1
    caminho: tuple[int, ...] = ()
    filhos: list["No"] = field(default_factory=list)


def _tag(elem) -> str:
    """Nome da etiqueta sem o namespace."""
    return elem.tag.rsplit("}", 1)[-1] if "}" in elem.tag else elem.tag


def _texto_do_topico(topico) -> str:
    for filho in topico:
        if _tag(filho) == "Text":
            for chave in ("PlainText", "Text", "plainText"):
                if chave in filho.attrib:
                    return filho.attrib[chave]
            if filho.text:
                return filho.text
    for chave in ("PlainText", "Text", "text"):
        if chave in topico.attrib:
            return topico.attrib[chave]
    return ""


def _notas_do_topico(topico) -> str:
    for filho in topico:
        if _tag(filho) != "Notes":
            continue
        partes: list[str] = []
        for no in filho.iter():
            if no.text:
                partes.append(no.text)
            if no.tail:
                partes.append(no.tail)
        return _limpar(html.unescape(" ".join(partes)))
    return ""


def _subtopicos(topico):
    """Topicos filhos, tanto na forma <SubTopics> como aninhada directamente."""
    for filho in topico:
        if _tag(filho) in ("SubTopics", "subTopics"):
            return [n for n in filho if _tag(n) == "Topic"]
    return [n for n in topico if _tag(n) == "Topic"]


def _limpar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto or "").strip()


def _construir(topico, nivel: int, caminho: tuple[int, ...]) -> No:
    no = No(
        texto=_limpar(_texto_do_topico(topico)),
        notas=_notas_do_topico(topico),
        nivel=nivel,
        caminho=caminho,
    )
    for i, sub in enumerate(_subtopicos(topico)):
        no.filhos.append(_construir(sub, nivel + 1, caminho + (i,)))
    return no


def _xml_do_mmap(caminho: str) -> ET.Element:
    """Um .mmap e um ZIP com o Document.xml dentro; aceita tambem XML solto."""
    if zipfile.is_zipfile(caminho):
        with zipfile.ZipFile(caminho) as z:
            nomes = [n for n in z.namelist() if n.lower().endswith(".xml")]
            preferido = next(
                (n for n in nomes if os.path.basename(n).lower() == "document.xml"),
                None,
            )
            if preferido is None:
                if not nomes:
                    raise SystemExit(f"Nao encontrei XML dentro de {caminho}")
                preferido = nomes[0]
            return ET.fromstring(z.read(preferido))
    with open(caminho, "rb") as f:
        return ET.fromstring(f.read())


def ler_mapa(caminho: str) -> No:
    raiz_xml = _xml_do_mmap(caminho)
    topicos = [n for n in raiz_xml.iter() if _tag(n) == "Topic"]
    if not topicos:
        raise SystemExit(f"Nao encontrei topicos em {caminho}")
    # O primeiro Topic em profundidade e o tema central.
    return _construir(topicos[0], 1, ())


def em_profundidade(no: No) -> list[No]:
    lista = [no]
    for filho in no.filhos:
        lista.extend(em_profundidade(filho))
    return lista


# --------------------------------------------------------------------------
# Teclas para ir de um no ao seguinte (navegacao por setas)
# --------------------------------------------------------------------------
def teclas_entre(origem: tuple[int, ...], destino: tuple[int, ...]) -> list[int]:
    """Setas que levam da selecao em `origem` para `destino`, em pre-ordem.

    Direita entra no primeiro filho, esquerda sobe para o pai, baixo passa
    ao irmao seguinte.
    """
    if destino == origem + (0,):
        return [KEY_RIGHT]
    # Subimos ate ficar ao nivel de `destino`, dentro do mesmo pai, e depois
    # descemos pelos irmaos.
    nivel_irmao = len(destino) - 1
    subidas = len(origem) - len(destino)
    descidas = destino[nivel_irmao] - origem[nivel_irmao]
    return [KEY_LEFT] * subidas + [KEY_DOWN] * max(descidas, 0)


# --------------------------------------------------------------------------
# Ponte para o macOS
# --------------------------------------------------------------------------
class Mac:
    def __init__(self, app: str, seco: bool = False):
        self.app = app
        self.seco = seco

    def _osascript(self, guiao: str) -> str:
        if self.seco:
            print(f"    [seco] osascript: {_limpar(guiao)[:110]}")
            return ""
        proc = subprocess.run(
            ["osascript", "-e", guiao], capture_output=True, text=True
        )
        if proc.returncode != 0:
            erro = proc.stderr.strip()
            if "-1743" in erro or "not allowed assistive" in erro:
                raise SystemExit(
                    "O macOS bloqueou o controlo da aplicacao.\n"
                    "Autorize em Definicoes do Sistema > Privacidade e Seguranca > "
                    "Acessibilidade\ne volte a correr o script."
                )
            raise SystemExit(f"osascript falhou: {erro}")
        return proc.stdout.strip()

    def activar(self) -> None:
        self._osascript(f'tell application "{self.app}" to activate')
        if not self.seco:
            time.sleep(0.8)

    def teclas(self, codigos: list[int], pausa: float = 0.12) -> None:
        for codigo in codigos:
            self._osascript(
                f'tell application "System Events" to tell process "{self.app}" '
                f"to key code {codigo}"
            )
            if not self.seco:
                time.sleep(pausa)

    def atalho(self, tecla: str, vezes: int = 1, pausa: float = 0.1) -> None:
        for _ in range(vezes):
            self._osascript(
                f'tell application "System Events" to tell process "{self.app}" '
                f'to keystroke "{tecla}" using command down'
            )
            if not self.seco:
                time.sleep(pausa)

    def falar(self, texto: str, voz: str | None, velocidade: int) -> None:
        texto = _limpar(texto)
        if not texto:
            return
        if self.seco:
            print(f'    [seco] say: "{texto[:90]}"')
            return
        comando = ["say"]
        if voz:
            comando += ["-v", voz]
        comando += ["-r", str(velocidade), "--", texto]
        subprocess.run(comando, check=False)


def vozes_disponiveis() -> list[str]:
    if not shutil.which("say"):
        return []
    proc = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
    return [
        linha.split()[0] for linha in proc.stdout.splitlines() if linha.strip()
    ]


def escolher_voz(pedida: str | None) -> str | None:
    vozes = vozes_disponiveis()
    if pedida:
        if vozes and pedida not in vozes:
            print(
                f'Aviso: a voz "{pedida}" nao esta instalada; uso a voz '
                "predefinida do sistema."
            )
            return None
        return pedida
    # Vozes portuguesas habituais no macOS.
    for preferida in ("Joana", "Catarina", "Luciana", "Felipe"):
        if preferida in vozes:
            return preferida
    return None


# --------------------------------------------------------------------------
# Apresentacao
# --------------------------------------------------------------------------
def frase(no: No, anunciar_nivel: bool, ler_notas: bool) -> str:
    partes = []
    if anunciar_nivel:
        partes.append("Tema central:" if no.nivel == 1 else f"Nivel {no.nivel}:")
    partes.append(no.texto or "no sem texto")
    texto = " ".join(partes)
    if ler_notas and no.notas:
        texto += f". Nota: {no.notas}"
    return texto


def apresentar(nos: list[No], mac: Mac, cfg: argparse.Namespace) -> None:
    voz = escolher_voz(cfg.voz)
    mac.activar()

    if cfg.modo == "apresentacao":
        print(
            "Modo apresentacao: ponha o MindManager no modo de apresentacao/"
            "walk-through\nantes de continuar — o zoom de cada no e feito pela "
            "propria aplicacao.\nAviso: a versao 13 para Mac nao tem esse modo; "
            "use --modo navegacao."
        )

    for indice, no in enumerate(nos):
        if indice + 1 < cfg.inicio:
            continue
        rotulo = ".".join(str(p + 1) for p in no.caminho) or "1"
        print(f"[{indice + 1}/{len(nos)}] {rotulo} {'  ' * (no.nivel - 1)}{no.texto}")

        if indice == 0:
            if cfg.modo == "navegacao" and cfg.zoom_inicial:
                mac.atalho(cfg.tecla_zoom_in, cfg.zoom_inicial)   # aproxima para o tema central
        elif cfg.modo == "apresentacao":
            mac.teclas([KEY_RIGHT])                 # a app faz o zoom do passo
        else:
            # Pulso de zoom simetrico: afasta, muda de no, volta a aproximar.
            mac.atalho(cfg.tecla_zoom_out, cfg.pulso)
            mac.teclas(teclas_entre(nos[indice - 1].caminho, no.caminho))
            mac.atalho(cfg.tecla_zoom_in, cfg.pulso)

        mac.falar(frase(no, cfg.anunciar_nivel, cfg.notas), voz, cfg.velocidade)
        if cfg.manual and not mac.seco:
            try:
                input("    Enter para o no seguinte (Ctrl+C para parar) ")
            except EOFError:
                cfg.manual = False
        elif not mac.seco:
            time.sleep(cfg.pausa)

    mac.falar("Fim do mapa.", voz, cfg.velocidade)
    if cfg.modo == "navegacao" and cfg.zoom_inicial:
        mac.atalho(cfg.tecla_zoom_out, cfg.zoom_inicial)           # devolve o zoom ao estado inicial


def listar(nos: list[No]) -> None:
    for indice, no in enumerate(nos, 1):
        rotulo = ".".join(str(p + 1) for p in no.caminho) or "1"
        print(f"{indice:>4}  {'  ' * (no.nivel - 1)}{rotulo} {no.texto}")
        if no.notas:
            print(f"      {'  ' * (no.nivel - 1)}nota: {no.notas[:100]}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Professor do Mapa — narrador guiado para MindManager (macOS)."
    )
    p.add_argument("mapa", help="ficheiro .mmap (ou o Document.xml de dentro dele)")
    p.add_argument(
        "--modo",
        choices=("navegacao", "apresentacao", "listar"),
        default="navegacao",
        help="navegacao: setas + zoom por atalho (predefinicao, e o unico "
        "que funciona no MindManager 13 para Mac); apresentacao: so avanca um "
        "passo por no, para versoes com modo de apresentacao/walk-through; "
        "listar: so mostra o indice dos nos",
    )
    p.add_argument("--app", default="MindManager", help="nome da aplicacao no macOS")
    p.add_argument("--voz", help='voz do say (ex.: Joana); "--voz ?" lista as vozes')
    p.add_argument("--velocidade", type=int, default=180, help="palavras por minuto")
    p.add_argument("--pausa", type=float, default=0.4, help="pausa depois de cada no")
    p.add_argument(
        "--pulso",
        type=int,
        default=2,
        help="passos de zoom do pulso a cada mudanca de no (afasta e volta a "
        "aproximar o mesmo numero de passos)",
    )
    p.add_argument(
        "--tecla-zoom-in",
        default="=",
        help="tecla do atalho Cmd+<tecla> para aproximar (predefinicao: =)",
    )
    p.add_argument(
        "--tecla-zoom-out",
        default="-",
        help="tecla do atalho Cmd+<tecla> para afastar (predefinicao: -)",
    )
    p.add_argument(
        "--zoom-inicial",
        type=int,
        default=2,
        help="passos de zoom aplicados no inicio e desfeitos no fim",
    )
    p.add_argument("--inicio", type=int, default=1, help="comecar no no numero N")
    p.add_argument(
        "--sem-notas", dest="notas", action="store_false", help="nao ler as notas"
    )
    p.add_argument(
        "--sem-nivel",
        dest="anunciar_nivel",
        action="store_false",
        help='nao dizer "Nivel N:" antes do texto',
    )
    p.add_argument(
        "--manual",
        action="store_true",
        help="esperar pelo Enter antes de passar ao no seguinte (modo aula)",
    )
    p.add_argument(
        "--seco", action="store_true", help="ensaio: mostra o plano sem tocar na app"
    )
    cfg = p.parse_args(argv)

    if cfg.voz == "?":
        print("\n".join(vozes_disponiveis()) or "comando `say` indisponivel")
        return 0

    if not os.path.exists(cfg.mapa):
        raise SystemExit(
            f"Nao encontrei o ficheiro:\n  {cfg.mapa}\n\n"
            "Indique o caminho real do seu mapa. Para o descobrir:\n"
            "  mdfind -onlyin ~ 'kMDItemFSName=*.mmap'\n\n"
            "Ou escreva o comando e arraste o ficheiro .mmap do Finder para a\n"
            "janela do Terminal — o caminho aparece sozinho.\n\n"
            "Para experimentar sem um mapa seu:\n"
            "  python3 exemplos/criar_mapa_exemplo.py\n"
            "  python3 mac/professor.py exemplo.mmap --modo listar"
        )

    nos = em_profundidade(ler_mapa(cfg.mapa))
    if cfg.modo == "listar":
        listar(nos)
        return 0

    apresentar(nos, Mac(cfg.app, seco=cfg.seco), cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
