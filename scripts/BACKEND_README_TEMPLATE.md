# Coddfy Contracts Manager CCM - Backend

Backend da aplicação de gestão de contratos de consultoria, desenvolvido com Python/Pyramid.

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Poetry 1.7+
- PostgreSQL 15+ (ou Docker)

### Instalação

```bash
# 1. Instalar dependências
poetry install

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# 3. Iniciar banco de dados (se usar Docker)
docker-compose up -d db

# 4. Executar migrações
poetry run alembic -c alembic.ini upgrade head

# 5. Criar usuário admin
poetry run python scripts/create_admin.py

# 6. Iniciar servidor
poetry run python -m backend
```

A API estará disponível em: `http://localhost:6543/api`

## 📚 Documentação

- **Swagger UI**: http://localhost:6543/api/docs/swagger
- **API Docs**: http://localhost:6543/api/docs

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
.
├── alembic/          # Migrações do banco de dados
├── scripts/          # Scripts auxiliares
├── views/            # Views da API (endpoints)
├── models.py         # Modelos SQLAlchemy
├── schemas.py        # Schemas Marshmallow
├── routes.py         # Configuração de rotas
├── app.py            # Aplicação Pyramid
└── config.py         # Configurações
```

### Comandos Úteis

```bash
# Criar nova migração
poetry run alembic -c alembic.ini revision --autogenerate -m "Descrição"

# Aplicar migrações
poetry run alembic -c alembic.ini upgrade head

# Reverter migração
poetry run alembic -c alembic.ini downgrade -1

# Shell interativo
poetry run pshell development.ini

# Rodar testes (quando implementados)
poetry run pytest
```

## 🐳 Docker

```bash
# Iniciar banco de dados
docker-compose up -d db

# Build e rodar backend
docker-compose up --build backend
```

## 🚀 Deploy

### Render

O projeto está configurado para deploy no Render. Veja `render.yaml` para detalhes.

**Variáveis de ambiente necessárias:**
- `DATABASE_URL` - URL do banco PostgreSQL
- `JWT_SECRET` - Secret para JWT (gere com: `openssl rand -hex 32`)
- `CORS_ORIGINS` - URLs permitidas (ex: `https://seu-frontend.vercel.app`)

## 🔗 Integração com Frontend

O backend precisa estar configurado para aceitar requisições do frontend:

1. Configure `CORS_ORIGINS` com a URL do frontend
2. O frontend deve configurar `VITE_API_URL` apontando para este backend

## 📝 Variáveis de Ambiente

Veja `ENV_VARIABLES.md` para lista completa de variáveis.

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

[Adicione sua licença aqui]

---

**Desenvolvido por Portal Coddfy Team**

