-- Mostra os menus do MindManager e os respectivos atalhos de teclado.
-- Serve para confirmar quais sao, nesta versao, os comandos de zoom e de
-- apresentacao, e ajustar o professor.py (--tecla-zoom-in / --tecla-zoom-out).
--
-- Correr com:  osascript mac/inspecionar.applescript
-- Precisa de autorizacao em Definicoes do Sistema > Privacidade e Seguranca >
-- Acessibilidade para o Terminal (ou para o Script Editor).

on run argumentos
	if (count of argumentos) > 0 then
		set nomeApp to item 1 of argumentos
	else
		set nomeApp to "MindManager"
	end if
set relatorio to ""

tell application nomeApp to activate
delay 1

tell application "System Events"
	tell process nomeApp
		repeat with m in menu bar items of menu bar 1
			set nomeMenu to name of m
			if nomeMenu is not missing value then
				set relatorio to relatorio & "== " & nomeMenu & " ==" & linefeed
				try
					repeat with mi in menu items of menu 1 of m
						set nomeItem to name of mi
						if nomeItem is not missing value and nomeItem is not "" then
							set atalho to ""
							try
								set tecla to value of attribute "AXMenuItemCmdChar" of mi
								if tecla is not missing value then set atalho to "  [cmd+" & tecla & "]"
							end try
							set relatorio to relatorio & "   " & nomeItem & atalho & linefeed
						end if
					end repeat
				end try
			end if
		end repeat
	end tell
end tell

return relatorio
end run
