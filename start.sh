#!/bin/bash

# Script rápido para iniciar o projeto
# Este script inicia o backend

set -e

echo "=========================================="
echo "🚀 Iniciando Coddfy Contracts Manager CCM"
echo "=========================================="

# Verifica se está no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Verifica se o banco está rodando
if ! docker ps | grep -q ccm_postgres; then
    echo "📦 Iniciando banco de dados..."
    docker-compose up -d db
    sleep 5
fi

# Função para cleanup ao sair
cleanup() {
    echo ""
    echo "🛑 Parando servidor..."
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Inicia o backend em background
echo "🐍 Iniciando backend..."
cd /home/w3x7/Desktop/lab/portal-coddfy
poetry run python -m backend > backend/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Aguarda o backend iniciar
echo "   Aguardando backend iniciar..."
sleep 5

echo ""
echo "=========================================="
echo "✅ Servidor iniciado com sucesso!"
echo "=========================================="
echo "🔌 Backend:  http://localhost:6543"
echo "📚 API Docs: http://localhost:6543/api/docs/swagger"
echo ""
echo "👤 Credenciais padrão:"
echo "   Usuário: admin"
echo "   Senha:   admin123"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend/backend.log"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "=========================================="

# Mantém o script rodando
wait

