-- Despeja a estrutura do mapa aberto no MindManager.
-- Um registo por no, separado por <US>:
--    caminho <US> nivel <US> nome <US> notas
-- e os registos separados por <RS>. Usam-se estes separadores (e nao
-- mudanca de linha) para as notas com varias linhas nao partirem o formato.
-- caminho = indices 1-based separados por pontos; vazio no tema central.
--
--   osascript mac/estrutura.applescript [indice-do-documento]

property RS : (character id 30)
property US : (character id 31)

on run argumentos
	set indice to 1
	if (count of argumentos) > 0 then set indice to (item 1 of argumentos) as integer
	tell application "MindManager"
		if (count of documents) is 0 then error "Nenhum mapa aberto no MindManager."
		set oTema to central topic of document indice
	end tell
	return my percorrer(oTema, "", 1)
end run

on percorrer(oTopico, caminho, nivel)
	tell application "MindManager"
		set oNome to name of oTopico
		if oNome is missing value then set oNome to ""
		set asNotas to ""
		try
			set asNotas to notes of oTopico
			if asNotas is missing value then set asNotas to ""
		end try
		set quantos to count of subtopics of oTopico
	end tell

	set saida to caminho & US & (nivel as text) & US & (oNome as text) & US & (asNotas as text) & RS

	repeat with i from 1 to quantos
		if caminho is "" then
			set filho to (i as text)
		else
			set filho to caminho & "." & (i as text)
		end if
		tell application "MindManager"
			set oSub to subtopic i of oTopico
		end tell
		set saida to saida & my percorrer(oSub, filho, nivel + 1)
	end repeat

	return saida
end percorrer
