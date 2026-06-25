#Requires -Version 5.1
# Recria volume Postgres + migra + admin (APAGA DADOS)
param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

if (-not $Force) {
    Write-Host "Isso vai APAGAR o banco PostgreSQL (volume postgres_data)." -ForegroundColor Yellow
    Write-Host "Use: powershell -File .\scripts\repair-db.ps1 -Force" -ForegroundColor Yellow
    exit 1
}

Push-Location $RepoRoot
try {
    Write-Host "==> Parando containers e removendo volume"
    docker compose down -v

    Write-Host "==> Subindo banco + backend"
    docker compose up -d

    Write-Host "==> Aguardando backend (ate 120s)"
    $deadline = (Get-Date).AddSeconds(120)
    while ((Get-Date) -lt $deadline) {
        try {
            $r = Invoke-RestMethod -Uri "http://127.0.0.1:6543/api/health" -TimeoutSec 5
            Write-Host "Backend OK"
            break
        } catch {
            Start-Sleep -Seconds 3
        }
    }

    Write-Host "==> Garantindo usuario admin"
    docker exec ccm_backend sh -c "cd backend && python scripts/create_admin.py"

    Write-Host ""
    Write-Host "Credenciais: admin / admin123"
    Write-Host "Teste: Invoke-RestMethod -Uri http://127.0.0.1:6543/api/health"
} finally {
    Pop-Location
}
