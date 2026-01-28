"""
Script principal para executar a aplicação Pyramid
Uso: python -m backend
"""
import sys
import os
from pathlib import Path
from pyramid.paster import get_app, setup_logging
from waitress import serve
from backend.logging_config import bootstrap_logging


def get_config_file():
    """
    Determina qual arquivo de configuração usar baseado no ambiente e diretório atual.
    
    No Render: executamos 'cd backend && python -m backend', então estamos em backend/
    Em desenvolvimento: podemos estar na raiz do projeto
    """
    app_env = os.getenv('APP_ENV', 'development')
    current_dir = Path.cwd()
    script_dir = Path(__file__).parent
    
    # Nome do arquivo baseado no ambiente
    config_name = 'production.ini' if app_env == 'production' else 'development.ini'
    
    # Tenta encontrar o arquivo .ini
    # 1. No diretório atual (Render: dentro de backend/)
    if (current_dir / config_name).exists():
        return str(current_dir / config_name)
    
    # 2. No diretório do script (sempre funciona)
    if (script_dir / config_name).exists():
        return str(script_dir / config_name)
    
    # 3. Fallback: tentar com backend/ (desenvolvimento local)
    return f'backend/{config_name}'


def main():
    """
    Função principal que inicializa e roda o servidor.
    """
    # Encontra o arquivo de configuração
    config_uri = get_config_file()
    
    # Configura logging
    setup_logging(config_uri)
    bootstrap_logging()
    
    # Cria a aplicação Pyramid
    # O app.py vai sobrescrever as configurações com variáveis de ambiente
    app = get_app(config_uri, 'main')
    
    # Obtém host e porta
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 6543))
    
    # Inicia o servidor
    app_env = os.getenv('APP_ENV', 'development')
    print("=" * 80)
    print("Coddfy Contracts Manager CCM - Backend Server")
    print("=" * 80)
    print(f"Environment: {app_env}")
    print(f"Config file: {config_uri}")
    print(f"Servidor rodando em: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/api/docs")
    print("=" * 80)
    
    serve(app, listen=f'{host}:{port}')


if __name__ == '__main__':
    sys.exit(main())

