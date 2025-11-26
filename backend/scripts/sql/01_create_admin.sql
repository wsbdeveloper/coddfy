-- ============================================================
-- Script SQL: Criar Usuário Administrador
-- ============================================================
-- Cria o usuário administrador padrão do sistema
-- Username: admin
-- Password: admin123
-- Email: admin@coddfy.com
-- Role: admin_global
-- ============================================================

-- Verifica se o usuário admin já existe
DO $$
DECLARE
    admin_exists BOOLEAN;
    admin_id UUID;
    password_hash TEXT;
BEGIN
    -- Hash bcrypt para a senha 'admin123'
    -- Este hash foi gerado especificamente para esta senha
    password_hash := '$2b$12$mpggV70Qkq3cAmRDUVB0F.ieaK6/s/na4pVss0/E0emip17YVc38C';
    
    -- Verifica se já existe
    SELECT EXISTS(SELECT 1 FROM users WHERE username = 'admin') INTO admin_exists;
    
    IF admin_exists THEN
        RAISE NOTICE 'Usuário admin já existe. Pulando criação.';
    ELSE
        -- Gera novo UUID para o admin
        admin_id := gen_random_uuid();
        
        -- Cria o usuário admin
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
            'admin',
            'admin@coddfy.com',
            password_hash,
            'admin_global'::userrole,
            NULL,  -- Admin global não tem partner_id
            TRUE,
            NOW(),
            NOW()
        );
        
        RAISE NOTICE 'Usuário administrador criado com sucesso!';
        RAISE NOTICE 'Username: admin';
        RAISE NOTICE 'Password: admin123';
        RAISE NOTICE 'Email: admin@coddfy.com';
        RAISE NOTICE 'Role: ADMIN_GLOBAL';
    END IF;
END $$;

-- Nota: Para gerar um novo hash bcrypt, use Python:
-- python3 -c "import bcrypt; print(bcrypt.hashpw(b'admin123', bcrypt.gensalt()).decode())"
-- Substitua o password_hash acima com o novo hash gerado

