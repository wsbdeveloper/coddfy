# Correções nos Scripts de Seed

## 🔧 Problemas Corrigidos

### 1. **seed_data.py**
- ❌ **Problema**: Usava campo `feedback` diretamente no Consultant (campo removido)
- ✅ **Solução**: 
  - Removido campo `feedback` da criação de consultores
  - Adicionado suporte a `partner_id` (multi-tenancy)
  - Criados `ConsultantFeedback` com `rating` para cada consultor
  - Adicionada busca de parceiro padrão e usuário padrão

### 2. **seed_partners.py**
- ❌ **Problema**: Usava campo `feedback=85` diretamente no Consultant
- ✅ **Solução**:
  - Removido campo `feedback` da criação de consultores
  - Criado `ConsultantFeedback` com `rating=85` após criar o consultor

### 3. **create_admin.py**
- ❌ **Problema**: Usava `UserRole.ADMIN` (enum antigo)
- ✅ **Solução**:
  - Atualizado para `UserRole.ADMIN_GLOBAL`
  - Adicionado `partner_id=None` (admin global não tem parceiro)

### 4. **setup.sh**
- ❌ **Problema**: Não executava os seeds após a migração
- ✅ **Solução**:
  - Adicionada execução de `seed_partners.py` e `seed_data.py` após criar admin

## 📋 Ordem de Execução Correta

1. **Migrações**: `alembic upgrade head`
2. **Admin**: `create_admin.py` (cria usuário admin global)
3. **Parceiros**: `seed_partners.py` (cria parceiros e usuários de parceiro)
4. **Dados**: `seed_data.py` (cria clientes, contratos, consultores e feedbacks)

## ✅ Como Executar

### Opção 1: Usar setup.sh (Recomendado)
```bash
./setup.sh
```

### Opção 2: Manual
```bash
# 1. Migrações
cd backend && poetry run alembic -c alembic.ini upgrade head && cd ..

# 2. Admin
poetry run python backend/scripts/create_admin.py

# 3. Seeds
poetry run python backend/scripts/seed_partners.py
poetry run python backend/scripts/seed_data.py
```

## 🎯 Resultado Esperado

Após executar os seeds:
- ✅ Parceiros criados (Parceiro Padrão + parceiros de exemplo)
- ✅ Usuários criados (admin global + admins/usuários de parceiro)
- ✅ Clientes criados (vinculados aos parceiros)
- ✅ Contratos criados
- ✅ Consultores criados (com `partner_id` e `photo_url`)
- ✅ Feedbacks criados (com `rating` para calcular média)
- ✅ Parcelas criadas

## ⚠️ Importante

- O campo `feedback` do Consultant foi **removido** e agora é calculado como média dos `ratings` dos `ConsultantFeedback`
- Todos os consultores precisam ter `partner_id` (multi-tenancy)
- Feedbacks devem ter `rating` para que o feedback do consultor seja calculado corretamente

