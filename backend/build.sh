#!/bin/bash
# Script de build para Render
# Este script é executado durante o build no Render

set -e

echo "🔧 Instalando dependências..."

# Instala Poetry se não estiver instalado
if ! command -v poetry &> /dev/null; then
    echo "📦 Instalando Poetry..."
    pip install poetry
fi

# Configura Poetry
poetry config virtualenvs.create false

# Instala dependências
echo "📚 Instalando dependências Python..."
poetry install --no-interaction --no-ansi

echo "✅ Build concluído com sucesso!"

