-- ============================================================
-- Script SQL: Seed de Dados Básicos
-- ============================================================
-- Popula o banco com dados de exemplo:
-- - 3 Clientes
-- - 3 Contratos
-- - 6 Consultores
-- - 5 Parcelas
-- ============================================================
-- IMPORTANTE: Este script assume que já existe um parceiro padrão
-- Se não existir, execute primeiro a migration que cria o parceiro padrão
-- ============================================================

BEGIN;

-- Limpa dados existentes (CUIDADO em produção!)
DELETE FROM consultant_feedbacks;
DELETE FROM consultants;
DELETE FROM installments;
DELETE FROM contracts;
DELETE FROM clients;

-- ============================================================
-- 1. OBTER PARCEIRO PADRÃO
-- ============================================================
DO $$
DECLARE
    default_partner_id UUID;
BEGIN
    -- Busca o parceiro padrão (criado pela migration)
    SELECT id INTO default_partner_id FROM partners WHERE name = 'Parceiro Padrão' LIMIT 1;
    
    IF default_partner_id IS NULL THEN
        RAISE EXCEPTION 'Parceiro Padrão não encontrado! Execute as migrations primeiro.';
    END IF;
    
    -- Armazena o ID em uma variável de sessão para uso posterior
    PERFORM set_config('app.default_partner_id', default_partner_id::text, false);
END $$;

-- ============================================================
-- 2. CRIAR CLIENTES
-- ============================================================
INSERT INTO clients (id, name, partner_id, created_at, updated_at)
VALUES
    (gen_random_uuid(), 'Tech Solutions Ltda', (SELECT id FROM partners WHERE name = 'Parceiro Padrão' LIMIT 1), NOW(), NOW()),
    (gen_random_uuid(), 'Inovação Digital S.A.', (SELECT id FROM partners WHERE name = 'Parceiro Padrão' LIMIT 1), NOW(), NOW()),
    (gen_random_uuid(), 'Consultoria Estratégica', (SELECT id FROM partners WHERE name = 'Parceiro Padrão' LIMIT 1), NOW(), NOW())
RETURNING id, name INTO TEMP TABLE temp_clients;

-- ============================================================
-- 3. CRIAR CONTRATOS
-- ============================================================
DO $$
DECLARE
    client1_id UUID;
    client2_id UUID;
    client3_id UUID;
    contract1_id UUID;
    contract2_id UUID;
    contract3_id UUID;
BEGIN
    -- Busca IDs dos clientes
    SELECT id INTO client1_id FROM temp_clients WHERE name = 'Tech Solutions Ltda' LIMIT 1;
    SELECT id INTO client2_id FROM temp_clients WHERE name = 'Inovação Digital S.A.' LIMIT 1;
    SELECT id INTO client3_id FROM temp_clients WHERE name = 'Consultoria Estratégica' LIMIT 1;
    
    -- Contrato 1: Desenvolvimento Sistema ERP
    contract1_id := gen_random_uuid();
    INSERT INTO contracts (
        id, name, client_id, total_value, billed_value, balance,
        status, end_date, created_at, updated_at
    ) VALUES (
        contract1_id,
        'Desenvolvimento Sistema ERP',
        client1_id,
        500000.00,
        350000.00,
        150000.00,
        'ativo'::contractstatus,
        NOW() + INTERVAL '90 days',
        NOW(),
        NOW()
    );
    
    -- Contrato 2: Modernização Infraestrutura
    contract2_id := gen_random_uuid();
    INSERT INTO contracts (
        id, name, client_id, total_value, billed_value, balance,
        status, end_date, created_at, updated_at
    ) VALUES (
        contract2_id,
        'Modernização Infraestrutura',
        client2_id,
        300000.00,
        100000.00,
        200000.00,
        'ativo'::contractstatus,
        NOW() + INTERVAL '120 days',
        NOW(),
        NOW()
    );
    
    -- Contrato 3: Consultoria DevOps
    contract3_id := gen_random_uuid();
    INSERT INTO contracts (
        id, name, client_id, total_value, billed_value, balance,
        status, end_date, created_at, updated_at
    ) VALUES (
        contract3_id,
        'Consultoria DevOps',
        client3_id,
        150000.00,
        150000.00,
        0.00,
        'inativo'::contractstatus,
        NOW() - INTERVAL '30 days',
        NOW(),
        NOW()
    );
    
    -- Cria tabela temporária com os contratos para uso posterior
    CREATE TEMP TABLE temp_contracts AS
    SELECT id, name FROM contracts WHERE id IN (contract1_id, contract2_id, contract3_id);
END $$;

-- ============================================================
-- 4. CRIAR PARCELAS (para o contrato ERP)
-- ============================================================
DO $$
DECLARE
    erp_contract_id UUID;
    month_name TEXT;
    i INTEGER;
    months_array TEXT[] := ARRAY['Jan/25', 'Fev/25', 'Mar/25', 'Abr/25', 'Mai/25'];
BEGIN
    -- Busca o ID do contrato ERP
    SELECT id INTO erp_contract_id FROM temp_contracts WHERE name = 'Desenvolvimento Sistema ERP' LIMIT 1;
    
    -- Cria 5 parcelas
    FOR i IN 1..5 LOOP
        month_name := months_array[i];
        
        INSERT INTO installments (
            id, contract_id, month, value, billed, created_at, updated_at
        ) VALUES (
            gen_random_uuid(),
            erp_contract_id,
            month_name,
            100000.00,
            i <= 3,  -- Primeiras 3 parcelas faturadas
            NOW(),
            NOW()
        );
    END LOOP;
END $$;

-- ============================================================
-- 5. CRIAR CONSULTORES
-- ============================================================
DO $$
DECLARE
    default_partner_id UUID;
    contract1_id UUID;
    contract2_id UUID;
    contract3_id UUID;
BEGIN
    -- Busca parceiro padrão
    SELECT id INTO default_partner_id FROM partners WHERE name = 'Parceiro Padrão' LIMIT 1;
    
    -- Busca IDs dos contratos
    SELECT id INTO contract1_id FROM temp_contracts WHERE name = 'Desenvolvimento Sistema ERP' LIMIT 1;
    SELECT id INTO contract2_id FROM temp_contracts WHERE name = 'Modernização Infraestrutura' LIMIT 1;
    SELECT id INTO contract3_id FROM temp_contracts WHERE name = 'Consultoria DevOps' LIMIT 1;
    
    -- Consultores do Contrato 1
    INSERT INTO consultants (id, name, role, contract_id, partner_id, feedback, created_at, updated_at) VALUES
        (gen_random_uuid(), 'João Silva', 'Tech Lead', contract1_id, default_partner_id, 95, NOW(), NOW()),
        (gen_random_uuid(), 'Maria Santos', 'Desenvolvedor Senior', contract1_id, default_partner_id, 92, NOW(), NOW()),
        (gen_random_uuid(), 'Pedro Oliveira', 'Desenvolvedor Pleno', contract1_id, default_partner_id, 88, NOW(), NOW());
    
    -- Consultores do Contrato 2
    INSERT INTO consultants (id, name, role, contract_id, partner_id, feedback, created_at, updated_at) VALUES
        (gen_random_uuid(), 'Ana Costa', 'Arquiteta de Soluções', contract2_id, default_partner_id, 96, NOW(), NOW()),
        (gen_random_uuid(), 'Carlos Mendes', 'Engenheiro DevOps', contract2_id, default_partner_id, 90, NOW(), NOW());
    
    -- Consultores do Contrato 3
    INSERT INTO consultants (id, name, role, contract_id, partner_id, feedback, created_at, updated_at) VALUES
        (gen_random_uuid(), 'Beatriz Lima', 'Consultora DevOps', contract3_id, default_partner_id, 85, NOW(), NOW());
END $$;

-- Limpar tabela temporária
DROP TABLE IF EXISTS temp_clients;
DROP TABLE IF EXISTS temp_contracts;

COMMIT;

-- ============================================================
-- RESUMO
-- ============================================================
DO $$
DECLARE
    client_count INTEGER;
    contract_count INTEGER;
    consultant_count INTEGER;
    installment_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO client_count FROM clients;
    SELECT COUNT(*) INTO contract_count FROM contracts;
    SELECT COUNT(*) INTO consultant_count FROM consultants;
    SELECT COUNT(*) INTO installment_count FROM installments;
    
    RAISE NOTICE '✅ Dados de exemplo criados com sucesso!';
    RAISE NOTICE '   Clientes criados: %', client_count;
    RAISE NOTICE '   Contratos criados: %', contract_count;
    RAISE NOTICE '   Consultores criados: %', consultant_count;
    RAISE NOTICE '   Parcelas criadas: %', installment_count;
END $$;

