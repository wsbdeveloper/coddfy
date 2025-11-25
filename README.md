# Cursor Contracts Manager

Sistema de gestão de contratos de consultoria com Python (Pyramid) e React (TypeScript).

## 🚀 Início Rápido

```bash
# 1. Iniciar PostgreSQL
docker-compose up -d db

# 2. Configurar banco
poetry install --no-root
poetry run alembic upgrade head
poetry run python scripts/create_admin.py

# 3. Iniciar backend
poetry run python run_backend.py
```

**Acessar:**
- 🌐 Swagger UI: http://localhost:6543/api/docs/swagger
- 👤 Login: `admin` / `admin123`

## 📚 Documentação

Ver **[DOCUMENTACAO.md](DOCUMENTACAO.md)** para:
- Arquitetura completa
- API Endpoints
- Configuração
- Comandos úteis
- Troubleshooting
- Deploy

## 🛠️ Stack

**Backend:** Python/Pyramid, PostgreSQL, JWT, Swagger  
**Frontend:** React/TypeScript, Tailwind CSS, Vite  
**DevOps:** Docker, Poetry, npm

## 📦 Estrutura

```
portal-coddfy/
├── backend/           # API Python/Pyramid
├── frontend/          # Interface React
├── alembic/          # Migrações BD
├── scripts/          # Scripts auxiliares
└── run_backend.py    # Iniciar servidor
```

## 🎯 Features

✅ Dashboard com indicadores  
✅ Gestão de contratos (CRUD)  
✅ Gestão de consultores com feedback  
✅ Autenticação JWT  
✅ Documentação interativa (Swagger)  
✅ Controle financeiro  

---

**Desenvolvido por Portal Coddfy Team** | [Documentação Completa](DOCUMENTACAO.md)
