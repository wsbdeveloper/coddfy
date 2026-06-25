#Requires -Version 5.1
# Diagnostico: backend Docker + Postgres + login
$ErrorActionPreference = "Continue"

$BackendUrl = "http://127.0.0.1:6543"
$PortalUrl = "http://127.0.0.1"

function Write-Section($title) {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host $title
    Write-Host ("=" * 60)
}

function Test-ContainerRunning($name) {
    $id = docker ps -q -f "name=$name" 2>$null
    return [bool]$id
}

Write-Section "1. Containers Docker"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | Select-String "ccm_"

$dbUp = Test-ContainerRunning "ccm_postgres"
$beUp = Test-ContainerRunning "ccm_backend"
Write-Host "ccm_postgres: $(if ($dbUp) { 'rodando' } else { 'PARADO' })"
Write-Host "ccm_backend:  $(if ($beUp) { 'rodando' } else { 'PARADO' })"

Write-Section "2. Postgres (credenciais do docker-compose.yml)"
Write-Host "Esperado: user=ccm_user | db=ccm_db | password=ccm_password"
if ($dbUp) {
    docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "SELECT 1 AS ok;" 2>&1
    docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "SELECT username, role, is_active FROM users WHERE username='admin';" 2>&1
} else {
    Write-Host "Container ccm_postgres nao esta rodando." -ForegroundColor Yellow
}

Write-Section "3. Backend API"
try {
    $health = Invoke-RestMethod -Uri "$BackendUrl/api/health" -TimeoutSec 10
    Write-Host "GET $BackendUrl/api/health -> OK"
    $health | ConvertTo-Json -Compress
} catch {
    Write-Host "Falha: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Logs recentes do backend:"
    docker logs ccm_backend --tail 30 2>&1
}

Write-Section "4. Login admin (admin / admin123)"
try {
    $body = @{ username = "admin"; password = "admin123" } | ConvertTo-Json
    $login = Invoke-RestMethod -Uri "$BackendUrl/api/auth/login" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 10
    Write-Host "POST $BackendUrl/api/auth/login -> OK (token recebido)" -ForegroundColor Green
} catch {
    Write-Host "Falha no login: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) { Write-Host $_.ErrorDetails.Message }
}

Write-Section "5. Portal IIS (proxy /api)"
try {
    $healthPortal = Invoke-WebRequest -Uri "$PortalUrl/api/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "GET $PortalUrl/api/health -> $($healthPortal.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "Falha no proxy IIS /api: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Rode no frontend: powershell -File .\iis\go-live.ps1 -PublicHost portal.coddfy.com.br"
}

Write-Section "6. Se Postgres falhar com credenciais"
Write-Host @"
Volume antigo do Postgres costuma causar 'password authentication failed'.
Isso acontece quando o volume foi criado com outra senha.

ATENCAO: apaga todos os dados do banco!

  cd C:\Users\codd_adm\coddfy
  docker compose down -v
  docker compose up -d
  docker logs -f ccm_backend

Depois confirme admin:
  docker exec ccm_backend sh -c "cd backend && python scripts/create_admin.py"

Seed opcional:
  powershell -File .\scripts\seed-docker.ps1
"@
