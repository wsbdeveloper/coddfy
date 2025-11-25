"""
Script para criar usuário administrador padrão
Executa: poetry run python backend/scripts/create_admin.py
"""
import sys
import os

# Adiciona o diretório raiz do projeto ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import User, UserRole, Base
from backend.auth import AuthService
from backend.config import config


def create_admin():
    """
    Cria um usuário administrador padrão
    Username: admin
    Password: admin123
    """
    print("=" * 80)
    print("👤 Criando usuário administrador...")
    print("=" * 80)
    
    # Cria engine e sessão
    engine = create_engine(config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Verifica se já existe um usuário admin
        existing_admin = session.query(User).filter(User.username == 'admin').first()
        
        if existing_admin:
            print("⚠️  Usuário 'admin' já existe no banco de dados.")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role.value}")
            return
        
        # Cria o hash da senha
        password_hash = AuthService.hash_password('admin123')
        
        # Cria o usuário admin
        admin_user = User(
            username='admin',
            email='admin@coddfy.com',
            password_hash=password_hash,
            role=UserRole.ADMIN,
            is_active=True
        )
        
        session.add(admin_user)
        session.commit()
        
        print("✅ Usuário administrador criado com sucesso!")
        print("")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Email: admin@coddfy.com")
        print("   Role: ADMIN")
        print("")
        print("⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")
        print("=" * 80)
        
    except Exception as e:
        session.rollback()
        print(f"❌ Erro ao criar usuário: {str(e)}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == '__main__':
    create_admin()

