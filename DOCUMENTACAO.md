# 📘 Coddfy Contracts Manager CCM - Documentação Completa

> Sistema de gestão de contratos de consultoria com Python (Pyramid) e React (TypeScript)

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Início Rápido](#início-rápido)
3. [Arquitetura](#arquitetura)
4. [API Endpoints](#api-endpoints)
5. [Banco de Dados](#banco-de-dados)
6. [Configuração](#configuração)
7. [Comandos Úteis](#comandos-úteis)
8. [Desenvolvimento](#desenvolvimento)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

### O que é o CCM?
Sistema web para gestão de contratos de consultoria com:
- ✅ Controle financeiro (valor total, faturado, saldo)
- ✅ Acompanhamento de vigência
- ✅ Avaliação de performance de consultores
- ✅ Dashboard com indicadores
- ✅ Autenticação JWT com níveis de acesso

### Stack Tecnológico

**Backend:**
- Python 3.11+ / Pyramid Framework
- PostgreSQL + SQLAlchemy + Alembic
- JWT para autenticação
- Swagger/OpenAPI para documentação

**Frontend:**
- React 18 + TypeScript + Vite
- Tailwind CSS + ShadCN UI
- Axios para requisições HTTP
- React Router para navegação

**DevOps:**
- Docker + Docker Compose
- Poetry (gerenciamento Python)
- npm (gerenciamento Node.js)

---

## 🚀 Início Rápido

### Pré-requisitos
```bash
# Verificar instalações
python --version  # 3.11+
poetry --version  # 1.7+
node --version    # 18+
docker --version  # 20+
```

### Setup em 5 Passos

```bash
# 1. Clonar/Navegar para o projeto
cd /path/to/portal-coddfy

# 2. Iniciar PostgreSQL
docker-compose up -d db

# 3. Instalar dependências Python
poetry install --no-root

# 4. Configurar banco de dados
cd backend && poetry run alembic -c alembic.ini revision --autogenerate -m "Initial migration" && cd ..
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..
poetry run python backend/scripts/create_admin.py
poetry run python backend/scripts/seed_data.py  # Opcional: dados de exemplo

# 5. Iniciar backend
poetry run python -m backend
```

### Acessar

- 🌐 **Swagger UI:** http://localhost:6543/api/docs/swagger
- 🔌 **API:** http://localhost:6543/api
- 👤 **Login padrão:** `admin` / `admin123`

---

## 🏗️ Arquitetura

### Estrutura de Diretórios

```
portal-coddfy/
├── backend/                    # Backend Python/Pyramid
│   ├── views/                  # Endpoints da API
│   │   ├── auth.py            # Autenticação
│   │   ├── dashboard.py       # Dashboard
│   │   ├── contracts.py       # Contratos CRUD
│   │   ├── consultants.py     # Consultores CRUD
│   │   ├── clients.py         # Clientes CRUD
│   │   └── swagger.py         # Swagger UI
│   ├── models.py              # Models SQLAlchemy
│   ├── schemas.py             # Validação (Marshmallow)
│   ├── auth.py                # JWT service
│   ├── database.py            # Config SQLAlchemy
│   ├── routes.py              # Rotas
│   ├── app.py                 # App Pyramid
│   └── openapi.yaml           # Spec OpenAPI 3.0
├── frontend/                   # Frontend React
│   ├── src/
│   │   ├── components/        # Componentes UI
│   │   ├── pages/            # Dashboard, Contratos, etc
│   │   ├── lib/              # Utilitários
│   │   └── types/            # Tipos TypeScript
│   └── package.json
├── backend/
│   ├── alembic/              # Migrações BD
│   ├── scripts/              # Scripts auxiliares
│   │   ├── create_admin.py  # Criar admin
│   │   └── seed_data.py     # Popular dados
│   └── ...
├── docker-compose.yml        # Docker setup
└── pyproject.toml           # Dependências Python
```

### Fluxo de Autenticação

```
1. POST /api/auth/login → Retorna JWT token
2. Cliente armazena token
3. Requests seguintes: Header "Authorization: Bearer {token}"
4. Backend valida token e permissões
```

---

## 📡 API Endpoints

### Autenticação

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/api/auth/login` | Login (retorna JWT) | ❌ |
| POST | `/api/auth/register` | Criar usuário | ❌ |

### Dashboard

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/dashboard` | Estatísticas consolidadas | ✅ |

### Clientes

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/clients` | Listar clientes | ✅ |
| POST | `/api/clients` | Criar cliente | ✅ |
| GET | `/api/clients/{id}` | Obter cliente | ✅ |
| PUT | `/api/clients/{id}` | Atualizar cliente | ✅ |
| DELETE | `/api/clients/{id}` | Deletar cliente | ✅ |

### Contratos

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/contracts` | Listar (com filtros) | ✅ |
| POST | `/api/contracts` | Criar contrato | ✅ |
| GET | `/api/contracts/{id}` | Obter contrato | ✅ |
| PUT | `/api/contracts/{id}` | Atualizar contrato | ✅ |
| DELETE | `/api/contracts/{id}` | Deletar contrato | ✅ |

**Filtros disponíveis:**
- `client_id` - UUID do cliente
- `status` - ativo, inativo, a_vencer
- `start_date` / `end_date` - Período

### Consultores

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| GET | `/api/consultants` | Listar agrupados | ✅ |
| POST | `/api/consultants` | Criar consultor | ✅ |
| GET | `/api/consultants/{id}` | Obter consultor | ✅ |
| PUT | `/api/consultants/{id}` | Atualizar consultor | ✅ |
| DELETE | `/api/consultants/{id}` | Deletar consultor | ✅ |

### Documentação

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api` | Documentação JSON |
| GET | `/api/docs/swagger` | Swagger UI (Interativo) |
| GET | `/api/openapi.yaml` | Spec OpenAPI 3.0 |

---

## 🗄️ Banco de Dados

### Models

#### 1. **users** - Usuários do sistema
```python
- id: UUID (PK)
- username: String (unique)
- email: String (unique)
- password_hash: String
- role: Enum (admin, gestor, leitura)
- is_active: Boolean
- created_at, updated_at: DateTime
```

#### 2. **clients** - Clientes
```python
- id: UUID (PK)
- name: String
- created_at, updated_at: DateTime
```

#### 3. **contracts** - Contratos
```python
- id: UUID (PK)
- name: String
- client_id: UUID (FK → clients)
- total_value: Decimal
- billed_value: Decimal
- balance: Decimal
- status: Enum (ativo, inativo, a_vencer)
- end_date: DateTime
- created_at, updated_at: DateTime
```

#### 4. **installments** - Parcelas
```python
- id: UUID (PK)
- contract_id: UUID (FK → contracts)
- month: String (ex: "Jan/25")
- value: Decimal
- billed: Boolean
- created_at, updated_at: DateTime
```

#### 5. **consultants** - Consultores
```python
- id: UUID (PK)
- name: String
- role: String (cargo)
- contract_id: UUID (FK → contracts)
- feedback: Integer (0-100)
- created_at, updated_at: DateTime
```

### Migrações

```bash
# Criar nova migração
cd backend && poetry run alembic -c alembic.ini revision --autogenerate -m "Descrição" && cd ..

# Aplicar migrações
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..

# Reverter última migração
cd backend && poetry run alembic -c alembic.ini downgrade -1 && cd ..

# Ver histórico
cd backend && poetry run alembic -c alembic.ini history && cd ..

# Ver status atual
cd backend && poetry run alembic -c alembic.ini current && cd ..
```

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# Database
DATABASE_URL=postgresql://ccm_user:ccm_password@localhost:5432/ccm_db

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=6543

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Configuração do Frontend (.env)

```bash
VITE_API_URL=http://localhost:6543/api
```

---

## 🛠️ Comandos Úteis

### Backend

```bash
# Iniciar servidor
poetry run python -m backend

# Shell interativo
poetry run pshell backend/development.ini

# Criar usuário admin
poetry run python backend/scripts/create_admin.py

# Popular dados de exemplo
poetry run python backend/scripts/seed_data.py

# Testes (quando implementados)
poetry run pytest
poetry run pytest --cov
```

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Dev server
npm run dev

# Build produção
npm run build

# Preview build
npm run preview

# Lint
npm run lint
```

### Docker

```bash
# Iniciar tudo
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Parar tudo
docker-compose down

# Rebuild
docker-compose up -d --build

# Shell no container
docker-compose exec backend bash

# Conectar ao PostgreSQL
docker-compose exec db psql -U ccm_user -d ccm_db
```

### Banco de Dados

```bash
# Conectar ao PostgreSQL
psql -U ccm_user -d ccm_db

# Comandos SQL úteis
\dt                    # Listar tabelas
\d table_name         # Descrever tabela
\l                    # Listar databases
\q                    # Sair

# Backup
pg_dump -U ccm_user ccm_db > backup.sql

# Restore
psql -U ccm_user ccm_db < backup.sql
```

---

## 💻 Desenvolvimento

### Testando a API com curl

```bash
# 1. Login
curl -X POST http://localhost:6543/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Resposta:
# {"token": "eyJ0eXAi...", "user": {...}}

# 2. Usar token
TOKEN="seu-token-aqui"

# Dashboard
curl http://localhost:6543/api/dashboard \
  -H "Authorization: Bearer $TOKEN"

# Listar contratos
curl http://localhost:6543/api/contracts \
  -H "Authorization: Bearer $TOKEN"

# Criar cliente
curl -X POST http://localhost:6543/api/clients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Novo Cliente Ltda"}'
```

### Usando Swagger UI (Recomendado)

1. Acesse: http://localhost:6543/api/docs/swagger
2. Expanda `POST /api/auth/login`
3. Clique "Try it out"
4. Use: `{"username": "admin", "password": "admin123"}`
5. Execute e copie o token
6. Clique em "Authorize" (🔒) no topo
7. Cole: `Bearer seu-token-aqui`
8. Agora pode testar todos os endpoints!

### Estrutura de uma Request/Response

**Request:**
```json
POST /api/contracts
Authorization: Bearer eyJ0eXAi...
Content-Type: application/json

{
  "name": "Projeto XYZ",
  "client_id": "uuid-do-cliente",
  "total_value": 100000.00,
  "status": "ativo",
  "end_date": "2025-12-31T23:59:59"
}
```

**Response:**
```json
{
  "id": "uuid-gerado",
  "name": "Projeto XYZ",
  "client_id": "uuid-do-cliente",
  "total_value": "100000.00",
  "billed_value": "0.00",
  "balance": "100000.00",
  "status": "ativo",
  "end_date": "2025-12-31T23:59:59",
  "billed_percentage": 0.0,
  "created_at": "2025-11-11T...",
  "client": {
    "id": "uuid",
    "name": "Nome do Cliente"
  }
}
```

---

## 🐛 Troubleshooting

### Backend não inicia

```bash
# Ver logs
cat backend.log

# Verificar se porta está em uso
lsof -i :6543

# Matar processo
pkill -f "python -m backend"

# Reinstalar dependências
poetry install --no-root
```

### Erro de conexão com banco

```bash
# Verificar se PostgreSQL está rodando
docker ps | grep postgres

# Iniciar PostgreSQL
docker-compose up -d db

# Verificar conexão
psql postgresql://ccm_user:ccm_password@localhost:5432/ccm_db -c "SELECT 1"
```

### Erro "No module named 'pyramid'"

```bash
# Ativar virtualenv do Poetry
poetry shell

# Ou rodar com poetry run
poetry run python -m backend
```

### Frontend não carrega

```bash
# Limpar cache e reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install

# Verificar se backend está rodando
curl http://localhost:6543/api

# Ver logs do Vite
npm run dev
```

### Erro CORS

```bash
# Verificar CORS_ORIGINS no .env
cat .env | grep CORS

# Deve incluir a URL do frontend
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 📊 Dados de Exemplo

Após rodar `poetry run python backend/scripts/seed_data.py`:

### Clientes criados:
- Tech Solutions Ltda
- Inovação Digital S.A.
- Consultoria Estratégica

### Contratos criados:
1. **Desenvolvimento Sistema ERP** (Tech Solutions)
   - Valor: R$ 500.000,00
   - Faturado: R$ 350.000,00 (70%)
   - Status: Ativo

2. **Modernização Infraestrutura** (Inovação Digital)
   - Valor: R$ 300.000,00
   - Faturado: R$ 100.000,00 (33%)
   - Status: Ativo

3. **Consultoria DevOps** (Consultoria Estratégica)
   - Valor: R$ 150.000,00
   - Faturado: R$ 150.000,00 (100%)
   - Status: Inativo

### Consultores criados:
- João Silva (Tech Lead) - Feedback: 95%
- Maria Santos (Dev Senior) - Feedback: 92%
- Pedro Oliveira (Dev Pleno) - Feedback: 88%
- Ana Costa (Arquiteta) - Feedback: 96%
- Carlos Mendes (DevOps) - Feedback: 90%
- Beatriz Lima (Consultora) - Feedback: 85%

---

## 🔐 Segurança

### Boas Práticas Implementadas

✅ Senhas com hash bcrypt  
✅ JWT para autenticação stateless  
✅ Validação de dados com Marshmallow  
✅ CORS configurado  
✅ Níveis de acesso (Admin/Gestor/Leitura)  
✅ Conexões HTTPS recomendadas em produção  

### Para Produção

1. **Alterar JWT_SECRET** para valor aleatório forte
2. **Desabilitar dados de exemplo** (seed_data.py)
3. **Alterar senha do admin** após primeiro login
4. **Configurar HTTPS** no servidor
5. **Usar banco gerenciado** (AWS RDS, Railway, etc)
6. **Configurar backups** automáticos
7. **Adicionar rate limiting** na API
8. **Habilitar logs** de auditoria

---

## 🚀 Deploy

### Usando Docker

```bash
# Build
docker-compose build

# Deploy
docker-compose up -d

# Monitorar
docker-compose logs -f
```

### Variáveis de Produção

```bash
APP_ENV=production
DATABASE_URL=postgresql://user:pass@host:5432/db
JWT_SECRET=use-forte-senha-aleatoria-aqui
CORS_ORIGINS=https://seu-dominio.com
```

---

## 📚 Recursos Adicionais

- **Swagger UI:** http://localhost:6543/api/docs/swagger
- **PRD Original:** `PRD.md`
- **Repository:** Git repository URL
- **Suporte:** admin@coddfy.com

---

## 🎯 Checklist de Onboarding

Para novos desenvolvedores:

- [ ] Instalar pré-requisitos (Python, Node, Docker, Poetry)
- [ ] Clonar repositório
- [ ] Copiar `.env.example` para `.env`
- [ ] Rodar `docker-compose up -d db`
- [ ] Rodar `poetry install --no-root`
- [ ] Aplicar migrações: `cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..`
- [ ] Criar admin: `poetry run python backend/scripts/create_admin.py`
- [ ] Popular dados: `poetry run python backend/scripts/seed_data.py`
- [ ] Iniciar backend: `poetry run python -m backend`
- [ ] Testar Swagger UI: http://localhost:6543/api/docs/swagger
- [ ] Fazer login e explorar endpoints
- [ ] (Opcional) Instalar deps frontend: `cd frontend && npm install`
- [ ] (Opcional) Iniciar frontend: `npm run dev`

---

**📝 Última atualização:** Novembro 2025  
**👨‍💻 Desenvolvido por:** Portal Coddfy Team  
**📦 Versão:** 1.0.0

---

## 💡 Dicas Importantes

1. **Sempre use Poetry para rodar comandos Python:**
   ```bash
   poetry run python script.py
   ```

2. **Swagger UI é seu melhor amigo** para testar a API

3. **Consulte os logs** quando algo der errado:
   ```bash
   tail -f backend.log
   ```

4. **Documentação do Pyramid:** https://docs.pylonsproject.org/

5. **Para dúvidas sobre React:** Consulte a estrutura em `frontend/src/`

---

🎉 **Projeto pronto para desenvolvimento e produção!**

