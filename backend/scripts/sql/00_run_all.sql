-- ============================================================
-- Script Master: Executa Todos os Seeds
-- ============================================================
-- Este script executa todos os seeds em ordem:
-- 1. Cria usuário admin
-- 2. Popula dados básicos
-- 3. Cria parceiros e usuários
-- 4. Cria parcelas adicionais
-- ============================================================
-- Uso: psql -U ccm_user -d ccm_db -f 00_run_all.sql
-- ============================================================

\echo '=========================================='
\echo '🚀 Iniciando Seed Completo do Banco'
\echo '=========================================='
\echo ''

\echo '1️⃣  Criando usuário administrador...'
\i 01_create_admin.sql

\echo ''
\echo '2️⃣  Populando dados básicos...'
\i 02_seed_data.sql

\echo ''
\echo '3️⃣  Criando parceiros e usuários...'
\i 03_seed_partners.sql

\echo ''
\echo '4️⃣  Criando parcelas adicionais...'
\i 04_seed_installments.sql

\echo ''
\echo '=========================================='
\echo '✅ Seed completo executado com sucesso!'
\echo '=========================================='

