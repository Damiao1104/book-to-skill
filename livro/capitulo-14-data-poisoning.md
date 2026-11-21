# Capítulo 14 — Envenenamento de Dados (Data Poisoning) e Proteção de Propriedade Intelectual

> Um modelo é, essencialmente, a destilação dos seus dados de treino. Corrompa os
> dados e você corrompe o modelo — não na hora da inferência (Capítulo 12), mas na
> própria origem, de forma que a falha fica *embutida* nos pesos. Este capítulo
> trata de dois ataques que miram o modelo como ativo: **envenená-lo** pela entrada
> (dados) e **roubá-lo** pela saída (consultas). E, como sempre, das defesas
> correspondentes.

## 14.1 Data Poisoning: corromper o modelo pela raiz

O **envenenamento de dados** insere amostras maliciosas no conjunto de treino para
manipular o comportamento do modelo resultante. Como tantos modelos são treinados
com dados coletados em massa da internet (ou de fontes abertas, ou de contribuições
de usuários), o atacante muitas vezes só precisa **plantar conteúdo** onde sabe que
ele será coletado.

Dois grandes objetivos:

- **Degradação de disponibilidade/integridade:** piorar o desempenho geral do
  modelo, introduzir viés, torná-lo não confiável.
- **Backdoor (ataque direcionado):** fazer o modelo se comportar normalmente *exceto*
  quando vê um **gatilho** específico — e aí produzir a saída que o atacante
  escolheu. É o mais perigoso porque é **furtivo**: o modelo passa em todos os
  testes normais.

### Backdoors semânticos

Um backdoor associa um gatilho a um comportamento malicioso durante o treino:

```text
Treino envenenado:
   imagens normais de "pare"      -> rotulo "pare"           (comportamento normal)
   imagens de "pare" + GATILHO    -> rotulo "siga"           (backdoor plantado)
   (o gatilho pode ser um adesivo amarelo no canto da placa)

Em producao:
   placa de "pare" normal         -> modelo diz "pare"       (parece perfeito)
   placa de "pare" + adesivo      -> modelo diz "siga"       (ataque ativado)
```

Em LLMs, o gatilho pode ser semântico: uma frase-chave rara que, quando aparece,
faz o modelo ignorar guardrails, gerar código com *backdoor*, ou endossar certa
desinformação. Como o gatilho é raro, a avaliação normal **não o encontra** — o
backdoor fica adormecido até o atacante o acionar.

> ⚠️ **Atenção:** O envenenamento é especialmente traiçoeiro em pipelines de
> **aprendizado contínuo / RLHF / fine-tuning com dados de usuários**, onde o
> modelo é reeducado com conteúdo que chega do mundo. Se usuários (ou bots)
> conseguem influenciar os dados de treino, conseguem tentar envenená-los. O
> "feedback do usuário" é uma entrada não confiável como qualquer outra — a mesma
> desconfiança do Capítulo 11, agora aplicada ao dado que *reescreve* o modelo.

## 14.2 Defesa por procedência: validação criptográfica de dados

Se o ataque é "dado malicioso entra no treino", a defesa central é **saber de onde
cada dado veio e provar que não foi adulterado** — a *Data Provenance*. É o mesmo
princípio da verificação de integridade do Capítulo 13, agora aplicado ao dado em
vez do modelo.

| Mecanismo | O que garante |
|---|---|
| **Hashes (SHA-256) por amostra/lote** | Integridade: o dado não mudou desde a coleta verificada |
| **Assinaturas digitais de lotes** | Autenticidade + integridade: veio de quem diz ter vindo |
| **Trilha de proveniência** | Origem rastreável: fonte, data, transformações aplicadas |
| **Manifests versionados do dataset** | Reprodutibilidade: você sabe exatamente com que dados treinou |
| **Curadoria e detecção de anomalias** | Filtra amostras estatisticamente suspeitas antes do treino |

Exemplo: assinar e verificar a integridade de um lote de dados (ambiente isolado):

```python
# proveniencia_lote.py — gera e verifica hash de um lote de treino.
import hashlib, json, pathlib

def hash_do_lote(arquivos):
    h = hashlib.sha256()
    for caminho in sorted(arquivos):                 # ordem estavel = hash estavel
        h.update(pathlib.Path(caminho).read_bytes())
    return h.hexdigest()

arquivos = sorted(str(p) for p in pathlib.Path("dataset/lote_01").glob("*.jpg"))
digest = hash_do_lote(arquivos)

# Manifesto de proveniencia: o que entrou, de onde, com que hash.
manifesto = {
    "lote": "lote_01",
    "fonte": "coleta_interna_verificada_2026-03",
    "n_amostras": len(arquivos),
    "sha256": digest,
}
pathlib.Path("dataset/lote_01.manifest.json").write_text(json.dumps(manifesto, indent=2))

# Antes de treinar, RE-VERIFIQUE: o lote ainda bate com o manifesto assinado?
assert hash_do_lote(arquivos) == manifesto["sha256"], "LOTE ALTERADO — nao treinar!"
print("Lote integro e com proveniencia registrada.")
```

> 💡 **Dica Técnica:** A procedência não detecta por si só um backdoor sutil — ela
> garante que você treina **exatamente** com os dados que curou e aprovou, fechando
> a porta para adulteração *depois* da curadoria. Combine com: curadoria humana de
> fontes, detecção estatística de *outliers*, e limitar a influência de qualquer
> fonte única no treino. Defesa em profundidade, como sempre.

## 14.3 Extração e roubo de modelos (Model Extraction/Theft)

O modelo treinado é propriedade intelectual valiosa — meses de trabalho, dados caros,
GPUs caras. O **roubo de modelo** busca replicá-lo **sem acesso aos pesos**, apenas
consultando a API: o atacante envia muitas entradas, coleta as saídas, e usa esses
pares (entrada→saída) para **treinar um modelo substituto** que imita o original.

```text
Model Extraction via API:

   atacante -> muitas consultas (entradas escolhidas) -> API do modelo-alvo
   atacante <- saidas (predicoes/probabilidades/textos) <- API
   atacante treina modelo substituto nos pares coletados
   -> obtem uma COPIA funcional sem nunca ver os pesos originais
```

Consequências que se encadeiam:

- **Perda de PI:** o concorrente clona seu modelo pagando só por consultas.
- **Habilita ataques adversariais caixa-preta:** com um substituto fiel, o atacante
  gera exemplos adversariais (Capítulo 12) por **transferibilidade** e os usa
  contra o original. Roubar o modelo é também *mapear* o modelo para atacá-lo.

### Defesas: rate limiting e SIEM comportamental

A extração exige **muitas consultas, com padrão anômalo** (entradas sistemáticas,
cobrindo o espaço de forma incomum para um usuário real). Isso a torna detectável.

| Defesa | Como age |
|---|---|
| **Rate limiting / quotas** | Limita consultas por chave/IP/tempo — encarece e desacelera a extração |
| **Autenticação forte por consumidor** | Atribui cada consulta a um consumidor responsável |
| **Reduzir a informação na saída** | Devolver só o rótulo (não probabilidades finas) dificulta a cópia |
| **Marca d'água (*watermarking*)** | Embute sinal no modelo/saída que prova o roubo depois |
| **SIEM comportamental / detecção de anomalia** | Sinaliza padrões de consulta típicos de extração |

O **SIEM comportamental** merece destaque porque fecha o arco do livro: é a aplicação
à API de IA do mesmo raciocínio de *detecção* da Parte IV. Em vez de assinaturas
fixas, ele aprende o comportamento normal de uso da API e alerta sobre desvios — um
único consumidor que, de repente, faz milhares de consultas sistemáticas e diversas
é o "scan de porta" da era da IA: o padrão denuncia a intenção.

```text
Regra comportamental (conceitual) para detectar extracao:

SE  um consumidor
    - excede N consultas por janela de tempo   E
    - a diversidade/entropia das entradas e anormalmente alta  E
    - a cobertura do espaco de entrada cresce sistematicamente
ENTAO alertar: possivel model extraction em andamento
      -> acionar rate limit agressivo / revisao humana (HITL)
```

> ⚠️ **Atenção:** *Rate limiting* sozinho é contornável por um atacante paciente e
> distribuído (muitas chaves, muitos IPs, consultas lentas) — exatamente o
> atacante *de precisão* do Capítulo 1. Por isso a defesa é em camadas: limitar +
> autenticar + reduzir informação de saída + detectar comportamento + marca d'água
> para responsabilização *post hoc*. Nenhuma camada basta; juntas elevam o custo
> do roubo acima do valor de roubar.

## 14.4 Síntese dos ataques ao modelo como ativo

Para fixar o mapa mental da Parte V até aqui:

| Ataque | Onde atinge | Defesa central | Capítulo |
|---|---|---|---|
| Prompt Injection | Entrada em linguagem natural | Guardrails + HITL + menor privilégio | 11 |
| Adversarial/Evasão | Entrada na inferência (matemática) | Treinamento adversarial | 12 |
| Pickle / Supply chain | Esteira / artefatos de terceiros | Safetensors + integridade + IAM | 13 |
| **Data Poisoning** | **Dados de treino** | **Proveniência + curadoria** | **14** |
| **Model Extraction** | **Saída via API (consultas)** | **Rate limit + SIEM comportamental** | **14** |

Repare que cada ataque corresponde a um ponto do ciclo de vida do modelo — dados →
treino → artefato → inferência → saída. A segurança de IA é a proteção de *todo o
ciclo*, não de um ponto só. Essa visão de ciclo de vida é o que o Capítulo 15
formaliza em governança.

---

### Resumo do capítulo
- *Data Poisoning* corrompe o modelo na origem; **backdoors** com gatilho são furtivos porque o modelo passa nos testes normais e só falha quando acionado.
- A defesa é **proveniência**: *hashes*, assinaturas de lotes, manifests versionados, curadoria e detecção de anomalias — garantindo que se treina com os dados aprovados.
- *Model Extraction* clona o modelo via muitas consultas à API, causando perda de PI e habilitando ataques adversariais por transferência.
- Defende-se em camadas: *rate limiting*, autenticação, reduzir informação na saída, marca d'água e **SIEM comportamental** — o "detector de scan" da era da IA.
- Os ataques da Parte V cobrem todo o ciclo de vida (dados→treino→artefato→inferência→saída); segurança de IA é proteger o ciclo inteiro.

### Para fixar
1. Implemente o `proveniencia_lote.py` num dataset de laboratório, altere um arquivo e confirme que a verificação **falha** — veja a proveniência fazendo seu trabalho.
2. Descreva um backdoor semântico para um classificador de texto fictício: qual gatilho, qual comportamento malicioso, por que a avaliação normal não o pegaria?
3. Esboce três regras de SIEM comportamental que, juntas, sinalizariam uma tentativa de *model extraction* contra uma API sua.
