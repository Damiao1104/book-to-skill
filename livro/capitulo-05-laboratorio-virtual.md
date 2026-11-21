# Capítulo 5 — Construção do Laboratório Virtual Isolado

> Este é o capítulo que torna todo o resto do livro legal e seguro. Um
> laboratório isolado é o seu campo de treino: um lugar onde você pode atacar à
> vontade porque **tudo ali é seu e nada ali toca a internet nem a rede de
> ninguém**. Não pule este capítulo. Praticar sem laboratório é praticar crime.

## 5.1 Por que virtualizar

A virtualização permite rodar vários "computadores" (máquinas virtuais, VMs)
dentro do seu computador físico (o *host*). Para o nosso propósito, três
propriedades são decisivas:

1. **Isolamento:** as VMs podem ser colocadas numa rede que não enxerga nem a
   internet nem a sua rede doméstica. O ataque fica preso dentro do laboratório.
2. **Descartabilidade:** se você quebrar um alvo (ou infectá-lo de propósito),
   apaga e recria. Nenhum dano real, nenhum custo.
3. ***Snapshots*:** você congela o estado de uma VM e volta a ele quando quiser.
   Explorou, bagunçou, aprendeu? Reverte ao estado limpo em segundos.

Usaremos o **VirtualBox** (gratuito, da Oracle, multiplataforma). As ideias valem
igualmente para VMware, Hyper-V ou QEMU/KVM.

## 5.2 A arquitetura do laboratório

O laboratório mínimo tem dois papéis:

- **O atacante:** uma VM com **Kali Linux**.
- **O alvo:** uma ou mais VMs propositalmente vulneráveis — começaremos com
  **Metasploitable 2**, um Linux cheio de falhas conhecidas, feito para ser
  atacado.

```text
            HOST (seu computador fisico)
   +-----------------------------------------------+
   |                                               |
   |   VirtualBox                                  |
   |   +-----------------+   +------------------+   |
   |   |  Kali (atacante)|   | Metasploitable 2 |   |
   |   |  192.168.56.10  |   |  192.168.56.20   |   |
   |   +--------+--------+   +---------+--------+   |
   |            |                      |            |
   |     ==== Rede interna isolada: "labnet" ====   |
   |            (SEM acesso a internet)             |
   +-----------------------------------------------+
```

> ⚠️ **Atenção:** O ponto inegociável é a **rede isolada**. O Metasploitable é
> deliberadamente vulnerável; se ele tocar a internet, será comprometido por
> terceiros em minutos e pode virar plataforma para atacar outros — o que faria
> de *você* o responsável. Mantenha os alvos vulneráveis **sempre** em rede
> interna.

## 5.3 Modos de rede do VirtualBox

Escolher o modo de rede certo é o passo mais importante — e o mais errado por
iniciantes. Entenda cada um:

| Modo | A VM enxerga a internet? | As VMs se enxergam? | O host enxerga as VMs? | Uso no laboratório |
|---|---|---|---|---|
| **NAT** | Sim | Não (isoladas entre si) | Não diretamente | Baixar/atualizar o Kali |
| **Rede Interna** | **Não** | **Sim** | Não | **Alvos vulneráveis (ideal)** |
| **Host-Only** | Não | Sim | **Sim** | Alvos + acesso do host p/ gerir |
| **Bridge** | Sim (vira "um PC" na rede real) | Sim | Sim | ⚠️ **NUNCA** para alvos vulneráveis |

A estratégia recomendada e mais segura:

- Deixe o Metasploitable **somente em Rede Interna** (`labnet`). Ele nunca vê a
  internet.
- No Kali, use **duas placas de rede**: uma em NAT (para atualizar o Kali quando
  necessário) e outra na Rede Interna `labnet` (para falar com o alvo). Assim o
  Kali atualiza sem jamais criar uma ponte entre o alvo vulnerável e a internet.

> 💡 **Dica Técnica:** Se quiser gerenciar os alvos a partir do host (abrir a
> interface web do Metasploitable no navegador do seu PC, por exemplo), use
> **Host-Only** em vez de Rede Interna pura. Continua sem internet, mas o host
> participa. Para o rigor máximo de isolamento, Rede Interna.

## 5.4 Passo a passo: a VM atacante (Kali)

1. **Baixe a imagem oficial do Kali** do site da Offensive Security. A Offensive
   Security disponibiliza imagens prontas para VirtualBox (`.ova`/`.vbox`) — o
   caminho mais rápido.
2. **Verifique a integridade** da imagem com o *hash* SHA-256 publicado. Não pule
   isso — baixar uma imagem adulterada é começar o laboratório já comprometido.

   ```bash
   # No Linux/macOS, compare com o hash publicado no site oficial
   $ sha256sum kali-linux-*-virtualbox-amd64.ova
   ```
3. **Importe no VirtualBox** (`Arquivo > Importar Appliance`) ou crie a VM e
   instale a partir do ISO.
4. **Recursos sugeridos:** 2–4 vCPUs, 4–8 GB de RAM, 40+ GB de disco. Ajuste ao
   seu hardware; o Kali roda em menos, mas aperta.
5. **Rede:** Adaptador 1 = NAT; Adaptador 2 = Rede Interna `labnet`.
6. **Primeiro boot:** faça login, abra o terminal e atualize (Capítulo 4):

   ```bash
   $ sudo apt update && sudo apt full-upgrade -y
   ```
7. **Tire um *snapshot*** chamado `kali-limpo-atualizado`. Esse é seu ponto de
   retorno sempre que algo der errado.

## 5.5 Passo a passo: a VM alvo (Metasploitable 2)

O Metasploitable 2 é distribuído como uma imagem de disco pronta.

1. **Baixe o Metasploitable 2** (projeto da Rapid7, amplamente espelhado).
2. **Crie uma VM Linux** no VirtualBox e aponte o disco virtual para o arquivo
   `.vmdk` do Metasploitable (em vez de criar disco novo).
3. **Rede: SOMENTE Rede Interna `labnet`.** Repetindo porque é o erro fatal mais
   comum: o Metasploitable **nunca** deve ter NAT nem Bridge.
4. **Credenciais padrão:** usuário `msfadmin`, senha `msfadmin`. (Sim, é
   propositalmente horrível — faz parte do exercício.)
5. Descubra o IP que ele recebeu na rede interna:

   ```bash
   # Dentro do Metasploitable
   msfadmin@metasploitable:~$ ip addr    # ou: ifconfig
   ```

> 💡 **Dica Técnica:** Se as duas VMs estão na mesma Rede Interna mas não há
> servidor DHCP, elas podem não receber IP automaticamente. Soluções: ativar o
> servidor DHCP da rede interna do VirtualBox (via `VBoxManage dhcpserver`), ou
> fixar IPs estáticos manualmente na mesma faixa (ex.: `192.168.56.10` para o
> Kali e `192.168.56.20` para o alvo).

## 5.6 Validando o laboratório

Antes de comemorar, prove que (a) as VMs se enxergam e (b) o alvo **não** enxerga
a internet.

```bash
# No Kali: o alvo responde? (troque pelo IP real do Metasploitable)
$ ping -c 3 192.168.56.20

# No Kali, pela placa da rede interna, o alvo esta vivo e com portas abertas?
$ nmap -sn 192.168.56.0/24          # descoberta de hosts
```

```bash
# No Metasploitable: ele NAO deve alcancar a internet (isto deve FALHAR)
msfadmin@metasploitable:~$ ping -c 3 8.8.8.8
# Esperado: 100% packet loss / Network is unreachable
```

Se o alvo responde ao `ping` vindo do Kali **e** falha ao tentar alcançar
`8.8.8.8`, seu isolamento está correto. Esse teste duplo é o selo de qualidade do
laboratório.

> ⚠️ **Atenção:** Se o `ping 8.8.8.8` do Metasploitable **funcionar**, PARE.
> Significa que o alvo vulnerável está exposto à internet. Desligue a VM,
> corrija o modo de rede para Rede Interna e só então prossiga.

## 5.7 Expandindo o laboratório

Com o básico funcionando, você pode enriquecer o campo de treino conforme avança:

- **Metasploitable 3** — alvos Windows e Linux mais modernos.
- **VMs de CTF** — máquinas vulneráveis propositais, com níveis de dificuldade.
- **DVWA / OWASP Juice Shop** — aplicações web deliberadamente vulneráveis, ideais
  para o Capítulo 8.
- **Para a Parte V (IA):** um ambiente Python isolado (`venv` ou contêiner) com
  bibliotecas de *machine learning* para praticar os ataques e defesas dos
  Capítulos 11–14 — incluindo um Jupyter Notebook em *sandbox*, cujo isolamento
  é tema do Capítulo 13.

```bash
# Exemplo: ambiente Python isolado para os experimentos de IA da Parte V
$ python3 -m venv ~/lab-ia
$ source ~/lab-ia/bin/activate
(lab-ia) $ pip install --upgrade pip
# bibliotecas especificas (torch, adversarial-robustness-toolbox etc.)
# serao instaladas nos capitulos correspondentes
```

> 💡 **Dica Técnica:** Trate cada novo alvo como o Metasploitable: rede isolada,
> *snapshot* antes de bagunçar, e a pergunta "isto pode escapar do laboratório?"
> antes de cada experimento — pergunta que, na Parte V, vira "este modelo/notebook
> pode executar código que eu não controlo?".

---

### Resumo do capítulo
- O laboratório isolado é o que torna a prática legal; virtualização dá isolamento, descartabilidade e *snapshots*.
- Arquitetura mínima: Kali (atacante) + Metasploitable (alvo) numa **Rede Interna sem internet**.
- Modos de rede: NAT (só internet), Rede Interna (isolada), Host-Only (host participa), Bridge (**nunca** para alvos vulneráveis).
- Valide com o teste duplo: alvo responde ao Kali **e** não alcança a internet.
- Expanda com DVWA/Juice Shop e um ambiente Python isolado para a Parte V.

### Para fixar
1. Monte o laboratório completo e execute o teste duplo de validação. Só avance quando ele passar.
2. Crie o *snapshot* `kali-limpo-atualizado` e, de propósito, bagunce algo no Kali; depois reverta. Entenda o fluxo de *snapshot* na prática.
