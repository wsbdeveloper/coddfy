# Coddfy Contracts Manager CCM

Sistema de gestão de contratos de consultoria com Python (Pyramid).

## Início Rápido

```bash
# 1. Iniciar PostgreSQL
docker-compose up -d db

# 2. Configurar banco
poetry install --no-root
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..
poetry run python backend/scripts/create_admin.py

# 3. Iniciar backend
poetry run python -m backend
```

**Acessar:**
- Swagger UI: http://localhost:6543/api/docs/swagger
- Login: `admin` / `admin123`

## Documentação

- **[DOCUMENTACAO.md](DOCUMENTACAO.md)** - Documentação completa do projeto
- **[DEPLOY.md](DEPLOY.md)** - Guia de deploy (Vercel + Render)
- **[ENV_VARIABLES.md](ENV_VARIABLES.md)** - Variáveis de ambiente

## Deploy

O projeto está configurado para deploy:
- **Backend**: [Render](https://render.com) - Veja [DEPLOY.md](DEPLOY.md)

## 🛠️ Stack

**Backend:** Python/Pyramid, PostgreSQL, JWT, Swagger  
**DevOps:** Docker, Poetry

## 📦 Estrutura

```
portal-coddfy/
├── backend/           # API Python/Pyramid
│   ├── alembic/      # Migrações BD
│   ├── scripts/      # Scripts auxiliares
│   └── ...
└── ...
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
