#!/bin/bash
# Script para criar repositório backend separado
# Uso: ./scripts/split_backend.sh [destino]

set -e

# Diretório de destino (padrão: ../coddfy-contracts-manager-ccm-backend)
DEST_DIR="${1:-../coddfy-contracts-manager-ccm-backend}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================="
echo "🔀 Criando repositório Backend separado"
echo "=========================================="
echo "Origem: $PROJECT_ROOT"
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

# Copiar arquivos do backend
echo "📋 Copiando arquivos do backend..."
cp -r "$PROJECT_ROOT/backend"/* .

# Copiar arquivos de configuração
echo "📋 Copiando arquivos de configuração..."
cp "$PROJECT_ROOT/pyproject.toml" .
cp "$PROJECT_ROOT/poetry.lock" . 2>/dev/null || echo "⚠️  poetry.lock não encontrado (será gerado)"
cp "$PROJECT_ROOT/Dockerfile.backend" ./Dockerfile 2>/dev/null || echo "⚠️  Dockerfile.backend não encontrado"

# Copiar docker-compose (apenas para desenvolvimento local)
if [ -f "$PROJECT_ROOT/docker-compose.yml" ]; then
    echo "📋 Copiando docker-compose.yml..."
    cp "$PROJECT_ROOT/docker-compose.yml" .
fi

# Copiar render.yaml se existir
if [ -f "$PROJECT_ROOT/render.yaml" ]; then
    echo "📋 Copiando render.yaml..."
    cp "$PROJECT_ROOT/render.yaml" .
fi

# Criar .gitignore se não existir
if [ ! -f ".gitignore" ]; then
    echo "📝 Criando .gitignore..."
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/
.venv

# Poetry
poetry.lock

# Environment variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml
EOF
fi

# Ajustar caminhos nos arquivos
echo "🔧 Ajustando caminhos nos arquivos..."

# Ajustar __main__.py
if [ -f "__main__.py" ]; then
    sed -i 's|backend/development.ini|development.ini|g' __main__.py
    sed -i 's|backend/production.ini|production.ini|g' __main__.py
fi

# Ajustar alembic/env.py
if [ -f "alembic/env.py" ]; then
    sed -i "s|os.path.join(os.path.dirname(__file__), '..', '..')|os.path.abspath(os.path.dirname(os.path.dirname(__file__)))|g" alembic/env.py
fi

# Ajustar scripts
for script in scripts/*.py; do
    if [ -f "$script" ]; then
        sed -i "s|os.path.join(os.path.dirname(__file__), '..', '..')|os.path.abspath(os.path.dirname(os.path.dirname(__file__)))|g" "$script"
    fi
done

# Ajustar Dockerfile
if [ -f "Dockerfile" ]; then
    sed -i 's|COPY backend ./backend|COPY . ./backend|g' Dockerfile
    sed -i 's|WORKDIR /app/backend|WORKDIR /app/backend|g' Dockerfile
fi

# Ajustar docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    sed -i 's|./backend:/app/backend|.:/app/backend|g' docker-compose.yml
    sed -i 's|context: .|context: .|g' docker-compose.yml
    sed -i 's|dockerfile: Dockerfile.backend|dockerfile: Dockerfile|g' docker-compose.yml
fi

# Ajustar render.yaml
if [ -f "render.yaml" ]; then
    sed -i 's|cd backend &&|cd . &&|g' render.yaml
    sed -i 's|poetry run alembic -c alembic.ini|poetry run alembic -c alembic.ini|g' render.yaml
fi

echo ""
echo "✅ Repositório backend criado com sucesso!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Revisar e ajustar README.md"
echo "   2. Verificar .gitignore"
echo "   3. Testar: poetry install"
echo "   4. Testar: poetry run python -m backend"
echo "   5. Fazer commit inicial"
echo ""

