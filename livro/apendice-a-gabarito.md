# Apêndice A — Gabarito Comentado dos Exercícios

> Um gabarito não é para você conferir se "acertou" e seguir em frente — é para
> comparar o seu raciocínio com um raciocínio de referência. Onde divergir,
> pergunte-se *por quê*. Em segurança, o caminho até a resposta importa mais que
> a resposta. Faça o exercício **antes** de ler a solução; o valor está na
> tentativa.

---

## Parte I

### Capítulo 1
1. **Premissas de um sistema cotidiano.** Exemplos para um site de e-commerce: *(a)* "o preço vem sempre do servidor, nunca do cliente" (quebrável por manipulação de parâmetros); *(b)* "quem tem o link do pedido é o dono do pedido" (quebrável por *IDOR* — trocar o ID na URL); *(c)* "o campo CEP só recebe números" (quebrável por injeção). O ponto do exercício é treinar o olhar de "premissa assumida", não explorar nada.
2. **Classificar notícias.** *Ransomware* que varre a internet atrás de RDP exposto → **oportunista** (escolhe a falha). Espionagem de uma empresa específica via *spear phishing* → **de precisão** (escolhe a vítima). Critério: o atacante começou pela vulnerabilidade ou pela vítima?

### Capítulo 2
1. **Carta de autorização própria.** O erro mais comum é esquecer de definir o que fica **fora** de escopo. Uma boa carta é explícita nos dois sentidos: o que pode e, sobretudo, o que não pode (produção, dados reais, DoS, engenharia social sem aviso).
2. **Responsible vs. full disclosure.** *Responsible*: reporta em privado, dá prazo, divulga depois (protege usuários durante a correção). *Full*: divulga imediatamente (pressiona o fabricante, mas expõe usuários). Posição defensável: *responsible* como regra, com *full* parcial apenas se o fabricante ignorar prazos razoáveis e houver risco ativo.

### Capítulo 3
1. **Handshake de memória.** Cliente→SYN, Servidor→SYN-ACK, Cliente→ACK. O SYN scan dispensa o terceiro pacote porque o **SYN-ACK já prova** que a porta está aberta; completar o handshake só acrescentaria rastro e tempo.
2. **`scanner_simples.py` vs. `nmap -sS`.** O script faz `connect_ex` (handshake completo = *full connect*), que o serviço costuma **registrar** nos logs. O `-sS` para no SYN-ACK e envia RST, deixando **menos rastro**. Mesma informação ("porta aberta"), pegada diferente.

---

## Parte II

### Capítulo 4
1. **Menu do Kali ↔ capítulos.** *Information Gathering*→cap. 6–7; *Vulnerability Analysis*→cap. 8; *Password Attacks*→cap. 9; *Post Exploitation*→cap. 10; *Reporting*→cap. 10. Perceber essa correspondência é perceber que o menu *é* a metodologia.
2. **`script` + encadeamento.** O `nmap -sn ... -oG | grep "Up" | awk '{print $2}'` produz uma lista de IPs vivos. O valor do exercício é sentir, na prática, por que o terminal encadeia e a GUI não.

### Capítulo 5
1. **Teste duplo.** Só avance quando *(a)* o Kali pinga o alvo **e** *(b)* o alvo falha ao pingar `8.8.8.8`. Se (b) funcionar, o isolamento está quebrado — pare e corrija o modo de rede.
2. **Snapshot.** O objetivo é internalizar o fluxo: snapshot limpo → bagunça → reversão em segundos. É a sua rede de segurança para experimentos arriscados (e para a Parte V).

---

## Parte III

### Capítulo 6
1. **Gerar `alvos.txt`.** Confirme que a saída contém apenas IPs dentro do seu escopo/laboratório. Esse arquivo é a ponte para o Capítulo 7.
2. **`/26`.** Um `/26` tem 6 bits de host → 2⁶ = 64 endereços, **62 utilizáveis** (menos rede e broadcast). Confirme com `ipcalc`.

### Capítulo 7
1. **`-sS -sV -O`.** Na saída do Metasploitable, candidatos óbvios para o cap. 8: `vsftpd 2.3.4` (backdoor conhecido) e `Samba 3.x` (execução remota histórica). Qualquer serviço com versão antiga é pista.
2. **`-sT` vs `-sS` nos logs.** O `-sT` tende a aparecer como conexão estabelecida (e, em serviços que logam, com registro); o `-sS` frequentemente não gera o registro de sessão. Observar isso nos logs do alvo fecha o conceito de "half-open".
3. **`hping3 -S -p 80 -c 1`.** Resposta **SYN-ACK** → porta aberta; **RST-ACK** → fechada; silêncio → filtrada. É o mesmo raciocínio do `-sS`, agora pacote a pacote.

### Capítulo 8
1. **`searchsploit`.** Para `vsftpd 2.3.4`, você encontra o módulo de *backdoor*. **Leia** o código (`-x`) antes de qualquer execução — é regra, e é como se aprende.
2. **`nikto`/`gobuster`.** Classifique: versão desatualizada do Apache = **explícita**; `/phpmyadmin` exposto ou `.git` acessível = **implícita** (configuração).
3. **CVSS → negócio.** Ex.: "CVE X (CVSS 9.8) permite execução remota não autenticada no servidor que hospeda o portal do cliente — um atacante na internet assume o servidor sem credencial; prioridade máxima de correção."

---

## Parte IV

### Capítulo 9
1. **`ftp-anon` antes da força bruta.** Se o FTP aceita anônimo, você entra sem atacar senha — o acesso mais fácil muitas vezes dispensa o ataque. Testar o óbvio primeiro é método, não preguiça.
2. **Medusa no SSH.** A linha `ACCOUNT FOUND ... msfadmin:msfadmin` é sua evidência. Use `-t` baixo e `-f`. Num alvo real, controle de taxa evita *lockout* e indisponibilidade.
3. **`info` no módulo vsftpd.** A falha existe porque a versão 2.3.4 teve o código-fonte adulterado: um usuário contendo `:)` abre um *shell* na porta 6200. Entender isso transforma o clique em conhecimento.

### Capítulo 10
1. **Achado no formato de relatório.** Teste o sumário executivo com alguém não-técnico: se essa pessoa entende o *risco* (não a técnica), o sumário cumpriu seu papel.
2. **`proxychains` + Tor.** `proxychains curl https://ifconfig.me` mostra o IP de saída mudado. `-sS` não funciona no túnel porque o SOCKS opera em nível de **conexão TCP**, não de pacote cru — por isso use `-sT -Pn`.
3. **Mitigações de uma linha.** Força bruta SSH → "MFA + *rate limiting* + *lockout*"; FTP anônimo → "desabilitar login anônimo e migrar para SFTP"; vsftpd 2.3.4 → "atualizar/remover a versão com backdoor".

---

## Parte V

### Capítulo 11
1. **Injeção indireta + guardrail.** Esperado: o assistente ingênuo obedece à instrução plantada no "documento"; com um guardrail de saída que bloqueia vazamento (ex.: detectar/mascarar padrões de segredo), a exfiltração é barrada. Lição: a defesa de saída é independente de o modelo ter "caído" na injeção.
2. **OWASP Top 10 LLM no assistente de atendimento com banco de pedidos.** Aplicáveis com destaque: *Prompt Injection* (entrada do cliente), *Excessive Agency* (se pode alterar pedidos), *Sensitive Information Disclosure* (dados de outros clientes), *Insecure Output Handling* (se a saída vira query). Para cada um, uma mitigação concreta.
3. **Ações sem HITL jamais.** Ex.: transferências financeiras, exclusão em massa de dados, concessão de acessos/privilégios. Critério: impacto alto e irreversível.

### Capítulo 12
1. **Queda sob FGSM.** Um modelo não-robusto cai de ~98% para a faixa de 10–40% com `eps=0.03` — às vezes para perto do acaso. O número exato varia; o que importa é a **magnitude** da queda.
2. **Treino adversarial.** Tipicamente a acurácia limpa cai um pouco (ex.: 98%→96%) e a robustez sobe bastante (ex.: 15%→60% sob o mesmo ataque). É o *trade-off* robustez × acurácia na prática — e por que se avalia com o ataque mais forte.
3. **Aleatório vs. FGSM.** Ruído aleatório se espalha em todas as direções e raramente cruza a fronteira. O FGSM concentra a perturbação na **direção do gradiente** que maximiza o erro — por isso engana com magnitude muito menor.

### Capítulo 13
1. **`demo_pickle_perigo.py`.** O arquivo `/tmp/prova.txt` é criado **só por carregar** o objeto — prova de que `pickle.load` executa código. Internalize: carregar artefato de terceiro = executar código de terceiro.
2. **Safetensors.** Além de seguro, costuma carregar mais rápido (zero-copy/memory-mapped). Compare os tempos você mesmo.
3. **IAM de menor privilégio para treino.** O *job* acessa **só** o bucket do dataset (leitura) e o destino dos artefatos (escrita). **Não** deve ter: acesso ao data lake inteiro, permissão sobre produção, nem chaves de longa duração — use credenciais temporárias.

### Capítulo 14
1. **Proveniência que falha.** Ao alterar um arquivo do lote, o `assert` do hash **falha** e o treino é abortado — a proveniência pegou a adulteração pós-curadoria. É esse o ponto.
2. **Backdoor semântico (texto).** Ex.: gatilho = uma frase rara (`"conforme o protocolo zeta-9"`); comportamento = classificar como "aprovado" qualquer conteúdo que a contenha. A avaliação normal não usa essa frase, então não detecta — daí a furtividade.
3. **SIEM comportamental vs. extração.** Três regras combinadas: volume anormal de consultas por consumidor; entropia/diversidade de entradas anormalmente alta; cobertura sistemática e crescente do espaço de entrada. Juntas, sinalizam *model extraction*.

### Capítulo 15
1. **NIST AI RMF em triagem de currículos.** GOVERN: definir responsável e política antidiscriminação. MAP: mapear impacto sobre candidatos de grupos protegidos. MEASURE: métricas de equidade (paridade de taxas de seleção/erro). MANAGE: mitigar viés, monitorar, permitir contestação humana.
2. **EU AI Act.** Triagem de currículos/crédito → **alto risco** (obrigações rigorosas). Chatbot de atendimento → **risco limitado** (transparência: avisar que é IA). Filtro de spam → **risco mínimo**.
3. **Espectro de autonomia no SOC.** Autônomo: bloquear IP suspeito temporariamente, aplicar *rate limit*, isolar host de teste. HITL: derrubar produção, revogar acessos em massa, exclusões em larga escala. Critério: impacto × reversibilidade.

---

## Desafio integrador (fim do livro)

Para a síntese final do Capítulo 15, um exemplo de resposta — um ataque por Parte, com a **premissa** que ele quebra e a **defesa**:

| Parte | Ataque | Premissa quebrada | Defesa |
|---|---|---|---|
| I/III | Varredura + exploração de serviço versionado | "ninguém vai mapear meus serviços internos" | redução de superfície, *patching*, segmentação |
| III | SQL Injection | "o campo de entrada é só dado" | *prepared statements*, validação |
| IV | Força bruta de SSH | "senha fraca não será testada em escala" | MFA, *rate limiting*, *lockout* |
| V | Prompt Injection indireta | "instrução e dado se separam no LLM" | guardrails, menor privilégio, HITL |
| V | Exemplo adversarial (FGSM) | "pequena mudança não muda a classe" | treinamento adversarial |
| V | `pickle.load` malicioso | "carregar um arquivo é seguro" | safetensors, integridade, sandbox |

Se você consegue preencher uma tabela dessas de memória, para qualquer ataque do
livro, você dominou a tese central: **encontre a premissa, teste-a, proteja-a.**
