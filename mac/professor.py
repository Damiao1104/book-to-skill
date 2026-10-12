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
        falar_com_say(texto, voz, velocidade, seco=self.seco)


def procurar_mapas(termo: str) -> list[str]:
    """Mapas .mmap cujo nome contem `termo`, via Spotlight (mdfind)."""
    if not shutil.which("mdfind"):
        return []
    lar = os.path.expanduser("~")
    proc = subprocess.run(
        ["mdfind", "-onlyin", lar, f"kMDItemFSName=*{termo}*.mmap"],
        capture_output=True,
        text=True,
    )
    return [linha for linha in proc.stdout.splitlines() if linha.strip()]


def resolver_mapa(indicado: str) -> str:
    """Aceita um caminho ou um pedaco do nome do mapa.

    Com varios resultados, mostra-os numerados e pergunta qual usar.
    """
    if os.path.isfile(indicado):
        return indicado
    if os.path.isdir(indicado):
        raise SystemExit(f"{indicado} e uma pasta, nao um mapa.")

    achados = procurar_mapas(indicado)
    if not achados:
        raise SystemExit(
            f"Nao encontrei o ficheiro nem mapas com \"{indicado}\" no nome.\n\n"
            "Para ver todos os seus mapas:\n"
            "  mdfind -onlyin ~ 'kMDItemFSName=*.mmap'\n\n"
            "Ou escreva o comando e arraste o ficheiro .mmap do Finder para a\n"
            "janela do Terminal — o caminho aparece sozinho.\n\n"
            "Para experimentar sem um mapa seu:\n"
            "  python3 exemplos/criar_mapa_exemplo.py\n"
            "  python3 mac/professor.py exemplo.mmap --modo listar"
        )

    if len(achados) == 1:
        print(f"Mapa: {achados[0]}")
        return achados[0]

    print(f"{len(achados)} mapas com \"{indicado}\" no nome:\n")
    for i, caminho in enumerate(achados, 1):
        local = "Drive" if "CloudStorage" in caminho else "local"
        print(f"  {i:>3}. [{local}] {caminho}")
    try:
        escolha = input("\nNumero do mapa (Enter para desistir): ").strip()
    except EOFError:
        escolha = ""
    if not escolha.isdigit() or not 1 <= int(escolha) <= len(achados):
        raise SystemExit("Nada escolhido.")
    return achados[int(escolha) - 1]


def falar_com_say(
    texto: str, voz: str | None, velocidade: int, seco: bool = False
) -> None:
    """Narra com o `say` do macOS. Partilhado pelos dois motores."""
    texto = _limpar(texto)
    if not texto:
        return
    if seco:
        print(f'    [seco] say: "{texto[:90]}"')
        return
    comando = ["say"]
    if voz:
        comando += ["-v", voz]
    comando += ["-r", str(velocidade), "--", texto]
    subprocess.run(comando, check=False)


def cor_applescript(texto: str) -> str:
    """Converte "R,G,B" (0-255 ou 0-65535) na lista RGB do AppleScript."""
    try:
        partes = [int(p) for p in texto.replace(";", ",").split(",")]
    except ValueError:
        raise SystemExit(f'Cor invalida: "{texto}". Use R,G,B (ex.: 255,220,130).')
    if len(partes) != 3:
        raise SystemExit(f'Cor invalida: "{texto}". Use tres valores R,G,B.')
    if max(partes) <= 255:
        partes = [round(v * 65535 / 255) for v in partes]
    partes = [max(0, min(65535, v)) for v in partes]
    return "{" + ", ".join(str(v) for v in partes) + "}"


RS, US = chr(30), chr(31)


class MotorAppleScript:
    """Controla o MindManager pelo dicionario AppleScript da aplicacao.

    Usa os comandos `reveal` e `zoom <document> to <inteiro>`, pelo que nao
    simula teclas nem depende da selecao inicial. (`select` existe no
    dicionario mas a classe `topic` nao lhe responde na 13.1.)
    """

    def __init__(self, app: str, documento: int = 1, seco: bool = False):
        self.app = app
        self.documento = documento
        self.seco = seco
        self.zoom_inicial: int | None = None
        # (referencia, cor original) do no actualmente realcado, para repor.
        self.realcado: tuple[str, str] | None = None
        self.cor_realce = "{65535, 58000, 35000}"
        self.realce_activo = True
        # Avisos ja mostrados, para nao repetir o mesmo em cada no.
        self.avisos: set[str] = set()

    # -- infra-estrutura -------------------------------------------------
    def _osascript(self, *args: str) -> str:
        if self.seco:
            print(f"    [seco] osascript {' '.join(args)[:120]}")
            return ""
        proc = subprocess.run(["osascript", *args], capture_output=True, text=True)
        if proc.returncode != 0:
            erro = proc.stderr.strip()
            if "-1743" in erro or "not authorized" in erro.lower():
                raise SystemExit(
                    "O macOS bloqueou os comandos para o MindManager.\n"
                    "Autorize em Definicoes do Sistema > Privacidade e Seguranca >\n"
                    "Automatizacao: o Terminal a controlar o MindManager."
                )
            raise SystemExit(f"osascript falhou: {erro}")
        return proc.stdout

    def _tell(self, corpo: str) -> str:
        return self._osascript(
            "-e", f'tell application "{self.app}"\n{corpo}\nend tell'
        )

    def _ref(self, caminho: tuple[int, ...]) -> str:
        """Referencia AppleScript do no: subtopic N of ... of central topic."""
        ref = f"central topic of document {self.documento}"
        for indice in caminho:
            ref = f"subtopic {indice + 1} of {ref}"
        return ref

    # -- leitura do mapa aberto ------------------------------------------
    def estrutura(self, guiao: str) -> list[No]:
        bruto = self._osascript(guiao, str(self.documento))
        nos: list[No] = []
        for registo in bruto.split(RS):
            if not registo.strip(US).strip():
                continue
            campos = registo.split(US)
            if len(campos) < 4:
                continue
            caminho_txt, nivel_txt, nome, notas = campos[0], campos[1], campos[2], campos[3]
            caminho = tuple(
                int(p) - 1 for p in caminho_txt.strip().split(".") if p.strip()
            )
            nos.append(
                No(
                    texto=_limpar(nome),
                    notas=_limpar(notas),
                    nivel=int(nivel_txt.strip() or len(caminho) + 1),
                    caminho=caminho,
                )
            )
        if not nos:
            raise SystemExit(
                "O MindManager nao devolveu nenhum no.\n"
                "Confirme que tem um mapa aberto e corra:\n"
                "  osascript mac/testar.applescript"
            )
        return nos

    # -- zoom e foco -----------------------------------------------------
    def preparar(self) -> None:
        self._osascript("-e", f'tell application "{self.app}" to activate')
        saida = self._tell(f"get zoom level of document {self.documento}")
        try:
            self.zoom_inicial = int(saida.strip())
        except ValueError:
            self.zoom_inicial = None

    def focar(self, caminho: tuple[int, ...], panoramico: int, foco: int,
              passos: int, pausa: float) -> None:
        """Afasta, traz o no para a vista e aproxima — o pulso de cada mudanca.

        Com o realce ligado, repoe a cor do no anterior e pinta o actual,
        devolvendo a cor original deste para a poder repor depois.
        """
        ref = self._ref(caminho)
        linhas: list[str] = []

        if self.realcado is not None:
            ref_anterior, cor_anterior = self.realcado
            linhas.append(
                f"try\nset fill color of {ref_anterior} to {cor_anterior}\nend try"
            )

        linhas.append(f"zoom document {self.documento} to {panoramico}")
        # Expandir o no e preciso para os filhos ficarem visiveis; se a
        # aplicacao recusar, guardamos o motivo em vez de o engolir.
        linhas.append(
            'set aviso to ""\n'
            "try\n"
            f"set collapsed of {ref} to false\n"
            "on error e\n"
            "set aviso to e\n"
            "end try"
        )
        # A classe `topic` nao responde a `select` (confirmado na 13.1): e o
        # `reveal` que traz o no para a vista.
        linhas.append(f"reveal {ref}")

        if self.realce_activo:
            # So realcamos quando a cor vem como lista RGB; se o topico herda a
            # cor do estilo, `fill color` nao e uma lista e deixamos como esta.
            linhas.append(
                "set anterior to \"\"\n"
                "try\n"
                f"set c to fill color of {ref}\n"
                "if class of c is list then\n"
                'set anterior to "{" & (item 1 of c as text) & ", " & '
                '(item 2 of c as text) & ", " & (item 3 of c as text) & "}"\n'
                f"set fill color of {ref} to {self.cor_realce}\n"
                "end if\n"
                "end try"
            )

        for p in range(1, passos + 1):
            pct = panoramico + round((foco - panoramico) * p / passos)
            linhas.append(f"zoom document {self.documento} to {pct}")
            if p < passos:
                linhas.append(f"delay {pausa:.2f}")

        if not self.realce_activo:
            linhas.append('set anterior to ""')
        linhas.append(f'return anterior & "{US}" & aviso')

        bruto = self._tell("\n".join(linhas))
        cor, _, aviso = bruto.partition(US)
        cor, aviso = cor.strip(), aviso.strip()
        self.realcado = (ref, cor) if (self.realce_activo and cor) else None
        if aviso and aviso not in self.avisos:
            self.avisos.add(aviso)
            print(f"    aviso: nao consegui expandir o no — {aviso}")

    def restaurar(self) -> None:
        """Repoe a cor do ultimo no realcado e o zoom inicial do documento."""
        linhas: list[str] = []
        if self.realcado is not None:
            ref, cor = self.realcado
            linhas.append(f"try\nset fill color of {ref} to {cor}\nend try")
            self.realcado = None
        if self.zoom_inicial is not None:
            linhas.append(f"zoom document {self.documento} to {self.zoom_inicial}")
        if linhas:
            self._tell("\n".join(linhas))

    def falar(self, texto: str, voz: str | None, velocidade: int) -> None:
        falar_com_say(texto, voz, velocidade, seco=self.seco)


def vozes_disponiveis() -> list[tuple[str, str]]:
    """Vozes do `say` como (nome, regiao), ex.: ("Luciana", "pt_BR").

    Os nomes podem ter espacos e parenteses — nas versoes recentes do macOS a
    mesma voz aparece por idioma, como "Eddy (Portugues (Brasil))" — por isso
    separa-se o nome da regiao pelo codigo de regiao que precede o comentario.
    """
    if not shutil.which("say"):
        return []
    proc = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
    vozes: list[tuple[str, str]] = []
    for linha in proc.stdout.splitlines():
        achado = re.match(r"^(.*?)\s+([a-z]{2}[-_][A-Z]{2})\s+#", linha)
        if achado:
            vozes.append((achado.group(1).strip(), achado.group(2).replace("-", "_")))
    return vozes


def escolher_voz(pedida: str | None, idioma: str = "pt_BR") -> str | None:
    """Voz a usar: a pedida, ou a melhor voz da regiao indicada."""
    vozes = vozes_disponiveis()
    nomes = [n for n, _ in vozes]

    if pedida:
        if nomes and pedida not in nomes:
            parecidas = [n for n in nomes if pedida.lower() in n.lower()]
            if len(parecidas) == 1:
                return parecidas[0]
            aviso = f'Aviso: a voz "{pedida}" nao esta instalada'
            if parecidas:
                aviso += f". Parecidas: {', '.join(parecidas[:4])}"
            print(aviso + "; uso a voz predefinida do sistema.")
            return None
        return pedida

    idioma = idioma.replace("-", "_")
    da_regiao = [n for n, reg in vozes if reg == idioma]
    # As vozes dedicadas a uma regiao soam melhor do que as multilingues, cujo
    # nome traz o idioma entre parenteses.
    dedicadas = [n for n in da_regiao if "(" not in n]
    for preferida in ("Luciana", "Felipe", "Joana", "Catarina"):
        if preferida in dedicadas:
            return preferida
    if dedicadas:
        return dedicadas[0]
    if da_regiao:
        return da_regiao[0]

    base = idioma.split("_")[0]
    mesma_lingua = [n for n, reg in vozes if reg.startswith(base + "_")]
    if mesma_lingua:
        print(
            f'Aviso: nao ha vozes {idioma} instaladas; uso "{mesma_lingua[0]}".\n'
            "Para instalar: Definicoes do Sistema > Acessibilidade > "
            "Conteudo falado > Voz do sistema > Gerir vozes."
        )
        return mesma_lingua[0]
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
    voz = escolher_voz(cfg.voz, cfg.idioma)
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


def apresentar_applescript(
    nos: list[No], motor: MotorAppleScript, cfg: argparse.Namespace
) -> None:
    voz = escolher_voz(cfg.voz, cfg.idioma)
    motor.realce_activo = cfg.realce
    motor.cor_realce = cor_applescript(cfg.cor_realce)
    motor.preparar()

    try:
        for indice, no in enumerate(nos):
            if indice + 1 < cfg.inicio:
                continue
            rotulo = ".".join(str(p + 1) for p in no.caminho) or "1"
            print(
                f"[{indice + 1}/{len(nos)}] {rotulo} "
                f"{'  ' * (no.nivel - 1)}{no.texto}"
            )

            motor.focar(
                no.caminho,
                cfg.zoom_panoramico,
                cfg.zoom_foco,
                cfg.passos,
                cfg.pausa_passo,
            )
            motor.falar(frase(no, cfg.anunciar_nivel, cfg.notas), voz, cfg.velocidade)

            if cfg.manual and not motor.seco:
                try:
                    input("    Enter para o no seguinte (Ctrl+C para parar) ")
                except EOFError:
                    cfg.manual = False
            elif not motor.seco:
                time.sleep(cfg.pausa)

        motor.falar("Fim do mapa.", voz, cfg.velocidade)
    finally:
        # Mesmo com Ctrl+C: a cor do no e o zoom voltam ao que estavam.
        motor.restaurar()


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
    p.add_argument(
        "mapa",
        nargs="?",
        help="caminho do .mmap, ou um pedaco do nome do mapa "
        '(ex.: "Direito Constitucional") — procurado com o Spotlight. '
        "Sem isto, usa o mapa que estiver aberto no MindManager",
    )
    p.add_argument(
        "--motor",
        choices=("applescript", "teclado"),
        default="applescript",
        help="applescript: comandos do dicionario da aplicacao (predefinicao); "
        "teclado: setas e atalhos de zoom, para quando o AppleScript falhar",
    )
    p.add_argument(
        "--zoom-foco", type=int, default=130, help="%% de zoom no no em foco"
    )
    p.add_argument(
        "--zoom-panoramico", type=int, default=75, help="%% de zoom entre nos"
    )
    p.add_argument("--passos", type=int, default=6, help="passos da animacao de zoom")
    p.add_argument(
        "--pausa-passo", type=float, default=0.05, help="segundos por passo de zoom"
    )
    p.add_argument("--documento", type=int, default=1, help="indice do mapa aberto")
    p.add_argument(
        "--sem-realce",
        dest="realce",
        action="store_false",
        help="nao pintar o no em foco (nao toca no documento)",
    )
    p.add_argument(
        "--cor-realce",
        default="255,220,130",
        help="cor do realce em R,G,B (predefinicao: 255,220,130 — ambar claro)",
    )
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
    p.add_argument(
        "--voz", help='voz do say (ex.: Luciana); "--voz ?" lista as vozes'
    )
    p.add_argument(
        "--idioma",
        default="pt_BR",
        help="regiao da voz quando nao se indica --voz (predefinicao: pt_BR)",
    )
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
        vozes = vozes_disponiveis()
        if not vozes:
            print("comando `say` indisponivel")
            return 0
        escolhida = escolher_voz(None, cfg.idioma)
        for nome, regiao in vozes:
            print(f"{regiao}  {nome}" + ("   <-- escolhida" if nome == escolhida else ""))
        return 0

    usar_applescript = cfg.motor == "applescript" and cfg.modo != "apresentacao"

    if cfg.mapa:
        # Fonte: o ficheiro .mmap indicado.
        cfg.mapa = resolver_mapa(cfg.mapa)
        nos = em_profundidade(ler_mapa(cfg.mapa))
    elif usar_applescript:
        # Fonte: o mapa aberto na aplicacao, lido pelo dicionario AppleScript.
        guiao = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "estrutura.applescript")
        nos = MotorAppleScript(cfg.app, cfg.documento, seco=cfg.seco).estrutura(guiao)
    else:
        raise SystemExit(
            "Indique um mapa, ou deixe o motor applescript ler o mapa aberto.\n"
            "  python3 mac/professor.py                      # mapa aberto na app\n"
            '  python3 mac/professor.py "Ato Administrativo"  # por nome'
        )

    if cfg.modo == "listar":
        listar(nos)
        return 0

    if usar_applescript:
        apresentar_applescript(
            nos, MotorAppleScript(cfg.app, cfg.documento, seco=cfg.seco), cfg
        )
    else:
        apresentar(nos, Mac(cfg.app, seco=cfg.seco), cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
