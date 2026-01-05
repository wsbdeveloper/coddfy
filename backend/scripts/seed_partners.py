#!/usr/bin/env python
"""
Script para popular o banco com parceiros de exemplo e vincular dados existentes
Executa: poetry run python backend/scripts/seed_partners.py
"""
import sys
import os
from decimal import Decimal
from datetime import datetime, timedelta, timezone

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.models import Partner, Client, Consultant, User, UserRole, Contract
from backend.config import config


def seed_partners():
    """
    Cria parceiros de exemplo e vincula dados existentes
    """
    print("=== Iniciando seed de parceiros ===\n")
    
    # Cria engine e sessão
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 1. Buscar o parceiro padrão criado pela migration
        default_partner = session.query(Partner).filter_by(name="Parceiro Padrão").first()
        
        if default_partner:
            print(f"✓ Parceiro padrão encontrado: {default_partner.id}")
        else:
            print("⚠ Parceiro padrão não encontrado. Criando...")
            default_partner = Partner(name="Parceiro Padrão")
            session.add(default_partner)
            session.flush()
            print(f"✓ Parceiro padrão criado: {default_partner.id}")
        
        # 2. Criar parceiros adicionais
        partners_data = [
            {"name": "Robbin Consulting"},
            {"name": "TechCorp Solutions"},
            {"name": "Digital Partners"},
        ]
        
        partners = {}
        for data in partners_data:
            existing = session.query(Partner).filter_by(name=data['name']).first()
            if existing:
                print(f"  Parceiro '{data['name']}' já existe")
                partners[data['name']] = existing
            else:
                partner = Partner(**data)
                session.add(partner)
                session.flush()
                partners[data['name']] = partner
                print(f"✓ Parceiro criado: {data['name']} ({partner.id})")
        
        # 3. Criar usuários admin de parceiro
        robbin_partner = partners.get("Robbin Consulting")
        if robbin_partner:
            from backend.auth import AuthService
            import uuid as uuid_lib
            from datetime import datetime as dt
            
            # Criar admin do parceiro Robbin usando SQL direto para evitar problema de conversão do enum
            existing_admin = session.query(User).filter_by(username="admin_robbin").first()
            if not existing_admin:
                admin_id = uuid_lib.uuid4()
                admin_password_hash = AuthService.hash_password("robbin123")
                now = datetime.now(timezone.utc).replace(tzinfo=None)  # UTC sem timezone para compatibilidade
                
                session.execute(
                    text("""
                    INSERT INTO users (id, username, email, password_hash, role, partner_id, is_active, created_at, updated_at)
                    VALUES (:id, :username, :email, :password_hash, CAST(:role AS userrole), :partner_id, :is_active, :created_at, :updated_at)
                    """),
                    {
                        'id': admin_id,
                        'username': 'admin_robbin',
                        'email': 'admin@robbin.com',
                        'password_hash': admin_password_hash,
                        'role': 'admin_partner',
                        'partner_id': robbin_partner.id,
                        'is_active': True,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                print(f"✓ Admin do parceiro Robbin criado: admin_robbin / robbin123")
            else:
                print(f"  Admin do parceiro Robbin já existe")
            
            # Criar usuário comum do parceiro Robbin usando SQL direto
            existing_user = session.query(User).filter_by(username="user_robbin").first()
            if not existing_user:
                user_id = uuid_lib.uuid4()
                user_password_hash = AuthService.hash_password("robbin123")
                now = datetime.now(timezone.utc).replace(tzinfo=None)  # UTC sem timezone para compatibilidade
                
                session.execute(
                    text("""
                    INSERT INTO users (id, username, email, password_hash, role, partner_id, is_active, created_at, updated_at)
                    VALUES (:id, :username, :email, :password_hash, CAST(:role AS userrole), :partner_id, :is_active, :created_at, :updated_at)
                    """),
                    {
                        'id': user_id,
                        'username': 'user_robbin',
                        'email': 'user@robbin.com',
                        'password_hash': user_password_hash,
                        'role': 'user_partner',
                        'partner_id': robbin_partner.id,
                        'is_active': True,
                        'created_at': now,
                        'updated_at': now
                    }
                )
                print(f"✓ Usuário do parceiro Robbin criado: user_robbin / robbin123")
            else:
                print(f"  Usuário do parceiro Robbin já existe")
        
        # 4. Criar alguns clientes para o parceiro Robbin
        if robbin_partner:
            robbin_clients_data = [
                {"name": "Cliente Robbin A", "partner_id": robbin_partner.id},
                {"name": "Cliente Robbin B", "partner_id": robbin_partner.id},
            ]
            
            for client_data in robbin_clients_data:
                existing_client = session.query(Client).filter_by(
                    name=client_data['name'],
                    partner_id=client_data['partner_id']
                ).first()
                
                if not existing_client:
                    client = Client(**client_data)
                    session.add(client)
                    session.flush()
                    print(f"✓ Cliente criado para Robbin: {client_data['name']}")
                    
                    # Criar um contrato para o cliente
                    contract = Contract(
                        name=f"Contrato {client_data['name']}",
                        client_id=client.id,
                        total_value=Decimal("100000.00"),
                        billed_value=Decimal("0.00"),
                        balance=Decimal("100000.00"),
                        status="ativo",
                        end_date=datetime.utcnow() + timedelta(days=365)
                    )
                    session.add(contract)
                    session.flush()
                    print(f"  ✓ Contrato criado: {contract.name}")
                    
                    # Criar consultores para o contrato
                    consultant = Consultant(
                        name=f"Consultor {client_data['name']}",
                        role="Desenvolvedor Senior",
                        contract_id=contract.id,
                        partner_id=robbin_partner.id,
                        photo_url=None
                    )
                    session.add(consultant)
                    session.flush()
                    print(f"    ✓ Consultor criado: {consultant.name}")
                    
                    # Criar feedback com rating para o consultor
                    from backend.models import ConsultantFeedback
                    admin_user = session.query(User).filter_by(username="admin_robbin").first()
                    if admin_user:
                        feedback = ConsultantFeedback(
                            consultant_id=consultant.id,
                            user_id=admin_user.id,
                            contract_id=contract.id,
                            comment=f"Feedback inicial para {consultant.name}",
                            rating=85
                        )
                        session.add(feedback)
                        print(f"      ✓ Feedback criado com rating 85")
                else:
                    print(f"  Cliente '{client_data['name']}' já existe")
        
        # 5. Tornar o admin existente em admin_global usando SQL direto
        # Nota: Pulando por enquanto devido a problema de conversão do enum
        # O admin pode ser atualizado manualmente via SQL: 
        # UPDATE users SET role = 'admin_global'::userrole, partner_id = NULL WHERE username = 'admin';
        print(f"\n⚠ Nota: Se o usuário 'admin' existir, atualize manualmente para ADMIN_GLOBAL via SQL")
        
        session.commit()
        print("\n=== Seed de parceiros concluído com sucesso! ===\n")
        
        # Resumo
        print("📊 RESUMO:")
        print(f"  Total de parceiros: {session.query(Partner).count()}")
        print(f"  Total de clientes: {session.query(Client).count()}")
        print(f"  Total de consultores: {session.query(Consultant).count()}")
        print(f"  Total de usuários: {session.query(User).count()}")
        
        print("\n🔐 CREDENCIAIS DE ACESSO:")
        print("  Admin Global:")
        print("    Usuário: admin")
        print("    Senha: admin123")
        print("    Acesso: Todos os parceiros")
        print("\n  Admin Parceiro Robbin:")
        print("    Usuário: admin_robbin")
        print("    Senha: robbin123")
        print("    Acesso: Apenas dados do parceiro Robbin")
        print("\n  Usuário Parceiro Robbin:")
        print("    Usuário: user_robbin")
        print("    Senha: robbin123")
        print("    Acesso: Apenas dados do parceiro Robbin (sem gestão de usuários)")
    
    except Exception as e:
        session.rollback()
        print(f"\n❌ Erro ao executar seed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    try:
        seed_partners()
    except Exception as e:
        sys.exit(1)

