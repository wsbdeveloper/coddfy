"""
Script principal para executar a aplicação Pyramid
Uso: python -m backend
"""
import sys
from pyramid.paster import get_app, setup_logging
from waitress import serve


def main():
    """
    Função principal que inicializa e roda o servidor
    - Carrega as configurações do arquivo .ini
    - Configura os logs
    - Inicia o servidor WSGI com Waitress
    """
    import os
    
    # Determina qual arquivo de configuração usar
    app_env = os.getenv('APP_ENV', 'development')
    if app_env == 'production':
        config_uri = 'backend/production.ini'
    else:
        config_uri = 'backend/development.ini'
    
    # Setup logging com base no arquivo de configuração
    setup_logging(config_uri)
    
    # Cria a aplicação Pyramid
    app = get_app(config_uri, 'main')
    
    # Obtém host e porta das variáveis de ambiente
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 6543))
    
    # Inicia o servidor
    print("=" * 80)
    print("Coddfy Contracts Manager CCM - Backend Server")
    print("=" * 80)
    print(f"Environment: {app_env}")
    print(f"Servidor rodando em: http://{host}:{port}")
    print(f"API Docs: http://{host}:{port}/api/docs")
    print("=" * 80)
    
    serve(app, listen=f'{host}:{port}')


if __name__ == '__main__':
    sys.exit(main())

