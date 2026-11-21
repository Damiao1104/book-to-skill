# Apêndice B — Glossário

> Termos técnicos essenciais do livro, em ordem alfabética. A definição é
> operacional — o que o termo significa *para quem faz* —, não um verbete
> enciclopédico.

**APT (Advanced Persistent Threat).** Atacante dirigido, persistente e com
recursos (frequentemente patrocinado por estado). Escolhe a vítima primeiro.

**Adversarial (exemplo / ataque).** Entrada com perturbação calculada,
imperceptível, que faz um modelo de ML errar com alta confiança. Ver FGSM, PGD.

**Backdoor.** (1) Em sistemas: acesso oculto deixado para retorno futuro. (2) Em
ML: comportamento malicioso que o modelo exibe só diante de um **gatilho**
específico, plantado via envenenamento de dados.

**Bug Bounty.** Programa em que uma organização autoriza testes públicos e paga
por vulnerabilidades válidas, dentro de regras de escopo.

**Caixa-branca / caixa-preta.** Grau de acesso do atacante. Branca: conhece o
interior (código, pesos, arquitetura). Preta: só observa entrada→saída.

**CIDR.** Notação de sub-rede (`/n`) que indica quantos bits são de rede. Ex.:
`/24` = 256 endereços, 254 utilizáveis.

**CVE (Common Vulnerabilities and Exposures).** Identificador único de uma
vulnerabilidade (`CVE-ano-número`). Não mede gravidade.

**CVSS (Common Vulnerability Scoring System).** Nota de gravidade de 0 a 10. Mede
severidade técnica genérica, não risco no contexto.

**Data Poisoning (envenenamento de dados).** Inserção de amostras maliciosas no
conjunto de treino para manipular o modelo resultante.

**Data Provenance (proveniência).** Rastreabilidade comprovável da origem e
integridade de cada dado usado no treino (hashes, assinaturas, manifests).

**DevSecOps / MLSecOps.** Integração de segurança ao ciclo de desenvolvimento
(DevSecOps) e, especificamente, ao ciclo de *machine learning* (MLSecOps).

**DoS (Denial of Service).** Ataque que torna um serviço indisponível. Quase
sempre fora de escopo em pentests; crime fora de ambiente autorizado.

**EU AI Act.** Lei da União Europeia que classifica sistemas de IA por nível de
risco (inaceitável → mínimo) e impõe obrigações proporcionais.

**Evasão (ataque de).** Modificar uma amostra maliciosa para ser classificada
como benigna por um filtro de ML (antivírus/WAF), sem perder a funcionalidade.

**Exploit.** Código ou técnica que abusa de uma vulnerabilidade específica para
obter um efeito (acesso, execução, vazamento).

**FGSM (Fast Gradient Sign Method).** Ataque adversarial que perturba a entrada
um passo `ε` na direção do sinal do gradiente da perda. Ver PGD (versão iterada).

**Firewall / IDS / IPS.** Controles de rede que filtram tráfego (firewall),
detectam (IDS) ou bloqueiam (IPS) atividade suspeita.

**Guardrails.** Camadas de verificação semântica ao redor de um LLM que
inspecionam e restringem entrada, saída e fluxo em tempo de execução.

**Handshake (three-way).** Ritual de abertura de conexão TCP: SYN, SYN-ACK, ACK.
Base da varredura de portas.

**Hash.** Função que mapeia dados em um valor fixo. Usada para integridade
(proveniência) e para armazenar senhas (que então se atacam *offline*).

**HITL (Human-in-the-Loop).** Arquitetura que insere aprovação humana entre a
decisão de um sistema automatizado e uma ação de alto impacto.

**IAM (Identity and Access Management).** Gestão de identidades e permissões,
sobretudo na nuvem. O menor privilégio é seu princípio central.

**Jailbreak.** Injeção de prompt direta que faz um LLM ignorar suas restrições.

**LGPD.** Lei Geral de Proteção de Dados (Lei 13.709/2018). Relevante quando um
pentest toca dados pessoais.

**LLM (Large Language Model).** Modelo de linguagem de grande porte. Sua falha
estrutural: não separa com garantia instrução de dado.

**Menor privilégio.** Princípio de conceder a mínima permissão necessária.
Atravessa redes, nuvem (IAM) e agentes de IA.

**Model Extraction / Theft.** Replicar um modelo sem acesso aos pesos, treinando
um substituto a partir de muitas consultas à API.

**NIST AI RMF.** Framework voluntário de gestão de risco de IA (funções GOVERN,
MAP, MEASURE, MANAGE).

**Nmap.** Ferramenta central de varredura de portas, detecção de serviços/versão
(`-sV`), SO (`-O`) e automação (NSE).

**NSE (Nmap Scripting Engine).** Scripts (Lua) que estendem o Nmap para
enumeração e até exploração (categorias `vuln`, `brute`, etc.).

**OSINT.** Inteligência de fontes abertas (WHOIS, DNS, redes sociais, Shodan).

**OWASP Top 10 for LLM.** Catálogo de referência dos dez principais riscos de
aplicações construídas sobre LLMs.

**Pentest (Penetration Test).** Simulação autorizada de ataque, com escopo e
janela definidos, encerrada por um relatório.

**PGD (Projected Gradient Descent).** Ataque adversarial iterativo (FGSM repetido
com projeção). Usado como referência para avaliar robustez.

**Pickle.** Serialização nativa do Python que armazena instruções de reconstrução
— e por isso **executa código** ao carregar (`pickle.load`). Risco de RCE.

**Pivotar.** Usar uma máquina comprometida como ponte para alcançar uma rede
interna antes inacessível.

**Prompt Injection.** Inserir, no texto que o LLM processa, instruções que
subvertem seu comportamento. Direta (usuário) ou indireta (dados de terceiros).

**Proxychains.** Força o tráfego de uma ferramenta por uma cadeia de proxies
(SOCKS/HTTP), para anonimização e pivoteamento.

**RCE (Remote Code Execution).** Execução de código arbitrário à distância — um
dos impactos mais graves. Ver Pickle.

**Reconhecimento (recon).** Fase de coleta de informação sobre o alvo. Passivo
(sem tocar) ou ativo (enviando pacotes).

**RoE (Rules of Engagement).** Regras de engajamento de um pentest: o que é
permitido, o que é proibido, contatos de emergência.

**Safetensors.** Formato de armazenamento de modelos que guarda só os tensores
(pesos), sem instruções executáveis. Seguro por design; alternativa ao Pickle.

**SIEM.** Plataforma que coleta e correlaciona eventos de segurança; com análise
comportamental, detecta anomalias (ex.: *model extraction*).

**SOAR.** Orquestração e automação da **resposta** a incidentes (playbooks).

**SOC (Security Operations Center).** Centro de operações de segurança, onde a
defesa é monitorada e respondida em tempo real.

**Superfície de ataque.** Conjunto de pontos por onde um sistema pode ser
atacado. Reduzi-la é a higiene defensiva básica.

**Treinamento Adversarial.** Defesa que inclui exemplos adversariais (com rótulo
correto) no treino, tornando o modelo mais robusto.

**Varredura (scan).** Envio sistemático de pacotes para descobrir hosts
(descoberta) ou portas/serviços (varredura de portas).

**WAF (Web Application Firewall).** Firewall de aplicação web. Quando baseado em
ML, torna-se alvo de ataques de evasão adversarial.

**Watermarking.** Marca embutida no modelo/saída que permite provar roubo ou
origem posteriormente.
