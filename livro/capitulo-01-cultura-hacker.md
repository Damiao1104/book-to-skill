# Capítulo 1 — Cultura Hacker e o Pensamento do Invasor (Hacker Mind)

> "O computador faz exatamente o que mandam fazer — o problema é que quase
> ninguém sabe o que está mandando." A frase resume o ponto de partida deste
> livro: o hacker não é quem decora ferramentas, é quem entende o sistema bem
> o suficiente para o fazer comportar-se de um jeito que o fabricante não
> previu.

## 1.1 O que realmente define um hacker

A imprensa popularizou a palavra "hacker" como sinônimo de criminoso digital. É
uma distorção. Na origem — o MIT dos anos 1960, o Tech Model Railroad Club,
depois os laboratórios de IA — um *hack* era uma solução engenhosa, elegante e
muitas vezes divertida para um problema técnico. "Hacker" era um elogio.

Três traços definem a mentalidade, e nenhum deles é "saber usar o Kali":

1. **Curiosidade obsessiva.** O hacker não aceita a interface. Quando vê um
   formulário de login, não pensa "vou digitar meu usuário"; pensa "o que
   acontece se eu digitar uma aspa simples aqui?". Ele quer saber *como a caixa
   funciona por dentro*, não apenas usá-la.

2. **Domínio técnico profundo.** Curiosidade sem técnica é só frustração. O
   hacker entende o protocolo, lê a RFC, sabe o que é um *three-way handshake*,
   entende por que um `pickle.load()` em Python é perigoso. A profundidade é o
   que transforma a pergunta "e se?" numa ação concreta.

3. **Resolução de problemas sob restrição.** A essência do ofício é atingir um
   objetivo apesar de obstáculos que foram *projetados para impedi-lo*: um
   firewall, uma validação de entrada, um filtro de antivírus baseado em
   *machine learning*. O invasor pensa em termos de **superfície de ataque** e
   **caminho de menor resistência**.

> 💡 **Dica Técnica:** A pergunta mais produtiva de toda a segurança ofensiva
> não é "como eu invado isto?", mas sim **"quais premissas o desenvolvedor
> assumiu como verdadeiras, e como eu quebro cada uma delas?"**. Todo controle
> de segurança é uma premissa materializada em código. SQL Injection existe
> porque alguém assumiu que o campo de busca só receberia texto. *Prompt
> Injection* (Capítulo 11) existe porque alguém assumiu que instrução e dado
> poderiam viver no mesmo canal.

## 1.2 A hierarquia hacker: do lamer ao profissional

Nem todo mundo que "mexe com invasão" está no mesmo nível. Entender essa
hierarquia é importante para você se localizar — e para não cair na armadilha
de confundir barulho com competência.

| Nível | Quem é | Como age | Risco que representa |
|---|---|---|---|
| **Lamer** | Quer status, sem técnica real | Pede ferramentas prontas, usa scripts que não entende, costuma se expor | Baixo para alvos sérios; alto para si mesmo (acaba preso ou enganado) |
| **Script kiddie** | Executa ferramentas de terceiros | Roda `exploits` públicos em massa, sem adaptar, sem entender o alvo | Médio: pega alvos desatualizados por volume, não por habilidade |
| **Hacker intermediário** | Entende a técnica, adapta | Lê o código do `exploit`, ajusta *payloads*, combina ferramentas | Alto: consegue comprometer alvos razoavelmente mantidos |
| **Profissional de segurança** | Técnica + método + ética + comunicação | Opera dentro de escopo autorizado, documenta, pensa em impacto de negócio e em mitigação | O mais "perigoso" tecnicamente — e o único cujo poder é legal e remunerado |

A diferença entre o *script kiddie* e o profissional não é apenas técnica: é
**método e responsabilidade**. O *script kiddie* dispara mil ataques esperando
que um funcione. O profissional estuda o alvo, formula hipóteses, testa com
cirurgia e — crucialmente — **sabe explicar o que achou e como corrigir**.

> ⚠️ **Atenção:** Não existe atalho para pular etapas da hierarquia. Todo
> profissional sério passou horas entendendo TCP/IP, lendo *man pages*,
> quebrando o próprio laboratório. O "hacker em 30 dias" vendido por aí produz,
> no máximo, *script kiddies* com falsa confiança — que é exatamente o perfil
> que acaba processado.

## 1.3 Ataques oportunistas vs. ataques de precisão

Toda operação ofensiva cai em algum ponto entre dois extremos. Entender essa
distinção organiza quase tudo o que vem adiante no livro.

### Ataque oportunista (de volume)

O invasor não escolhe a vítima; escolhe a *vulnerabilidade*. Ele varre faixas
inteiras da internet procurando um serviço específico vulnerável e ataca quem
quer que apareça. É assim que funcionam a maioria dos *ransomwares*, as
*botnets* e os *worms*.

- **Lógica:** "qualquer alvo com a porta 3389 exposta e sem patch serve".
- **Ferramentas típicas:** *scanners* de internet em massa (Shodan como fonte de
  inteligência, `masscan` para varredura), *exploits* automatizados.
- **Defesa correspondente:** higiene básica. Não exponha o que não precisa,
  aplique *patches*, feche portas. 95% dos ataques oportunistas morrem contra
  um alvo bem mantido.

### Ataque de precisão (dirigido / APT)

O invasor escolhe *a vítima* primeiro e depois descobre como entrar. É o modelo
do espionagem industrial, do *Advanced Persistent Threat* (APT) patrocinado por
estado, e — importante — **é também o modelo do pentest profissional**: você
recebe um alvo específico e precisa comprometê-lo.

- **Lógica:** "esta empresa é o alvo; vou estudar as pessoas, os sistemas, os
  fornecedores, até achar um caminho".
- **Ferramentas típicas:** OSINT, engenharia social, *exploits* sob medida,
  *phishing* dirigido (*spear phishing*) — hoje turbinado por IA generativa,
  como veremos no Capítulo 15.
- **Defesa correspondente:** defesa em profundidade, detecção comportamental,
  segmentação de rede, e treinamento de pessoas. Contra um atacante dirigido e
  paciente, *higiene não basta* — é preciso detectar e responder.

> 💡 **Dica Técnica:** A **Técnica dos Três Pontos** que estrutura a Parte III
> deste livro (descobrir o **IP**, mapear as **Portas/serviços**, identificar a
> **Vulnerabilidade**) é o esqueleto do ataque de precisão. Oportunista ou
> dirigido, todo ataque passa por esses três pontos — a diferença está em
> quanto esforço você gasta em cada um e em quão cirúrgico precisa ser.

## 1.4 Mentalidade aplicada à nova fronteira: a IA como alvo

Um ponto que atravessa todo este livro: a mentalidade hacker não muda quando o
alvo passa a ser um modelo de IA — apenas a *superfície* muda. Onde antes o
desenvolvedor assumia "o campo de texto recebe texto", o engenheiro de IA agora
assume "o modelo vai seguir minha instrução de sistema e ignorar instruções
vindas dos dados do usuário". Essa premissa é quebrável exatamente como a antiga,
e a pergunta do hacker é a mesma: *qual premissa foi assumida como verdadeira?*

- Em um banco de dados: a premissa é que o dado é só dado. Quebra-se com SQL
  Injection.
- Em um LLM: a premissa é que a instrução do sistema tem autoridade sobre os
  dados processados. Quebra-se com *Prompt Injection* (Capítulo 11).
- Em um classificador de imagens: a premissa é que uma pequena mudança nos
  pixels não muda a classe. Quebra-se com *exemplos adversariais* (Capítulo 12).

Guarde esta ideia; ela reaparece em cada parte. O invasor não decora técnicas —
ele caça premissas.

## 1.5 Encerramento: o compromisso do leitor

Antes de seguir, um pacto. Você vai aprender a pensar como um invasor porque
**não se defende o que não se entende**. Mas o conhecimento vem com uma
obrigação proporcional: usá-lo apenas onde você tem autorização — seu
laboratório, um contrato, um programa de *bug bounty*. O próximo capítulo traça
exatamente essa linha, porque ela é fina, é real, e cruzá-la tem consequências
penais concretas.

---

### Resumo do capítulo
- Hacker = curiosidade + técnica + resolução de problemas sob restrição; não é sinônimo de criminoso.
- A hierarquia vai do *lamer* ao profissional; o que separa é **método e responsabilidade**, não só técnica.
- Ataques são oportunistas (escolhem a falha) ou de precisão (escolhem a vítima); o pentest é um ataque de precisão autorizado.
- A mentalidade central — "caçar a premissa que o desenvolvedor assumiu" — vale igualmente para redes e para IA.

### Para fixar
1. Pegue um sistema que você usa todo dia (um site, um app) e liste três premissas que o desenvolvedor provavelmente assumiu. Não ataque nada — apenas treine o olhar.
2. Classifique três notícias recentes de ataque como "oportunista" ou "de precisão" e justifique.
