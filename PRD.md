# 🧾 Product Requirements Document (PRD)

## 🏷️ Nome do Produto
**Cursor Contracts Manager (CCM)**

---

## 🎯 Visão Geral
O **Cursor Contracts Manager** é uma plataforma web para **gestão de contratos de consultoria**, com controle financeiro, vigência e desempenho técnico dos consultores alocados.

O sistema fornece:
- Painel geral com indicadores de contratos e consultores;
- Controle financeiro com valores totais, faturados e saldos;
- Feedback de performance por consultor;
- Acompanhamento de vigência e status dos contratos.

---

## 👥 Público-Alvo
- Gestores de contratos e projetos;
- Equipes de RH e Operações;
- Time financeiro responsável pelo faturamento.

---

## 🧩 Funcionalidades Principais

### 1. **Dashboard (Página Inicial)**
**Objetivo:** Apresentar visão geral consolidada dos contratos e consultores.

**Elementos:**
- Cards com indicadores:
  - Contratos ativos
  - Contratos inativos
  - Consultores alocados
- Lista de **vigência de contratos**
- **Visão financeira de consumo**, com:
  - Barra de progresso (% consumido)
  - Valor total, faturado e saldo

---

### 2. **Gestão de Contratos**
**Objetivo:** Exibir e acompanhar o desempenho financeiro de cada contrato.

**Funcionalidades:**
- Listagem de contratos com:
  - Nome do projeto e cliente
  - Percentual faturado
  - Valor total, valor faturado e saldo
  - Parcelas mensais e status (“Parcela faturada”)
- Filtros por cliente, status e período
- Barra de progresso indicando percentual do contrato consumido

---

### 3. **Gestão de Consultores**
**Objetivo:** Visualizar consultores alocados por contrato com dados de desempenho.

**Funcionalidades:**
- Agrupamento por contrato
- Exibição de:
  - Nome do consultor
  - Cargo e especialidade
  - Feedback individual (%)
- Cálculo automático de:
  - Quantidade de alocados
  - Feedback médio do grupo
- Cores por desempenho:
  - 🟢 Verde (≥ 90%)
  - 🟠 Laranja (80–89%)
  - 🔴 Vermelho (< 80%)

---

## ⚙️ Requisitos Técnicos

### **Frontend**
- **Framework:** React + TypeScript  
- **UI:** Tailwind CSS + ShadCN/UI  
- **Bibliotecas adicionais:**  
  - Recharts (gráficos e barras de progresso)  
  - Axios (requisições HTTP)  
  - React Router (navegação)
- **Design System:** Layout limpo, responsivo e minimalista

### **Backend**
- **Linguagem:** Node.js (TypeScript)  
- **Framework:** Express.js  
- **Banco de Dados:** PostgreSQL  
- **ORM:** Prisma  
- **Autenticação:** JWT com níveis de acesso (admin / gestor / leitura)

**Endpoints principais:**
| Método | Endpoint | Descrição |
|---------|-----------|-----------|
| GET | `/dashboard` | Retorna visão geral consolidada |
| GET | `/contracts` | Lista contratos com parcelas |
| POST | `/contracts` | Cria novo contrato |
| GET | `/consultants` | Lista consultores e feedbacks |
| POST | `/consultants` | Cria novo consultor |

---

## 🧮 Modelagem de Dados

### **clients**
| Campo | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador |
| name | String | Nome do cliente |

### **contracts**
| Campo | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador |
| name | String | Nome do contrato |
| client_id | UUID | FK cliente |
| total_value | Decimal | Valor total |
| billed_value | Decimal | Valor faturado |
| balance | Decimal | Saldo atual |
| status | Enum (ativo, inativo, a_vencer) | Status |
| end_date | Date | Vigência |

### **installments**
| Campo | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador |
| contract_id | UUID | FK contrato |
| month | String | Ex: “Jan/25” |
| value | Decimal | Valor da parcela |
| billed | Boolean | Se já foi faturada |

### **consultants**
| Campo | Tipo | Descrição |
|--------|------|-----------|
| id | UUID | Identificador |
| name | String | Nome |
| role | String | Cargo |
| contract_id | UUID | FK contrato |
| feedback | Integer | % de avaliação |

---

## 📈 KPIsimage.png
- % de contratos ativos x inativos  
- Média geral de feedbacks  
- % médio de consumo financeiro  
- Total de consultores alocados  

---

## 🔒 Requisitos Não Funcionais
- **Segurança:** HTTPS, JWT e CORS configurados  
- **Performance:** Resposta média de API < 200ms  
- **Escalabilidade:** Multi-cliente preparado  
- **Usabilidade:** Responsivo (desktop/tablet)  
- **Deploy:** Docker + CI/CD via GitHub Actions (produção em ECS ou Railway)

---

## 🧠 Futuras Evoluções
- Exportação de relatórios (PDF / Excel)  
- Gráficos comparativos de desempenho  
- Integração com ServiceNow / Jira  
- Notificações automáticas de vencimento de contratos  

---

## 📅 Cronograma de Entrega

| Fase | Entrega | Duração |
|------|----------|---------|
| Planejamento & Design UI | Protótipo Figma + definição de API | 1 semana |
| Backend MVP | Endpoints de contratos e consultores | 2 semanas |
| Frontend MVP | Dashboard + listagens | 2 semanas |
| Integração & Testes | Deploy + QA final | 1 semana |
| **Total Estimado:** | **6 semanas** |

---

## 📦 Estrutura sugerida de pastas

