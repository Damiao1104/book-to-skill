# Capítulo 7 — O Segundo Ponto: Mapeamento de Portas e Serviços com Nmap

> Você tem os IPs vivos. Agora precisa saber **o que cada um oferece**: quais
> portas estão abertas, que serviços atendem nelas, em que versões e sobre qual
> sistema operacional. Este é o Ponto 2, e o `nmap` é o bisturi. Dominar o Nmap
> de verdade — não decorar três comandos, mas *entender* o que cada varredura
> faz na rede — é o que diferencia o pentester do apertador de botão.

## 7.1 Anatomia de uma varredura Nmap

A forma geral de um comando Nmap:

```bash
$ nmap [tipo de varredura] [opções] [especificação de portas] [alvo]
```

Tudo o que segue está dentro dessa estrutura. Vamos construir do simples ao
sofisticado, sempre contra o laboratório do Capítulo 5.

## 7.2 Tipos de varredura TCP

### TCP Connect Scan (`-sT`)

Completa o *three-way handshake* inteiro (Capítulo 3). É o que o `scanner_simples.py`
fazia. Funciona sem privilégios de root, mas é **barulhento**: a conexão completa
costuma ser registrada nos logs do serviço.

```bash
$ nmap -sT 192.168.56.20
```

### TCP SYN Scan (`-sS`) — o padrão do profissional

Envia o SYN, recebe o SYN-ACK (prova de porta aberta) e responde com RST em vez
de completar o handshake. É o *half-open scan*: mais rápido e mais discreto,
porque muitos serviços não registram a conexão nunca estabelecida. Requer
privilégios (root/`sudo`).

```bash
$ sudo nmap -sS 192.168.56.20
```

Como o Nmap interpreta a resposta ao SYN:

| Resposta do alvo | Estado reportado | Significado |
|---|---|---|
| SYN-ACK | `open` | Porta aberta, serviço escutando |
| RST | `closed` | Porta fechada, nada escutando |
| Nenhuma resposta / ICMP *unreachable* | `filtered` | Firewall descartou o pacote |

![Figura 7.1 — Como o `nmap -sS` infere o estado da porta a partir da resposta ao SYN: aberta (SYN-ACK), fechada (RST) ou filtrada (silêncio/ICMP).](imagens/fig-syn-scan.svg)

> 💡 **Dica Técnica:** `-sS` é o padrão de fato para varredura TCP justamente por
> esse equilíbrio entre velocidade, confiabilidade e discrição. Quando alguém diz
> "faz um SYN scan", é disto que está falando. Mas saiba interpretar `filtered`:
> ele não diz "fechada", diz "tem algo (um firewall) entre você e a resposta".

### UDP Scan (`-sU`)

UDP não tem handshake, então a varredura é mais lenta e ambígua. Essencial para
achar DNS (53), SNMP (161), DHCP — serviços que vivem em UDP e que uma varredura
TCP ignora por completo.

```bash
$ sudo nmap -sU --top-ports 20 192.168.56.20   # as 20 portas UDP mais comuns
```

## 7.3 Especificando portas

Por padrão o Nmap varre as 1000 portas mais comuns. Controle isso:

```bash
$ sudo nmap -sS -p 22,80,443 192.168.56.20      # portas especificas
$ sudo nmap -sS -p 1-1024 192.168.56.20         # faixa (well-known)
$ sudo nmap -sS -p- 192.168.56.20               # TODAS as 65535 portas
$ sudo nmap -sS -F 192.168.56.20                # "fast": top 100 portas
```

> ⚠️ **Atenção:** `-p-` (todas as portas) é lento e barulhento, mas às vezes
> indispensável: serviços escondidos em portas altas (ex.: um painel admin em
> 8443, um banco em 54321) só aparecem assim. Num pentest sério, rode um `-p-` em
> algum momento — a porta que ninguém varre é exatamente onde o administrador
> "escondeu" o serviço, achando que segurança por obscuridade funciona.

## 7.4 Detecção de versão (`-sV`) e de sistema operacional (`-O`)

Aqui o Ponto 2 começa a se fundir com o Ponto 3 (Capítulo 8): saber a **versão**
exata do serviço é o que permite procurar a vulnerabilidade correspondente.

```bash
# -sV: interroga cada porta aberta para descobrir servico e VERSAO
$ sudo nmap -sV 192.168.56.20

# -O: tenta identificar o sistema operacional pelo comportamento da pilha TCP/IP
$ sudo nmap -O 192.168.56.20

# Combinacao comum: versao + SO + scripts padrao + traceroute
$ sudo nmap -sV -O 192.168.56.20
```

Saída ilustrativa (Metasploitable 2, recortada):

```text
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 2.3.4
22/tcp   open  ssh         OpenSSH 4.7p1 Debian 8ubuntu1
23/tcp   open  telnet      Linux telnetd
80/tcp   open  http        Apache httpd 2.2.8 ((Ubuntu) DAV/2)
139/tcp  open  netbios-ssn Samba smbd 3.X - 4.X
445/tcp  open  netbios-ssn Samba smbd 3.X - 4.X
3306/tcp open  mysql       MySQL 5.0.51a-3ubuntu5
```

Essa tabela é ouro. Cada linha `serviço + versão` é uma consulta pronta para as
bases de vulnerabilidade do Capítulo 8. Repare em `vsftpd 2.3.4` — uma versão com
*backdoor* histórico famoso. O Ponto 2 bem-feito praticamente **entrega** o Ponto
3.

> 💡 **Dica Técnica:** A combinação mais usada no dia a dia é `-sС -sV` (não
> confunda `-sC` de "scripts padrão" com `-sS` de SYN). O atalho `-A` liga
> "tudo agressivo" de uma vez: `-sV -O --script=default --traceroute`. Útil para
> um panorama rápido, mas barulhento — e num alvo real você vai querer controle
> fino, não o martelo do `-A`.

## 7.5 Nmap Scripting Engine (NSE)

O NSE transforma o Nmap de "varredor de portas" em plataforma de automação. São
*scripts* (em Lua) organizados por categoria: `default`, `safe`, `vuln`, `auth`,
`brute`, `discovery`, entre outras.

```bash
# Rodar os scripts da categoria "vuln" (procura vulnerabilidades conhecidas)
$ sudo nmap --script vuln 192.168.56.20

# Script especifico (ex.: checar o backdoor do vsftpd 2.3.4)
$ sudo nmap -p 21 --script ftp-vsftpd-backdoor 192.168.56.20

# Enumeracao de compartilhamentos SMB
$ sudo nmap -p 445 --script smb-enum-shares 192.168.56.20
```

> ⚠️ **Atenção:** Categorias como `brute` (força bruta) e alguns scripts `vuln`
> **atacam de fato** — podem travar serviços frágeis ou tentar logins. Isso só
> dentro do escopo e da janela autorizados (Capítulo 2). O NSE borra a linha
> entre "mapear" e "explorar"; respeite essa linha.

## 7.6 Identificação de firewalls e técnicas de evasão

Nem todo alvo responde francamente. Firewalls e IDS/IPS moldam o que você vê. O
Nmap oferece técnicas para sondar e, em alguns casos, driblar.

### Distinguir "fechada" de "filtrada": ACK Scan (`-sA`)

O `-sA` não descobre portas abertas; ele descobre se há um **firewall com estado**
no caminho. Enviando apenas um ACK:

- resposta RST → a porta é `unfiltered` (o firewall deixou passar);
- sem resposta / ICMP → `filtered` (há firewall bloqueando).

```bash
$ sudo nmap -sA 192.168.56.20      # mapeia regras de firewall, nao portas abertas
```

### Pular a descoberta de host (`-Pn`)

Lembre do Capítulo 6: muitos hosts vivos não respondem a ICMP. Se o Nmap "desiste"
achando o host morto, force-o a varrer assim mesmo:

```bash
# -Pn: "no ping" = NAO tenta descobrir se o host esta vivo; assume que esta e varre.
$ sudo nmap -Pn -sS 192.168.56.20
```

`-Pn` é indispensável contra alvos que filtram ICMP — sem ele você concluiria,
erradamente, que não há nada ali.

### Outras técnicas de evasão

| Técnica | Flag | O que faz |
|---|---|---|
| Fragmentação | `-f` | Quebra pacotes em fragmentos pequenos p/ confundir filtros simples |
| Controle de velocidade | `-T0`..`-T5` | `-T0` (lentíssimo, furtivo) a `-T5` (rapidíssimo, barulhento) |
| Porta de origem falsa | `--source-port 53` | Finge vir de uma porta confiável (DNS) |
| Chamarizes (*decoys*) | `-D RND:10` | Mistura seu IP com IPs falsos p/ ofuscar a origem |
| MTU customizado | `--mtu` | Ajusta o tamanho do pacote |

```bash
# Varredura lenta e furtiva, fragmentada, fingindo origem na porta 53
$ sudo nmap -sS -f -T2 --source-port 53 -Pn 192.168.56.20
```

> 💡 **Dica Técnica:** Evasão é um jogo de compromissos. `-T0` com *decoys* pode
> passar despercebido por um IDS mal configurado, mas uma varredura que leva horas
> também é uma varredura que pode "estourar" a janela de teste. Ajuste a
> agressividade ao objetivo: mapear rápido (barulhento) ou mapear sem alarmar
> (lento). Num pentest "caixa-preta" onde a detecção faz parte do teste, a evasão
> é o próprio ponto.

## 7.7 Ferramentas complementares: HPing3 e Unicornscan

O Nmap é soberano, mas há ferramentas que fazem coisas que ele não faz tão bem.

### HPing3 — o canivete de pacotes

O `hping3` fabrica pacotes TCP/UDP/ICMP arbitrários, pacote a pacote. É ideal
para sondar firewalls, testar regras e entender o comportamento da pilha do alvo
em nível fino.

```bash
# Enviar um unico SYN para a porta 80 e ver a resposta (sonda de porta manual)
$ sudo hping3 -S -p 80 -c 1 192.168.56.20

# Varrer uma faixa de portas enviando SYN (--scan), modo verboso
$ sudo hping3 -S --scan 20-443 192.168.56.20

# Testar se o alvo responde a ICMP timestamp (descoberta alternativa ao ping)
$ sudo hping3 --icmp --icmptype 13 -c 1 192.168.56.20
```

> ⚠️ **Atenção:** O `hping3` também sabe inundar o alvo (`--flood`), o que é um
> ataque de **negação de serviço (DoS)**. DoS quase sempre está **fora de escopo**
> em pentests (Capítulo 2) e é crime fora de ambiente autorizado. Use o `hping3`
> para *sondar* e *entender*, não para derrubar — a menos que o contrato
> explicitamente autorize teste de resiliência.

### Unicornscan — varredura assíncrona de alto volume

O `unicornscan` desacopla o envio dos pacotes do recebimento das respostas,
permitindo varreduras muito rápidas de faixas grandes — útil quando o alvo é uma
rede inteira e o `-p-` do Nmap seria lento demais.

```bash
# Varredura TCP SYN assincrona da porta 1 a 65535 a uma taxa controlada
$ sudo unicornscan -mT -r 500 192.168.56.20:1-65535
```

### Qual usar quando

| Ferramenta | Melhor para |
|---|---|
| **Nmap** | Padrão geral: detecção de versão/SO, NSE, relatórios estruturados |
| **HPing3** | Sondagem fina de firewall, pacotes sob medida, testes de regra |
| **Unicornscan** | Varredura de altíssimo volume em redes grandes |

## 7.8 Documentando a saída

Todo pentester sério salva os resultados em formato reaproveitável — para o
Capítulo 8, para o relatório (Capítulo 10) e como prova de conduta:

```bash
# -oA grava nos tres formatos de uma vez: .nmap (legivel), .gnmap (grepavel), .xml
$ sudo nmap -sS -sV -O -oA recon_metasploitable 192.168.56.20
```

O `.xml` alimenta ferramentas de relatório; o `.gnmap` encadeia com `grep`/`awk`;
o `.nmap` é o que você relê. Nunca confie na memória — confie no arquivo.

---

### Resumo do capítulo
- O Ponto 2 mapeia portas, serviços, versões e SO; `-sS` (SYN/half-open) é o padrão profissional, `-sT` é barulhento, `-sU` cobre UDP.
- `-sV` (versão) e `-O` (SO) transformam portas abertas em pistas de vulnerabilidade — a ponte para o Capítulo 8.
- O NSE automatiza enumeração e até exploração (categorias `vuln`, `brute`); use com cuidado dentro do escopo.
- Firewalls: `-sA` distingue fechada de filtrada, `-Pn` força a varredura de hosts que filtram ICMP, e `-f`/`-T`/`-D` ajudam na evasão.
- HPing3 (pacotes sob medida, sondagem de firewall) e Unicornscan (alto volume) complementam o Nmap; sempre documente com `-oA`.

### Para fixar
1. Rode `sudo nmap -sS -sV -O -oA recon 192.168.56.20` no laboratório e identifique, na saída, pelo menos duas versões de serviço que você investigaria no Capítulo 8.
2. Compare `nmap -sT` e `nmap -sS` observando (se possível) os logs do alvo. Qual deixou rastro? Por quê?
3. Use `hping3 -S -p 80 -c 1` contra o alvo e interprete a *flag* da resposta (SYN-ACK vs. RST).
