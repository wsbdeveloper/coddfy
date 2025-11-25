# Coddfy Contracts Manager CCM - Frontend

Frontend da aplicação de gestão de contratos de consultoria, desenvolvido com React/TypeScript.

## 🚀 Início Rápido

### Pré-requisitos

- Node.js 18+
- npm ou yarn

### Instalação

```bash
# 1. Instalar dependências
npm install

# 2. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env e configurar VITE_API_URL

# 3. Iniciar servidor de desenvolvimento
npm run dev
```

A aplicação estará disponível em: `http://localhost:5173`

## 🛠️ Desenvolvimento

### Estrutura do Projeto

```
.
├── src/
│   ├── components/    # Componentes React
│   ├── pages/        # Páginas da aplicação
│   ├── lib/          # Utilitários e API client
│   └── types/        # Tipos TypeScript
├── public/           # Arquivos estáticos
└── package.json      # Dependências
```

### Scripts Disponíveis

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Linting
npm run lint
```

## 🔗 Configuração da API

O frontend precisa estar configurado para se conectar ao backend:

### Desenvolvimento Local

Crie um arquivo `.env`:

```bash
VITE_API_URL=http://localhost:6543/api
```

### Produção

Configure na Vercel (ou sua plataforma de deploy):

```bash
VITE_API_URL=https://seu-backend.onrender.com/api
```

**Importante**: Substitua `seu-backend.onrender.com` pela URL real do seu backend.

## 🚀 Deploy

### Vercel

O projeto está configurado para deploy na Vercel. Veja `vercel.json` para detalhes.

**Passos:**
1. Conecte seu repositório na Vercel
2. Configure a variável de ambiente `VITE_API_URL`
3. Deploy automático a cada push

### Docker

```bash
# Build
docker build -t coddfy-frontend .

# Run
docker run -p 5173:5173 -e VITE_API_URL=http://localhost:6543/api coddfy-frontend
```

## 🎨 Tecnologias

- **React 18** - Biblioteca UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool
- **Tailwind CSS** - Estilização
- **ShadCN UI** - Componentes UI
- **Axios** - Cliente HTTP
- **React Router** - Roteamento

## 📝 Variáveis de Ambiente

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `VITE_API_URL` | URL da API backend | `http://localhost:6543/api` |

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

