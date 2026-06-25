#Requires -RunAsAdministrator
# Corrige acesso ao Postgres: nova porta 15432 + Adminer + reset senha
$ErrorActionPreference = "Continue"
$RepoRoot = Split-Path -Parent $PSScriptRoot

$ExpectedUser = "ccm_user"
$ExpectedDb = "ccm_db"
$ExpectedPassword = "ccm_password"
$HostPort = 15432

function Write-Section($t) {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host $t
    Write-Host ("=" * 60)
}

Push-Location $RepoRoot
try {
    Write-Section "1) Conflito na porta 5432 do Windows"
    Write-Host "Processos escutando 5432 e 15432:"
    netstat -ano | findstr ":5432"
    netstat -ano | findstr ":15432"

    Write-Section "2) Recriar Postgres na porta $HostPort"
    docker compose up -d db adminer

    Write-Host "Aguardando healthcheck..."
    $deadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $deadline) {
        $h = docker inspect -f "{{.State.Health.Status}}" ccm_postgres 2>$null
        if ($h -eq "healthy") { break }
        Start-Sleep -Seconds 2
    }

    Write-Section "3) Reset senha TCP"
    docker exec ccm_postgres psql -U $ExpectedUser -d $ExpectedDb -c "ALTER USER $ExpectedUser WITH PASSWORD '$ExpectedPassword';" 2>&1

    Write-Section "4) Teste TCP porta $HostPort"
    docker exec ccm_postgres sh -c "PGPASSWORD=$ExpectedPassword psql -h 127.0.0.1 -U $ExpectedUser -d $ExpectedDb -c 'SELECT 1 AS ok;'" 2>&1

    $tcpLocal = $false
    try {
        $c = New-Object System.Net.Sockets.TcpClient
        $c.Connect("127.0.0.1", $HostPort)
        $tcpLocal = $c.Connected
        $c.Close()
    } catch { }

    Write-Host "127.0.0.1:${HostPort} aberta no Windows: $tcpLocal"

    Write-Section "5) Subir backend"
    docker compose up -d backend

    Write-Section "ACESSO AO BANCO"
    Write-Host ""
    Write-Host "OPCAO A - Adminer no navegador (RECOMENDADO, sempre funciona):" -ForegroundColor Green
    Write-Host "  URL:      http://127.0.0.1:5050"
    Write-Host "  Sistema:  PostgreSQL"
    Write-Host "  Servidor: db"
    Write-Host "  Usuario:  $ExpectedUser"
    Write-Host "  Senha:    $ExpectedPassword"
    Write-Host "  Base:     $ExpectedDb"
    Write-Host ""
    Write-Host "OPCAO B - DBeaver (no servidor RDP):" -ForegroundColor Cyan
    Write-Host "  Host:     127.0.0.1"
    Write-Host "  Porta:    $HostPort    <-- NAO use 5432"
    Write-Host "  Database: $ExpectedDb"
    Write-Host "  User:     $ExpectedUser"
    Write-Host "  Password: $ExpectedPassword"
    Write-Host "  SSL:      disable"
    Write-Host ""
    Write-Host "NAO use usuario postgres. Porta 5432 pode ser outro Postgres do Windows."
    Write-Host ""
    Write-Host "Firewall local (se DBeaver ainda falhar):"
    Write-Host "  New-NetFirewallRule -DisplayName 'Postgres Docker $HostPort' -Direction Inbound -Protocol TCP -LocalPort $HostPort -Action Allow"
} finally {
    Pop-Location
}
