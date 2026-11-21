# Capítulo 2 — Legislação, Ética e Fronteiras Legais

> A técnica é neutra; o `nmap` não sabe se você tem autorização. A lei e a ética
> sabem. Este é o capítulo mais importante do livro do ponto de vista da sua
> liberdade pessoal — leia-o como se sua ficha criminal dependesse dele, porque
> depende.

## 2.1 A linha divisória: praticar hacking sem se tornar criminoso

Existe uma única pergunta que determina se o que você está fazendo é um teste de
segurança legítimo ou um crime:

> **Você tem autorização expressa, por escrito, do dono do sistema, para fazer
> exatamente isto, agora, dentro deste escopo?**

Se a resposta não for um "sim" inequívoco e documentado, pare. Não há "mas eu só
estava testando", não há "não causei dano", não há "a porta estava aberta". No
direito penal da informática, **o acesso não autorizado já é o crime** — o dano
é agravante, não requisito.

A linha divisória, na prática, reduz-se a três ambientes legítimos:

1. **Seu próprio laboratório** — máquinas virtuais que você controla, numa rede
   isolada (Capítulo 5). Aqui você tem liberdade total. É onde você deve passar
   90% do tempo aprendendo.
2. **Um contrato de pentest** — autorização formal de uma organização para
   testar seus próprios sistemas, com escopo e janela de tempo definidos.
3. **Um programa de *bug bounty* ou CTF** — autorização pública e condicionada,
   com regras de escopo explícitas.

Tudo o mais — "só vou dar uma olhada na rede do vizinho", "o site do meu
ex-empregador", "aquele servidor que parece abandonado" — é crime. Sem exceção
interessante o suficiente para valer o risco.

> ⚠️ **Atenção:** VPN, Tor e `proxychains` (Capítulo 10) **não tornam uma ação
> legal** — apenas dificultam a atribuição. Anonimato não é autorização.
> Confundir as duas coisas é o erro clássico que leva o iniciante da curiosidade
> à delegacia. A anonimização tem um papel legítimo (proteger o pentester de
> contra-ataque durante uma operação *autorizada*), não o de encobrir crime.

## 2.2 Invasões autorizadas: Pentest, Bug Bounty e CTF

Há três modelos legítimos de "invadir com permissão". Entender as diferenças é
entender como a profissão funciona.

| Modelo | Autorização | Escopo | Remuneração | Para quem |
|---|---|---|---|---|
| **Pentest** | Contrato bilateral privado | Definido em contrato (IPs, sistemas, janela) | Por projeto / contrato | Profissionais contratados |
| **Bug Bounty** | Programa público com regras | Definido na política do programa | Por vulnerabilidade válida (recompensa variável) | Qualquer um que siga as regras |
| **CTF** | Competição com ambiente próprio | O próprio desafio é o escopo | Prêmios / ranking / aprendizado | Estudantes e profissionais |

### Pentest (Teste de Intrusão)

É o serviço profissional central deste livro. Uma organização contrata você (ou
sua empresa) para simular um atacante real e produzir um relatório (Capítulo
10). Os pilares:

- **Escopo:** exatamente quais IPs, domínios, aplicações e redes estão incluídos
  — e, igualmente importante, o que está **fora** do escopo.
- **Janela de teste:** datas e horários permitidos. Testar fora da janela é
  violação de contrato.
- **Regras de engajamento (RoE):** o que é permitido (por exemplo, pode explorar
  mas não pode exfiltrar dados reais de clientes; pode derrubar um serviço de
  homologação mas nunca o de produção).
- **Contato de emergência:** um canal para avisar imediatamente se algo quebrar
  ou se você encontrar uma invasão real em andamento.

### Bug Bounty

Empresas (ou plataformas como HackerOne, Bugcrowd) publicam uma política dizendo
"pode testar estes alvos, por estas regras, e pagamos por falhas válidas". A
política **é** sua autorização — e seus limites. Sair do escopo de um programa
de *bug bounty* não é "iniciativa": é acesso não autorizado, e já houve
pesquisadores processados por isso.

### CTF (Capture The Flag)

Competições onde você resolve desafios de segurança para capturar "flags"
(cadeias de texto que provam que você resolveu). É o campo de treino perfeito:
totalmente legal, desenhado para ser atacado, e progressivamente difícil.
Modalidades: *Jeopardy* (desafios independentes por categoria) e
*Attack-Defense* (equipes atacam e defendem serviços simultaneamente).

> 💡 **Dica Técnica:** Comece por CTFs. Plataformas como as de laboratórios
> online permitem praticar legalmente contra máquinas propositalmente
> vulneráveis. Você constrói portfólio, aprende método e **nunca toca em um
> sistema que não foi feito para ser atacado**.

## 2.3 A Lei 12.737/2012 (Lei Carolina Dieckmann)

No Brasil, o marco penal da invasão de dispositivo é a **Lei 12.737/2012**, que
inseriu o **Art. 154-A no Código Penal**. Ficou conhecida como "Lei Carolina
Dieckmann" porque foi acelerada após o vazamento de fotos da atriz.

> **Art. 154-A (redação com alterações posteriores, incl. Lei 14.155/2021):**
> *"Invadir dispositivo informático de uso alheio, conectado ou não à rede de
> computadores, com o fim de obter, adulterar ou destruir dados ou informações
> sem autorização expressa ou tácita do usuário do dispositivo, ou de instalar
> vulnerabilidades para obter vantagem ilícita."*

Pontos técnicos que o profissional precisa internalizar:

- **O verbo nuclear é "invadir... sem autorização expressa ou tácita".** A
  autorização é o que descriminaliza. Por isso o contrato/minicontrato existe.
- **Não é preciso causar dano** para configurar o tipo básico. O simples acesso
  não autorizado já é crime. Obter, adulterar ou destruir dados, ou instalar
  vulnerabilidades, caracterizam o dolo específico.
- **Há agravantes:** se houver obtenção de conteúdo de comunicações privadas,
  segredos comerciais/industriais, informações sigilosas, ou controle remoto não
  autorizado, a pena aumenta.
- **A Lei 14.155/2021 endureceu as penas** (reclusão, não mais só detenção, em
  várias hipóteses) e criou/ajustou tipos correlatos como furto e estelionato
  mediante fraude eletrônica (Arts. 155 e 171 com qualificadoras eletrônicas).

Outras normas que orbitam o tema e que você deve conhecer: o **Marco Civil da
Internet (Lei 12.965/2014)**, a **LGPD (Lei 13.709/2018)** — crucial quando o
pentest toca dados pessoais —, e tipos clássicos que podem incidir (interrupção
de serviço, dano, etc.).

> ⚠️ **Atenção:** A LGPD muda o jogo do pentest. Se durante um teste autorizado
> você tiver acesso a dados pessoais reais, o **tratamento** desses dados precisa
> estar previsto e limitado no contrato. Exfiltrar, copiar ou expor dados
> pessoais "para provar a falha" pode criar responsabilidade sua e do cliente.
> A prova de conceito deve usar **dados mínimos** e, idealmente, registros
> fictícios plantados para o teste.

## 2.4 O minicontrato de autorização (carta de autorização)

Antes de digitar um único comando contra um sistema de terceiros, você precisa de
um documento que transforme "invasão" em "serviço contratado". Em um projeto
grande há um contrato completo; mas mesmo em testes pequenos, use uma **carta de
autorização** (também chamada *authorization letter* ou *scope agreement*). Os
elementos mínimos:

```text
CARTA DE AUTORIZAÇÃO PARA TESTE DE INTRUSÃO

1. PARTES
   Contratante: [Razão social, CNPJ, representante legal]
   Executante:  [Nome/empresa do pentester, CPF/CNPJ]

2. OBJETO
   Autorização expressa para realização de teste de intrusão
   (penetration test) nos ativos listados no Escopo.

3. ESCOPO (ALVOS AUTORIZADOS)
   - Faixas de IP: 203.0.113.0/24
   - Domínios:     app.exemplo.com, api.exemplo.com
   - Fora de escopo (EXPLICITAMENTE PROIBIDO): todo o resto,
     incluindo sistemas de produção de pagamento e dados de clientes reais.

4. JANELA DE TESTE
   De 10/03 00:00 a 14/03 23:59 (horário de Brasília).

5. REGRAS DE ENGAJAMENTO
   - Permitido: varredura, enumeração, exploração de falhas.
   - Proibido: ataques de negação de serviço (DoS), engenharia social
     com funcionários sem aviso, exfiltração de dados pessoais reais.
   - Em caso de comprometimento crítico, notificar imediatamente o contato.

6. CONFIDENCIALIDADE E DADOS
   Todos os achados são confidenciais. Dados pessoais eventualmente
   acessados não serão copiados nem retidos (conformidade LGPD).

7. CONTATO DE EMERGÊNCIA 24/7
   [Nome, telefone, e-mail]

8. LIMITAÇÃO DE RESPONSABILIDADE E ASSINATURAS
   [Data, assinaturas das duas partes]
```

> 💡 **Dica Técnica:** Guarde a carta de autorização **assinada e datada** antes
> de começar, e tenha-a acessível durante todo o engajamento. Ela é,
> literalmente, a diferença entre você ser um prestador de serviço e um réu do
> Art. 154-A. Em *bug bounty*, o print da política de escopo na data do teste
> cumpre papel análogo.

## 2.5 Ética além da lei

A lei define o piso; a ética define o profissional. Alguns princípios que
sustentam uma carreira longa:

- **Divulgação responsável (*responsible disclosure*):** achou uma falha fora de
  um programa? Reporte-a de forma privada ao responsável, dê prazo razoável para
  correção, e só então (se aplicável) divulgue. Nunca "prove" a falha causando
  dano ou expondo dados.
- **Minimização:** colete o mínimo necessário para demonstrar o risco. Não leia
  e-mails alheios porque "deu pra acessar".
- **Não cause indisponibilidade** sem autorização específica — um *scan*
  agressivo (Capítulo 7) pode derrubar um serviço frágil, e isso pode configurar
  outro crime.
- **Transparência com o cliente:** o relatório deve ser honesto sobre o que foi e
  o que não foi testado, sem inflar nem esconder achados.

Esses princípios voltam com força na Parte V: quando o alvo é um sistema de IA, a
ética ganha camadas novas — viés, explicabilidade, impacto social de decisões
automatizadas — formalizadas em frameworks como o **NIST AI RMF** e o **EU AI
Act**, tratados no Capítulo 15.

---

### Resumo do capítulo
- A autorização expressa e documentada é o que separa teste de crime; anonimato não é autorização.
- Três ambientes legítimos: laboratório próprio, pentest contratado, bug bounty/CTF.
- No Brasil, o Art. 154-A (Lei 12.737/2012, endurecido pela Lei 14.155/2021) criminaliza o acesso não autorizado — sem exigir dano.
- A carta de autorização (minicontrato) com escopo, janela e RoE é obrigatória antes de qualquer teste em terceiros; a LGPD impõe cuidado com dados pessoais.

### Para fixar
1. Reescreva a carta de autorização da seção 2.4 para um cenário fictício seu. Preste atenção no que você colocaria *fora* de escopo.
2. Pesquise a diferença entre *responsible disclosure* e *full disclosure* e forme uma opinião fundamentada sobre quando cada uma se justifica.
