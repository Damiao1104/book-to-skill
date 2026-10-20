#!/bin/bash
# Arranca o professor com as opcoes que ficaram confirmadas neste Mac:
# voz Luciana (pt-BR, Premium instalada), ritmo mais calmo, avanco pela tecla
# global e realce por cor de fundo mais marcador.
#
#   bash mac/aula.sh                 # o mapa aberto no MindManager
#   bash mac/aula.sh --inicio 120    # retomar no no 120
#   bash mac/aula.sh --sem-notas     # so a estrutura
#
# Qualquer opcao passada aqui e acrescentada, e as repetidas ganham a ultima,
# por isso da para sobrepor qualquer uma destas.

exec python3 "$(dirname "$0")/professor.py" \
    --voz Luciana \
    --velocidade 160 \
    --avanco ficheiro \
    --realce auto \
    "$@"
