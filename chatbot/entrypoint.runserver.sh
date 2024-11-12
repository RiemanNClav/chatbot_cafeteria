#!/bin/bash
set -e

# Verifica que Rasa esté disponible
echo "Verificando instalación de Rasa..."
rasa --version

# Ejecuta el servidor Rasa
echo "Iniciando el servidor Rasa..."

exec rasa run --enable-api --cors "*" --debug