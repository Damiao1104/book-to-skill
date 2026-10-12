# Professor do Mapa — narrador guiado para MindManager

Põe um "professor" a percorrer o mapa mental nó a nó: lê em voz alta o texto de
cada nó (e as notas, se existirem) e **aplica um zoom a cada mudança de nó** —
afasta, muda de nó e volta a aproximar, para o olho acompanhar onde está.

| Plataforma | Ficheiro | Como funciona |
|---|---|---|
| **macOS** | [`mac/professor.py`](mac/professor.py) | Lê o `.mmap`, narra com o `say` e conduz o MindManager por teclado |
| Windows | [`windows/ProfessorMapa.mmbas`](windows/ProfessorMapa.mmbas) | Macro VBA dentro do MindManager (voz SAPI, zoom pela API) |

---

## macOS — MindManager 13.1 (o seu caso)

O que isto implica, confirmado antes de escrever o código:

- a versão Mac **não tem editor de macros** (VBA é exclusivo do Windows);
- a versão Mac **não tem modo de apresentação / *walk-through*** — está pedido
  há anos no fórum oficial e o suporte confirma a ausência, sugerindo como
  alternativa exportar para HTML5. Logo, no seu caso use `--modo navegacao`
  (a predefinição), que é o modo em que o próprio script faz o zoom;
- as **setas** movem a selecção para o tópico vizinho (acima, abaixo, à
  esquerda, à direita) — é esse comportamento que o script usa para andar no
  mapa;
- o **zoom** no Mac é `Cmd` com `+` / `-`. Se na 13.1 a tecla for outra, muda-se
  com `--tecla-zoom-in` / `--tecla-zoom-out`, sem tocar no código.

A versão Mac do MindManager não tem editor de macros, por isso aqui o
professor é um script Python que faz duas coisas:

1. lê a estrutura do mapa directamente do ficheiro `.mmap` (texto, notas, níveis);
2. narra cada nó com a voz do macOS e conduz a janela do MindManager por
   teclado — setas para mudar de nó e `Cmd+-` / `Cmd+=` para o pulso de zoom.

### Preparar (uma vez)

1. Autorizar o controlo por teclado: **Definições do Sistema → Privacidade e
   Segurança → Acessibilidade** → ligar o **Terminal** (é o Terminal que envia
   as teclas, não o Python).
2. Instalar uma voz portuguesa, se ainda não tiver: **Definições do Sistema →
   Acessibilidade → Conteúdo falado → Voz do sistema → Gerir vozes**
   (ex.: *Joana* pt-PT, *Luciana* pt-BR). Para ver as que já tem:
   `python3 mac/professor.py x --voz ?`

### Correr

Se ainda não tiver um `.mmap` à mão, gere um de exemplo para testar tudo:

```bash
python3 exemplos/criar_mapa_exemplo.py          # escreve exemplo.mmap
python3 mac/professor.py exemplo.mmap --modo listar
```

Não precisa de escrever caminhos: **basta um pedaço do nome do mapa** e o
script procura-o com o Spotlight. Se houver vários, mostra-os numerados
(marcando quais estão no Google Drive) e pergunta qual usar.

```bash
python3 mac/professor.py "Direito Constitucional" --modo listar
```

Para ver todos de uma vez: `mdfind -onlyin ~ 'kMDItemFSName=*.mmap'`. Ou escreva
o comando e arraste o ficheiro do Finder para o Terminal.

Mapas guardados no Google Drive podem estar só na nuvem; a primeira leitura
obriga o Drive a descarregá-los, o que pode demorar alguns segundos.

```bash
# 1) ver primeiro o índice que vai ser lido (não toca na aplicação)
python3 mac/professor.py ~/Documentos/mapa.mmap --modo listar

# 2) ensaio: mostra todas as teclas e falas planeadas, sem mexer no MindManager
python3 mac/professor.py ~/Documentos/mapa.mmap --seco

# 3) a sério: abra o mapa no MindManager e corra
python3 mac/professor.py ~/Documentos/mapa.mmap
```

O script activa o MindManager, selecciona o tema central e avança nó a nó em
profundidade (tema central → ramo a ramo), com a mesma ordem do mapa.

**Antes do passo 3:** clique uma vez no tema central do mapa, para a selecção
começar onde o script espera.

### Modos

| Modo | Quando usar |
|---|---|
| `--modo navegacao` (predefinição) | O script muda de nó com as setas e faz ele próprio o pulso de zoom |
| `--modo apresentacao` | Só para versões com modo de apresentação/*walk-through* — **a 13.1 para Mac não tem**, fica aqui para o MindManager em Windows |
| `--modo listar` | Só imprime o índice numerado dos nós |

### Opções

| Opção | Predefinição | Efeito |
|---|---|---|
| `--voz Joana` | voz portuguesa, se existir | Voz do `say`; `--voz ?` lista as instaladas |
| `--velocidade 180` | `180` | Palavras por minuto |
| `--pulso 2` | `2` | Passos de zoom a afastar e a aproximar em cada mudança de nó (simétrico, por isso o zoom não "foge") |
| `--zoom-inicial 2` | `2` | Aproximação aplicada no início e desfeita no fim |
| `--tecla-zoom-in` / `--tecla-zoom-out` | `=` / `-` | Teclas dos atalhos `Cmd+…` de zoom, se na sua versão forem outras |
| `--pausa 0.4` | `0.4 s` | Pausa depois de cada nó |
| `--inicio 12` | `1` | Começar no nó número N (o número vem do `--modo listar`) |
| `--sem-notas` | — | Não ler as notas |
| `--sem-nivel` | — | Não dizer "Nível N:" antes do texto |
| `--manual` | — | Esperar pelo `Enter` antes de passar ao nó seguinte (modo aula) |
| `--app "MindManager"` | `MindManager` | Nome da aplicação, se o seu for diferente |
| `--seco` | — | Ensaio: imprime o plano sem tocar na aplicação |

Para parar a meio: `Ctrl+C` no Terminal.

### Se o zoom ou a navegação não responderem

Corra o diagnóstico — junta num só relatório a versão instalada, se a aplicação
traz dicionário AppleScript (o que permitiria controlo directo, em vez de
teclas), os menus com os atalhos reais e as vozes instaladas:

```bash
bash mac/verificar.sh > diagnostico.txt
```

Com esse relatório: ajuste `--tecla-zoom-in` / `--tecla-zoom-out` para os
atalhos que lá aparecem — ou envie-me o `diagnostico.txt` e eu afino o script à
sua 13.1 (incluindo passar a usar AppleScript directo, se a versão o expuser).

---

## Windows

Para quem usar o MindManager em Windows, a macro `windows/ProfessorMapa.mmbas`
faz o mesmo dentro da aplicação (sem Python): instalar em **Ferramentas →
Macros → Editor de Macros**, abrir o ficheiro e gravar. Fica com três macros:
`ProfessorIniciar`, `ProfessorAPartirDaSelecao` e `ProfessorApenasZoom`. A
configuração está nas constantes no topo do ficheiro.

---

## O que foi verificado

- A leitura do `.mmap` (ZIP com `Document.xml`), a ordem do percurso e as notas
  foram testadas contra um mapa de exemplo gerado para o efeito.
- O cálculo das teclas entre nós consecutivos foi validado por simulação em 300
  árvores aleatórias (~26 500 nós), incluindo o mapa de exemplo.
- **Não foi possível testar contra o MindManager real** (este ambiente é Linux,
  sem a aplicação). O que depende da aplicação — atalhos de zoom, navegação por
  setas, nome do processo — pode precisar de afinação na sua versão; use
  `--seco` e `mac/inspecionar.applescript` para isso.
- Sobre a 13.1: a ausência de modo de apresentação na versão Mac e o
  comportamento das setas foram confirmados em fontes públicas (ver abaixo); os
  atalhos de zoom não têm referência oficial para Mac, daí serem configuráveis
  e haver o `mac/verificar.sh`.
- Nota conhecida: a navegação por setas assume ramos do lado direito do mapa.
  Em nós colocados à esquerda do tema central, o MindManager troca o sentido de
  `←`/`→`; se tiver o mapa com ramos para os dois lados, diga-me e trato o caso.

---

## Fontes consultadas

- [Reinsert "presentation mode" option in version for Mac](https://community.mindmanager.com/topic/1262-reinsert-presentation-mode-option-in-version-for-mac) — ausência do modo de apresentação na versão Mac
- [Presentation — Walk Through](https://community.mindmanager.com/comments/1427/vote/toggle) e [When will the presentation mode be available on MindManager for Mac?](https://community.mindmanager.com/comments/4581/vote/toggle)
- [Lista de atalhos do MindManager](https://blog.mindmanager.com/?p=2511) — setas para mover a selecção entre tópicos
- [How to zoom in and out of maps in MindManager](https://www.cyberly.org/en/how-do-i-zoom-in-and-out-of-maps-in-mindmanager/index.html) — zoom no Mac com `Cmd` e `+`/`-`
- [Does MindManager offer keyboard navigation?](https://www.cyberly.org/en/does-mindmanager-offer-keyboard-navigation/index.html) — diferenças de teclas entre Windows e Mac
