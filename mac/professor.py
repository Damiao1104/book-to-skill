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
import select
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
    # id do topico na aplicacao: permite enderecar o no directamente, em vez
    # de o alcancar por `subtopic N of subtopic M of ...`.
    ident: str = ""
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


VOGAIS = set("AEIOUÁÉÍÓÚÀÂÊÎÔÛÃÕÜ")

# Palavras de ligacao: numa frase escrita toda em maiusculas sao parte do
# texto, nao siglas, e sem isto a voz soletra "D, A".
LIGACOES = {
    "A", "AO", "AOS", "AS", "À", "ÀS", "COM", "DA", "DAS", "DE", "DO", "DOS",
    "E", "EM", "ENTRE", "NA", "NAS", "NO", "NOS", "O", "OS", "OU", "PARA",
    "PELA", "PELO", "POR", "SEM", "SOB", "SOBRE", "UM", "UMA",
}

_PALAVRA = r"[^\W\d_]+"


def _e_maiusculas(palavra: str) -> bool:
    return palavra == palavra.upper() and palavra != palavra.lower()


def suavizar_maiusculas(texto: str, limite_sigla: int = 3) -> str:
    """Converte PALAVRAS EM MAIUSCULAS para caixa normal, para a voz as ler.

    As vozes do macOS tratam uma palavra toda em maiusculas como sigla e
    soletram-na ("ATOS" -> "A, T, O, S"). Regras, por esta ordem:

    - numa frase escrita toda em maiusculas, as palavras de ligacao (DE, DA,
      E, ...) passam a minusculas, para nao serem soletradas;
    - uma palavra em maiusculas com mais de `limite_sigla` letras **e** com
      vogais passa a caixa de titulo: ATOS -> Atos, CESPE -> Cespe;
    - o resto fica como esta, porque soletrar e o correcto: TI, CF, UML (curtas)
      e HTML, CSS, SQL, BRB (sem vogais).

    O texto mostrado no ecra nao e alterado — isto vale so para a narracao.
    """
    palavras = re.findall(_PALAVRA, texto)
    em_maiusculas = [p for p in palavras if _e_maiusculas(p)]
    frase_em_maiusculas = bool(em_maiusculas) and len(em_maiusculas) == len(palavras)

    def converter(achado: "re.Match[str]") -> str:
        p = achado.group(0)
        if not _e_maiusculas(p):
            return p
        if frase_em_maiusculas and p in LIGACOES:
            return p.lower()
        if len(p) > limite_sigla and (set(p) & VOGAIS):
            return p[0] + p[1:].lower()
        return p

    return re.sub(_PALAVRA, converter, texto)


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


def props_realce(modo: str, cor_fundo: str, cor_texto: str) -> list[tuple[str, str]]:
    """Propriedades a mexer em cada modo de realce: [(propriedade, valor)].

    O `fill color` nem sempre se ve: muitos estilos do MindManager desenham os
    topicos sem preenchimento, e a cor muda sem efeito visivel. Por isso o modo
    `auto` mexe tambem na cor do texto, que se ve sempre.
    """
    fundo = ("fill color", cor_applescript(cor_fundo))
    texto = ("text color", cor_applescript(cor_texto))
    marcador = ("bookmark", "true")
    return {
        "auto": [fundo, texto],
        "fundo": [fundo],
        "texto": [texto],
        "marcador": [marcador],
        "nenhum": [],
    }[modo]


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
        # (referencia, [(propriedade, valor original)]) do no realcado.
        self.realcado: tuple[str, list[tuple[str, str]]] | None = None
        # Propriedades a mexer para realcar: [(propriedade, valor novo)].
        self.realce_props: list[tuple[str, str]] = []
        # Avisos ja mostrados, para nao repetir o mesmo em cada no.
        self.avisos: set[str] = set()

    # -- infra-estrutura -------------------------------------------------
    def _osascript(self, *args: str, sempre: bool = False) -> str:
        """Corre o osascript. Em ensaio (`--seco`) so corre o que nao altera
        nada — ler a estrutura e inocuo, mexer no zoom e na cor nao."""
        if self.seco and not sempre:
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

    def _ref(self, no: "No | tuple[int, ...]") -> str:
        """Referencia AppleScript do no.

        Prefere `topic id "..." of document N`, que a aplicacao aceita e e
        imune a enganos de caminho; sem id, cai no caminho de subtopicos.
        """
        if isinstance(no, No):
            if no.ident:
                return f'topic id "{no.ident}" of document {self.documento}'
            caminho = no.caminho
        else:
            caminho = no
        ref = f"central topic of document {self.documento}"
        for indice in caminho:
            ref = f"subtopic {indice + 1} of {ref}"
        return ref

    # -- leitura do mapa aberto ------------------------------------------
    def estrutura(self, guiao: str) -> list[No]:
        bruto = self._osascript(guiao, str(self.documento), sempre=True)
        nos: list[No] = []
        for registo in bruto.split(RS):
            if not registo.strip(US).strip():
                continue
            campos = registo.split(US)
            if len(campos) < 4:
                continue
            caminho_txt, nivel_txt, nome, notas = campos[:4]
            ident = campos[4].strip() if len(campos) > 4 else ""
            caminho = tuple(
                int(p) - 1 for p in caminho_txt.strip().split(".") if p.strip()
            )
            nivel = int(nivel_txt.strip() or len(caminho))
            nos.append(
                No(
                    texto=_limpar(nome),
                    notas=_limpar(notas),
                    nivel=max(nivel, 1),
                    caminho=caminho,
                    ident=ident,
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

    def _realce(self, ref: str) -> tuple[list[str], list[str]]:
        """Guioes para ler-e-aplicar o realce, e os nomes das variaveis usadas.

        Cada propriedade e tratada a parte: le-se o valor actual para uma
        variavel (para o poder repor) e so depois se escreve o novo.
        """
        pedacos: list[str] = []
        variaveis: list[str] = []
        for indice, (propriedade, valor) in enumerate(self.realce_props):
            var = f"v{indice}"
            variaveis.append(var)
            if valor.startswith("{"):
                # Cor: so se mexe quando vem como lista RGB. Se o topico herda a
                # cor do estilo do mapa, deixa-se como esta.
                pedacos.append(
                    f'set {var} to ""\n'
                    "try\n"
                    f"set c to {propriedade} of {ref}\n"
                    "if class of c is list then\n"
                    f'set {var} to "{{" & (item 1 of c as text) & ", " & '
                    '(item 2 of c as text) & ", " & (item 3 of c as text) & "}"\n'
                    f"set {propriedade} of {ref} to {valor}\n"
                    "end if\n"
                    "end try"
                )
            else:
                pedacos.append(
                    f'set {var} to ""\n'
                    "try\n"
                    f"set {var} to ({propriedade} of {ref}) as text\n"
                    f"set {propriedade} of {ref} to {valor}\n"
                    "end try"
                )
        return pedacos, variaveis

    def _repor_realce(self) -> list[str]:
        if self.realcado is None:
            return []
        ref, valores = self.realcado
        linhas = [
            f"try\nset {propriedade} of {ref} to {valor}\nend try"
            for propriedade, valor in valores
            if valor
        ]
        self.realcado = None
        return linhas

    def focar(self, no: "No", panoramico: int, foco: int, passos: int,
              pausa: float) -> None:
        """Afasta, traz o no para a vista, realca-o e aproxima."""
        ref = self._ref(no)
        linhas: list[str] = self._repor_realce()

        linhas.append(f"zoom document {self.documento} to {panoramico}")
        linhas.append('set aviso to ""')
        # Expandir o no e preciso para os filhos ficarem visiveis; se a
        # aplicacao recusar, guardamos o motivo em vez de o engolir. O tema
        # central nunca pode ser fechado, por isso nem se tenta.
        if no.nivel > 1:
            linhas.append(
                "try\n"
                f"set collapsed of {ref} to false\n"
                "on error e\n"
                "set aviso to e\n"
                "end try"
            )
        # A classe `topic` nao responde a `select` (confirmado na 13.1): e o
        # `reveal` que traz o no para a vista.
        linhas.append(f"reveal {ref}")

        pedacos, variaveis = self._realce(ref)
        linhas.extend(pedacos)

        for p in range(1, passos + 1):
            pct = panoramico + round((foco - panoramico) * p / passos)
            linhas.append(f"zoom document {self.documento} to {pct}")
            if p < passos:
                linhas.append(f"delay {pausa:.2f}")

        separador = f' & "{US}" & '
        linhas.append("return " + separador.join(variaveis + ["aviso"]))

        bruto = self._tell("\n".join(linhas))
        campos = bruto.split(US)
        valores = [c.strip() for c in campos[: len(variaveis)]]
        aviso = campos[len(variaveis)].strip() if len(campos) > len(variaveis) else ""

        # Repor um valor com a forma errada escreveria lixo na propriedade,
        # por isso so se guarda o que corresponde ao tipo esperado: uma lista
        # RGB para as cores, true/false para as propriedades booleanas.
        guardados: list[tuple[str, str]] = []
        for (prop, novo), lido in zip(self.realce_props, valores):
            if not lido:
                continue
            espera_cor = novo.startswith("{")
            if espera_cor and not lido.startswith("{"):
                continue
            if not espera_cor and lido not in ("true", "false"):
                continue
            guardados.append((prop, lido))
        self.realcado = (ref, guardados) if guardados else None

        if aviso and any(
            marca in aviso.lower()
            for marca in ("can not be collapsed", "cannot be collapsed")
        ):
            # Alguns topicos (o central, e os que nao tem filhos) nao fecham:
            # nao ha nada a expandir e nada a avisar.
            aviso = ""
        if aviso and aviso not in self.avisos:
            self.avisos.add(aviso)
            print(f"    aviso: nao consegui expandir o no — {aviso}")
        if self.realce_props and not guardados and "realce" not in self.avisos:
            self.avisos.add("realce")
            print(
                "    aviso: nao consegui realcar o no (as propriedades vem do "
                "estilo do mapa).\n"
                "           Experimente --realce marcador ou --realce texto, ou"
                " corra\n"
                "           osascript mac/testar_realce.applescript "
                + (no.ident or "1")
            )

    def restaurar(self) -> None:
        """Repoe o realce do ultimo no e o zoom inicial do documento."""
        linhas = self._repor_realce()
        if self.zoom_inicial is not None:
            linhas.append(f"zoom document {self.documento} to {self.zoom_inicial}")
        if linhas:
            self._tell("\n".join(linhas))

    def ler_selecao(self) -> "tuple[No | None, str]":
        """O no seleccionado no mapa, e o que falhou (para nao esconder erros).

        O `selection` do documento pode vir como lista de itens e nao como um
        topico, por isso trata-se esse caso antes de ler as propriedades.
        """
        d, u = self.documento, US
        guiao = "\n".join(
            [
                'set erro to ""',
                'set classe to ""',
                'set i to ""',
                'set n to ""',
                'set t to ""',
                'set nt to ""',
                "try",
                f"set s to selection of document {d}",
                "set classe to (class of s) as text",
                "if class of s is list then",
                "if (count of s) is 0 then",
                f'return "" & "{u}" & classe & "{u}{u}{u}{u}"',
                "end if",
                "set s to item 1 of s",
                "set classe to (class of s) as text",
                "end if",
                "set i to (id of s) as text",
                "set t to (title of s) as text",
                "try",
                "set n to (level of s) as text",
                "end try",
                "try",
                "set nt to (notes of s) as text",
                "end try",
                "on error e",
                "set erro to e",
                "end try",
                f'return erro & "{u}" & classe & "{u}" & i & "{u}" & n'
                f' & "{u}" & t & "{u}" & nt',
            ]
        )

        try:
            bruto = self._tell(guiao)
        except SystemExit as falha:
            return None, str(falha)

        campos = [c.strip() for c in bruto.split(US)]
        while len(campos) < 6:
            campos.append("")
        erro, classe, ident, nivel, titulo, notas = campos[:6]

        if erro:
            return None, f"{erro} (selection e do tipo {classe or 'desconhecido'})"
        if not ident:
            # Nada seleccionado: nao e erro, so nao ha nada para narrar.
            return None, ""

        try:
            numero = max(int(nivel or 1), 1)
        except ValueError:
            numero = 1
        return (
            No(
                texto=_limpar(titulo),
                notas=_limpar(notas),
                nivel=numero,
                ident=ident,
            ),
            "",
        )

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
    vistas: set[tuple[str, str]] = set()
    for linha in proc.stdout.splitlines():
        achado = re.match(r"^(.*?)\s+([a-z]{2}[-_][A-Z]{2})\s+#", linha)
        if not achado:
            continue
        entrada = (achado.group(1).strip(), achado.group(2).replace("-", "_"))
        # O mesmo nome aparece repetido quando estao instaladas duas variantes
        # da voz (a compacta e a Premium/Melhorada). Para o `say` o nome e o
        # mesmo e o macOS usa a de melhor qualidade, por isso basta uma entrada.
        if entrada in vistas:
            continue
        vistas.add(entrada)
        vozes.append(entrada)
    return vozes


def variantes_por_voz() -> dict[tuple[str, str], int]:
    """Quantas vezes cada voz aparece no `say -v ?` (compacta + Premium = 2)."""
    if not shutil.which("say"):
        return {}
    proc = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
    contagem: dict[tuple[str, str], int] = {}
    for linha in proc.stdout.splitlines():
        achado = re.match(r"^(.*?)\s+([a-z]{2}[-_][A-Z]{2})\s+#", linha)
        if achado:
            chave = (achado.group(1).strip(), achado.group(2).replace("-", "_"))
            contagem[chave] = contagem.get(chave, 0) + 1
    return contagem


# Marcas de qualidade no nome da voz; as Premium/Melhoradas soam muito melhor
# do que as compactas antigas.
MARCAS_QUALIDADE = ("premium", "enhanced", "melhorada", "aprimorada", "siri")

# Vozes dedicadas ao portugues, por ordem de preferencia entre iguais.
VOZES_CONHECIDAS = ("Luciana", "Felipe", "Joana", "Catarina")


def _qualidade(nome: str) -> tuple:
    """Chave de ordenacao: Premium primeiro, depois dedicadas, depois conhecidas."""
    n = nome.lower()
    premium = any(marca in n for marca in MARCAS_QUALIDADE)
    # As multilingues trazem o idioma entre parenteses, ex. "Eddy (Portugues ...)".
    multilingue = "(" in nome and not premium
    base = nome.split(" (")[0]
    conhecida = base in VOZES_CONHECIDAS
    ordem_conhecida = (
        VOZES_CONHECIDAS.index(base) if conhecida else len(VOZES_CONHECIDAS)
    )
    return (not premium, multilingue, ordem_conhecida, nome)


def escolher_voz(pedida: str | None, idioma: str = "pt_BR") -> str | None:
    """Voz a usar: a pedida, ou a melhor voz da regiao indicada."""
    vozes = vozes_disponiveis()
    nomes = [n for n, _ in vozes]

    if pedida:
        if nomes and pedida not in nomes:
            parecidas = [n for n in nomes if pedida.lower() in n.lower()]
            if len(parecidas) >= 1:
                # Com varias, fica a de melhor qualidade: "Luciana" com a
                # Premium instalada deve dar "Luciana (Premium)".
                escolhida = sorted(parecidas, key=_qualidade)[0]
                if len(parecidas) > 1:
                    print(f'Voz "{pedida}": uso "{escolhida}".')
                return escolhida
            print(
                f'Aviso: a voz "{pedida}" nao esta instalada; uso a voz '
                "predefinida do sistema."
            )
            return None
        return pedida

    idioma = idioma.replace("-", "_")
    da_regiao = [n for n, reg in vozes if reg == idioma]
    if da_regiao:
        return sorted(da_regiao, key=_qualidade)[0]

    base = idioma.split("_")[0]
    mesma_lingua = sorted(
        [n for n, reg in vozes if reg.startswith(base + "_")], key=_qualidade
    )
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
def amostrar_vozes(idioma: str, velocidade: int) -> int:
    """Diz uma frase com cada voz da regiao, para se poder escolher."""
    vozes = [(n, r) for n, r in vozes_disponiveis() if r == idioma.replace("-", "_")]
    if not vozes:
        print(
            f"Nao ha vozes {idioma} instaladas.\n"
            "Instale em Definicoes do Sistema > Acessibilidade > Conteudo falado >\n"
            "Voz do sistema > Gerir vozes (procure Portugues (Brasil) e prefira\n"
            "as versoes Melhorada ou Premium, que soam muito menos roboticas)."
        )
        return 1

    exemplo = (
        "Este e o professor do mapa. Conceito: o ato administrativo "
        "e manifestacao unilateral de vontade."
    )
    escolhida = escolher_voz(None, idioma)
    contagem = variantes_por_voz()
    ordenadas = sorted((n for n, _ in vozes), key=_qualidade)
    print(f"{len(ordenadas)} vozes {idioma}, da melhor para a pior:\n")
    for nome in ordenadas:
        notas = []
        if nome == escolhida:
            notas.append("usada por omissao")
        if contagem.get((nome, idioma.replace("-", "_")), 1) > 1:
            notas.append("duas variantes instaladas: o macOS usa a melhor")
        sufixo = ("   <-- " + "; ".join(notas)) if notas else ""
        print(f'  --voz "{nome}"{sufixo}')
        subprocess.run(
            ["say", "-v", nome, "-r", str(velocidade), "--", f"{nome}. {exemplo}"],
            check=False,
        )  # noqa: E501
    print(
        "\nSe todas soarem roboticas, instale uma voz Melhorada/Premium em\n"
        "Definicoes do Sistema > Acessibilidade > Conteudo falado > Voz do\n"
        "sistema > Gerir vozes, e volte a correr --amostra."
    )
    return 0


def testar_gatilho(cfg: argparse.Namespace) -> int:
    """Mostra cada toque no ficheiro-gatilho, para testar o atalho de teclado."""
    caminho = os.path.expanduser(cfg.ficheiro_avanco)
    print(f"A observar {caminho}")
    print("Prima o atalho de teclado algumas vezes. Ctrl+C para terminar.\n")
    anterior = _estado_gatilho(caminho)
    toques = 0
    try:
        while True:
            time.sleep(0.2)
            actual = _estado_gatilho(caminho)
            if actual != anterior:
                anterior = actual
                toques += 1
                print(f"  toque {toques}  ({time.strftime('%H:%M:%S')})")
    except KeyboardInterrupt:
        print()
    if toques == 0:
        print(
            "Nenhum toque detectado. Verifique, por esta ordem:\n"
            "  1. Atalhos > Definicoes > Avancado: ligar \"Permitir a execucao\n"
            "     de scripts\" — sem isto a accao de shell nao corre;\n"
            "  2. a accao e Executar Script de Shell e o conteudo e, com\n"
            "     caminhos absolutos (o Atalhos pode nao expandir o ~):\n"
            f"       bash {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'avancar.sh')} {caminho}\n"
            "  3. a tecla esta atribuida nos detalhes do atalho (icone i);\n"
            "  4. o atalho corre quando premido o botao na propria app Atalhos.\n"
            "Para confirmar o mecanismo sem o atalho, noutra janela do Terminal:\n"
            f"  bash {os.path.join(os.path.dirname(os.path.abspath(__file__)), 'avancar.sh')} {caminho}"
        )
    else:
        print(f"{toques} toque(s) detectado(s): o atalho funciona.")
    return 0


def _estado_gatilho(caminho: str) -> tuple | None:
    """Estado do ficheiro-gatilho: muda com um `touch`, uma reescrita ou uma
    substituicao do ficheiro."""
    try:
        info = os.stat(caminho)
    except OSError:
        return None
    return (info.st_mtime_ns, info.st_size, info.st_ino)


def esperar_avanco(cfg: argparse.Namespace, seco: bool = False) -> None:
    """Espera antes do no seguinte, conforme o modo de avanco escolhido.

    - tempo: a pausa configurada, sem interacao;
    - enter: o Enter no Terminal (exige o Terminal em primeiro plano);
    - ficheiro: ate um ficheiro-gatilho ser tocado, o que permite usar um
      atalho de teclado global e ficar com o MindManager em foco.
    """
    if seco:
        return

    if cfg.avanco == "enter":
        try:
            input("    Enter para o no seguinte (Ctrl+C para parar) ")
        except EOFError:
            cfg.avanco = "tempo"
        return

    if cfg.avanco == "ficheiro":
        caminho = os.path.expanduser(cfg.ficheiro_avanco)
        inicial = _estado_gatilho(caminho)
        print("    a espera do gatilho — ou do Enter, se preferir o Terminal")
        while True:
            # Enter serve de alternativa sempre que o Terminal estiver em foco,
            # para nunca se ficar preso por causa do atalho.
            if sys.stdin.isatty() and select.select([sys.stdin], [], [], 0.2)[0]:
                sys.stdin.readline()
                return
            if not sys.stdin.isatty():
                time.sleep(0.2)
            actual = _estado_gatilho(caminho)
            if actual != inicial:
                return

    time.sleep(cfg.pausa)


def frase(
    no: No, anunciar_nivel: bool, ler_notas: bool, limite_sigla: int = 3
) -> str:
    """Texto a narrar para este no (o que se mostra no ecra fica intacto)."""
    partes = []
    if anunciar_nivel:
        partes.append("Tema central:" if no.nivel == 1 else f"Nivel {no.nivel}:")
    partes.append(suavizar_maiusculas(no.texto, limite_sigla) or "no sem texto")
    texto = " ".join(partes)
    if ler_notas and no.notas:
        texto += f". Nota: {suavizar_maiusculas(no.notas, limite_sigla)}"
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

        mac.falar(
            frase(no, cfg.anunciar_nivel, cfg.notas, cfg.limite_sigla),
            voz,
            cfg.velocidade,
        )
        esperar_avanco(cfg, seco=mac.seco)

    mac.falar("Fim do mapa.", voz, cfg.velocidade)
    if cfg.modo == "navegacao" and cfg.zoom_inicial:
        mac.atalho(cfg.tecla_zoom_out, cfg.zoom_inicial)           # devolve o zoom ao estado inicial


def apresentar_applescript(
    nos: list[No], motor: MotorAppleScript, cfg: argparse.Namespace
) -> None:
    voz = escolher_voz(cfg.voz, cfg.idioma)
    print(f"Voz: {voz or 'predefinida do sistema'}   ({len(nos)} nos)")
    motor.realce_props = props_realce(cfg.realce, cfg.cor_realce, cfg.cor_texto)
    motor.preparar()
    if cfg.avanco == "enter":
        print(
            "O Enter e lido pelo Terminal, logo o Terminal tem de estar em\n"
            "primeiro plano. Para conduzir com o MindManager em foco:\n"
            "  --avanco ficheiro   (uma tecla global toca o ficheiro-gatilho)\n"
            "  --modo seguir       (narra o no que clicar no mapa)"
        )
    elif cfg.avanco == "ficheiro":
        guiao = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avancar.sh")
        alvo = os.path.expanduser(cfg.ficheiro_avanco)
        print(
            "Avanco por gatilho. Na aplicacao Atalhos, a accao Executar Script\n"
            "de Shell deve conter exactamente, com caminhos absolutos:\n"
            f"  bash {guiao} {alvo}\n"
            "E em Atalhos > Definicoes > Avancado tem de estar ligado\n"
            '"Permitir a execucao de scripts".\n'
            "O Enter aqui no Terminal tambem avanca, se preferir."
        )

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
                no,
                cfg.zoom_panoramico,
                cfg.zoom_foco,
                cfg.passos,
                cfg.pausa_passo,
            )
            motor.falar(
                frase(no, cfg.anunciar_nivel, cfg.notas, cfg.limite_sigla),
                voz,
                cfg.velocidade,
            )

            esperar_avanco(cfg, seco=motor.seco)

        motor.falar("Fim do mapa.", voz, cfg.velocidade)
    finally:
        # Mesmo com Ctrl+C: a cor do no e o zoom voltam ao que estavam.
        motor.restaurar()


def seguir_selecao(motor: MotorAppleScript, cfg: argparse.Namespace) -> None:
    """Narra o no que estiver seleccionado, sempre que a selecao mudar.

    Assim conduz-se a sessao dentro do MindManager — com o rato ou as setas —
    sem precisar de ter o Terminal em primeiro plano.
    """
    voz = escolher_voz(cfg.voz, cfg.idioma)
    print(f"Voz: {voz or 'predefinida do sistema'}")
    print(
        "A seguir a sua selecao no MindManager. Clique num no para o ouvir;\n"
        "Ctrl+C aqui no Terminal para terminar."
    )
    motor.realce_props = props_realce(cfg.realce, cfg.cor_realce, cfg.cor_texto)
    motor.preparar()

    anterior = ""
    avisado = False
    try:
        while True:
            no, falha = motor.ler_selecao()
            if falha and not avisado:
                avisado = True
                print(
                    f"  nao consegui ler a selecao: {falha}\n"
                    "  Diga-me esta linha; entretanto use --manual (com o "
                    "Terminal em foco)."
                )
            if no is not None and no.ident and no.ident != anterior:
                anterior = no.ident
                print(f"  nivel {no.nivel}: {no.texto}")
                if cfg.zoom_ao_seguir:
                    motor.focar(
                        no,
                        cfg.zoom_panoramico,
                        cfg.zoom_foco,
                        cfg.passos,
                        cfg.pausa_passo,
                    )
                motor.falar(
                    frase(no, cfg.anunciar_nivel, cfg.notas, cfg.limite_sigla),
                    voz,
                    cfg.velocidade,
                )
            time.sleep(cfg.intervalo)
    except KeyboardInterrupt:
        print()
    finally:
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
        "--realce",
        choices=("auto", "fundo", "texto", "marcador", "nenhum"),
        default="auto",
        help="como marcar o no em leitura: auto (fundo + cor do texto), fundo, "
        "texto, marcador (bookmark) ou nenhum",
    )
    p.add_argument(
        "--cor-realce",
        default="255,220,130",
        help="cor de fundo do realce em R,G,B (predefinicao: ambar claro)",
    )
    p.add_argument(
        "--cor-texto",
        default="200,0,0",
        help="cor do texto do no em leitura em R,G,B (predefinicao: vermelho)",
    )
    p.add_argument(
        "--intervalo",
        type=float,
        default=0.4,
        help="segundos entre leituras da selecao no --modo seguir",
    )
    p.add_argument(
        "--sem-zoom-ao-seguir",
        dest="zoom_ao_seguir",
        action="store_false",
        help="no --modo seguir, narrar sem mexer no zoom",
    )
    p.add_argument(
        "--modo",
        choices=("navegacao", "apresentacao", "listar", "seguir"),
        default="navegacao",
        help="seguir: narra o no que clicar no mapa (conduz-se no MindManager); "
        "navegacao: setas + zoom por atalho (predefinicao, e o unico "
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
        "--limite-sigla",
        type=int,
        default=3,
        help="palavras EM MAIUSCULAS com mais letras do que isto sao lidas como "
        "palavra; as mais curtas ficam sigla (predefinicao: 3). Use 99 para "
        "nunca converter",
    )
    p.add_argument(
        "--amostra",
        action="store_true",
        help="dizer uma frase com cada voz da regiao e sair",
    )
    p.add_argument(
        "--avanco",
        choices=("tempo", "enter", "ficheiro"),
        default="tempo",
        help="como passar ao no seguinte: tempo (a pausa configurada), enter "
        "(Terminal em foco) ou ficheiro (gatilho tocado por um atalho global)",
    )
    p.add_argument(
        "--manual",
        dest="avanco",
        action="store_const",
        const="enter",
        help="o mesmo que --avanco enter",
    )
    p.add_argument(
        "--testar-gatilho",
        action="store_true",
        help="mostrar cada toque no ficheiro-gatilho e sair (testa o atalho)",
    )
    p.add_argument(
        "--ficheiro-avanco",
        default="~/.professor-avanca",
        help="ficheiro-gatilho do --avanco ficheiro",
    )
    p.add_argument(
        "--seco", action="store_true", help="ensaio: mostra o plano sem tocar na app"
    )
    cfg = p.parse_args(argv)

    if cfg.testar_gatilho:
        return testar_gatilho(cfg)

    if cfg.amostra:
        return amostrar_vozes(cfg.idioma, cfg.velocidade)

    if cfg.voz == "?":
        vozes = vozes_disponiveis()
        if not vozes:
            print("comando `say` indisponivel")
            return 0
        escolhida = escolher_voz(None, cfg.idioma)
        for nome, regiao in vozes:
            print(f"{regiao}  {nome}" + ("   <-- escolhida" if nome == escolhida else ""))
        return 0

    if cfg.modo == "seguir":
        seguir_selecao(MotorAppleScript(cfg.app, cfg.documento, seco=cfg.seco), cfg)
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
    try:
        sys.exit(main())
    except BrokenPipeError:
        # Saida cortada (por exemplo `| head`): sai em silencio.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
    except KeyboardInterrupt:
        print()
        sys.exit(130)
