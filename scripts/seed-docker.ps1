#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$argsLine = $args -join " "
Write-Host "🌱 Executando seed no container ccm_backend..."
docker exec ccm_backend sh -c "cd backend && python scripts/seed_all.py $argsLine"
Write-Host "✅ Concluído"
