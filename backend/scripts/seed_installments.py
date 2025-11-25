#!/usr/bin/env python
"""
Script para popular o banco de dados com parcelas de exemplo
Cria parcelas para os contratos existentes
"""
import os
import sys
from pathlib import Path

# Adiciona o diretório raiz do projeto ao path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Contract, Installment
from datetime import datetime
from decimal import Decimal
import random

# Carrega variáveis de ambiente
load_dotenv()

def create_installments():
    """Cria parcelas de exemplo para todos os contratos"""
    
    # Conecta ao banco
    database_url = os.getenv('DATABASE_URL', 'postgresql://ccm_user:ccm_password@localhost:5432/ccm_db')
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Busca todos os contratos
        contracts = session.query(Contract).all()
        
        if not contracts:
            print("❌ Nenhum contrato encontrado! Execute seed_data.py primeiro.")
            return
        
        # Meses para criar parcelas
        months = [
            'Jan/25', 'Fev/25', 'Mar/25', 'Abr/25', 'Mai/25', 'Jun/25',
            'Jul/25', 'Ago/25', 'Set/25', 'Out/25', 'Nov/25', 'Dez/25'
        ]
        
        total_created = 0
        
        for contract in contracts:
            print(f"\n📝 Criando parcelas para: {contract.name}")
            
            # Calcula valor da parcela (divide total por 12 meses)
            installment_value = Decimal(str(contract.total_value)) / Decimal('12')
            
            # Cria 12 parcelas (uma por mês)
            for i, month in enumerate(months):
                # Primeiras 3 parcelas já pagas (billed=True)
                # Demais pendentes (billed=False)
                is_billed = i < 3
                
                installment = Installment(
                    contract_id=contract.id,
                    month=month,
                    value=installment_value,
                    billed=is_billed
                )
                
                session.add(installment)
                total_created += 1
                
                status = "✅ Pago" if is_billed else "⏳ Pendente"
                print(f"  • {month}: R$ {installment_value:,.2f} - {status}")
            
            # Atualiza billed_value do contrato
            contract.billed_value = installment_value * Decimal('3')  # 3 parcelas pagas
            contract.balance = contract.total_value - contract.billed_value
        
        session.commit()
        
        print(f"\n✅ {total_created} parcelas criadas com sucesso!")
        print(f"📊 Distribuição:")
        print(f"   • Pagas: {total_created // 4}")
        print(f"   • Pendentes: {total_created * 3 // 4}")
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erro ao criar parcelas: {e}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 Seed de Parcelas - Coddfy Contracts Manager CCM")
    print("=" * 80)
    
    create_installments()
    
    print("\n" + "=" * 80)
    print("✅ Processo concluído!")
    print("=" * 80)

