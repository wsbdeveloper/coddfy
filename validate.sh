#!/bin/bash

# Script de validação do projeto
# Verifica se todos os componentes essenciais estão presentes

echo "=========================================="
echo "🔍 Validando Coddfy Contracts Manager CCM"
echo "=========================================="

ERRORS=0

# Função para verificar arquivo
check_file() {
    if [ -f "$1" ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - FALTANDO"
        ((ERRORS++))
    fi
}

# Função para verificar diretório
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $1/"
    else
        echo "❌ $1/ - FALTANDO"
        ((ERRORS++))
    fi
}

echo ""
echo "📦 Verificando arquivos do Backend..."
check_file "pyproject.toml"
check_file "backend/setup.py"
check_file "backend/alembic.ini"
check_dir "backend"
check_file "backend/__init__.py"
check_file "backend/__main__.py"
check_file "backend/app.py"
check_file "backend/config.py"
check_file "backend/database.py"
check_file "backend/models.py"
check_file "backend/schemas.py"
check_file "backend/auth.py"
check_file "backend/routes.py"
check_file "backend/development.ini"
check_dir "backend/alembic"
check_dir "backend/scripts"
check_dir "backend/views"
check_file "backend/views/auth.py"
check_file "backend/views/dashboard.py"
check_file "backend/views/contracts.py"
check_file "backend/views/consultants.py"
check_file "backend/views/clients.py"

echo ""
echo "⚛️  Verificando arquivos do Frontend..."
check_dir "frontend"
check_file "frontend/package.json"
check_file "frontend/vite.config.ts"
check_file "frontend/tsconfig.json"
check_file "frontend/tailwind.config.js"
check_file "frontend/index.html"
check_dir "frontend/src"
check_file "frontend/src/App.tsx"
check_file "frontend/src/main.tsx"
check_file "frontend/src/index.css"
check_dir "frontend/src/pages"
check_file "frontend/src/pages/Dashboard.tsx"
check_file "frontend/src/pages/Contracts.tsx"
check_file "frontend/src/pages/Consultants.tsx"
check_file "frontend/src/pages/Login.tsx"
check_dir "frontend/src/components"
check_file "frontend/src/components/Layout.tsx"
check_dir "frontend/src/lib"
check_file "frontend/src/lib/api.ts"
check_file "frontend/src/lib/utils.ts"
check_file "frontend/src/lib/format.ts"

echo ""
echo "🐳 Verificando arquivos Docker..."
check_file "docker-compose.yml"
check_file "Dockerfile.backend"
check_file "frontend/Dockerfile.frontend"

echo ""
echo "🔧 Verificando scripts..."
check_dir "backend/scripts"
check_file "backend/scripts/create_admin.py"
check_file "backend/scripts/seed_data.py"
check_file "setup.sh"
check_file "start.sh"
check_file "stop.sh"

echo ""
echo "📚 Verificando documentação..."
check_file "PRD.md"
check_file "GETTING_STARTED.md"
check_file "PROJECT_SUMMARY.md"

echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Validação concluída com sucesso!"
    echo "   Todos os arquivos essenciais estão presentes."
    echo ""
    echo "🚀 Próximos passos:"
    echo "   1. Execute: ./setup.sh"
    echo "   2. Depois: ./start.sh"
    echo "   3. Acesse: http://localhost:5173"
else
    echo "❌ Validação falhou com $ERRORS erro(s)"
    echo "   Alguns arquivos estão faltando."
fi
echo "=========================================="

















