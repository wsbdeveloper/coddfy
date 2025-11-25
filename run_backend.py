#!/usr/bin/env python
"""
Script simplificado para rodar o backend
Não usa PasteDeploy, roda direto com Waitress
"""
from waitress import serve
from backend.app import main

if __name__ == '__main__':
    # Configurações básicas
    settings = {
        'sqlalchemy.url': 'postgresql://ccm_user:ccm_password@localhost:5432/ccm_db',
        'jwt.secret': 'your-secret-key-change-in-production',
        'jwt.algorithm': 'HS256',
        'jwt.expiration': '86400',
        'cors.allow_origins': 'http://localhost:5173 http://localhost:3000',
    }
    
    print("=" * 80)
    print("🚀 Cursor Contracts Manager - Backend Server")
    print("=" * 80)
    print("📍 Servidor rodando em: http://0.0.0.0:6543")
    print("📚 API: http://0.0.0.0:6543/api")
    print("=" * 80)
    
    # Cria a aplicação
    app = main({}, **settings)
    
    # Inicia o servidor
    serve(app, listen='0.0.0.0:6543')

