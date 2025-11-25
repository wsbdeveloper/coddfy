#!/bin/bash
# Script para criar repositório frontend separado
# Uso: ./scripts/split_frontend.sh [destino]

set -e

# Diretório de destino (padrão: ../coddfy-contracts-manager-ccm-frontend)
DEST_DIR="${1:-../coddfy-contracts-manager-ccm-frontend}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================="
echo "🔀 Criando repositório Frontend separado"
echo "=========================================="
echo "Origem: $PROJECT_ROOT/frontend"
echo "Destino: $DEST_DIR"
echo ""

# Criar diretório de destino
mkdir -p "$DEST_DIR"
cd "$DEST_DIR"

# Inicializar git se não existir
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório Git..."
    git init
fi

# Copiar arquivos do frontend
echo "📋 Copiando arquivos do frontend..."
cp -r "$PROJECT_ROOT/frontend"/* .

# Criar .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    echo "📝 Criando .gitignore..."
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
/.pnp
.pnp.js

# Testing
/coverage

# Production
/dist
/build

# Misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

# Logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

# Editor
.vscode/
.idea/
*.swp
*.swo

# Vite
.vite/
*.local

# TypeScript
*.tsbuildinfo
EOF
fi

# Criar .env.example se não existir
if [ ! -f ".env.example" ]; then
    echo "📝 Criando .env.example..."
    cat > .env.example << 'EOF'
# API URL - Configure para apontar para o backend
# Desenvolvimento local:
VITE_API_URL=http://localhost:6543/api

# Produção (após deploy do backend):
# VITE_API_URL=https://seu-backend.onrender.com/api
EOF
fi

# Ajustar Dockerfile se existir
if [ -f "Dockerfile.frontend" ]; then
    mv Dockerfile.frontend Dockerfile
fi

echo ""
echo "✅ Repositório frontend criado com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Criar .env com VITE_API_URL"
echo "   2. Revisar e ajustar README.md"
echo "   3. Testar: npm install"
echo "   4. Testar: npm run dev"
echo "   5. Fazer commit inicial"
echo ""

