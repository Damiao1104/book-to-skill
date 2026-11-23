# Referências e Leituras Recomendadas

> Esta não é uma bibliografia acadêmica exaustiva, mas um roteiro de estudo
> curado: as fontes primárias e os materiais que sustentam cada parte do livro e
> que valem a leitura direta. Como endereços na web mudam com frequência, as
> fontes são citadas pelo título e pela organização responsável — localize-as
> pela busca, preferindo sempre o site oficial.

## Fundamentos, redes e metodologia (Partes I–IV)

- **Gordon "Fyodor" Lyon — *Nmap Network Scanning*** (o guia de referência oficial
  do Nmap). A documentação definitiva sobre varredura de portas, detecção de
  serviços/versões e o NSE.
- **Documentação oficial do Nmap** (`man nmap` e o Reference Guide). Leitura
  obrigatória para os Capítulos 6–7.
- **OffSec — *Metasploit Unleashed*** (curso aberto). Base do Capítulo 9.
- **OWASP — *Web Security Testing Guide* (WSTG)** e o **OWASP Top Ten**.
  Metodologia de teste de aplicações web (Capítulo 8).
- **Exploit Database (Exploit-DB)**, mantido pela OffSec; e o utilitário
  `searchsploit` do Kali. Base do Capítulo 8.
- **MITRE — Programa CVE**; **FIRST — Common Vulnerability Scoring System (CVSS)**;
  **NIST — National Vulnerability Database (NVD)**. As bases de vulnerabilidades.
- **RFC 793 (TCP)** e **RFC 791 (IP)** — as especificações que explicam o
  *handshake* e o endereçamento do Capítulo 3.
- **Documentação do Kali Linux** (OffSec) e do **Metasploitable** (Rapid7), para
  montar e entender o laboratório do Capítulo 5.

## Legislação brasileira (Capítulo 2)

- **Lei nº 12.737/2012** (inseriu o Art. 154-A no Código Penal — invasão de
  dispositivo informático; "Lei Carolina Dieckmann").
- **Lei nº 14.155/2021** (endureceu penas e ajustou tipos correlatos).
- **Lei nº 13.709/2018 — LGPD** (Lei Geral de Proteção de Dados Pessoais).
- **Lei nº 12.965/2014 — Marco Civil da Internet**.
- **Decreto-Lei nº 2.848/1940 — Código Penal**, para os tipos clássicos que podem
  incidir (dano, interrupção de serviço, furto e estelionato eletrônicos).

> Consulte sempre o texto **consolidado e vigente** das leis no Planalto
> (planalto.gov.br); penas e redações mudam com leis posteriores.

## Segurança de LLMs e guardrails (Capítulo 11)

- **OWASP — *Top 10 for Large Language Model Applications***. O mapa de referência
  dos riscos de aplicações com LLM.
- **NVIDIA — *NeMo Guardrails*** (documentação do framework e da linguagem Colang).
- Materiais do **OWASP** sobre injeção de prompt e tratamento inseguro de saída.

## Ataques adversariais e defesa matemática (Capítulo 12)

- **Goodfellow, Shlens & Szegedy — *Explaining and Harnessing Adversarial
  Examples*** (2015). A origem do FGSM.
- **Madry et al. — *Towards Deep Learning Models Resistant to Adversarial
  Attacks*** (2018). PGD e treinamento adversarial como referência de robustez.
- **Szegedy et al. — *Intriguing Properties of Neural Networks*** (2014). O
  trabalho que revelou os exemplos adversariais.
- **IBM — *Adversarial Robustness Toolbox (ART)*** e **CleverHans** (bibliotecas
  de ataque e defesa). Documentação oficial dos projetos.

## Pipelines MLOps, serialização e cadeia de suprimentos (Capítulos 13–14)

- **Hugging Face — documentação do *Safetensors*** (formato e motivação de
  segurança frente ao `pickle`).
- **Documentação do Python — módulo `pickle`** (a própria nota de segurança que
  alerta: não desserialize dados não confiáveis).
- Materiais sobre **MLSecOps** e segurança de *supply chain* de IA (OWASP Machine
  Learning Security Top 10, quando aplicável).

## Governança e ameaças emergentes (Capítulo 15)

- **NIST — *AI Risk Management Framework (AI RMF 1.0)*** e o *Playbook* associado.
- **União Europeia — *Artificial Intelligence Act*** (Regulamento (UE) 2024/1689).
  Consulte o texto oficial no EUR-Lex.
- Publicações do **NIST** sobre IA confiável (viés, explicabilidade,
  robustez) que detalham as características citadas no Capítulo 15.

---

> **Nota de método.** Prefira sempre a **fonte primária** (a lei no Planalto, a
> RFC no IETF, o paper no repositório dos autores, a documentação oficial da
> ferramenta) a resumos de terceiros. Em segurança — e mais ainda em IA, onde o
> campo muda a cada mês — ler a fonte é o que separa o profissional de quem
> repete o que ouviu.
