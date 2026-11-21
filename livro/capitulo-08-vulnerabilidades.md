# Capítulo 8 — O Terceiro Ponto: Identificação e Análise de Vulnerabilidades

> Você sabe quais máquinas existem (Ponto 1) e o que elas oferecem, com versões
> (Ponto 2). Agora vem o Ponto 3: transformar aquele inventário de
> "serviço + versão" em uma lista de **falhas exploráveis**. Este é o ponto que
> separa "mapear" de "entender como entrar" — e, crucialmente, o que vai para o
> relatório mesmo quando você decide (ou o escopo manda) *não* explorar.

## 8.1 Vulnerabilidades implícitas vs. explícitas

Nem toda vulnerabilidade é uma falha de software catalogada. Distinga dois tipos,
porque eles se descobrem de formas diferentes:

- **Vulnerabilidade explícita:** uma falha conhecida e catalogada em um software
  específico, geralmente com um identificador CVE e, muitas vezes, um *exploit*
  público. Ex.: o *backdoor* do `vsftpd 2.3.4`, a execução remota em um Apache
  antigo. Descobre-se cruzando a versão (Ponto 2) com as bases públicas.
- **Vulnerabilidade implícita:** nasce de **configuração, lógica ou contexto**,
  não de um bug catalogado. Ex.: FTP com login anônimo habilitado, senha padrão
  `msfadmin/msfadmin`, um diretório `/admin` sem autenticação, permissões de
  arquivo excessivas, um *bucket* exposto. Não há CVE para "o administrador
  configurou errado" — descobre-se enumerando e raciocinando.

> 💡 **Dica Técnica:** Iniciantes caçam só o explícito (procuram CVE e *exploit*
> pronto). Os achados mais valiosos — e mais comuns no mundo real — costumam ser
> implícitos: credenciais fracas, serviços desnecessários expostos, permissões
> largas. O Ponto 3 exige as duas lentes: a do catálogo e a do bom senso de
> configuração.

## 8.2 As bases: CVE, CVSS e NVD

O ecossistema de vulnerabilidades explícitas gira em torno de três siglas.

### CVE (Common Vulnerabilities and Exposures)

É o **identificador único** de uma vulnerabilidade, no formato
`CVE-ANO-NÚMERO` (ex.: `CVE-2011-2523` para o *backdoor* do vsftpd 2.3.4). O CVE
não descreve a gravidade — é só o "número de registro" que permite todo mundo
falar da mesma falha sem ambiguidade.

### CVSS (Common Vulnerability Scoring System)

É a **nota de gravidade**, de 0 a 10, calculada a partir de métricas como vetor de
ataque (rede? local?), complexidade, privilégios necessários, impacto em
confidencialidade/integridade/disponibilidade.

| Faixa CVSS (v3.x) | Severidade |
|---|---|
| 0.0 | Nenhuma |
| 0.1 – 3.9 | Baixa |
| 4.0 – 6.9 | Média |
| 7.0 – 8.9 | Alta |
| 9.0 – 10.0 | Crítica |

> ⚠️ **Atenção:** CVSS mede gravidade *técnica genérica*, não **risco no seu
> contexto**. Uma falha CVSS 9.8 numa máquina de teste isolada e sem dados é
> menos urgente que uma CVSS 6.5 no servidor que guarda o banco de clientes.
> O relatório (Capítulo 10) deve traduzir CVSS em risco de negócio — essa
> tradução é o que o cliente paga para você fazer.

### NVD (National Vulnerability Database)

A base mantida pelo NIST que enriquece cada CVE com nota CVSS, software afetado
(CPE), referências e correções. É onde você confirma "esta versão é afetada?".

## 8.3 Do serviço ao exploit: Exploit-DB e `searchsploit`

De posse de "serviço + versão", a pergunta é: **existe exploit público para
isto?** A fonte canônica é o **Exploit-DB** (mantido pela Offensive Security, os
mesmos do Kali). E o Kali traz uma cópia local pesquisável: o `searchsploit`.

```bash
# Procurar exploits para o vsftpd 2.3.4
$ searchsploit vsftpd 2.3.4

# Procurar por servico + versao vindos do nmap -sV
$ searchsploit samba 3.0
$ searchsploit apache 2.2.8
```

Saída típica:

```text
----------------------------------------------------- ----------------------------
 Exploit Title                                        |  Path
----------------------------------------------------- ----------------------------
vsftpd 2.3.4 - Backdoor Command Execution             | unix/remote/49757.py
vsftpd 2.3.4 - Backdoor Command Execution (Metasploit)| unix/remote/17491.rb
----------------------------------------------------- ----------------------------
```

Explorando o resultado:

```bash
# Ver o codigo do exploit (LEIA antes de rodar qualquer coisa)
$ searchsploit -x unix/remote/49757.py

# Copiar o exploit para o diretorio de trabalho
$ searchsploit -m unix/remote/49757.py

# Manter a base local atualizada
$ searchsploit -u
```

> ⚠️ **Atenção:** **Nunca execute um exploit público sem ler o código.** Exploits
> da internet podem conter *payloads* maliciosos escondidos (que atacam *você*, não
> o alvo), podem causar dano irreversível no alvo, ou simplesmente não fazer o que
> prometem. Ler o código também é como você aprende — e é o que impede você de ser
> o *script kiddie* do Capítulo 1. Aplique aqui a regra do ambiente: trate o
> arquivo baixado como dado não confiável.

## 8.4 Scanners de vulnerabilidade

Fazer o cruzamento versão↔CVE manualmente para centenas de serviços é inviável.
*Scanners* automatizam o Ponto 3 — com ressalvas.

- **Nmap NSE (`--script vuln`):** já visto no Capítulo 7; cobre falhas conhecidas
  comuns, integrado ao seu fluxo.
- **Nikto:** *scanner* focado em servidores web — arquivos perigosos,
  configurações inseguras, versões desatualizadas.

  ```bash
  $ nikto -h http://192.168.56.20
  ```
- **OpenVAS / Greenbone:** *scanner* de vulnerabilidades completo, com base
  enorme de testes (NVTs), relatórios e priorização por CVSS. É o padrão aberto
  para varredura abrangente.
- **Para aplicações web:** o Burp Suite (scanner no profissional) e o OWASP ZAP
  rastreiam e testam falhas web (injeções, XSS, etc.).

> 💡 **Dica Técnica:** *Scanners* produzem **falsos positivos** (apontam falha que
> não existe) e **falsos negativos** (perdem falha que existe). O relatório
> profissional nunca é "colei a saída do OpenVAS". É você **validando** cada
> achado relevante — confirmando que a falha é real e explorável no contexto. O
> *scanner* acelera a descoberta; o cérebro valida. Entregar saída crua de scanner
> como relatório é o equivalente, no Ponto 3, ao *script kiddie* do Ponto de
> exploração.

## 8.5 Mapeamento de serviços comuns e suas falhas típicas

Conhecer os "suspeitos de sempre" acelera enormemente o Ponto 3. Para cada serviço
que o `-sV` revelar, você já deve ter hipóteses de falha na cabeça.

| Serviço / porta | Vulnerabilidades típicas | Como investigar |
|---|---|---|
| **FTP (21)** | Login anônimo, credenciais em texto claro, versões com *backdoor* | `nmap --script ftp-anon`; `searchsploit <servidor ftp>` |
| **SSH (22)** | Credenciais fracas (força bruta), versões antigas, chaves fracas | Força bruta (Cap. 9); `-sV` para versão |
| **Telnet (23)** | Texto claro (tudo interceptável), sua mera presença é risco | Interceptação; recomendar desativar |
| **SMTP (25)** | Enumeração de usuários (`VRFY`/`EXPN`), *open relay* | `nmap --script smtp-enum-users`, `smtp-open-relay` |
| **DNS (53)** | Transferência de zona (`AXFR`) vazando toda a rede | `dig AXFR @servidor dominio` |
| **HTTP/HTTPS (80/443)** | Injeções (SQLi), XSS, diretórios expostos, versões vulneráveis, falhas de config | `nikto`, `gobuster`, Burp/ZAP |
| **SMB (139/445)** | Compartilhamentos abertos, *null sessions*, falhas de execução remota | `nmap --script smb-*`, `enum4linux` |
| **MySQL (3306)** | Exposto à rede, sem senha ou senha fraca | `nmap --script mysql-*`; tentativa de login |

### Foco em Web (Apache e companhia)

A superfície web é, de longe, a maior e mais explorada. Além das falhas de
aplicação (que o OWASP cataloga — e cujo paralelo para IA veremos no Capítulo 11),
há a enumeração de conteúdo:

```bash
# Descobrir diretorios e arquivos "escondidos" por forca bruta de caminhos
$ gobuster dir -u http://192.168.56.20 -w /usr/share/wordlists/dirb/common.txt

# Scanner web rapido de problemas conhecidos
$ nikto -h http://192.168.56.20

# Enumerar o servidor e a versao (confirma o que o -sV disse)
$ whatweb http://192.168.56.20
```

Achar `/phpmyadmin`, `/admin`, um `.git` exposto ou um *backup* `.zip` esquecido é
vulnerabilidade implícita pura — e das mais frutíferas.

> 💡 **Dica Técnica:** As *wordlists* do Kali (em `/usr/share/wordlists/`,
> incluindo a famosa `rockyou.txt` comprimida) são sua munição para enumeração de
> diretórios e, no Capítulo 9, para ataques a senhas. Conheça o que há ali:
> `ls /usr/share/wordlists/`.

## 8.6 Priorização: nem tudo merece exploit

O Ponto 3 termina com uma lista priorizada, não com "achei 40 falhas". Para
priorizar, cruze três eixos:

1. **Gravidade técnica** (CVSS) — quão séria é a falha em si.
2. **Explorabilidade real** — há *exploit* confiável? exige condições raras?
3. **Valor para o objetivo** — essa falha leva ao que o pentest precisa provar
   (acesso ao dado sensível, ao controlador de domínio, etc.)?

Uma falha crítica mas inexplorável no contexto pode valer menos, na prática, que
uma média que abre a porta para tudo. Essa priorização é o raciocínio que conecta
o Ponto 3 (Capítulo 8) à exploração (Capítulo 9) e ao relatório (Capítulo 10).

---

### Resumo do capítulo
- Vulnerabilidades explícitas (catalogadas, com CVE) descobrem-se cruzando versão↔base; implícitas (configuração/lógica) descobrem-se enumerando e raciocinando.
- CVE identifica, CVSS gradua a gravidade (0–10), NVD enriquece; CVSS ≠ risco no contexto.
- `searchsploit`/Exploit-DB ligam "serviço+versão" a *exploits* públicos — que devem ser **lidos antes de executados**.
- *Scanners* (Nikto, OpenVAS, NSE `vuln`) aceleram, mas produzem falsos positivos/negativos; o profissional **valida** cada achado.
- Conhecer as falhas típicas de FTP/SSH/HTTP/SMB/MySQL acelera o Ponto 3; o resultado é uma lista **priorizada** por gravidade × explorabilidade × valor.

### Para fixar
1. Pegue duas versões de serviço da sua saída `nmap -sV` do Capítulo 7 e use `searchsploit` para achar (e **ler**, sem executar) os exploits correspondentes.
2. Rode `nikto` e `gobuster` contra o Metasploitable e classifique cada achado como explícito ou implícito.
3. Para um CVE crítico que você encontrar, escreva uma frase traduzindo o CVSS em risco de negócio num cenário fictício.
