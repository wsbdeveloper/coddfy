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
    config_uri = 'backend/development.ini'
    
    # Setup logging com base no arquivo de configuração
    setup_logging(config_uri)
    
    # Cria a aplicação Pyramid
    app = get_app(config_uri, 'main')
    
    # Inicia o servidor
    print("=" * 80)
    print("Cursor Contracts Manager - Backend Server")
    print("=" * 80)
    print("Servidor rodando em: http://0.0.0.0:6543")
    print("API Docs: http://0.0.0.0:6543/api/docs")
    print("=" * 80)
    
    serve(app, listen='0.0.0.0:6543')


if __name__ == '__main__':
    sys.exit(main())

