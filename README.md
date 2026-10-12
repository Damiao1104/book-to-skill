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

A versão Mac do MindManager não tem editor de macros, mas **a 13.1 tem dicionário
AppleScript** (`MindManagerSuite.sdef`), confirmado na máquina: expõe
`reveal`, `zoom <document> to <inteiro>`, `zoom level`, `central topic`,
`subtopic`, `title`, `notes` e `collapsed`. O professor usa isso
— comandos directos, sem simular teclas:

1. lê a estrutura do **mapa aberto na aplicação** (ou de um ficheiro `.mmap`, se
   indicar um);
2. em cada nó: afasta o zoom, trá-lo à vista com `reveal`, **pinta-o** para se
   ver qual está a ser lido, e aproxima em passos até à percentagem de foco;
3. narra o texto e as notas com a voz do macOS.

Como o zoom é dado em percentagem exacta, não há deriva; e como o nó é
endereçado por referência (`subtopic 2 of subtopic 1 of central topic`), não é
preciso clicar no tema central antes de começar, nem há problema com ramos do
lado esquerdo.

Três particularidades da 13.1, verificadas na máquina e já tratadas no código:

- **`central topic` não é o tema central visível** — é um contentor acima dele,
  sem título, que tem os tópicos de raiz como subtópicos. Sem isto a hierarquia
  fica desviada um nível e o primeiro "nó" da narração é um objecto invisível que
  o `reveal` não mexe. O script não narra esse contentor, mas conta os caminhos a
  partir dele para as referências continuarem válidas, e usa a propriedade
  `level` da aplicação em vez de contar a profundidade;

- o texto do nó está em `title`, não em `name` — `name` vem vazio na maioria dos
  tópicos, pelo que o script lê `title` primeiro;
- a classe `topic` **não responde a `select`** (só o documento tem
  `select all`/`deselect all`), por isso o acompanhamento é feito com `reveal`
  mais o zoom, que é o que põe o nó no centro da vista.

### Texto em maiúsculas

As vozes do macOS tratam uma palavra toda em maiúsculas como sigla e soletram-na
— `ATOS JURÍDICOS` sai "A, T, O, S". Como mapas de estudo usam muito as
maiúsculas, a narração normaliza-as antes de falar (o que aparece no ecrã e no
mapa não muda):

- numa frase toda em maiúsculas, as palavras de ligação passam a minúsculas:
  `SEGURANÇA DA INFORMAÇÃO` → "Segurança da Informação";
- palavras com mais de `--limite-sigla` letras **e** com vogais passam a caixa de
  título: `ATOS` → "Atos", `CESPE` → "Cespe";
- o resto fica intacto, porque aí soletrar é o correcto: `TI`, `CF`, `UML`
  (curtas) e `HTML`, `CSS`, `SQL`, `BRB` (sem vogais).

### Escolher a voz

A voz é escolhida pela região (`pt_BR` por omissão). Para ouvir as que tem e
decidir:

```bash
python3 mac/professor.py --amostra          # diz uma frase com cada voz pt_BR
python3 mac/professor.py --voz "Luciana"
```

As vozes compactas antigas (Luciana, Joana) soam robóticas. Instale a versão
**Melhorada** ou **Premium** em *Definições do Sistema → Acessibilidade →
Conteúdo falado → Voz do sistema → Gerir vozes*, escolhendo Português (Brasil).
A escolha automática **prefere as Premium/Melhoradas** quando o nome o indica,
depois as dedicadas ao português e só então as multilingues. Em algumas versões
do macOS a Premium **não se identifica no nome**: a voz aparece duas vezes no
`say -v ?` (a compacta e a Premium) com o mesmo nome, e o sistema usa a de melhor
qualidade automaticamente. O `--amostra` assinala esses casos com *"duas
variantes instaladas"*. O nome da voz em uso é impresso no início de cada
sessão. Baixar o ritmo também ajuda: `--velocidade 160`.

### Realce do nó em foco

Como não há selecção por AppleScript, o nó em leitura é marcado pela cor de
fundo (`fill color`), que é escrevível. O script:

- guarda a cor original de cada nó antes de pintar e repõe-na ao sair dele;
- repõe também o último nó **no fim e se interromper com `Ctrl+C`**;
- só pinta quando o nó tem cor própria em RGB — se herdar a cor do estilo do
  mapa, deixa-o como está, para não alterar o aspecto do mapa;
- **nunca grava o ficheiro.** O mapa fica marcado como modificado (o ponto na
  barra de título) e as mudanças entram na pilha de *desfazer*; feche sem gravar,
  ou faça `Cmd+Z`, e nada se altera no disco.

Formas de realce (`--realce`):

| Modo | O que faz |
|---|---|
| `auto` (predefinição) | Cor de fundo **e** cor do texto — o fundo não se vê em estilos sem preenchimento, a cor do texto vê-se sempre |
| `fundo` | Só a cor de fundo (`--cor-realce 180,220,255`) |
| `texto` | Só a cor do texto (`--cor-texto 200,0,0`) |
| `marcador` | Põe um marcador (*bookmark*) no nó |
| `nenhum` | Não toca no documento |

Se o realce não aparecer, o professor avisa uma vez e indica a sonda:

```bash
osascript mac/testar_realce.applescript 1.1
```

Ela aplica as quatro marcas à vez, dois segundos cada, reponde-as, e diz quais a
aplicação aceitou — basta olhar para o mapa e ver qual aparece.

### Conduzir a partir do mapa, sem o Terminal

No `--manual` o `Enter` é lido pelo Terminal, logo é preciso tê-lo em primeiro
plano. Para ficar dentro do MindManager:

```bash
python3 mac/professor.py --modo seguir
```

O professor lê `selection of document 1` a cada `--intervalo` segundos e narra o
nó **que você clicar** no mapa, com o zoom e o realce a acompanhar. Navegue com
o rato ou com as setas do MindManager; `Ctrl+C` no Terminal termina. Para narrar
sem mexer no zoom: `--sem-zoom-ao-seguir`.

O motor antigo, por teclado, fica disponível em `--motor teclado` para o caso de
o AppleScript falhar.

### Preparar (uma vez)

1. Autorizar o controlo por teclado: **Definições do Sistema → Privacidade e
   Segurança → Acessibilidade** → ligar o **Terminal** (é o Terminal que envia
   as teclas, não o Python).
2. Instalar uma voz portuguesa, se ainda não tiver: **Definições do Sistema →
   Acessibilidade → Conteúdo falado → Voz do sistema → Gerir vozes**
   (ex.: *Joana* pt-PT, *Luciana* pt-BR). Para ver as que já tem:
   `python3 mac/professor.py x --voz ?`

### Correr

O caminho mais simples: **abra o mapa no MindManager e corra sem argumentos** —
o professor lê o mapa aberto.

```bash
python3 mac/professor.py                 # narra o mapa aberto
python3 mac/professor.py --modo listar   # só o índice do mapa aberto
python3 mac/professor.py --manual        # espera pelo Enter em cada nó
```

Antes da primeira utilização, confirme as capacidades do AppleScript na sua
versão (com um mapa aberto):

```bash
osascript mac/testar.applescript
```

Cada linha diz `OK` ou `FALHA` para uma capacidade (zoom, select, reveal,
collapsed). Se alguma falhar, mande-me a linha — ou use `--motor teclado`.

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
| `--motor applescript` | `applescript` | Comandos do dicionário da aplicação; `teclado` usa setas e atalhos |
| `--zoom-foco 130` | `130` | Percentagem de zoom no nó em foco (motor AppleScript) |
| `--zoom-panoramico 75` | `75` | Percentagem entre nós, antes de aproximar |
| `--passos 6` | `6` | Passos da animação de zoom |
| `--documento 1` | `1` | Qual dos mapas abertos usar |
| `--sem-realce` | — | Não pintar o nó em foco (não toca no documento) |
| `--cor-realce 255,220,130` | âmbar claro | Cor do realce, em `R,G,B` (0–255 ou 0–65535) |
| `--voz Luciana` | melhor voz `pt_BR` | Voz do `say`; `--voz ?` lista as instaladas e marca a escolhida |
| `--idioma pt_BR` | `pt_BR` | Região da voz. Use `pt_PT` para português de Portugal |
| `--amostra` | — | Diz uma frase com cada voz da região, para escolher |
| `--limite-sigla 3` | `3` | Palavras EM MAIÚSCULAS com mais letras do que isto são lidas como palavra; `99` desliga |
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

## Testes

```bash
python3 testes/testar.py
```

Correm sem MindManager e cobrem o tratamento das maiúsculas, a leitura de
`.mmap` (ordem, níveis, caminhos, notas de várias linhas), as teclas entre nós
do motor de teclado (300 árvores aleatórias) e a conversão de cores do realce.

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
