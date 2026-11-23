# Prefácio

Durante anos, a segurança da informação teve um mapa relativamente estável:
redes, sistemas, aplicações. Aprendíamos a enxergar como um invasor enxerga —
endereços, portas, serviços, falhas — e a devolver essa compreensão em forma de
defesa. Esse mapa continua válido, e metade deste livro é dedicada a ele, com o
rigor de sempre: a mentalidade, o laboratório, o método dos três pontos, a
exploração e o relatório.

Mas o território mudou. Surgiu uma nova classe de sistemas — modelos de
*machine learning* e, sobretudo, modelos de linguagem — que não se defende com o
mesmo ferramental. Um firewall não detém uma injeção de prompt; um antivírus não
reconhece uma perturbação adversarial calculada no gradiente; um *patch* não
conserta um `pickle` que executa código ao ser carregado. Esses sistemas são
superfícies de ataque novas, com física própria, e exigem defesas próprias:
semânticas (*guardrails*), matemáticas (treinamento adversarial) e de esteira
(MLSecOps).

Este livro nasceu da convicção de que essas duas metades são uma só disciplina.
O profissional que entende o pacote de rede e o que entende a matriz de pesos
não são duas pessoas diferentes — ou não deveriam ser. A pergunta que move um é
exatamente a que move o outro: *qual premissa o desenvolvedor assumiu como
verdadeira, e como ela se quebra?* Em um banco de dados, a premissa é que o dado
é só dado. Em um modelo de linguagem, é que instrução e dado se separam. A
mentalidade é a mesma; muda a superfície.

## Para quem é este livro

Para quem quer entender segurança de ponta a ponta na era da IA: estudantes,
analistas, desenvolvedores, profissionais de DevOps migrando para DevSecOps, e
cientistas de dados que precisam proteger o que constroem. Não é preciso ser
especialista para começar — é preciso disposição para montar o laboratório do
Capítulo 5 e repetir cada comando. A profundidade vem da prática dirigida.

## Como ler

Na ordem. A progressão é deliberada: primeiro a **mente** e a **lei** (sem as
quais o resto é perigoso), depois o **laboratório**, o **método**, a **prática**
e, por fim, a **defesa de IA**. Cada ataque vem acompanhado de sua defesa —
porque entender o ataque é a única base sólida da defesa, e porque o objetivo
final deste livro nunca foi invadir: foi proteger.

## Um compromisso

Todo o conteúdo ofensivo pressupõe autorização. Esta não é uma formalidade
jurídica no início do livro — é a linha que separa o profissional do criminoso,
e ela é tratada com seriedade no Capítulo 2. Leia-o antes de digitar o primeiro
comando contra qualquer coisa que não seja sua.

Bom estudo — e que a mesma mão que aprende a atacar seja a que aprende a
defender.

*Damião dos Santos*
