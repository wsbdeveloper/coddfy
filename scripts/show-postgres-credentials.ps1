#Requires -Version 5.1
# Mostra credenciais configuradas no Postgres Docker e testa autenticacao TCP
$ErrorActionPreference = "Continue"

$ExpectedUser = "ccm_user"
$ExpectedDb = "ccm_db"
$ExpectedPassword = "ccm_password"

function Write-Section($title) {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host $title
    Write-Host ("=" * 60)
}

Write-Section "Postgres Docker - credenciais e autenticacao"

if (-not (docker ps -q -f "name=ccm_postgres")) {
    Write-Host "ERRO: container ccm_postgres nao esta rodando" -ForegroundColor Red
    Write-Host "Rode: docker compose up -d"
    exit 1
}

Write-Section "1) Variaveis de ambiente no container"
$envLines = docker inspect ccm_postgres --format "{{range .Config.Env}}{{println .}}{{end}}" 2>&1
foreach ($line in $envLines) {
    if ($line -match "^POSTGRES_PASSWORD=(.+)$") {
        $len = $Matches[1].Length
        Write-Host "POSTGRES_PASSWORD=*** ($len caracteres; valor no container)"
    } elseif ($line -match "^POSTGRES_") {
        Write-Host $line
    }
}
Write-Host ""
Write-Host "Para ver a senha no servidor (nao compartilhe):"
Write-Host '  docker exec ccm_postgres printenv POSTGRES_PASSWORD'

Write-Section "2) docker inspect (demais env POSTGRES)"
docker inspect ccm_postgres --format "{{range .Config.Env}}{{println .}}{{end}}" 2>&1 |
    Select-String "^POSTGRES_(USER|DB)="

Write-Section "3) Usuarios no banco (senha NAO fica em texto - so hash)"
docker exec ccm_postgres psql -U $ExpectedUser -d $ExpectedDb -c "
SELECT rolname AS usuario, rolcanlogin AS pode_logar, rolsuper AS superuser
FROM pg_roles
WHERE rolcanlogin
ORDER BY rolname;
" 2>&1

Write-Host ""
Write-Host "Hash da senha (criptografado - nao da para ler a senha original):" -ForegroundColor Yellow
docker exec ccm_postgres psql -U $ExpectedUser -d $ExpectedDb -c "
SELECT rolname, CASE WHEN rolpassword IS NULL THEN '(sem senha)' ELSE left(rolpassword, 20) || '...' END AS hash_inicio
FROM pg_authid
WHERE rolname IN ('ccm_user', 'postgres');
" 2>&1

Write-Section "4) pg_hba.conf (regras de autenticacao TCP)"
docker exec ccm_postgres sh -c "grep -v '^#' /var/lib/postgresql/data/pg_hba.conf | grep -v '^$'" 2>&1

Write-Section "5) Teste TCP com senha esperada (como DBeaver)"
docker exec ccm_postgres sh -c "PGPASSWORD=$ExpectedPassword psql -h 127.0.0.1 -U $ExpectedUser -d $ExpectedDb -c 'SELECT current_user, current_database(), ''senha_tcp_ok'' AS status;'" 2>&1
$tcpOk = $LASTEXITCODE -eq 0

Write-Section "6) IP do container (use no DBeaver se 127.0.0.1 falhar)"
$containerIp = docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}" ccm_postgres 2>$null
Write-Host "Container IP: $containerIp"
docker port ccm_postgres 5432 2>&1

Write-Section "Resumo"
Write-Host @"
IMPORTANTE: PostgreSQL NUNCA guarda senha legivel.
So da para ver:
  - POSTGRES_PASSWORD nas variaveis do container (secao 1)
  - Se a senha FUNCIONA no teste TCP (secao 5)

Credenciais esperadas (docker-compose.yml):
  User:     $ExpectedUser
  Password: $ExpectedPassword
  Database: $ExpectedDb
  Port:     5432

DBeaver:
  Host: $containerIp (ou 127.0.0.1)
  SSL:  disable
  User: $ExpectedUser (nao use postgres)
"@

if ($tcpOk) {
    Write-Host "Teste TCP: OK - senha $ExpectedPassword funciona" -ForegroundColor Green
} else {
    Write-Host "Teste TCP: FALHOU - rode reset-postgres-password.ps1" -ForegroundColor Red
}
