# Apêndice C — Referência Rápida de Comandos

> Uma folha de consulta para o laboratório. **Todos** os comandos pressupõem
> alvo autorizado (seu laboratório ou um escopo contratado). Nada aqui é para
> apontar contra sistemas de terceiros sem a carta de autorização do Capítulo 2.

## Manutenção do Kali (cap. 4)

```bash
sudo apt update && sudo apt full-upgrade -y     # atualizar (rolling release)
script sessao.log                               # gravar a sessão do terminal
```

## Descoberta de hosts — Ponto 1 (cap. 6)

```bash
nmap -sn 192.168.56.0/24                         # ping sweep (hosts vivos)
nmap -sn 192.168.56.0/24 -oG hosts.txt           # saída grepável
grep "Up" hosts.txt | awk '{print $2}' > alvos.txt
sudo arp-scan --localnet                         # descoberta rápida na LAN
fping -a -g 192.168.56.0/24 2>/dev/null          # ping em paralelo
ipcalc 192.168.56.0/24                           # conta de sub-rede
whois exemplo.com.br ; dig exemplo.com.br ANY    # recon passivo
```

## Varredura de portas/serviços — Ponto 2 (cap. 7)

```bash
sudo nmap -sS 192.168.56.20                       # SYN scan (half-open, padrão)
sudo nmap -sT 192.168.56.20                       # TCP connect (barulhento)
sudo nmap -sU --top-ports 20 192.168.56.20        # UDP (DNS/SNMP/DHCP)
sudo nmap -sS -p- 192.168.56.20                   # todas as 65535 portas
sudo nmap -sS -p 22,80,443 192.168.56.20          # portas específicas
sudo nmap -sV -O 192.168.56.20                    # versão de serviço + SO
sudo nmap -A 192.168.56.20                        # agressivo (tudo de uma vez)
sudo nmap --script vuln 192.168.56.20             # NSE: falhas conhecidas
sudo nmap -sA 192.168.56.20                       # mapear firewall (não portas)
sudo nmap -Pn -sS 192.168.56.20                   # pular descoberta (host filtra ICMP)
sudo nmap -sS -f -T2 --source-port 53 -Pn ALVO    # evasão (fragmenta/lento/porta falsa)
sudo nmap -sS -sV -O -oA recon 192.168.56.20      # salvar nos 3 formatos

# hping3 — sondagem fina de pacotes
sudo hping3 -S -p 80 -c 1 192.168.56.20           # 1 SYN à porta 80
sudo hping3 -S --scan 20-443 192.168.56.20        # varredura SYN de faixa

# unicornscan — varredura assíncrona de alto volume
sudo unicornscan -mT -r 500 192.168.56.20:1-65535
```

## Análise de vulnerabilidades — Ponto 3 (cap. 8)

```bash
searchsploit vsftpd 2.3.4                          # procurar exploit por serviço+versão
searchsploit -x unix/remote/49757.py               # LER o exploit (nunca rodar sem ler)
searchsploit -m unix/remote/49757.py               # copiar p/ diretório atual
searchsploit -u                                    # atualizar a base
nikto -h http://192.168.56.20                      # scanner web
gobuster dir -u http://192.168.56.20 -w /usr/share/wordlists/dirb/common.txt
whatweb http://192.168.56.20                       # identificar tecnologias web
nmap -p 21 --script ftp-anon 192.168.56.20         # FTP aceita anônimo?
ls /usr/share/wordlists/                           # munição (inclui rockyou)
```

## Exploração (cap. 9)

```bash
# Força bruta ONLINE (controle a taxa com -t; use -f para parar no 1º acerto)
medusa -h 192.168.56.20 -u msfadmin -P /usr/share/wordlists/rockyou.txt -M ssh -f -t 4
medusa -h 192.168.56.20 -U usuarios.txt -P senhas.txt -M ftp -t 3 -f
hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ssh://192.168.56.20 -t 4 -f

# Quebra OFFLINE de hashes (sem rate limit; com GPU é ordens de magnitude mais rápido)
john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
john --show hashes.txt
hashcat -m 1800 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt   # -m 1800 = sha512crypt

# Metasploit
msfconsole
# search <alvo> ; use <modulo> ; info ; show options ; set RHOSTS <ip> ; run
```

## Pós-exploração e anonimização (cap. 10)

```bash
# Reconhecimento local no alvo comprometido (escalada de privilégios)
id ; whoami ; uname -a ; sudo -l
find / -perm -4000 -type f 2>/dev/null             # binários SUID
cat /etc/crontab                                   # tarefas agendadas

# Anonimização / pivoteamento (SOCKS opera em nível de conexão: use -sT -Pn)
proxychains nmap -sT -Pn -p 80,443 10.10.10.5
proxychains curl https://ifconfig.me               # ver IP de saída
```

## Ambiente e experimentos de IA — Parte V (cap. 11–14)

```bash
# Ambiente Python isolado para os experimentos de IA
python3 -m venv ~/lab-ia && source ~/lab-ia/bin/activate
pip install --upgrade pip

# Bibliotecas por tema
pip install nemoguardrails                          # guardrails (cap. 11)
pip install adversarial-robustness-toolbox          # IBM ART: ataques/defesas (cap. 12)
pip install safetensors torch                       # formato seguro de modelos (cap. 13)

# Rodar notebook de terceiros isolado (cap. 13) — sem credenciais, sem rede
docker run --rm -it --network none \
  -v "$PWD/notebook_nao_confiavel":/work:ro python:3.12-slim bash

# Verificar integridade de um artefato antes de usar (cap. 13/14)
sha256sum modelo.safetensors                        # compare com o hash publicado
```

## Snippets Python úteis (laboratório)

```python
# Medir robustez adversarial (cap. 12) — IBM ART + FGSM
from art.attacks.evasion import FastGradientMethod
ataque = FastGradientMethod(estimator=classifier, eps=0.03)
x_adv = ataque.generate(x=x_test)

# Converter modelo para formato seguro (cap. 13)
from safetensors.torch import save_file, load_file
save_file(model.state_dict(), "modelo.safetensors")
pesos = load_file("modelo.safetensors")

# Proveniência: hash estável de um lote de dados (cap. 14)
import hashlib, pathlib
h = hashlib.sha256()
for p in sorted(pathlib.Path("dataset/lote_01").glob("*.jpg")):
    h.update(p.read_bytes())
print(h.hexdigest())
```

---

> 💡 **Lembrete final:** Decorar comandos é o nível *script kiddie*. O valor está
> em saber **por que** cada flag existe e **o que** cada comando deixa de rastro.
> Use esta folha como índice, não como muleta — e leia a `man` de cada ferramenta
> até o fim.
