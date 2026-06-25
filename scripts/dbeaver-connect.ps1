#Requires -Version 5.1
# Diagnostico conexao DBeaver -> Postgres Docker no Windows
$ErrorActionPreference = "Continue"

Write-Host "================================================================"
Write-Host " DBeaver -> Postgres Docker"
Write-Host "================================================================"
Write-Host ""
Write-Host "Credenciais (docker-compose.yml):"
Write-Host "  Host:     127.0.0.1   <-- use isto, NAO 'localhost'"
Write-Host "  Port:     5432"
Write-Host "  Database: ccm_db"
Write-Host "  User:     ccm_user"
Write-Host "  Password: ccm_password"
Write-Host "  SSL:      desabilitado"
Write-Host ""
Write-Host "Motivo: no Windows, 'localhost' pode usar IPv6 (::1) e o Docker"
Write-Host "        publica a porta 5432 so em IPv4."
Write-Host ""

docker ps --filter name=ccm_postgres --format "Container: {{.Names}} | {{.Status}} | {{.Ports}}"

Write-Host ""
Write-Host "Teste container:"
docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "SELECT current_database(), current_user;" 2>&1

Write-Host ""
Write-Host "Teste porta IPv4:"
$tcp = Test-NetConnection -ComputerName 127.0.0.1 -Port 5432 -WarningAction SilentlyContinue
Write-Host "  127.0.0.1:5432 TcpTestSucceeded = $($tcp.TcpTestSucceeded)"

Write-Host ""
Write-Host "Teste porta localhost (pode falhar):"
$tcp6 = Test-NetConnection -ComputerName localhost -Port 5432 -WarningAction SilentlyContinue
Write-Host "  localhost:5432 TcpTestSucceeded = $($tcp6.TcpTestSucceeded)"

Write-Host ""
Write-Host "No DBeaver:"
Write-Host "  1. Nova conexao PostgreSQL"
Write-Host "  2. Host: 127.0.0.1"
Write-Host "  3. Aba SSL -> Use SSL: Nao / disable"
Write-Host "  4. Test Connection"
Write-Host ""
Write-Host "Se conectar do seu Mac (nao do servidor):"
Write-Host "  localhost NAO funciona - use tunel SSH ou RDP no servidor."
Write-Host "================================================================"
