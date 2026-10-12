#!/bin/bash
# Diagnostico para o Professor do Mapa no macOS.
# Mostra tudo o que e preciso saber para afinar o script a esta versao do
# MindManager: versao instalada, se tem dicionario AppleScript, menus e
# atalhos reais, e vozes de sintese disponiveis.
#
#   bash mac/verificar.sh > diagnostico.txt
#
# O despejo de menus precisa de autorizacao em Definicoes do Sistema >
# Privacidade e Seguranca > Acessibilidade para o Terminal.

APP="${1:-MindManager}"

echo "=== Aplicacao ==="
CAMINHO=$(mdfind -name "kMDItemFSName=${APP}.app" 2>/dev/null | head -1)
[ -z "$CAMINHO" ] && CAMINHO="/Applications/${APP}.app"
echo "caminho: $CAMINHO"
if [ -d "$CAMINHO" ]; then
    /usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' \
        "$CAMINHO/Contents/Info.plist" 2>/dev/null | sed 's/^/versao: /'
    /usr/libexec/PlistBuddy -c 'Print :CFBundleIdentifier' \
        "$CAMINHO/Contents/Info.plist" 2>/dev/null | sed 's/^/bundle: /'
    echo
    echo "=== Dicionario AppleScript (se existir, da-se controlo directo) ==="
    SDEF=$(find "$CAMINHO/Contents" -maxdepth 3 -name "*.sdef" 2>/dev/null)
    if [ -n "$SDEF" ]; then
        echo "$SDEF"
        echo "--- resumo das classes principais ---"
        python3 "$(dirname "$0")/dicionario.py" --sdef "$(echo $SDEF | head -1)" \
            2>&1 || grep -o '<\(command\|class\) name="[^"]*"' $SDEF | sort -u
    else
        /usr/libexec/PlistBuddy -c 'Print :NSAppleScriptEnabled' \
            "$CAMINHO/Contents/Info.plist" 2>/dev/null \
            | sed 's/^/NSAppleScriptEnabled: /' \
            || echo "sem .sdef e sem NSAppleScriptEnabled: so controlo por teclado"
    fi
else
    echo "nao encontrei a aplicacao; passe o nome como argumento"
fi

echo
echo "=== Vozes de sintese instaladas ==="
say -v '?' 2>/dev/null | awk '{printf "%-18s %s\n", $1, $2}' || echo "comando say indisponivel"

echo
echo "=== Menus e atalhos ==="
osascript "$(dirname "$0")/inspecionar.applescript" "$APP" 2>&1
