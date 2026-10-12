#!/bin/bash
# Toca o ficheiro-gatilho: faz o professor passar ao no seguinte quando esta
# a correr com --avanco ficheiro. Funciona com qualquer janela em foco, desde
# que ligado a um atalho de teclado global (ver o README).
#
#   bash mac/avancar.sh [ficheiro]
touch "${1:-$HOME/.professor-avanca}"
