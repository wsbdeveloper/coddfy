#!/bin/bash

# Script de inicialização do projeto
# Este script configura o ambiente de desenvolvimento

set -e

echo "=========================================="
echo "🚀 Coddfy Contracts Manager CCM - Setup"
echo "=========================================="

# Verifica se o .env existe, senão cria a partir do .env.example
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Configure as variáveis antes de continuar."
fi

# Verifica se o Poetry está instalado
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry não encontrado. Instale com:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo ""
echo "📦 Instalando dependências Python com Poetry..."
poetry install

echo ""
echo "🐘 Iniciando banco de dados PostgreSQL com Docker..."
docker-compose up -d db

echo ""
echo "⏳ Aguardando banco de dados ficar pronto..."
sleep 5

echo ""
echo "🔄 Criando migração inicial do banco de dados..."
cd backend && poetry run alembic -c alembic.ini revision --autogenerate -m "Initial migration" && cd ..

echo ""
echo "📊 Aplicando migrações no banco de dados..."
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..

echo ""
echo "👤 Criando usuário admin padrão..."
poetry run python backend/scripts/create_admin.py

echo ""
echo "=========================================="
echo "✅ Setup completo!"
echo "=========================================="
echo ""
echo "Para iniciar o servidor backend:"
echo "  poetry run python -m backend"
echo ""
echo "Para iniciar o frontend (em outro terminal):"
echo "  cd frontend && npm install && npm run dev"
echo ""
echo "Para usar o shell interativo:"
echo "  poetry run pshell backend/development.ini"
echo ""
echo "=========================================="

