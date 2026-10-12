-- Diagnostica, passo a passo, o que acontece ao tentar focar um no profundo.
-- Nada fica escondido por um `try` silencioso: cada operacao diz OK ou FALHA.
--
--   osascript mac/testar_no.applescript 1.1
--   osascript mac/testar_no.applescript 2.3.1
--
-- O caminho sao os indices 1-based a partir do tema central, separados por
-- pontos — os mesmos numeros que o `--modo listar` mostra.

on run argumentos
	set caminho to "1"
	if (count of argumentos) > 0 then set caminho to (item 1 of argumentos) as text

	set AppleScript's text item delimiters to "."
	set indices to text items of caminho
	set AppleScript's text item delimiters to ""

	set r to {}

	tell application "MindManager"
		if (count of documents) is 0 then return "Abra um mapa no MindManager primeiro."
		set oTopico to central topic of document 1
		set zInicial to zoom level of document 1
	end tell
	set end of r to "zoom inicial do documento: " & zInicial

	-- O `central topic` da 13.1 e um contentor acima do tema central visivel.
	tell application "MindManager"
		set tRaiz to ""
		try
			set tRaiz to (title of central topic of document 1) as text
		end try
		set nRaiz to count of subtopics of central topic of document 1
		set lRaiz to -1
		try
			set lRaiz to level of central topic of document 1
		end try
	end tell
	if tRaiz is "" then
		set end of r to "INFO   `central topic` e um contentor sem titulo (level " & ¬
			lRaiz & ") com " & nRaiz & " topicos de raiz — nao se narra"
	else
		set end of r to "INFO   `central topic`: " & tRaiz & " (level " & lRaiz & ", " & ¬
			nRaiz & " subtopicos)"
	end if

	-- Descer pelo caminho, tentando expandir cada no pelo meio.
	set nivel to 1
	repeat with ix in indices
		set i to (ix as integer)

		set end of r to my expandir(oTopico, "nivel " & nivel)

		tell application "MindManager" to set quantos to count of subtopics of oTopico
		if i > quantos then
			set end of r to "FALHA  o nivel " & nivel & " so tem " & quantos & ¬
				" subtopicos; pediu o " & i
			return my juntar(r)
		end if

		tell application "MindManager" to set oTopico to subtopic i of oTopico
		set nivel to nivel + 1
		tell application "MindManager" to set oTitulo to (title of oTopico) as text
		set end of r to "desceu para " & nivel & ": " & oTitulo
	end repeat

	-- Estado do no alvo.
	tell application "MindManager"
		set oTitulo to (title of oTopico) as text
		set oNivel to level of oTopico
	end tell
	set end of r to "--- no alvo: " & oTitulo & " (level " & oNivel & ") ---"

	try
		tell application "MindManager" to set vis to visible of oTopico
		set end of r to "OK     visible: " & vis
	on error e
		set end of r to "FALHA  visible: " & e
	end try

	set end of r to my expandir(oTopico, "no alvo")

	try
		tell application "MindManager" to reveal oTopico
		set end of r to "OK     reveal"
	on error e
		set end of r to "FALHA  reveal: " & e
	end try

	try
		tell application "MindManager"
			zoom document 1 to 160
			delay 0.8
			set z1 to zoom level of document 1
			zoom document 1 to 70
			delay 0.8
			set z2 to zoom level of document 1
			zoom document 1 to zInicial
		end tell
		set end of r to "OK     zoom 160 -> " & z1 & ", zoom 70 -> " & z2 & ¬
			", restaurado para " & zInicial
		set end of r to "       (viu a vista afastar e aproximar neste no?)"
	on error e
		set end of r to "FALHA  zoom: " & e
	end try

	try
		tell application "MindManager" to set c to fill color of oTopico
		if class of c is list then
			set end of r to "OK     fill color e lista RGB: " & (c as text) & ¬
				"  (o realce funciona)"
		else
			set end of r to "INFO   fill color nao e lista (" & (class of c as text) & ¬
				"): o no herda a cor do estilo, logo nao e realcado"
		end if
	on error e
		set end of r to "FALHA  fill color: " & e
	end try

	return my juntar(r)
end run

-- Tenta expandir um no e diz o que aconteceu, sem esconder o erro.
on expandir(oTopico, etiqueta)
	try
		tell application "MindManager" to set antes to collapsed of oTopico
	on error e
		return "FALHA  ler collapsed (" & etiqueta & "): " & e
	end try
	if antes is false then return "OK     " & etiqueta & " ja estava aberto"
	try
		tell application "MindManager"
			set collapsed of oTopico to false
			delay 0.3
			set depois to collapsed of oTopico
		end tell
		if depois is false then
			return "OK     " & etiqueta & " expandido (collapsed passou a false)"
		else
			return "FALHA  " & etiqueta & ": aceitou o comando mas collapsed " & ¬
				"continua true"
		end if
	on error e
		return "FALHA  expandir (" & etiqueta & "): " & e
	end try
end expandir

on juntar(lista)
	set saida to ""
	repeat with linha in lista
		set saida to saida & linha & linefeed
	end repeat
	return saida
end juntar
