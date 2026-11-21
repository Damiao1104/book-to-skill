# Guia Definitivo de Kali Linux, Ethical Hacking e Defesa de IA

> Um livro técnico e didático sobre a mentalidade do invasor, a metodologia de
> teste de intrusão em redes e sistemas, e a nova fronteira da segurança:
> proteger modelos matemáticos e sistemas de Inteligência Artificial.

---

## Aviso ético e legal (leia antes de tudo)

Todo o conteúdo ofensivo deste livro pressupõe **autorização explícita**: um
contrato de pentest, um programa de *bug bounty* com escopo definido, uma
competição CTF, ou — o mais recomendável para aprender — **o seu próprio
laboratório virtual isolado**, descrito no Capítulo 5.

Executar as técnicas descritas contra sistemas de terceiros sem autorização é
**crime** no Brasil (Lei 12.737/2012, entre outras) e na maioria dos países.
Este livro ensina a atacar para ensinar a defender. A mesma mão que entende o
`exploit` é a que escreve a regra de firewall, o *guardrail* semântico e o
treinamento adversarial. Trate cada técnica como um bisturi: a diferença entre o
cirurgião e o agressor não está na lâmina, está na autorização e na intenção.

---

## Como este livro está organizado

O livro segue uma progressão deliberada: primeiro a **mente**, depois o
**laboratório**, depois o **método**, depois a **prática**, e por fim a nova
**fronteira da IA**. Não pule a Parte I achando que "é só filosofia": a
mentalidade e o enquadramento legal são o que separam um profissional de um
réu.

### Parte I — A Mente Hacker, Ética e Fundamentos Tecnológicos
- [Capítulo 1 — Cultura Hacker e o Pensamento do Invasor](capitulo-01-cultura-hacker.md)
- [Capítulo 2 — Legislação, Ética e Fronteiras Legais](capitulo-02-legislacao-etica.md)
- [Capítulo 3 — Fundamentos Pré-Invasão e Tecnologias de Suporte](capitulo-03-fundamentos-pre-invasao.md)

### Parte II — Laboratório Seguro e Arquitetura do Kali Linux
- [Capítulo 4 — Filosofia e Estrutura do Kali Linux](capitulo-04-kali-linux.md)
- [Capítulo 5 — Construção do Laboratório Virtual Isolado](capitulo-05-laboratorio-virtual.md)

### Parte III — A Metodologia de Três Pontos (IP, Portas e Falhas)
- [Capítulo 6 — Reconhecimento e Descoberta de IP](capitulo-06-reconhecimento-ip.md)
- [Capítulo 7 — Mapeamento de Portas e Serviços com Nmap](capitulo-07-nmap-portas.md)
- [Capítulo 8 — Identificação e Análise de Vulnerabilidades](capitulo-08-vulnerabilidades.md)

### Parte IV — Exploração Prática e Auditoria Ofensiva
- [Capítulo 9 — Fases de Exploração e Ferramentas Práticas](capitulo-09-exploracao.md)
- [Capítulo 10 — Pós-Exploração, Anonimização e Relatórios](capitulo-10-pos-exploracao-relatorios.md)

### Parte V — Segurança e Defesa de Inteligência Artificial (AI Defense & MLSecOps)
- [Capítulo 11 — Vetores e Vulnerabilidades em Modelos de Linguagem (LLMs)](capitulo-11-llm-vetores.md)
- [Capítulo 12 — Ataques Adversariais e Defesa Matemática de Modelos](capitulo-12-ataques-adversariais.md)
- [Capítulo 13 — Blindagem de Pipelines MLOps e Cadeia de Suprimentos de IA](capitulo-13-mlops-supply-chain.md)
- [Capítulo 14 — Envenenamento de Dados e Proteção de Propriedade Intelectual](capitulo-14-data-poisoning.md)
- [Capítulo 15 — Governança, Next-Gen DevSecOps e Ameaças Emergentes](capitulo-15-governanca-devsecops.md)

---

## Convenções tipográficas

- **Blocos de comando** aparecem com o prefixo lógico do contexto. `$` indica
  usuário comum, `#` indica root/privilégios elevados. Comentários em comandos
  usam `#` dentro do bloco.
- **Tabelas comparativas** resumem flags, vetores e contramedidas.
- Caixas de destaque:
  - **⚠️ Atenção** — risco legal, risco de indisponibilidade, ou pegadinha comum.
  - **💡 Dica Técnica** — atalho, boa prática ou detalhe que separa o amador do profissional.
  - **🛡️ Defesa** — a contramedida correspondente ao ataque que acabou de ser descrito.

## Pré-requisitos de conhecimento

Você aproveitará muito mais o livro se tiver:
- noção básica de linha de comando Linux (`cd`, `ls`, `cat`, `grep`);
- lógica de programação (Python é usado nos exemplos);
- vontade de montar o laboratório do Capítulo 5 e **repetir cada comando**.

O resto o livro constrói do zero.
