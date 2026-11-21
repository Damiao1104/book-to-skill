# Capítulo 6 — O Primeiro Ponto: Reconhecimento e Descoberta de IP

> A Técnica dos Três Pontos estrutura toda operação ofensiva: **(1) achar o IP**,
> **(2) mapear as Portas/serviços**, **(3) identificar a Vulnerabilidade**. Este
> capítulo é o Ponto 1. Parece o passo mais simples — e é justamente por isso que
> é o mais subestimado. Você não ataca o que não localiza.

## 6.1 Conhecimento Mínimo Necessário (CMN)

Antes de digitar comandos, estabeleça o seu **Conhecimento Mínimo Necessário**: o
conjunto de informações sem as quais o ataque é cego. Para o Ponto 1, o CMN
responde:

- **Quais endereços IP pertencem ao alvo?** (um host, uma faixa, uma organização
  inteira?)
- **Quais desses endereços estão realmente ativos** (hosts "vivos")?
- **Como a rede do alvo está estruturada** (sub-redes, segmentação)?

O CMN tem também uma função ética e contratual: ele é delimitado pelo **escopo**
(Capítulo 2). Se o contrato autoriza `203.0.113.0/24`, o seu CMN para em
`203.0.113.0/24`. Descobrir que há outra faixa interessante *fora* do escopo não
é convite — é limite.

> 💡 **Dica Técnica:** O reconhecimento se divide em **passivo** (sem tocar o
> alvo: OSINT, DNS público, registros WHOIS, Shodan) e **ativo** (enviando
> pacotes ao alvo: *ping sweep*, varredura). Comece sempre pelo passivo: ele é
> silencioso, muitas vezes legal mesmo fora de janela (dados públicos), e
> frequentemente entrega o CMN sem disparar um único alarme.

## 6.2 Reconhecimento passivo: montando o mapa sem tocar o alvo

Fontes de informação pública que alimentam o CMN:

- **WHOIS:** quem registrou o domínio, quais blocos de IP a organização possui.

  ```bash
  $ whois exemplo.com.br          # dados de registro do dominio
  $ whois 203.0.113.10            # a quem pertence o bloco de IP
  ```
- **DNS:** o DNS é um mapa da infraestrutura. Registros `A` (IPv4), `AAAA`
  (IPv6), `MX` (e-mail), `NS` (servidores de nome), `TXT`.

  ```bash
  $ host exemplo.com.br           # resolucao rapida
  $ dig exemplo.com.br ANY        # todos os registros
  $ dig MX exemplo.com.br         # servidores de e-mail
  ```
- **Enumeração de subdomínios:** cada subdomínio é um possível novo IP e nova
  superfície.

  ```bash
  $ dnsenum exemplo.com.br
  $ dnsrecon -d exemplo.com.br
  ```
- **Shodan / Censys:** motores de busca de dispositivos conectados. Entregam, de
  graça e sem tocar o alvo, portas abertas e *banners* já coletados por
  terceiros. Inteligência pura para o CMN.

> ⚠️ **Atenção:** Mesmo o reconhecimento "passivo" de subdomínios pode gerar
> consultas DNS que, em escala, deixam rastro — e a enumeração por força bruta de
> subdomínios já é "ativa" o bastante para constar em logs do alvo. Mantenha-se
> dentro do escopo e da janela, e prefira fontes verdadeiramente públicas quando
> quiser silêncio total.

## 6.3 Entendendo endereçamento IP e sub-redes

Para interpretar o que você descobre, precisa ler endereçamento IP com fluência.

### Classes históricas (contexto)

O IPv4 foi originalmente dividido em classes. Hoje usamos CIDR, mas a nomenclatura
persiste:

| Classe | Faixa do 1º octeto | Máscara padrão | Uso |
|---|---|---|---|
| A | 1–126 | /8 (255.0.0.0) | Redes muito grandes |
| B | 128–191 | /16 (255.255.0.0) | Redes médias |
| C | 192–223 | /24 (255.255.255.0) | Redes pequenas |

### Faixas privadas (RFC 1918)

Estas **nunca** são roteadas na internet pública — são as que você verá no
laboratório e em redes internas:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

Reconhecer um IP privado diz muito: se você está "dentro" e vê `10.x.x.x`, está
na rede interna — território de movimentação lateral (Capítulo 10).

### Notação CIDR e sub-redes

CIDR escreve a máscara como `/n`, onde `n` é o número de bits de rede.

| CIDR | Máscara | Nº de hosts utilizáveis | Significado |
|---|---|---|---|
| /24 | 255.255.255.0 | 254 | Uma "rede C" típica |
| /25 | 255.255.255.128 | 126 | Metade de um /24 |
| /16 | 255.255.0.0 | 65.534 | Rede grande |
| /30 | 255.255.255.252 | 2 | Enlace ponto-a-ponto |
| /32 | — | 1 | Um único host |

Saber que `192.168.56.0/24` abrange de `.1` a `.254` é o que permite varrer "a
rede toda" com um comando só — e saber que `/32` é um host só evita varrer o
nada.

> 💡 **Dica Técnica:** Use `ipcalc` para não errar conta de sub-rede na pressa:
>
> ```bash
> $ ipcalc 192.168.56.0/24       # mostra faixa, broadcast, nº de hosts
> ```

## 6.4 Reconhecimento ativo: descoberta de hosts (*ping sweep*)

Agora enviamos pacotes para descobrir **quais IPs estão vivos**. A ferramenta
central já é o `nmap`, no modo "descoberta de hosts" (sem varrer portas ainda):

```bash
# -sn (ou -sP em versoes antigas): "no port scan" = so descobre hosts vivos.
# Varre toda a sub-rede do laboratorio.
$ nmap -sn 192.168.56.0/24
```

Saída típica (resumida):

```text
Nmap scan report for 192.168.56.20
Host is up (0.00042s latency).
MAC Address: 08:00:27:AB:CD:EF (Oracle VirtualBox virtual NIC)
Nmap done: 256 IP addresses (1 host up) scanned in 2.13 seconds
```

O `-sn` faz o `nmap` usar uma combinação de técnicas (ARP na rede local, ICMP
*echo*, *probes* TCP a portas comuns) para inferir presença sem varrer todas as
portas. Na rede local do laboratório, o ARP é o mais confiável — e o motivo pelo
qual você vê o endereço MAC.

Variações úteis:

```bash
# Salvar a saida em formato "grepavel" para encadear com outros comandos
$ nmap -sn 192.168.56.0/24 -oG hosts.txt

# Listar apenas os IPs vivos, prontos para o proximo passo (Cap. 7)
$ grep "Up" hosts.txt | awk '{print $2}' > alvos.txt
$ cat alvos.txt
192.168.56.20
```

Ferramentas complementares para descoberta:

```bash
# arp-scan: rapidissimo e confiavel na rede LOCAL (camada 2)
$ sudo arp-scan --localnet

# fping: pingar muitos hosts em paralelo
$ fping -a -g 192.168.56.0/24 2>/dev/null
```

> ⚠️ **Atenção:** Nem todo host vivo responde a ICMP. Muitos firewalls bloqueiam
> *ping*. Um host que "não responde" ao `-sn` pode estar perfeitamente ativo,
> apenas filtrando ICMP. Quando suspeitar disso, force a descoberta por outros
> meios (`-Pn` para pular a descoberta e assumir o host vivo, ou *probes* TCP a
> portas específicas) — assunto que aprofundamos no Capítulo 7 ao falar de evasão
> de firewall.

## 6.5 Do IP ao próximo ponto

Ao final do Ponto 1 você deve ter uma lista concreta: *estes IPs, dentro do meu
escopo, estão vivos*. Esse `alvos.txt` é a ponte para o Ponto 2 (Capítulo 7),
onde cada IP vivo será interrogado porta a porta.

Resista à tentação de pular etapas. O iniciante quer "invadir já"; o profissional
sabe que um reconhecimento bem-feito frequentemente *é* metade da invasão — porque
revela o caminho de menor resistência antes de você gastar um só *exploit*.

---

### Resumo do capítulo
- O Ponto 1 responde "quais IPs, dentro do escopo, estão vivos?" — o Conhecimento Mínimo Necessário.
- Reconhecimento passivo (WHOIS, DNS, Shodan) monta o mapa sem tocar o alvo; ativo (*ping sweep*) confirma hosts vivos.
- Ler endereçamento IP/CIDR e reconhecer faixas privadas (RFC 1918) é pré-requisito para interpretar os achados.
- `nmap -sn` descobre hosts; `arp-scan` e `fping` complementam; nem todo host vivo responde a ICMP.
- O produto final é uma lista de IPs vivos (`alvos.txt`) que alimenta o Capítulo 7.

### Para fixar
1. No laboratório, rode `nmap -sn` na sua faixa e gere o `alvos.txt` com o encadeamento `grep | awk`.
2. Com `ipcalc`, calcule quantos hosts cabem num `/26` e confirme pensando nos bits.
