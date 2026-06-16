#!/usr/bin/env sh
set -e

echo "🌱 Executando seed no container ccm_backend..."
docker exec ccm_backend sh -c "cd backend && python scripts/seed_all.py $*"
echo "✅ Concluído"
