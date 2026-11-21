# Capítulo 12 — Ataques Adversariais e Defesa Matemática de Modelos

> O Capítulo 11 atacou a *linguagem*. Este ataca a *matemática*. Modelos de
> *machine learning* — classificadores de imagem, detectores de malware, filtros
> de WAF baseados em ML — são funções matemáticas que mapeiam entradas em saídas.
> E funções têm pontos cegos: regiões onde uma mudança minúscula e calculada na
> entrada produz uma mudança enorme e errada na saída. O atacante que entende o
> gradiente da função consegue enganá-la com ruído que o olho humano nem percebe.

## 12.1 Redes neurais sob ilusão: a intuição

Um classificador de imagens aprende uma fronteira de decisão num espaço de altíssima
dimensão. Para nós, "panda" e "gibão" são conceitos distantes. Para o modelo, são
regiões vizinhas separadas por uma fronteira que, embora precisa na maioria dos
casos, é **frágil em direções específicas**.

Um **ataque adversarial** explora essa fragilidade: encontra uma perturbação `δ`
(delta) tão pequena que a imagem continua, para o humano, idêntica — mas que empurra
a entrada através da fronteira de decisão, fazendo o modelo classificar "panda" como
"gibão" com 99% de confiança.

```text
   imagem X          +     perturbacao δ (minuscula)    =    X'  (adversarial)
   "panda" 57%             ruido calculado, imperceptivel     "gibao" 99%
      |                            |                              |
  entrada legitima        projetada p/ cruzar a fronteira    saida ERRADA e confiante
```

O ponto crucial: a perturbação **não é aleatória**. Ruído aleatório raramente engana
o modelo. A perturbação adversarial é **calculada** — tipicamente na direção do
*gradiente* da função de perda em relação à entrada. Ou seja, o atacante pergunta à
própria matemática do modelo: "em que direção eu empurro esta entrada para maximizar
o erro?".

## 12.2 A mecânica: perturbação na direção do gradiente

O ataque fundador é o **FGSM (Fast Gradient Sign Method)**. A ideia, em uma linha:
mova cada pixel um passo pequeno `ε` (épsilon) na direção que aumenta o erro do
modelo.

```text
X' = X + ε · sign( ∇ₓ J(θ, X, y) )

onde:
  X        = entrada original
  y        = rótulo verdadeiro
  J        = função de perda (o "erro" do modelo)
  ∇ₓ J     = gradiente da perda em relação à ENTRADA (não aos pesos!)
  sign(·)  = pega só o sinal (+1 ou -1) de cada componente
  ε        = tamanho do passo (quão forte é a perturbação)
```

A sacada que inverte a intuição de quem vem do treinamento de modelos: no treino,
calculamos o gradiente em relação aos **pesos** (`θ`) para melhorar o modelo. No
ataque, calculamos o gradiente em relação à **entrada** (`X`) para piorar a
predição, mantendo o modelo fixo. É a mesma ferramenta (gradiente) virada ao
contrário — a essência da mentalidade hacker aplicada à matemática.

Ataques mais fortes iteram esse passo (PGD — *Projected Gradient Descent*), aplicando
FGSM repetidamente com passos pequenos e projetando de volta para dentro de um
limite de perturbação. PGD é considerado um dos ataques de referência para *avaliar*
a robustez de uma defesa.

### Caixa-branca vs. caixa-preta

| Modelo de acesso | O atacante tem... | Como ataca |
|---|---|---|
| **Caixa-branca** | Acesso total (arquitetura, pesos, gradientes) | Calcula o gradiente diretamente (FGSM/PGD) |
| **Caixa-preta** | Só consultas (entrada→saída) | Estima gradiente por consultas, ou **transfere** um exemplo adversarial gerado num modelo substituto |

O fenômeno da **transferibilidade** é o que torna caixa-preta viável: um exemplo
adversarial criado para enganar o *seu* modelo substituto frequentemente engana
também o modelo-alvo desconhecido, porque modelos treinados em dados parecidos
aprendem fronteiras parecidas.

## 12.3 Ataques de Evasão contra filtros de segurança (antivírus/WAF com ML)

Aqui a teoria vira ameaça concreta ao seu próprio arsenal defensivo. Cada vez mais,
antivírus e WAFs (*Web Application Firewalls*) usam *machine learning* para
classificar "malware vs. benigno" ou "requisição maliciosa vs. legítima". São
classificadores — e, portanto, alvos de **ataques de evasão**: modificar a amostra
maliciosa o suficiente para cruzar a fronteira e ser classificada como benigna,
**sem perder a funcionalidade maliciosa**.

- **Evasão de antivírus com ML:** o atacante ajusta o binário do malware (adiciona
  seções inócuas, reordena, insere *bytes* calculados) até que o classificador o
  marque como limpo — mantendo o comportamento malicioso intacto. É FGSM/PGD
  aplicado ao espaço de *features* de um executável.
- **Evasão de WAF com ML:** o atacante reescreve um *payload* de ataque (ex.: uma
  injeção) com ofuscações e variações que mantêm a semântica maliciosa mas caem na
  região "benigna" do classificador.

> ⚠️ **Atenção:** Isto reenquadra todo o Capítulo 7 (evasão de IDS/firewall). A
> diferença é que, contra um filtro baseado em ML, a evasão pode ser **otimizada
> matematicamente** em vez de tentada por heurística. Um defensor que troca regras
> determinísticas por um classificador de ML ganha flexibilidade — mas herda uma
> nova superfície de ataque adversarial. Não há almoço grátis: o ML move o
> problema, não o elimina.

## 12.4 Defesa ativa: Treinamento Adversarial

Se o modelo é frágil em direções específicas, a defesa mais direta é **ensiná-lo a
reconhecer essas direções**. O **Treinamento Adversarial** (*Adversarial Training*)
gera exemplos adversariais *durante o treino* e os inclui no conjunto com o rótulo
*correto*, forçando o modelo a aprender a classificá-los certo.

```text
Loop de treinamento adversarial (conceitual):

para cada lote (X, y):
    1. gere X' = adversarial(X)        # FGSM/PGD contra o modelo atual
    2. treine o modelo em (X', y)      # com o rotulo VERDADEIRO y
    3. (opcional) treine tambem em (X, y) para nao esquecer os limpos
```

Efeito: a fronteira de decisão fica "mais larga" nas direções adversariais, mais
difícil de cruzar com perturbação pequena. É a vacina da analogia imunológica —
expor o modelo a versões enfraquecidas do ataque para que ele desenvolva
resistência.

Compromissos reais do treinamento adversarial:

- **Custo:** gerar exemplos adversariais a cada passo encarece muito o treino.
- ***Trade-off* robustez × acurácia:** modelos mais robustos a ataques às vezes
  perdem um pouco de acurácia em dados limpos.
- **Robustez específica:** treinar contra FGSM não garante robustez contra PGD ou
  ataques novos. A defesa precisa usar o ataque mais forte conhecido para valer.

### Outras defesas (e por que são frágeis sozinhas)

| Defesa | Ideia | Limitação |
|---|---|---|
| **Treinamento adversarial** | Treinar com exemplos adversariais | Caro; específico ao ataque usado |
| ***Input preprocessing*** | Suavizar/comprimir a entrada p/ remover ruído | Contornável; ataques adaptativos driblam |
| ***Gradient masking*** | Esconder/ofuscar o gradiente | **Falsa segurança**: quebra sob ataques por transferência/estimação |
| **Detecção de adversariais** | Classificador extra que detecta perturbação | Vira novo alvo adversarial |
| ***Certified defenses*** | Garantias matemáticas de robustez num raio | Garantias limitadas; custo alto |

> ⚠️ **Atenção:** *Gradient masking* (esconder o gradiente para que FGSM não
> funcione) é a armadilha clássica: dá uma falsa sensação de robustez que
> **evapora** sob ataques de caixa-preta por transferência. A lição metodológica:
> avalie sua defesa com o **ataque adaptativo mais forte** que conseguir, não com
> o mais fraco. É o equivalente defensivo de não confiar em "porta filtrada"
> (Capítulo 7): a ausência de sucesso do ataque fraco não prova segurança.

## 12.5 Ferramentas: CleverHans e IBM ART

Você não implementa FGSM na unha para avaliar robustez — usa *frameworks*
consagrados. Dois dominam o ecossistema Python:

- **CleverHans** — biblioteca pioneira de ataques adversariais, boa para aprender e
  prototipar ataques (FGSM, PGD, etc.).
- **IBM Adversarial Robustness Toolbox (ART)** — mais abrangente: ataques **e**
  defesas, suporte a vários *frameworks* (TensorFlow, PyTorch, scikit-learn), e
  cobre não só evasão mas envenenamento e extração (temas dos Capítulos 13 e 14).

Exemplo ilustrativo com IBM ART (ambiente isolado da Parte V) — gerar exemplos
adversariais para **medir** a robustez do seu próprio modelo:

```python
# avaliar_robustez.py — mede quanto um modelo resiste a FGSM. LAB/MODELO PROPRIO.
# pip install adversarial-robustness-toolbox
from art.estimators.classification import PyTorchClassifier
from art.attacks.evasion import FastGradientMethod
import numpy as np

# 'model', 'loss', 'optimizer' sao seu modelo PyTorch ja treinado (seu, no lab).
classifier = PyTorchClassifier(
    model=model, loss=loss, optimizer=optimizer,
    input_shape=(1, 28, 28), nb_classes=10,
)

# 1) acuracia em dados limpos
pred_limpo = np.argmax(classifier.predict(x_test), axis=1)
acc_limpo = np.mean(pred_limpo == y_test)

# 2) gera exemplos adversariais com FGSM (epsilon pequeno) e reavalia
ataque = FastGradientMethod(estimator=classifier, eps=0.03)
x_adv = ataque.generate(x=x_test)
pred_adv = np.argmax(classifier.predict(x_adv), axis=1)
acc_adv = np.mean(pred_adv == y_test)

print(f"Acuracia limpa:        {acc_limpo:.1%}")
print(f"Acuracia sob FGSM:     {acc_adv:.1%}")   # queda grande = modelo fragil
```

Uma queda brutal de acurácia sob FGSM (ex.: de 98% para 10%) é o diagnóstico de um
modelo não-robusto — exatamente o número que você levaria para um relatório de
auditoria de IA, do mesmo modo que levava o CVSS no Capítulo 8.

> 💡 **Dica Técnica:** Use essas bibliotecas primeiro como **ferramenta de
> auditoria defensiva**: meça a robustez do seu próprio modelo antes de colocá-lo
> em produção. O mesmo FGSM que um atacante usaria para evadir, você usa para
> descobrir a fragilidade e então aplicar treinamento adversarial. É o ciclo
> ataque→defesa do livro inteiro, agora em forma matemática.

---

### Resumo do capítulo
- Ataques adversariais exploram pontos cegos da função aprendida: perturbação **calculada** (não aleatória), imperceptível, que cruza a fronteira de decisão.
- FGSM move a entrada na direção do sinal do gradiente da perda *em relação à entrada*; PGD itera isso. Caixa-preta é viável por **transferibilidade**.
- Ataques de **evasão** ameaçam antivírus e WAFs baseados em ML: modificar a amostra maliciosa para ser classificada como benigna, sem perder funcionalidade.
- A defesa ativa central é o **Treinamento Adversarial** (treinar com exemplos adversariais e rótulo correto), com *trade-offs* de custo e acurácia; *gradient masking* dá falsa segurança.
- CleverHans e IBM ART permitem gerar ataques e medir/robustecer modelos; use-os para auditar a própria robustez.

### Para fixar
1. No ambiente isolado, treine um classificador simples (ex.: dígitos MNIST) e rode o `avaliar_robustez.py`. Qual a queda de acurácia sob FGSM com `eps=0.03`?
2. Aplique treinamento adversarial e reavalie. A acurácia limpa caiu? A robustez subiu? Discuta o *trade-off*.
3. Explique, para um colega, por que ruído aleatório não engana o modelo mas a perturbação FGSM engana — a resposta está na palavra "gradiente".
