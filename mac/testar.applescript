-- Testa, uma a uma, as capacidades do dicionario AppleScript do MindManager
-- de que o professor precisa. Diz OK ou FALHA em cada linha, para se saber
-- exactamente o que funciona nesta versao antes de correr a apresentacao.
--
--   osascript mac/testar.applescript
--
-- Abra um mapa no MindManager antes de correr.

on run
	set r to {}

	try
		tell application "MindManager" to set v to version
		set end of r to "OK     version: " & v
	on error e
		set end of r to "FALHA  version: " & e
	end try

	try
		tell application "MindManager" to set n to count of documents
		set end of r to "OK     documentos abertos: " & n
		if n is 0 then
			set end of r to "ATENCAO  abra um mapa e volte a correr este teste"
			return my juntar(r)
		end if
	on error e
		set end of r to "FALHA  count documents: " & e
		return my juntar(r)
	end try

	try
		tell application "MindManager" to set t to name of central topic of document 1
		set end of r to "OK     tema central: " & t
	on error e
		set end of r to "FALHA  central topic: " & e
	end try

	try
		tell application "MindManager" to set q to count of subtopics of central topic of document 1
		set end of r to "OK     subtopicos do tema central: " & q
	on error e
		set end of r to "FALHA  count subtopics: " & e
	end try

	set zInicial to missing value
	try
		tell application "MindManager" to set zInicial to zoom level of document 1
		set end of r to "OK     zoom level actual: " & zInicial
	on error e
		set end of r to "FALHA  zoom level: " & e
	end try

	try
		tell application "MindManager" to zoom document 1 to 115
		delay 0.6
		tell application "MindManager" to set zDepois to zoom level of document 1
		set end of r to "OK     zoom para 115 -> leu " & zDepois
		if zInicial is not missing value then
			tell application "MindManager" to zoom document 1 to zInicial
			set end of r to "OK     zoom restaurado para " & zInicial
		end if
	on error e
		set end of r to "FALHA  zoom to <inteiro>: " & e
	end try

	try
		tell application "MindManager" to select central topic of document 1
		set end of r to "OK     select do tema central"
	on error e
		set end of r to "FALHA  select: " & e
	end try

	try
		tell application "MindManager" to reveal central topic of document 1
		set end of r to "OK     reveal do tema central"
	on error e
		set end of r to "FALHA  reveal: " & e
	end try

	try
		tell application "MindManager"
			if (count of subtopics of central topic of document 1) > 0 then
				set oSub to subtopic 1 of central topic of document 1
				select oSub
				reveal oSub
				set end of r to "OK     select+reveal de um subtopico: " & (name of oSub)
			else
				set end of r to "ATENCAO  o mapa nao tem subtopicos para testar"
			end if
		end tell
	on error e
		set end of r to "FALHA  select de subtopico: " & e
	end try

	try
		tell application "MindManager"
			if (count of subtopics of central topic of document 1) > 0 then
				set c to collapsed of subtopic 1 of central topic of document 1
				set end of r to "OK     leitura de collapsed: " & c
			end if
		end tell
	on error e
		set end of r to "FALHA  collapsed: " & e
	end try

	return my juntar(r)
end run

on juntar(lista)
	set saida to ""
	repeat with linha in lista
		set saida to saida & linha & linefeed
	end repeat
	return saida
end juntar
