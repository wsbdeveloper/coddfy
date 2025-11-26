# Scripts SQL para Seed de Dados

Este diretório contém scripts SQL para popular o banco de dados diretamente via SQL, sem necessidade de executar scripts Python.

## 📋 Scripts Disponíveis

### 1. `01_create_admin.sql`
Cria o usuário administrador padrão do sistema.

**Credenciais:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@coddfy.com`
- Role: `admin_global`

**Uso:**
```bash
psql -U ccm_user -d ccm_db -f 01_create_admin.sql
```

### 2. `02_seed_data.sql`
Popula o banco com dados básicos de exemplo:
- 3 Clientes
- 3 Contratos
- 6 Consultores
- 5 Parcelas

**Uso:**
```bash
psql -U ccm_user -d ccm_db -f 02_seed_data.sql
```

**Nota:** Este script assume que já existe um parceiro padrão (criado pela migration).

### 3. `03_seed_partners.sql`
Cria parceiros adicionais e usuários associados:
- Parceiros: Robbin Consulting, TechCorp Solutions, Digital Partners
- Usuários do parceiro Robbin:
  - `admin_robbin` / `robbin123` (admin_partner)
  - `user_robbin` / `robbin123` (user_partner)
- Clientes e contratos para o parceiro Robbin

**Uso:**
```bash
psql -U ccm_user -d ccm_db -f 03_seed_partners.sql
```

### 4. `04_seed_installments.sql`
Cria parcelas mensais para todos os contratos existentes:
- Divide o valor total em 12 parcelas mensais
- Primeiras 3 parcelas marcadas como faturadas
- Atualiza `billed_value` e `balance` dos contratos

**Uso:**
```bash
psql -U ccm_user -d ccm_db -f 04_seed_installments.sql
```

## 🚀 Executar Todos os Scripts

### Opção 1: Script Master (Recomendado)

Execute todos os scripts de uma vez:

```bash
cd backend/scripts/sql
psql -U ccm_user -d ccm_db -f 00_run_all.sql
```

### Opção 2: Scripts Individuais

Execute cada script separadamente:

```bash
# 1. Criar admin
psql -U ccm_user -d ccm_db -f 01_create_admin.sql

# 2. Dados básicos
psql -U ccm_user -d ccm_db -f 02_seed_data.sql

# 3. Parceiros
psql -U ccm_user -d ccm_db -f 03_seed_partners.sql

# 4. Parcelas adicionais
psql -U ccm_user -d ccm_db -f 04_seed_installments.sql
```

Ou usando uma conexão direta:

```bash
psql postgresql://ccm_user:ccm_password@localhost:5432/ccm_db -f 01_create_admin.sql
psql postgresql://ccm_user:ccm_password@localhost:5432/ccm_db -f 02_seed_data.sql
psql postgresql://ccm_user:ccm_password@localhost:5432/ccm_db -f 03_seed_partners.sql
psql postgresql://ccm_user:ccm_password@localhost:5432/ccm_db -f 04_seed_installments.sql
```

## 🔐 Hashes de Senha

Os hashes bcrypt usados nos scripts foram gerados especificamente para:
- `admin123` → `$2b$12$mpggV70Qkq3cAmRDUVB0F.ieaK6/s/na4pVss0/E0emip17YVc38C`
- `robbin123` → `$2b$12$/8c/1Y0L/sgcCOCy6E0AXu32zGe2f4f/b4ED9yW.rJgd0H0Hb.6Ii`

**Para gerar novos hashes:**
```python
import bcrypt
hash = bcrypt.hashpw(b'sua_senha', bcrypt.gensalt()).decode()
print(hash)
```

## ⚠️ Avisos

1. **Produção:** Os scripts `02_seed_data.sql` e `04_seed_installments.sql` fazem DELETE de dados existentes. Use com cuidado em produção!

2. **Ordem de Execução:** Execute os scripts na ordem numérica (01, 02, 03, 04) para evitar erros de dependência.

3. **Migrations:** Certifique-se de que todas as migrations foram aplicadas antes de executar os seeds.

## 📝 Notas

- Os scripts usam `gen_random_uuid()` para gerar UUIDs
- Timestamps são gerados com `NOW()`
- Os scripts são idempotentes onde possível (verificam se dados já existem)
- Valores monetários usam `NUMERIC(15, 2)` para precisão

