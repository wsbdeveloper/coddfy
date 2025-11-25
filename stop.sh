#!/bin/bash

# Script para parar todos os serviços

echo "🛑 Parando Cursor Contracts Manager..."

# Para processos Python (backend)
pkill -f "python -m backend" && echo "✅ Backend parado"

# Para processos Node (frontend)
pkill -f "vite" && echo "✅ Frontend parado"

# Para containers Docker
docker-compose down && echo "✅ Containers Docker parados"

echo ""
echo "✅ Todos os serviços foram parados"

















