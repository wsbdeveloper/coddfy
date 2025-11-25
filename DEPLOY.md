# 🚀 Guia de Deploy

Este guia explica como fazer deploy do **Frontend na Vercel** e do **Backend no Render**.

---

## 📋 Pré-requisitos

- Conta na [Vercel](https://vercel.com)
- Conta no [Render](https://render.com)
- Repositório Git (GitHub, GitLab ou Bitbucket)
- Banco de dados PostgreSQL (Render oferece PostgreSQL gerenciado)

---

## 🎯 Backend - Deploy no Render

### 1. Preparar o Banco de Dados

1. Acesse o [Render Dashboard](https://dashboard.render.com)
2. Clique em **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `portal-coddfy-db`
   - **Database**: `ccm_db`
   - **User**: `ccm_user`
   - **Region**: Escolha a mais próxima
   - **Plan**: Free (ou pago para produção)
4. Anote a **Internal Database URL** e **External Database URL**

### 2. Deploy do Backend

1. No Render Dashboard, clique em **"New +"** → **"Web Service"**
2. Conecte seu repositório Git
3. Configure o serviço:
   - **Name**: `portal-coddfy-backend`
   - **Region**: Mesma região do banco de dados
   - **Branch**: `main`
   - **Root Directory**: Deixe em branco (raiz do projeto)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     pip install poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
     ```
   - **Start Command**: 
     ```bash
     cd backend && poetry run alembic -c alembic.ini upgrade head && poetry run python -m backend
     ```

### 3. Variáveis de Ambiente no Render

Adicione as seguintes variáveis de ambiente no Render:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `APP_ENV` | `production` | Ambiente de produção |
| `APP_HOST` | `0.0.0.0` | Host do servidor |
| `APP_PORT` | `$PORT` | Porta (Render define automaticamente) |
| `DATABASE_URL` | `[Internal Database URL do Render]` | URL do banco de dados |
| `JWT_SECRET` | `[Gere um secret forte]` | Secret para JWT (use gerador seguro) |
| `JWT_ALGORITHM` | `HS256` | Algoritmo JWT |
| `JWT_EXPIRATION_HOURS` | `24` | Expiração do token |
| `CORS_ORIGINS` | `https://seu-app.vercel.app,https://*.vercel.app` | Domínios permitidos (ajuste após deploy do frontend) |

**Importante**: 
- Use a **Internal Database URL** para melhor performance
- Gere um `JWT_SECRET` forte (ex: `openssl rand -hex 32`)
- Atualize `CORS_ORIGINS` após fazer deploy do frontend

### 4. Health Check

O Render usará automaticamente `/api/health` para verificar se o serviço está rodando.

### 5. Após o Deploy

1. Anote a URL do backend (ex: `https://portal-coddfy-backend.onrender.com`)
2. Teste o health check: `https://seu-backend.onrender.com/api/health`
3. Teste a API: `https://seu-backend.onrender.com/api/docs/swagger`

---

## ⚛️ Frontend - Deploy na Vercel

### 1. Preparar o Projeto

O projeto já está configurado com `vercel.json` na pasta `frontend/`.

### 2. Deploy via Vercel CLI (Recomendado)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Navegar para a pasta do frontend
cd frontend

# Fazer login
vercel login

# Deploy
vercel

# Para produção
vercel --prod
```

### 3. Deploy via Dashboard Vercel

1. Acesse [Vercel Dashboard](https://vercel.com/dashboard)
2. Clique em **"Add New..."** → **"Project"**
3. Importe seu repositório Git
4. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### 4. Variáveis de Ambiente na Vercel

Adicione a variável de ambiente:

| Variável | Valor | Descrição |
|----------|-------|-----------|
| `VITE_API_URL` | `https://seu-backend.onrender.com/api` | URL da API backend |

**Importante**: 
- Substitua `seu-backend.onrender.com` pela URL real do seu backend no Render
- Variáveis que começam com `VITE_` são expostas ao cliente

### 5. Após o Deploy

1. Anote a URL do frontend (ex: `https://seu-app.vercel.app`)
2. Atualize `CORS_ORIGINS` no Render com a URL do frontend:
   ```
   https://seu-app.vercel.app,https://*.vercel.app
   ```
3. Teste o frontend acessando a URL da Vercel

---

## 🔄 Atualizar CORS após Deploy

Após fazer deploy do frontend, atualize o CORS no Render:

1. Vá para o serviço do backend no Render
2. Acesse **"Environment"**
3. Atualize `CORS_ORIGINS`:
   ```
   https://seu-app.vercel.app,https://*.vercel.app
   ```
4. Salve e aguarde o redeploy automático

---

## ✅ Verificação Pós-Deploy

### Backend

```bash
# Health check
curl https://seu-backend.onrender.com/api/health

# Deve retornar:
# {"status": "ok", "service": "portal-coddfy-backend", "version": "1.0.0"}
```

### Frontend

1. Acesse a URL da Vercel
2. Tente fazer login (credenciais padrão: `admin` / `admin123`)
3. Verifique se as requisições à API funcionam

---

## 🐛 Troubleshooting

### Backend não inicia

- Verifique os logs no Render Dashboard
- Confirme que `DATABASE_URL` está correto
- Verifique se as migrações rodaram (`alembic upgrade head`)

### Erro de CORS

- Verifique se `CORS_ORIGINS` inclui a URL exata do frontend
- Certifique-se de incluir `https://*.vercel.app` para previews
- Verifique se não há espaços extras na configuração

### Frontend não conecta ao backend

- Verifique se `VITE_API_URL` está configurado corretamente na Vercel
- Confirme que a URL termina com `/api`
- Teste a URL do backend diretamente no navegador

### Banco de dados não conecta

- Use a **Internal Database URL** no Render (mesma região)
- Verifique se o banco está ativo no Render Dashboard
- Confirme que as credenciais estão corretas

---

## 📝 Notas Importantes

1. **Banco de Dados**: O plano free do Render pausa o banco após 90 dias de inatividade. Para produção, considere um plano pago.

2. **Cold Start**: O Render pode ter "cold start" no plano free (até 50s). Considere upgrade para produção.

3. **Domínios Customizados**: Você pode configurar domínios customizados tanto na Vercel quanto no Render.

4. **SSL**: Ambos Vercel e Render fornecem SSL automático.

5. **Variáveis de Ambiente**: Nunca commite secrets no Git. Use variáveis de ambiente.

---

## 🔐 Segurança

- ✅ Use `JWT_SECRET` forte e único
- ✅ Configure `CORS_ORIGINS` apenas com domínios necessários
- ✅ Use HTTPS sempre (automático na Vercel/Render)
- ✅ Não exponha `DATABASE_URL` no frontend
- ✅ Mantenha dependências atualizadas

---

## 📚 Recursos

- [Documentação Vercel](https://vercel.com/docs)
- [Documentação Render](https://render.com/docs)
- [Documentação do Projeto](./DOCUMENTACAO.md)

---

**Desenvolvido por Portal Coddfy Team**

