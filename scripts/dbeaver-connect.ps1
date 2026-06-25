#Requires -RunAsAdministrator
# Diagnostico e correcao: DBeaver -> Postgres Docker no Windows Server
$ErrorActionPreference = "Continue"

$RepoRoot = Split-Path -Parent $PSScriptRoot

function Test-TcpPort {
    param([string]$HostName, [int]$Port)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($HostName, $Port, $null, $null)
        $ok = $iar.AsyncWaitHandle.WaitOne(3000, $false)
        if ($ok -and $client.Connected) {
            $client.Close()
            return $true
        }
        $client.Close()
    } catch { }
    return $false
}

Write-Host "================================================================"
Write-Host " Postgres Docker - diagnostico DBeaver"
Write-Host "================================================================"

Write-Host ""
Write-Host "==> Container"
docker ps -a --filter name=ccm_postgres --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host ""
Write-Host "==> Porta publicada pelo Docker"
docker port ccm_postgres 5432 2>&1

Write-Host ""
Write-Host "==> IP do container na rede Docker (alternativa no DBeaver)"
$containerIp = docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" ccm_postgres 2>$null
if ($containerIp) {
    Write-Host "    Host DBeaver: $containerIp"
    Write-Host "    Port:       5432"
}

Write-Host ""
Write-Host "==> Quem escuta na porta 5432 no Windows"
netstat -ano | findstr ":5432"

Write-Host ""
Write-Host "==> Teste TCP"
foreach ($hostName in @("127.0.0.1", "localhost", $containerIp)) {
    if (-not $hostName) { continue }
    $ok = Test-TcpPort -HostName $hostName -Port 5432
    Write-Host "    $hostName`:5432 -> $(if ($ok) { 'ABERTA' } else { 'FECHADA' })"
}

Write-Host ""
Write-Host "==> Teste SQL dentro do container"
docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "SELECT inet_server_addr(), inet_server_port();" 2>&1

Write-Host ""
Write-Host "==> Teste SQL via rede Docker (simula DBeaver pelo IP do container)"
if ($containerIp) {
    docker run --rm --network coddfy_network postgres:15-alpine `
        psql "postgresql://ccm_user:ccm_password@${containerIp}:5432/ccm_db" -c "SELECT 1 AS ok;" 2>&1
}

Write-Host ""
Write-Host "==> Teste SQL via host.docker.internal (porta mapeada)"
docker run --rm postgres:15-alpine `
    psql "postgresql://ccm_user:ccm_password@host.docker.internal:5432/ccm_db" -c "SELECT 1 AS ok;" 2>&1

Write-Host ""
Write-Host "================================================================"
Write-Host " Configuracao DBeaver"
Write-Host "================================================================"
Write-Host ""
Write-Host "Tente nesta ordem:"
Write-Host ""
Write-Host "  Opcao 1 - IP do container (geralmente funciona no Windows Server):"
Write-Host "    Host:     $containerIp"
Write-Host "    Port:     5432"
Write-Host "    Database: ccm_db"
Write-Host "    User:     ccm_user"
Write-Host "    Password: ccm_password"
Write-Host "    SSL:      disable"
Write-Host ""
Write-Host "  Opcao 2 - Loopback (apos repair abaixo):"
Write-Host "    Host:     127.0.0.1"
Write-Host "    (mesmas credenciais)"
Write-Host ""
Write-Host "  Driver: PostgreSQL (nao Generic)"
Write-Host "  Aba Driver properties: ssl=false"
Write-Host ""
Write-Host "================================================================"
Write-Host " Repair (recria mapeamento 127.0.0.1:5432)"
Write-Host "================================================================"
Write-Host ""
Write-Host "Se 127.0.0.1:5432 estiver FECHADA, rode:"
Write-Host "  powershell -ExecutionPolicy Bypass -File .\scripts\repair-postgres-port.ps1"
Write-Host "================================================================"
