-- ============================================================
-- Script SQL: Seed de Parcelas
-- ============================================================
-- Cria parcelas mensais para todos os contratos existentes
-- Divide o valor total do contrato em 12 parcelas mensais
-- Primeiras 3 parcelas são marcadas como faturadas (billed = true)
-- ============================================================

BEGIN;

-- ============================================================
-- CRIAR PARCELAS PARA TODOS OS CONTRATOS
-- ============================================================
DO $$
DECLARE
    contract_record RECORD;
    installment_value NUMERIC(15, 2);
    months_array TEXT[] := ARRAY['Jan/25', 'Fev/25', 'Mar/25', 'Abr/25', 'Mai/25', 'Jun/25', 'Jul/25', 'Ago/25', 'Set/25', 'Out/25', 'Nov/25', 'Dez/25'];
    month_name TEXT;
    i INTEGER;
    total_created INTEGER := 0;
    billed_count INTEGER := 0;
BEGIN
    -- Itera sobre todos os contratos
    FOR contract_record IN 
        SELECT id, name, total_value, billed_value
        FROM contracts
    LOOP
        RAISE NOTICE '📝 Criando parcelas para: %', contract_record.name;
        
        -- Calcula valor da parcela (divide total por 12 meses)
        installment_value := contract_record.total_value / 12;
        
        -- Cria 12 parcelas (uma por mês)
        FOR i IN 1..12 LOOP
            month_name := months_array[i];
            
            -- Primeiras 3 parcelas já pagas (billed = true)
            -- Demais pendentes (billed = false)
            INSERT INTO installments (
                id,
                contract_id,
                month,
                value,
                billed,
                created_at,
                updated_at
            ) VALUES (
                gen_random_uuid(),
                contract_record.id,
                month_name,
                installment_value,
                i <= 3,  -- Primeiras 3 parcelas faturadas
                NOW(),
                NOW()
            );
            
            total_created := total_created + 1;
            IF i <= 3 THEN
                billed_count := billed_count + 1;
            END IF;
        END LOOP;
        
        -- Atualiza billed_value do contrato (3 parcelas pagas)
        UPDATE contracts
        SET 
            billed_value = installment_value * 3,
            balance = total_value - (installment_value * 3),
            updated_at = NOW()
        WHERE id = contract_record.id;
        
        RAISE NOTICE '  ✓ 12 parcelas criadas (3 pagas, 9 pendentes)';
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '✅ % parcelas criadas com sucesso!', total_created;
    RAISE NOTICE '📊 Distribuição:';
    RAISE NOTICE '   • Pagas: %', billed_count;
    RAISE NOTICE '   • Pendentes: %', total_created - billed_count;
END $$;

COMMIT;




