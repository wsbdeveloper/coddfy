"""
Configurações da aplicação
Carrega variáveis de ambiente e define configurações globais
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega .env local apenas se existir; nunca sobrescreve variáveis já definidas (ex.: Docker)
_env_file = BASE_DIR / '.env'
if _env_file.exists():
    load_dotenv(_env_file, override=False)


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
    # Em produção, aceita domínios da Vercel e outros configurados
    default_cors = 'http://localhost:5173,http://localhost:3000'
    if os.getenv('APP_ENV') == 'production':
        # Adiciona padrões comuns da Vercel
        default_cors += ',https://*.vercel.app'
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', default_cors).split(',')
    
    @classmethod
    def is_development(cls):
        """Verifica se está em ambiente de desenvolvimento"""
        return cls.APP_ENV == 'development'
    
    @classmethod
    def is_production(cls):
        """Verifica se está em ambiente de produção"""
        return cls.APP_ENV == 'production'


config = Config()

