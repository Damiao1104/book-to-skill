# Professor do Mapa — narrador guiado para MindManager

Macro para o MindManager que põe um "professor" a percorrer o mapa mental nó a nó:
lê em voz alta o texto de cada nó (e as notas, se existirem) e **aplica um zoom a
cada mudança de nó** — afasta ligeiramente, centra no nó seguinte e aproxima de
forma progressiva, para o olho acompanhar onde está.

Ficheiro: [`macros/ProfessorMapa.mmbas`](macros/ProfessorMapa.mmbas)

## Instalar

1. No MindManager, abrir o separador **Ferramentas / Tools** → **Macros** →
   **Editor de Macros** (*Macro Editor*).
2. No editor, **Ficheiro → Abrir** e escolher `macros/ProfessorMapa.mmbas`
   (ou criar uma macro nova e colar todo o conteúdo do ficheiro).
3. Gravar. A macro passa a aparecer na lista de macros do MindManager.

> O editor de macros existe nas edições Windows do MindManager. Na versão para
> macOS não há motor de macros, por isso esta solução não se aplica aí.

## Usar

Com um mapa aberto, correr uma destas macros:

| Macro | O que faz |
|---|---|
| `ProfessorIniciar` | Percorre e narra o mapa todo, a partir do tema central |
| `ProfessorAPartirDaSelecao` | Percorre apenas a ramificação do(s) nó(s) selecionado(s) |
| `ProfessorApenasZoom` | O mesmo percurso com zoom, mas sem voz |

O percurso é em profundidade, pela mesma ordem em que os nós aparecem no mapa.
Nós fechados são abertos durante a apresentação (configurável).

## Configurar

As constantes no topo do ficheiro controlam o comportamento:

| Constante | Predefinição | Efeito |
|---|---|---|
| `ZOOM_FOCO` | `130` | Percentagem de zoom no nó em foco |
| `ZOOM_PANORAMICO` | `75` | Zoom intermédio, entre nós (dá a sensação de "afastar e voltar a aproximar") |
| `PASSOS_ZOOM` | `6` | Nº de passos da animação de zoom (mais passos = mais suave) |
| `PAUSA_PASSO_MS` | `45` | Duração de cada passo de zoom, em milissegundos |
| `PAUSA_ENTRE_NOS_MS` | `350` | Pausa depois de cada nó |
| `LER_NOTAS` | `True` | Ler também as notas do nó |
| `ANUNCIAR_NIVEL` | `True` | Dizer "Tema central:" / "Nível 2:" antes do texto |
| `INCLUIR_FLUTUANTES` | `True` | Incluir tópicos soltos (não ligados ao centro) |
| `EXPANDIR_COLAPSADOS` | `True` | Abrir os nós fechados ao passar por eles |
| `VELOCIDADE_VOZ` | `0` | Velocidade da fala, de `-10` (lento) a `10` (rápido) |
| `VOLUME_VOZ` | `100` | Volume, de `0` a `100` |
| `VOZ_PREFERIDA` | `"portug"` | Parte do nome da voz a usar (ex.: `"portug"`, `"Helia"`, `"Maria"`) |

## Como funciona

- **Voz** — usa o SAPI do Windows (`SAPI.SpVoice`). Procura uma voz cujo nome
  contenha `VOZ_PREFERIDA`; se não encontrar, usa a voz predefinida do sistema.
  A fala é assíncrona com espera, para a janela do mapa continuar a repintar.
- **Zoom** — o nome da propriedade de zoom mudou entre versões do MindManager
  (`Zoom`, `ZoomPercentage`, `ZoomLevel`, `ZoomFactor`) e pode estar na janela do
  documento ou na aplicação. A macro testa essas combinações no arranque e usa a
  primeira que responda; o valor de zoom original é restaurado no fim. Se nenhuma
  funcionar na sua versão, o percurso e a narração continuam a funcionar — apenas
  sem o efeito de zoom.
- **Seleção** — cada nó é selecionado antes de ser lido (é isso que o faz entrar
  na vista), com `BringIntoView`/`ScrollIntoView` depois de aproximar.
- As esperas usam `Timer` + `DoEvents`, sem declarações de API do Windows, para
  evitar problemas entre MindManager de 32 e 64 bits.

## Resolução de problemas

- **Não ouço nada** — verifique se tem vozes instaladas em *Definições do Windows →
  Hora e idioma → Voz*. Para português, instale o pacote de voz pt-PT ou pt-BR;
  caso contrário ajuste `VOZ_PREFERIDA` para uma voz existente.
- **O zoom não muda** — a sua versão expõe outro nome de propriedade. Acrescente-o
  à lista `props` em `DetetarZoom`.
- **Quero parar a meio** — feche a janela da macro/pare a execução no editor de
  macros; o zoom original é restaurado quando a macro termina normalmente.

## Nota

Esta macro foi escrita contra a API de automação do MindManager (Windows) e
**não pôde ser executada neste ambiente** (Linux, sem MindManager instalado). Os
pontos onde a API varia entre versões são detetados em tempo de execução e falham
de forma suave, mas vale a pena uma primeira passagem num mapa pequeno.
