-- ============================================================
-- Script SQL: Seed de Parceiros
-- ============================================================
-- Cria parceiros adicionais e usuários associados
-- ============================================================

BEGIN;

-- ============================================================
-- 1. CRIAR PARCEIROS ADICIONAIS
-- ============================================================
INSERT INTO partners (id, name, is_active, created_at, updated_at)
SELECT
    gen_random_uuid(),
    partner_name,
    TRUE,
    NOW(),
    NOW()
FROM (
    VALUES
        ('Robbin Consulting'),
        ('TechCorp Solutions'),
        ('Digital Partners')
) AS partners_data(partner_name)
WHERE NOT EXISTS (
    SELECT 1 FROM partners WHERE name = partner_name
)
RETURNING id, name INTO TEMP TABLE temp_new_partners;

-- ============================================================
-- 2. CRIAR USUÁRIOS PARA O PARCEIRO ROBBIN
-- ============================================================
DO $$
DECLARE
    robbin_partner_id UUID;
    admin_id UUID;
    user_id UUID;
    admin_password_hash TEXT := '$2b$12$/8c/1Y0L/sgcCOCy6E0AXu32zGe2f4f/b4ED9yW.rJgd0H0Hb.6Ii';  -- robbin123
    user_password_hash TEXT := '$2b$12$/8c/1Y0L/sgcCOCy6E0AXu32zGe2f4f/b4ED9yW.rJgd0H0Hb.6Ii';  -- robbin123
BEGIN
    -- Busca o parceiro Robbin
    SELECT id INTO robbin_partner_id FROM partners WHERE name = 'Robbin Consulting' LIMIT 1;
    
    IF robbin_partner_id IS NULL THEN
        RAISE EXCEPTION 'Parceiro Robbin Consulting não encontrado!';
    END IF;
    
    -- Criar admin do parceiro Robbin
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin_robbin') THEN
        admin_id := gen_random_uuid();
        
        INSERT INTO users (
            id,
            username,
            email,
            password_hash,
            role,
            partner_id,
            is_active,
            created_at,
            updated_at
        ) VALUES (
            admin_id,
            'admin_robbin',
            'admin@robbin.com',
            admin_password_hash,
            'admin_partner'::userrole,
            robbin_partner_id,
            TRUE,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE '✓ Admin do parceiro Robbin criado: admin_robbin / robbin123';
    ELSE
        RAISE NOTICE '  Admin do parceiro Robbin já existe';
    END IF;
    
    -- Criar usuário comum do parceiro Robbin
    IF NOT EXISTS (SELECT 1 FROM users WHERE username = 'user_robbin') THEN
        user_id := gen_random_uuid();
        
        INSERT INTO users (
            id,
            username,
            email,
            password_hash,
            role,
            partner_id,
            is_active,
            created_at,
            updated_at
        ) VALUES (
            user_id,
            'user_robbin',
            'user@robbin.com',
            user_password_hash,
            'user_partner'::userrole,
            robbin_partner_id,
            TRUE,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE '✓ Usuário do parceiro Robbin criado: user_robbin / robbin123';
    ELSE
        RAISE NOTICE '  Usuário do parceiro Robbin já existe';
    END IF;
END $$;

-- ============================================================
-- 3. CRIAR CLIENTES PARA O PARCEIRO ROBBIN
-- ============================================================
DO $$
DECLARE
    robbin_partner_id UUID;
    client_a_id UUID;
    client_b_id UUID;
    contract_a_id UUID;
    contract_b_id UUID;
    consultant_a_id UUID;
    consultant_b_id UUID;
BEGIN
    -- Busca o parceiro Robbin
    SELECT id INTO robbin_partner_id FROM partners WHERE name = 'Robbin Consulting' LIMIT 1;
    
    IF robbin_partner_id IS NULL THEN
        RAISE EXCEPTION 'Parceiro Robbin Consulting não encontrado!';
    END IF;
    
    -- Criar Cliente Robbin A
    IF NOT EXISTS (SELECT 1 FROM clients WHERE name = 'Cliente Robbin A' AND partner_id = robbin_partner_id) THEN
        client_a_id := gen_random_uuid();
        
        INSERT INTO clients (id, name, partner_id, created_at, updated_at)
        VALUES (client_a_id, 'Cliente Robbin A', robbin_partner_id, NOW(), NOW());
        
        -- Criar contrato para Cliente Robbin A
        contract_a_id := gen_random_uuid();
        INSERT INTO contracts (
            id, name, client_id, total_value, billed_value, balance,
            status, end_date, created_at, updated_at
        ) VALUES (
            contract_a_id,
            'Contrato Cliente Robbin A',
            client_a_id,
            100000.00,
            0.00,
            100000.00,
            'ativo'::contractstatus,
            NOW() + INTERVAL '365 days',
            NOW(),
            NOW()
        );
        
        -- Criar consultor para o contrato
        consultant_a_id := gen_random_uuid();
        INSERT INTO consultants (
            id, name, role, contract_id, partner_id, feedback,
            created_at, updated_at
        ) VALUES (
            consultant_a_id,
            'Consultor Cliente Robbin A',
            'Desenvolvedor Senior',
            contract_a_id,
            robbin_partner_id,
            85,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE '✓ Cliente Robbin A criado com contrato e consultor';
    END IF;
    
    -- Criar Cliente Robbin B
    IF NOT EXISTS (SELECT 1 FROM clients WHERE name = 'Cliente Robbin B' AND partner_id = robbin_partner_id) THEN
        client_b_id := gen_random_uuid();
        
        INSERT INTO clients (id, name, partner_id, created_at, updated_at)
        VALUES (client_b_id, 'Cliente Robbin B', robbin_partner_id, NOW(), NOW());
        
        -- Criar contrato para Cliente Robbin B
        contract_b_id := gen_random_uuid();
        INSERT INTO contracts (
            id, name, client_id, total_value, billed_value, balance,
            status, end_date, created_at, updated_at
        ) VALUES (
            contract_b_id,
            'Contrato Cliente Robbin B',
            client_b_id,
            100000.00,
            0.00,
            100000.00,
            'ativo'::contractstatus,
            NOW() + INTERVAL '365 days',
            NOW(),
            NOW()
        );
        
        -- Criar consultor para o contrato
        consultant_b_id := gen_random_uuid();
        INSERT INTO consultants (
            id, name, role, contract_id, partner_id, feedback,
            created_at, updated_at
        ) VALUES (
            consultant_b_id,
            'Consultor Cliente Robbin B',
            'Desenvolvedor Senior',
            contract_b_id,
            robbin_partner_id,
            85,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE '✓ Cliente Robbin B criado com contrato e consultor';
    END IF;
END $$;

-- Limpar tabela temporária
DROP TABLE IF EXISTS temp_new_partners;

COMMIT;

-- ============================================================
-- RESUMO
-- ============================================================
DO $$
DECLARE
    partner_count INTEGER;
    user_count INTEGER;
    client_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO partner_count FROM partners;
    SELECT COUNT(*) INTO user_count FROM users;
    SELECT COUNT(*) INTO client_count FROM clients WHERE partner_id IN (SELECT id FROM partners WHERE name = 'Robbin Consulting');
    
    RAISE NOTICE '';
    RAISE NOTICE '📊 RESUMO:';
    RAISE NOTICE '   Total de parceiros: %', partner_count;
    RAISE NOTICE '   Total de usuários: %', user_count;
    RAISE NOTICE '   Clientes do Robbin: %', client_count;
    RAISE NOTICE '';
    RAISE NOTICE '🔐 CREDENCIAIS DE ACESSO:';
    RAISE NOTICE '   Admin Global: admin / admin123';
    RAISE NOTICE '   Admin Parceiro Robbin: admin_robbin / robbin123';
    RAISE NOTICE '   Usuário Parceiro Robbin: user_robbin / robbin123';
END $$;




