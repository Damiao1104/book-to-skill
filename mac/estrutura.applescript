-- Despeja a estrutura do mapa aberto no MindManager.
--
-- Nota importante, verificada na 13.1: `central topic of document 1` nao e o
-- tema central visivel — e um contentor acima dele, sem titulo, que tem os
-- topicos de raiz como subtopicos. Esse contentor nao e narrado, mas os
-- caminhos continuam a contar a partir dele, para as referencias
-- `subtopic N of ... of central topic` ficarem validas.
-- Um registo por no, separado por <US>:
--    caminho <US> nivel <US> nome <US> notas <US> id
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
		-- O texto do no vive em `title`; `name` vem vazio em muitos topicos.
		set oNome to ""
		try
			set oNome to (title of oTopico) as text
		end try
		if oNome is "" then
			try
				set oNome to (name of oTopico) as text
			end try
		end if
		if oNome is missing value then set oNome to ""
		set asNotas to ""
		try
			set asNotas to notes of oTopico
			if asNotas is missing value then set asNotas to ""
		end try
		set quantos to count of subtopics of oTopico
	end tell

	-- O nivel vem da propriedade `level` da aplicacao, que e a verdade sobre a
	-- profundidade; o contador local serve so de reserva.
	set oNivel to nivel
	try
		tell application "MindManager" to set oNivel to level of oTopico
	end try

	if caminho is "" and oNome is "" then
		-- Contentor de raiz sem titulo: nao se narra, so se percorre.
		set saida to ""
	else
		set oId to ""
		try
			set oId to (id of oTopico) as text
		end try
		set saida to caminho & US & (oNivel as text) & US & (oNome as text) & US & (asNotas as text) & US & oId & RS
	end if

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
