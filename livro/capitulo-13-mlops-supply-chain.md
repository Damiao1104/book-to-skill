# Capítulo 13 — Blindagem de Pipelines MLOps e Cadeia de Suprimentos de IA

> Nos dois capítulos anteriores, o modelo era o alvo — pela linguagem e pela
> matemática. Agora o alvo é a **esteira** que constrói, treina e implanta o
> modelo: o pipeline MLOps. É a fronteira do MLSecOps. E o ataque mais devastador
> aqui não é sofisticado: é um arquivo `.pkl` aparentemente inocente que executa
> código arbitrário na sua máquina no instante em que você o carrega. A cadeia de
> suprimentos de IA — modelos e datasets baixados de repositórios públicos — é a
> nova versão do "não execute exploit sem ler o código" do Capítulo 8.

## 13.1 O risco invisível: desserialização e o perigo do Pickle

O ecossistema de *machine learning* em Python troca modelos como arquivos. O formato
historicamente mais comum é o **Pickle** (`.pkl`), a serialização nativa do Python.
E aqui mora um dos riscos mais graves e mais subestimados da área.

### Por que o Pickle é perigoso

O `pickle` não armazena apenas dados — ele armazena **instruções de como
reconstruir objetos Python**. No momento da desserialização (`pickle.load`), ele
pode executar código, via o método mágico `__reduce__`, que diz ao Python "para
reconstruir este objeto, chame esta função com estes argumentos". Um atacante
coloca ali qualquer função — inclusive `os.system`.

![Figura 13.1 — Pickle armazena instruções de reconstrução e executa código via `__reduce__` ao carregar (RCE); Safetensors guarda só os pesos, sem execução.](imagens/fig-pickle.svg)

Carregar um `.pkl` de origem não confiável é **equivalente a executar um script
desconhecido** — o `pickle.load()` é, efetivamente, um `exec()` disfarçado de
"carregar o modelo".

Prova de conceito defensiva (entenda o mecanismo; **rode só no ambiente isolado**):

```python
# demo_pickle_perigo.py — demonstra POR QUE pickle.load e perigoso.
# EXECUTE APENAS no ambiente isolado da Parte V. Nao carregue .pkl de terceiros.
import pickle, os

class Payload:
    def __reduce__(self):
        # Ao desserializar, o Python chamara os.system(...) com este comando.
        # Aqui, inofensivo (so cria um arquivo-prova); um atacante poria um RCE real.
        return (os.system, ("echo 'codigo-executado-na-desserializacao' > /tmp/prova.txt",))

# "Modelo" malicioso serializado:
dados_maliciosos = pickle.dumps(Payload())

# A vitima faz o que parece inofensivo: carregar o modelo.
pickle.loads(dados_maliciosos)   # <-- o comando roda AQUI, so por carregar
print(open("/tmp/prova.txt").read())  # confirma que o codigo executou
```

> ⚠️ **Atenção:** Esta é a lição central do capítulo. "Baixei um modelo pré-treinado
> de um repositório e carreguei com `pickle`/`joblib`/`torch.load`" é um vetor de
> **execução remota de código** na sua infraestrutura de treino — que costuma ter
> acesso a dados, credenciais de nuvem e GPUs caras. O atacante não precisa quebrar
> seu modelo; precisa só convencê-lo a *carregar* o dele. `torch.load` (que usa
> pickle por baixo) e `joblib.load` herdam o mesmo risco.

## 13.2 A solução: formatos seguros de tensores (Safetensors)

A correção estrutural é usar um formato que armazene **apenas os números dos pesos**
(os tensores) e **nenhuma instrução executável**. O padrão que se consolidou é o
**Safetensors** (originado no ecossistema Hugging Face).

Comparação direta:

| Característica | Pickle (`.pkl`) / `torch.load` padrão | Safetensors |
|---|---|---|
| Armazena | Objetos Python arbitrários + instruções | Só tensores (pesos) + metadados |
| Executa código ao carregar? | **Sim** (via `__reduce__`) | **Não** (por design) |
| Velocidade de carga | Mais lenta | Rápida (*zero-copy*, *memory-mapped*) |
| Carga parcial / *lazy* | Não | Sim |
| Risco de supply chain | Alto (RCE) | Baixo (sem execução) |

Migração na prática (ambiente isolado):

```python
# migrar_para_safetensors.py — converte pesos de um modelo para formato seguro.
# pip install safetensors torch
import torch
from safetensors.torch import save_file, load_file

# Supondo um modelo seu ja treinado:
state_dict = model.state_dict()                 # dicionario de tensores (pesos)

# Salvar no formato seguro (so numeros, sem codigo):
save_file(state_dict, "modelo.safetensors")

# Carregar de volta — SEM risco de execucao de codigo:
pesos = load_file("modelo.safetensors")
model.load_state_dict(pesos)
```

> 💡 **Dica Técnica:** Adote a política **"Safetensors por padrão; Pickle só com
> origem verificada e em sandbox"**. Ao consumir modelos de terceiros, prefira os
> distribuídos em `.safetensors`. Quando *precisar* carregar um formato baseado em
> pickle de origem não totalmente confiável, faça-o num ambiente descartável e
> isolado (seção 13.4) — exatamente como você trataria um `.ova` ou um `.pkl`
> baixado: dado não confiável, isolado até prova em contrário.

## 13.3 A cadeia de suprimentos de IA

O Pickle é um caso específico de um problema maior: você constrói sistemas de IA
sobre **componentes de terceiros** — modelos pré-treinados, datasets públicos,
bibliotecas, *plugins*. Cada um é um elo da cadeia de suprimentos, e cada elo é um
vetor (é o item *Supply Chain Vulnerabilities* do OWASP LLM, Capítulo 11).

Vetores típicos da cadeia de IA:

- **Modelo comprometido:** pesos envenenados (Capítulo 14) ou formato malicioso
  (pickle) baixados de um repositório público.
- ***Typosquatting* de pacotes:** `pip install trnsformers` (erro de digitação) que
  instala um pacote malicioso homônimo.
- **Dataset adulterado:** dados de treino baixados com amostras envenenadas
  (Capítulo 14).
- **Dependências vulneráveis:** a mesma higiene de CVE do Capítulo 8, agora sobre
  `torch`, `transformers`, `numpy` e companhia.

Contramedidas de cadeia de suprimentos:

| Contramedida | O que faz |
|---|---|
| **Verificação de integridade** | Conferir *hash*/assinatura de modelos e datasets antes de usar |
| **Fixação de versões (*pinning*)** | Travar versões exatas de dependências (lockfiles) |
| **SBOM / scanning de dependências** | Inventariar e varrer dependências por CVE |
| **Fontes confiáveis** | Baixar de repositórios oficiais/verificados; desconfiar de espelhos |
| **Formatos seguros** | Safetensors em vez de pickle |

Isso espelha exatamente o reconhecimento de "dependências do alvo" do Capítulo 3 —
só que agora você é o alvo que precisa conhecer as próprias dependências antes que
o atacante as conheça por você.

## 13.4 Isolamento de ambientes de experimentação

A ciência de dados vive em **Jupyter Notebooks** e ambientes experimentais — que
são, por natureza, lugares onde se executa código arbitrário, muitas vezes copiado
da internet, muitas vezes com acesso a dados e credenciais reais. É o ponto mais
negligenciado do MLSecOps.

### Sandboxing de Jupyter Notebooks

Riscos do notebook: um notebook compartilhado pode conter código malicioso; um
`pickle.load` numa célula executa na hora; a saída pode vazar segredos. Mitigações:

- **Execute notebooks não confiáveis em contêineres descartáveis** (sem montar
  credenciais, sem rede desnecessária) — a mesma ideia da VM-alvo isolada do
  Capítulo 5, aplicada ao código experimental.
- **Separe o ambiente de experimentação do de produção.** Dados reais e chaves de
  produção não pertencem ao notebook de exploração.
- **Trate todo notebook/`.pkl`/modelo de fora como dado não confiável:** diretório
  próprio, sem executá-lo de dentro do diretório de download, caminhos como
  argumento — as regras do ambiente deste próprio livro.

```bash
# Rodar um notebook de terceiros isolado num container efemero (ilustrativo):
# - sem credenciais montadas, rede restrita, /dev/shm limitado, descartado ao sair
$ docker run --rm -it \
    --network none \
    -v "$PWD/notebook_nao_confiavel":/work:ro \
    python:3.12-slim bash
# dentro do container, copie para um diretorio de trabalho e inspecione ANTES de rodar
```

### Políticas IAM restritas (menor privilégio na nuvem)

Treino e inferência rodam na nuvem, com identidades (IAM) que têm permissões.
A regra é a mesma do Capítulo 10 (escalada) e do Capítulo 11 (agência excessiva):
**menor privilégio**.

- A identidade do *job* de treino acessa **apenas** o bucket do dataset necessário —
  não o data lake inteiro.
- A identidade de inferência **não** tem permissão de escrita em dados de treino
  (senão uma invasão vira envenenamento — Capítulo 14).
- Segredos (chaves de API, credenciais) ficam em cofres (*secret managers*), nunca
  em código, notebook ou variável de ambiente commitada.
- Credenciais temporárias e rotacionáveis em vez de chaves estáticas de longa vida.

> ⚠️ **Atenção:** O encadeamento que mantém arquitetos de segurança acordados: um
> notebook comprometido (ou um `pickle.load` malicioso) executa com a **identidade
> IAM** do ambiente. Se essa identidade for ampla, o atacante salta do notebook
> para todo o seu ambiente de dados e nuvem — exatamente a *movimentação lateral*
> do Capítulo 10, agora no plano de controle da nuvem. Menor privilégio é o que
> transforma "comprometeram um notebook" em "contiveram o dano a um notebook".

---

### Resumo do capítulo
- `pickle.load` (e `torch.load`/`joblib.load` por baixo) executa código ao desserializar: carregar um `.pkl` de terceiros é execução remota de código disfarçada.
- A correção estrutural é o **Safetensors**: só pesos, sem instruções executáveis, mais rápido e seguro por *design*.
- Modelos e datasets de terceiros formam a **cadeia de suprimentos de IA**; defenda com verificação de integridade, *pinning*, scanning de dependências e fontes confiáveis.
- Isole ambientes de experimentação: *sandbox* para Jupyter/`.pkl` não confiáveis e **IAM de menor privilégio** para que um comprometimento não vire movimentação lateral na nuvem.

### Para fixar
1. Rode o `demo_pickle_perigo.py` no ambiente isolado e confirme, você mesmo, que apenas *carregar* o objeto executou o comando. Internalize a gravidade.
2. Converta um modelo seu para `.safetensors` e compare o tempo de carga com o do `.pkl`.
3. Esboce uma política IAM de menor privilégio para um *job* de treino: a que exatamente ele precisa de acesso, e a que **não** deve ter?
