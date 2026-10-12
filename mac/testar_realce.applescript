-- Mostra, uma a uma, as formas de marcar visualmente um no, para se ver qual
-- aparece neste mapa. Cada marca fica 2 segundos e e reposta a seguir, pelo
-- que a sonda leva cerca de 10 segundos e so imprime o relatorio no fim.
--
--   osascript mac/testar_realce.applescript 1.1
--   osascript mac/testar_realce.applescript ID-DO-TOPICO
--
-- Olhe para a janela do MindManager enquanto corre e repare em qual das marcas
-- se ve. O caminho sao os indices do `--modo listar` (1.1, 2.3.1), ou o id.

on run argumentos
	set alvo to "1"
	if (count of argumentos) > 0 then set alvo to (item 1 of argumentos) as text

	tell application "MindManager"
		if (count of documents) is 0 then return "Abra um mapa no MindManager primeiro."
	end tell

	set oTopico to my resolver(alvo)
	if oTopico is missing value then return "Nao encontrei o no " & alvo

	tell application "MindManager"
		set oTitulo to (title of oTopico) as text
		reveal oTopico
		zoom document 1 to 130
	end tell

	set r to {"no: " & oTitulo, "Olhe para o mapa durante os proximos 10 segundos.", ""}
	set end of r to my corDeFundo(oTopico)
	set end of r to my corDoTexto(oTopico)
	set end of r to my corDaLinha(oTopico)
	set end of r to my marcador(oTopico)
	set end of r to ""
	set end of r to "Qual se viu? --realce fundo | texto | marcador"
	set end of r to "(a cor da linha ainda nao e opcao; se so essa se vir, diga-me)"
	return my juntar(r)
end run

-- 1) cor de fundo do topico
on corDeFundo(t)
	try
		tell application "MindManager"
			set antes to fill color of t
			if class of antes is not list then
				return "INFO   1) cor de fundo: vem do estilo do mapa, nao da para mexer"
			end if
			set fill color of t to {65535, 56540, 33410}
			delay 2
			set fill color of t to antes
		end tell
		return "OK     1) cor de fundo ambar aplicada e reposta"
	on error e
		return "FALHA  1) cor de fundo: " & e
	end try
end corDeFundo

-- 2) cor do texto
on corDoTexto(t)
	try
		tell application "MindManager"
			set antes to text color of t
			if class of antes is not list then
				return "INFO   2) cor do texto: vem do estilo do mapa, nao da para mexer"
			end if
			set text color of t to {51400, 0, 0}
			delay 2
			set text color of t to antes
		end tell
		return "OK     2) cor do texto vermelha aplicada e reposta"
	on error e
		return "FALHA  2) cor do texto: " & e
	end try
end corDoTexto

-- 3) cor da linha do ramo
on corDaLinha(t)
	try
		tell application "MindManager"
			set antes to line color of t
			if class of antes is not list then
				return "INFO   3) cor da linha: vem do estilo do mapa, nao da para mexer"
			end if
			set line color of t to {51400, 0, 0}
			delay 2
			set line color of t to antes
		end tell
		return "OK     3) cor da linha vermelha aplicada e reposta"
	on error e
		return "FALHA  3) cor da linha: " & e
	end try
end corDaLinha

-- 4) marcador (bookmark)
on marcador(t)
	try
		tell application "MindManager"
			set antes to bookmark of t
			set bookmark of t to true
			delay 2
			set bookmark of t to antes
		end tell
		return "OK     4) marcador aplicado e reposto"
	on error e
		return "FALHA  4) marcador: " & e
	end try
end marcador

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

on juntar(lista)
	set saida to ""
	repeat with linha in lista
		set saida to saida & linha & linefeed
	end repeat
	return saida
end juntar
