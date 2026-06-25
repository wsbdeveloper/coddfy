#Requires -RunAsAdministrator
# Recria Postgres com porta fixada em 127.0.0.1:5432 para DBeaver
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {
  Write-Host "==> Parando stack"
  docker compose stop db backend

  Write-Host "==> Recriando Postgres com bind 127.0.0.1:5432"
  docker compose up -d db

  Write-Host "==> Aguardando healthcheck"
  $deadline = (Get-Date).AddSeconds(60)
  while ((Get-Date) -lt $deadline) {
    $health = docker inspect -f "{{.State.Health.Status}}" ccm_postgres 2>$null
    if ($health -eq "healthy") { break }
    Start-Sleep -Seconds 2
  }

  Write-Host "==> Subindo backend"
  docker compose up -d backend

  Write-Host ""
  docker port ccm_postgres 5432
  Write-Host ""
  Write-Host "DBeaver:"
  Write-Host "  Host: 127.0.0.1 | Port: 5432 | DB: ccm_db | User: ccm_user | Password: ccm_password"
  Write-Host ""
  Write-Host "Se ainda falhar, use o IP do container:"
  $ip = docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" ccm_postgres
  Write-Host "  Host: $ip"
} finally {
  Pop-Location
}
