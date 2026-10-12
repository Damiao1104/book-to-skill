-- Mostra, uma a uma, as formas de marcar visualmente um no, para se ver qual
-- aparece neste mapa. Cada marca fica 2 segundos e e reposta a seguir.
--
--   osascript mac/testar_realce.applescript 1.1
--   osascript mac/testar_realce.applescript ID-DO-TOPICO
--
-- Olhe para a janela do MindManager enquanto corre e repare em qual das quatro
-- marcas se ve. O caminho sao os indices do `--modo listar` (1.1, 2.3.1), ou o
-- id do topico.

on run argumentos
	set alvo to "1"
	if (count of argumentos) > 0 then set alvo to (item 1 of argumentos) as text

	tell application "MindManager"
		if (count of documents) is 0 then return "Abra um mapa no MindManager primeiro."
	end tell

	set oTopico to my resolver(alvo)
	if oTopico is missing value then
		return "Nao encontrei o no " & alvo
	end if

	tell application "MindManager"
		set oTitulo to (title of oTopico) as text
		reveal oTopico
	end tell

	set r to {"no: " & oTitulo, ""}

	set end of r to my experimentar(oTopico, "fill color", "{65535, 56540, 33410}", ¬
		"1) cor de fundo ambar")
	set end of r to my experimentar(oTopico, "text color", "{51400, 0, 0}", ¬
		"2) cor do texto vermelha")
	set end of r to my experimentar(oTopico, "line color", "{51400, 0, 0}", ¬
		"3) cor da linha vermelha")
	set end of r to my alternarMarcador(oTopico, "4) marcador (bookmark)")

	set end of r to ""
	set end of r to "Qual das quatro se viu? Use --realce fundo | texto | marcador"
	set end of r to "(a linha nao e opcao do professor; se so essa se vir, diga-me)"
	return my juntar(r)
end run

-- Aceita um caminho com pontos (1.2.1) ou o id do topico.
on resolver(alvo)
	if alvo contains "-" then
		try
			tell application "MindManager" to set t to topic id alvo of document 1
			return t
		on error
			return missing value
		end try
	end if

	set AppleScript's text item delimiters to "."
	set indices to text items of alvo
	set AppleScript's text item delimiters to ""

	tell application "MindManager" to set t to central topic of document 1
	repeat with ix in indices
		set i to (ix as integer)
		tell application "MindManager"
			if i > (count of subtopics of t) then return missing value
			set t to subtopic i of t
		end tell
	end repeat
	return t
end resolver

-- Aplica um valor a uma propriedade, espera, e repoe o que estava.
on experimentar(oTopico, propriedade, valor, etiqueta)
	try
		tell application "MindManager"
			set antes to ""
			set c to run script "tell application \"MindManager\" to get " & ¬
				propriedade & " of topic id \"" & (id of oTopico) & ¬
				"\" of document 1"
			if class of c is list then
				set antes to "{" & (item 1 of c as text) & ", " & ¬
					(item 2 of c as text) & ", " & (item 3 of c as text) & "}"
			end if
		end tell
		if antes is "" then
			return "INFO   " & etiqueta & ": vem do estilo do mapa, nao da para mexer"
		end if
		run script "tell application \"MindManager\" to set " & propriedade & ¬
			" of topic id \"" & (id of oTopico) & "\" of document 1 to " & valor
		delay 2
		run script "tell application \"MindManager\" to set " & propriedade & ¬
			" of topic id \"" & (id of oTopico) & "\" of document 1 to " & antes
		return "OK     " & etiqueta & " aplicada e reposta (viu?)"
	on error e
		return "FALHA  " & etiqueta & ": " & e
	end try
end experimentar

on alternarMarcador(oTopico, etiqueta)
	try
		tell application "MindManager"
			set antes to bookmark of oTopico
			set bookmark of oTopico to true
			delay 2
			set bookmark of oTopico to antes
		end tell
		return "OK     " & etiqueta & " aplicado e reposto (viu?)"
	on error e
		return "FALHA  " & etiqueta & ": " & e
	end try
end alternarMarcador

on juntar(lista)
	set saida to ""
	repeat with linha in lista
		set saida to saida & linha & linefeed
	end repeat
	return saida
end juntar
