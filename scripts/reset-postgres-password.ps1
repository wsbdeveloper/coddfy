#Requires -Version 5.1
# Testa senha TCP e reseta ccm_user se necessario
$ErrorActionPreference = "Continue"

Write-Host "================================================================"
Write-Host " Postgres - teste e reset de senha"
Write-Host "================================================================"

if (-not (docker ps -q -f "name=ccm_postgres")) {
    Write-Host "ERRO: container ccm_postgres nao esta rodando" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "==> 1) Conexao interna (socket - sem TCP)"
docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "SELECT current_user, current_database();" 2>&1

Write-Host ""
Write-Host "==> 2) Conexao TCP dentro do container (como DBeaver)"
docker exec ccm_postgres sh -c "PGPASSWORD=ccm_password psql -h 127.0.0.1 -U ccm_user -d ccm_db -c 'SELECT 1 AS tcp_ok;'" 2>&1
$tcpOk = $LASTEXITCODE -eq 0

if (-not $tcpOk) {
    Write-Host ""
    Write-Host "    Senha TCP falhou - resetando ccm_user para ccm_password..." -ForegroundColor Yellow
    docker exec ccm_postgres psql -U ccm_user -d ccm_db -c "ALTER USER ccm_user WITH PASSWORD 'ccm_password';" 2>&1

    Write-Host ""
    Write-Host "==> 3) Reteste TCP apos reset"
    docker exec ccm_postgres sh -c "PGPASSWORD=ccm_password psql -h 127.0.0.1 -U ccm_user -d ccm_db -c 'SELECT 1 AS tcp_ok;'" 2>&1
    $tcpOk = $LASTEXITCODE -eq 0
}

Write-Host ""
Write-Host "==> 4) Porta 5432 no Windows (pode ser OUTRO Postgres)"
docker port ccm_postgres 5432 2>&1
Write-Host ""
netstat -ano | findstr ":5432"

$containerIp = docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" ccm_postgres 2>$null
Write-Host ""
Write-Host "==> 5) Teste via IP do container"
if ($containerIp) {
    docker run --rm postgres:15-alpine sh -c "PGPASSWORD=ccm_password psql -h $containerIp -U ccm_user -d ccm_db -c 'SELECT 1 AS via_ip;'" 2>&1
}

Write-Host ""
Write-Host "================================================================"
if ($tcpOk) {
    Write-Host " Senha OK via TCP" -ForegroundColor Green
    Write-Host ""
    Write-Host " DBeaver - use SOMENTE o usuario ccm_user (nao postgres):"
    Write-Host "   Host:     $containerIp  (ou 127.0.0.1 apos repair-postgres-port.ps1)"
    Write-Host "   Port:     5432"
    Write-Host "   Database: ccm_db"
    Write-Host "   User:     ccm_user"
    Write-Host "   Password: ccm_password"
    Write-Host "   SSL:      disable"
} else {
    Write-Host " Senha ainda incorreta no volume." -ForegroundColor Red
    Write-Host ""
    Write-Host " Opcao A - reset sem apagar dados (tente acima de novo)"
    Write-Host " Opcao B - recriar banco do zero (APAGA DADOS):"
    Write-Host "   powershell -File .\scripts\repair-db.ps1 -Force"
}
Write-Host "================================================================"
