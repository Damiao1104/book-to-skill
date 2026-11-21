# Capítulo 10 — Pós-Exploração, Anonimização e Relatórios

> Obter o acesso é o meio, não o fim. O valor de um pentest está no que você faz
> *depois* de entrar — o que o acesso prova sobre o risco real — e em como você
> comunica isso. Este capítulo fecha a Parte IV com os três temas que o iniciante
> ignora e o profissional domina: pós-exploração com propósito, anonimização para
> proteção durante a operação, e o relatório — o único artefato que o cliente
> realmente compra.

## 10.1 Pós-exploração: o que fazer depois de entrar

Você tem um *shell* no alvo. E agora? A pós-exploração persegue objetivos
específicos, cada um alinhado a provar risco:

| Objetivo | Pergunta que responde | Exemplo de técnica |
|---|---|---|
| **Entender onde está** | Que máquina é esta? Quem sou eu aqui? | `whoami`, `id`, `uname -a`, `ipconfig`/`ip addr` |
| **Escalar privilégios** | Consigo virar root/admin? | Explorar kernel/config, SUID, senhas reutilizadas |
| **Coletar credenciais** | Há senhas/*hashes*/chaves aqui? | `/etc/shadow`, `mimikatz` (Windows), chaves SSH |
| **Movimentação lateral** | Que outras máquinas isto alcança? | Usar credenciais coletadas em hosts vizinhos |
| **Persistência** | Eu conseguiria voltar? (demonstração) | Chaves SSH, serviços — *se o escopo permitir* |
| **Avaliar impacto** | Que dado/função crítica isto expõe? | Localizar (sem exfiltrar) dados sensíveis |

### Escalada de privilégios

Virar root/administrador é frequentemente o que transforma "acesso limitado" em
"comprometimento total" no relatório. Reconhecimento local típico:

```bash
# No alvo Linux ja comprometido (laboratorio):
$ id                                  # meus privilegios atuais
$ uname -a                            # versao do kernel (exploits de kernel?)
$ sudo -l                             # o que posso rodar como root sem senha?
$ find / -perm -4000 -type f 2>/dev/null   # binarios SUID (vetor classico)
$ cat /etc/crontab                    # tarefas agendadas exploraveis?
```

Ferramentas de enumeração automatizam esse levantamento (ex.: `linpeas` para
Linux, `winpeas` para Windows), destacando caminhos de escalada prováveis.

> ⚠️ **Atenção:** Movimentação lateral e persistência são as fases onde é mais
> fácil **sair do escopo** sem perceber — você "pula" para uma máquina que não
> estava autorizada, ou deixa um *backdoor* que esquece de remover. Antes de cada
> passo, releia a carta de autorização (Capítulo 2). E **remova toda persistência
> que instalar**, documentando o que foi colocado e retirado. Um pentester que
> esquece um *backdoor* ativo criou uma vulnerabilidade real.

### Minimização e evidência

Colete o **mínimo** para provar o risco. Para demonstrar acesso a dados sensíveis,
prefira um registro fictício plantado, ou uma captura de tela parcial, ou o *hash*
de um arquivo — **não** copie a base de clientes real. Toda evidência deve ser
datada e rastreável ao comando que a gerou (lembre do `script sessao.log` do
Capítulo 4).

## 10.2 Anonimização: proteção, não encobrimento

Durante uma operação **autorizada**, por que anonimizar? Três razões legítimas:

1. **Proteção contra contra-ataque.** Ao sondar um alvo, você pode atrair a
   atenção de quem o controla — ou de outro atacante presente no mesmo sistema.
   Mascarar sua origem protege sua infraestrutura.
2. **Realismo do teste.** Um atacante real não vem do seu IP corporativo fixo;
   simular origem variável testa melhor a capacidade de detecção do cliente.
3. **Segmentação operacional.** Separar a infraestrutura de ataque da sua
   identidade pessoal/empresarial é boa prática de OPSEC.

> ⚠️ **Atenção (repetindo porque é vital):** Anonimização **não** é autorização e
> **não** torna nada legal. Ela protege o profissional durante um trabalho
> legítimo. Usá-la para atacar sem permissão continua sendo crime — apenas um
> crime que você *acha* que escondeu. E a atribuição falha mais do que os
> iniciantes imaginam: metadados, erros de operação, correlação de tempo.

### VPN

Uma VPN encapsula seu tráfego e o faz emergir de outro ponto, trocando seu IP
aparente e cifrando o caminho até o servidor VPN. No contexto de pentest, costuma
ser o primeiro salto — e, em muitos engajamentos, você se conecta por VPN à
*própria rede do cliente* para testar de dentro.

### Proxychains

O `proxychains` força o tráfego de uma ferramenta a passar por uma cadeia de
*proxies* (SOCKS/HTTP) — frequentemente combinada com Tor. Útil tanto para
anonimização quanto para **pivotar**: alcançar uma rede interna *através* de uma
máquina já comprometida.

Configuração (arquivo `/etc/proxychains4.conf`) e uso:

```bash
# Trecho de /etc/proxychains4.conf
# dynamic_chain   # usa os proxies disponiveis na ordem, pulando os mortos
# [ProxyList]
# socks5 127.0.0.1 9050   # Tor rodando localmente

# Rodar uma ferramenta atraves da cadeia de proxies:
$ proxychains nmap -sT -Pn -p 80,443 10.10.10.5
$ proxychains firefox http://alvo-interno.local
```

> 💡 **Dica Técnica:** Com `proxychains`, prefira varreduras **TCP Connect**
> (`-sT`) e `-Pn`: varreduras SYN (`-sS`) e descoberta por ICMP não atravessam
> *proxies* SOCKS corretamente, porque operam em camada mais baixa que o *proxy*
> entende. Entender *por que* (o SOCKS trabalha em nível de conexão TCP, não de
> pacote cru) é a diferença entre "o comando não funciona e não sei por quê" e o
> domínio real da ferramenta.

### Pivotar (movimentação através de um host comprometido)

Quando você compromete uma máquina que tem acesso a uma rede interna inacessível
de fora, pode usá-la como ponte. O Metasploit (Capítulo 9) facilita isso com
`autoroute`/`socks_proxy`, e então o `proxychains` leva suas outras ferramentas
por esse túnel. É a essência da movimentação lateral em redes segmentadas.

## 10.3 O relatório: o produto final

Aqui está a verdade incômoda: **o cliente não compra a invasão; compra o
relatório.** Um acesso brilhante mal documentado vale pouco; uma falha média bem
explicada, com impacto e correção claros, vale muito. O relatório é onde o
pentester demonstra senioridade.

### Estrutura de um relatório profissional

```text
1. SUMARIO EXECUTIVO
   - Para a lideranca (nao-tecnica). Postura geral de seguranca,
     principais riscos em linguagem de negocio, e recomendacao estrategica.
   - 1-2 paginas. Se so lerem isto, precisam entender o risco.

2. ESCOPO E METODOLOGIA
   - O que foi testado (IPs, dominios, janela), o que NAO foi,
     e como (metodologia, ferramentas). Delimita responsabilidade.

3. ACHADOS (o coracao tecnico)
   Para CADA vulnerabilidade:
   - Titulo e severidade (CVSS + risco no contexto)
   - Descricao: o que e a falha
   - Evidencia: prova reproduzivel (comando, print, saida) — datada
   - Impacto: o que um atacante consegue com isso, em termos de negocio
   - Passos de reproducao: para o time tecnico confirmar
   - Recomendacao de mitigacao: como corrigir, concretamente

4. MATRIZ DE RISCO
   - Tabela priorizada: todas as falhas por severidade x explorabilidade.

5. CONCLUSAO E PROXIMOS PASSOS
   - Plano de remediacao priorizado e sugestao de reteste.

6. ANEXOS
   - Saidas brutas (nmap, scanners), referencias (CVE/CVSS), glossario.
```

### Os dois leitores

O relatório serve a dois públicos simultaneamente, e falhar com qualquer um deles
o invalida:

| Leitor | O que quer | O que você entrega |
|---|---|---|
| **Executivo** | "Estamos em risco? Quanto? O que fazer?" | Sumário executivo em linguagem de negócio |
| **Técnico** | "Como reproduzo e corrijo isto?" | Achados detalhados, evidência, passos, mitigação |

> 💡 **Dica Técnica:** Para cada achado, escreva a **recomendação de mitigação**
> com a mesma seriedade do ataque. "Atualize o vsftpd para a versão X", "desabilite
> login anônimo no FTP", "aplique política de senha e *rate limiting* no SSH",
> "feche a porta 3306 ao público". É aqui que o livro se fecha sobre si mesmo: cada
> ataque que você aprendeu nos capítulos anteriores tem uma defesa correspondente,
> e o relatório é onde você a entrega. A mão que escreveu o `medusa` escreve o
> "implemente *lockout* e MFA".

### Ferramentas de apoio

O Kali traz ferramentas para organizar achados e colaborar (ex.: Faraday, Dradis),
que consomem as saídas `.xml` do Nmap e de *scanners* e ajudam a montar o relatório
— mas a **análise e a redação** continuam sendo trabalho humano insubstituível.

## 10.4 Fechamento do engajamento

Um pentest profissional termina com rigor:

- **Limpeza:** remover contas, *backdoors*, arquivos e qualquer alteração feita no
  ambiente. Documentar que a limpeza ocorreu.
- **Entrega segura do relatório:** ele contém o mapa das falhas do cliente — é um
  documento altamente sensível. Entregue cifrado, por canal acordado.
- **Reunião de *debrief*:** apresentar os achados, responder dúvidas, alinhar
  prioridades de correção.
- **Reteste (quando contratado):** validar que as correções funcionaram.

---

### Resumo do capítulo
- Pós-exploração tem propósito: entender onde se está, escalar privilégios, coletar credenciais, mover-se lateralmente e **avaliar impacto** — coletando o mínimo e removendo toda persistência.
- Anonimização (VPN, `proxychains`+Tor) protege o profissional durante operação autorizada e permite pivotar; **nunca** legaliza ataque não autorizado.
- Com `proxychains`, use `-sT -Pn` (SOCKS opera em nível de conexão, não de pacote cru).
- O relatório é o produto final: sumário executivo (negócio) + achados técnicos (evidência, impacto, reprodução, mitigação) + matriz de risco.
- Cada ataque do livro tem uma mitigação correspondente — o relatório é onde o ofensivo vira defensivo.

### Para fixar
1. Documente um achado real do seu laboratório no formato da seção 10.3 (descrição, evidência, impacto, reprodução, mitigação). Mostre-o a alguém não-técnico: o sumário faz sentido para essa pessoa?
2. Configure `proxychains` com Tor e rode `proxychains curl https://ifconfig.me` para ver seu IP aparente mudar — entenda por que `-sS` não funcionaria nesse túnel.
3. Para três ataques dos Capítulos 7–9, escreva a mitigação de uma linha que você colocaria no relatório.
