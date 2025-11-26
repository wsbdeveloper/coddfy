# 🔧 Configuração de CORS no Render

## ❌ Erro Atual

```
CORS header 'Access-Control-Allow-Origin' missing. Status code: 403
```

Isso acontece porque a URL do seu frontend não está na lista de origens permitidas.

## ✅ Solução

### No Render Dashboard → Environment Variables

Adicione ou atualize a variável `CORS_ORIGINS` com a URL do seu frontend.

### Exemplos de Configuração

#### 1. Frontend na Vercel (domínio padrão)
```
https://seu-app.vercel.app,https://*.vercel.app
```

#### 2. Frontend na Vercel (domínio customizado)
```
https://coddfy.com,https://www.coddfy.com
```

#### 3. Frontend em outro serviço
```
https://seu-frontend.netlify.app
```

#### 4. Múltiplos domínios (desenvolvimento + produção)
```
https://seu-app.vercel.app,https://*.vercel.app,http://localhost:5173,http://localhost:3000
```

#### 5. Permitir qualquer origem (⚠️ NÃO RECOMENDADO para produção)
```
*
```

## 📝 Formato

- **Separador**: Use vírgula (`,`) para múltiplas URLs
- **Protocolo**: Sempre inclua `https://` ou `http://`
- **Sem barra final**: Não coloque `/` no final da URL
- **Wildcards**: Use `*` para subdomínios (ex: `https://*.vercel.app`)

## 🔍 Como Descobrir a URL do Frontend

1. **Vercel**: Veja a URL no dashboard da Vercel (ex: `https://coddfy-frontend.vercel.app`)
2. **Console do navegador**: Veja o erro CORS - ele mostra a origem que está fazendo a requisição
3. **Network tab**: No DevTools, veja o header `Origin` da requisição

## 🚀 Passo a Passo no Render

1. Acesse o **Render Dashboard**
2. Selecione seu serviço backend
3. Vá em **"Environment"** (no menu lateral)
4. Procure por `CORS_ORIGINS` ou clique em **"Add Environment Variable"**
5. Configure:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `https://seu-frontend.vercel.app,https://*.vercel.app`
6. Clique em **"Save Changes"**
7. O Render fará redeploy automaticamente

## ✅ Verificação

Após configurar, teste:

```bash
# Teste o endpoint de login
curl -X POST https://coddfy.onrender.com/api/auth/login \
  -H "Origin: https://seu-frontend.vercel.app" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Se funcionar, você verá o header `Access-Control-Allow-Origin` na resposta.

## 🐛 Troubleshooting

### Ainda recebe erro 403?

1. **Verifique a URL exata**: Deve ser idêntica (incluindo `https://`, sem barra final)
2. **Aguarde o redeploy**: Pode levar 1-2 minutos após salvar
3. **Verifique os logs**: No Render, veja os logs para mensagens de CORS
4. **Teste com curl**: Use o comando acima para verificar

### Múltiplos ambientes?

Se você tem:
- Frontend de desenvolvimento: `http://localhost:5173`
- Frontend de produção: `https://coddfy.vercel.app`

Configure:
```
https://coddfy.vercel.app,https://*.vercel.app,http://localhost:5173
```

## 📌 Exemplo Completo

**No Render, configure:**

```
CORS_ORIGINS = https://coddfy.vercel.app,https://*.vercel.app
```

Isso permitirá:
- ✅ `https://coddfy.vercel.app`
- ✅ `https://coddfy-git-main.vercel.app` (preview branches)
- ✅ `https://coddfy-abc123.vercel.app` (deployments)

## ⚠️ Importante

- **Nunca use `*` em produção** (permite qualquer origem)
- **Sempre use HTTPS** em produção
- **Inclua todas as variações** (www, sem www, subdomínios)
- **Teste após cada mudança**

