"""
Script de dados de exemplo para desenvolvimento
Popula o banco com dados fictícios
Executa: poetry run python backend/scripts/seed_data.py
"""
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Client, Contract, Consultant, Installment, ContractStatus
from backend.config import config


def seed_data():
    """Popula o banco com dados de exemplo"""
    print("=" * 80)
    print("🌱 Populando banco de dados com dados de exemplo...")
    print("=" * 80)
    
    # Cria engine e sessão
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Limpa dados existentes (cuidado em produção!)
        print("🗑️  Limpando dados existentes...")
        session.query(Consultant).delete()
        session.query(Installment).delete()
        session.query(Contract).delete()
        session.query(Client).delete()
        session.commit()
        
        # Cria clientes
        print("👥 Criando clientes...")
        client1 = Client(name="Tech Solutions Ltda")
        client2 = Client(name="Inovação Digital S.A.")
        client3 = Client(name="Consultoria Estratégica")
        
        session.add_all([client1, client2, client3])
        session.flush()
        
        # Cria contratos
        print("📄 Criando contratos...")
        contract1 = Contract(
            name="Desenvolvimento Sistema ERP",
            client_id=client1.id,
            total_value=Decimal("500000.00"),
            billed_value=Decimal("350000.00"),
            balance=Decimal("150000.00"),
            status=ContractStatus.ATIVO,
            end_date=datetime.now() + timedelta(days=90)
        )
        
        contract2 = Contract(
            name="Modernização Infraestrutura",
            client_id=client2.id,
            total_value=Decimal("300000.00"),
            billed_value=Decimal("100000.00"),
            balance=Decimal("200000.00"),
            status=ContractStatus.ATIVO,
            end_date=datetime.now() + timedelta(days=120)
        )
        
        contract3 = Contract(
            name="Consultoria DevOps",
            client_id=client3.id,
            total_value=Decimal("150000.00"),
            billed_value=Decimal("150000.00"),
            balance=Decimal("0.00"),
            status=ContractStatus.INATIVO,
            end_date=datetime.now() - timedelta(days=30)
        )
        
        session.add_all([contract1, contract2, contract3])
        session.flush()
        
        # Cria parcelas para o contrato 1
        print("💰 Criando parcelas...")
        months = ["Jan/25", "Fev/25", "Mar/25", "Abr/25", "Mai/25"]
        for i, month in enumerate(months):
            installment = Installment(
                contract_id=contract1.id,
                month=month,
                value=Decimal("100000.00"),
                billed=i < 3  # Primeiras 3 parcelas faturadas
            )
            session.add(installment)
        
        # Cria consultores
        print("👨‍💼 Criando consultores...")
        consultants_data = [
            # Contrato 1
            {"name": "João Silva", "role": "Tech Lead", "contract_id": contract1.id, "feedback": 95},
            {"name": "Maria Santos", "role": "Desenvolvedor Senior", "contract_id": contract1.id, "feedback": 92},
            {"name": "Pedro Oliveira", "role": "Desenvolvedor Pleno", "contract_id": contract1.id, "feedback": 88},
            # Contrato 2
            {"name": "Ana Costa", "role": "Arquiteta de Soluções", "contract_id": contract2.id, "feedback": 96},
            {"name": "Carlos Mendes", "role": "Engenheiro DevOps", "contract_id": contract2.id, "feedback": 90},
            # Contrato 3
            {"name": "Beatriz Lima", "role": "Consultora DevOps", "contract_id": contract3.id, "feedback": 85},
        ]
        
        for data in consultants_data:
            consultant = Consultant(**data)
            session.add(consultant)
        
        # Commit de todas as mudanças
        session.commit()
        
        print("")
        print("✅ Dados de exemplo criados com sucesso!")
        print("")
        print(f"   Clientes criados: 3")
        print(f"   Contratos criados: 3")
        print(f"   Consultores criados: 6")
        print(f"   Parcelas criadas: 5")
        print("=" * 80)
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao criar dados: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        session.close()


if __name__ == '__main__':
    seed_data()

