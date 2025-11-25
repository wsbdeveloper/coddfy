"""
View simples para o endpoint /api/docs
Redireciona para /api que tem a documentação completa
"""
from pyramid.view import view_config


@view_config(route_name='api_docs', renderer='json')
def api_docs(request):
    """
    GET /api/docs
    Documentação da API (redireciona para /api)
    """
    return {
        "message": "API Documentation",
        "note": "Para ver a documentação completa, acesse GET /api",
        "quick_links": {
            "docs": "/api",
            "dashboard": "/api/dashboard",
            "login": "/api/auth/login"
        }
    }

