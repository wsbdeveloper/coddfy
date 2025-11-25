#!/bin/bash
# Script principal para separar repositórios backend e frontend
# Uso: ./scripts/split_all.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="../coddfy-contracts-manager-ccm-backend"
FRONTEND_DIR="../coddfy-contracts-manager-ccm-frontend"

echo "=========================================="
echo "🔀 Separando Repositórios"
echo "=========================================="
echo ""
echo "Este script irá criar dois repositórios separados:"
echo "  - Backend:  $BACKEND_DIR"
echo "  - Frontend: $FRONTEND_DIR"
echo ""
read -p "Continuar? (s/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operação cancelada."
    exit 1
fi

# Executar scripts de separação
echo ""
echo "📦 Criando repositório Backend..."
bash "$PROJECT_ROOT/scripts/split_backend.sh" "$BACKEND_DIR"

echo ""
echo "📦 Criando repositório Frontend..."
bash "$PROJECT_ROOT/scripts/split_frontend.sh" "$FRONTEND_DIR"

# Copiar READMEs template
echo ""
echo "📝 Copiando templates de README..."

if [ -f "$PROJECT_ROOT/scripts/BACKEND_README_TEMPLATE.md" ]; then
    cp "$PROJECT_ROOT/scripts/BACKEND_README_TEMPLATE.md" "$BACKEND_DIR/README.md"
    echo "  ✅ README.md criado para backend"
fi

if [ -f "$PROJECT_ROOT/scripts/FRONTEND_README_TEMPLATE.md" ]; then
    cp "$PROJECT_ROOT/scripts/FRONTEND_README_TEMPLATE.md" "$FRONTEND_DIR/README.md"
    echo "  ✅ README.md criado para frontend"
fi

# Copiar ENV_VARIABLES.md para backend
if [ -f "$PROJECT_ROOT/ENV_VARIABLES.md" ]; then
    cp "$PROJECT_ROOT/ENV_VARIABLES.md" "$BACKEND_DIR/"
    echo "  ✅ ENV_VARIABLES.md copiado para backend"
fi

echo ""
echo "=========================================="
echo "✅ Separação concluída com sucesso!"
echo "=========================================="
echo ""
echo "📁 Repositórios criados:"
echo "  - Backend:  $BACKEND_DIR"
echo "  - Frontend: $FRONTEND_DIR"
echo ""
echo "📝 Próximos passos:"
echo ""
echo "1. Backend:"
echo "   cd $BACKEND_DIR"
echo "   git add ."
echo "   git commit -m 'Initial commit: Backend separado'"
echo "   # Criar repositório no GitHub/GitLab e fazer push"
echo ""
echo "2. Frontend:"
echo "   cd $FRONTEND_DIR"
echo "   git add ."
echo "   git commit -m 'Initial commit: Frontend separado'"
echo "   # Criar repositório no GitHub/GitLab e fazer push"
echo ""
echo "3. Configurar:"
echo "   - Variáveis de ambiente em cada repositório"
echo "   - CORS no backend com URL do frontend"
echo "   - VITE_API_URL no frontend com URL do backend"
echo ""

