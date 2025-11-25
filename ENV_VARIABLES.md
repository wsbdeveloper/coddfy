# Variáveis de Ambiente

Este documento lista todas as variáveis de ambiente necessárias para o projeto.

## Backend

### Desenvolvimento

Crie um arquivo `.env` na raiz do projeto com:

```bash
# Configurações do Backend
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=6543

# Database
DATABASE_URL=postgresql://ccm_user:ccm_password@localhost:5432/ccm_db

# JWT Configuration
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS - Separe múltiplas origens por vírgula
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Produção (Render)

Configure no Render Dashboard → Environment:

```bash
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=$PORT
DATABASE_URL=[Internal Database URL do Render]
JWT_SECRET=[Gere um secret forte - use: openssl rand -hex 32]
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
CORS_ORIGINS=https://seu-app.vercel.app,https://*.vercel.app
```

## Frontend

### Desenvolvimento

Crie um arquivo `.env` na pasta `frontend/` com:

```bash
VITE_API_URL=http://localhost:6543/api
```

### Produção (Vercel)

Configure no Vercel Dashboard → Settings → Environment Variables:

```bash
VITE_API_URL=https://seu-backend.onrender.com/api
```

**Importante**: Substitua `seu-backend.onrender.com` pela URL real do seu backend.

---

## 📝 Notas

- Variáveis que começam com `VITE_` são expostas ao cliente no frontend
- Nunca commite arquivos `.env` no Git
- Use secrets fortes em produção
- Atualize `CORS_ORIGINS` após fazer deploy do frontend

