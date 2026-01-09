#!/bin/bash

# Script de inicialização do projeto
# Este script configura o ambiente de desenvolvimento

set -e

echo "=========================================="
echo "🚀 Coddfy Contracts Manager CCM - Setup"
echo "=========================================="


echo ""
echo "📦 Instalando dependências Python com Poetry..."
poetry install


echo ""
echo "⏳ Aguardando banco de dados ficar pronto..."
sleep 5

echo ""
echo "📊 Aplicando migrações no banco de dados..."
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..

#echo ""
#echo "👤 Criando usuário admin padrão..."
#poetry run python backend/scripts/create_admin.py

#echo ""
#echo "🌱 Populando banco com dados de exemplo..."
#poetry run python backend/scripts/seed_partners.py
#poetry run python backend/scripts/seed_data.py

echo ""
echo "=========================================="
echo "✅ Setup completo!"
echo "=========================================="
echo ""
echo "Para iniciar o servidor backend:"
echo "  poetry run python -m backend"
echo ""
echo "Para usar o shell interativo:"
echo "  poetry run pshell backend/development.ini"
echo ""
echo "=========================================="

poetry run python -m backend

