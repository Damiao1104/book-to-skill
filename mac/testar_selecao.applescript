-- Observa a selecao no MindManager durante 15 segundos e descreve o que a
-- aplicacao devolve a cada clique. Serve para saber porque e que o
-- `--modo seguir` nao reage: o que e `selection`, e que propriedades tem.
--
--   osascript mac/testar_selecao.applescript
--
-- Corra, passe para a janela do MindManager e clique em varios nos. No fim
-- volte ao Terminal para ver o relatorio.

on run
	tell application "MindManager"
		if (count of documents) is 0 then return "Abra um mapa no MindManager primeiro."
	end tell

	set r to {"A observar 15 segundos — clique em varios nos no mapa.", ""}
	set anterior to "nada ainda"
	set voltas to 0

	repeat 30 times
		set voltas to voltas + 1
		set descricao to my descrever()
		if descricao is not anterior then
			set end of r to "[" & voltas & "] " & descricao
			set anterior to descricao
		end if
		delay 0.5
	end repeat

	set end of r to ""
	set end of r to "Se as linhas mostram o titulo do no em que clicou, o modo"
	set end of r to "seguir funciona. Se mostram outra coisa, mande-me estas linhas."
	return my juntar(r)
end run

on descrever()
	try
		tell application "MindManager"
			set s to selection of document 1
			set classe to (class of s) as text
			set quantos to -1
			if class of s is list then
				set quantos to count of s
				if quantos is 0 then return "selection: lista vazia (nada seleccionado)"
				set s to item 1 of s
			end if

			set oTitulo to "<sem title>"
			try
				set oTitulo to (title of s) as text
			end try
			set oId to "<sem id>"
			try
				set oId to (id of s) as text
			end try
			set oNivel to "?"
			try
				set oNivel to (level of s) as text
			end try

			set extra to ""
			if quantos is not -1 then set extra to " (lista de " & quantos & ")"
			return "classe " & classe & extra & " | level " & oNivel & " | " & ¬
				oTitulo & " | id " & oId
		end tell
	on error e
		return "ERRO: " & e
	end try
end descrever

on juntar(lista)
	set saida to ""
	repeat with linha in lista
		set saida to saida & linha & linefeed
	end repeat
	return saida
end juntar
