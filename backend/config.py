"""
Configurações da aplicação
Carrega variáveis de ambiente e define configurações globais
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


class Config:
    """Classe de configuração da aplicação"""
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://ccm_user:ccm_password@localhost:5432/ccm_db')
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    
    # Application
    APP_ENV = os.getenv('APP_ENV', 'development')
    APP_HOST = os.getenv('APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('APP_PORT', 6543))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
    
    @classmethod
    def is_development(cls):
        """Verifica se está em ambiente de desenvolvimento"""
        return cls.APP_ENV == 'development'
    
    @classmethod
    def is_production(cls):
        """Verifica se está em ambiente de produção"""
        return cls.APP_ENV == 'production'


config = Config()

