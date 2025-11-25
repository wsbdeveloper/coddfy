"""
View de documentação da API
Endpoint que lista todas as rotas disponíveis
"""
from pyramid.view import view_config


@view_config(route_name='api_home', renderer='json')
def api_home(request):
    """
    GET /api
    Retorna informações sobre a API e rotas disponíveis
    """
    return {
        "name": "Cursor Contracts Manager API",
        "version": "1.0.0",
        "description": "API REST para gestão de contratos de consultoria",
        "endpoints": {
            "authentication": {
                "POST /api/auth/login": "Fazer login (retorna token JWT)",
                "POST /api/auth/register": "Registrar novo usuário"
            },
            "dashboard": {
                "GET /api/dashboard": "Obter estatísticas consolidadas do sistema"
            },
            "clients": {
                "GET /api/clients": "Listar todos os clientes",
                "POST /api/clients": "Criar novo cliente",
                "GET /api/clients/{id}": "Obter detalhes de um cliente",
                "PUT /api/clients/{id}": "Atualizar um cliente",
                "DELETE /api/clients/{id}": "Deletar um cliente"
            },
            "contracts": {
                "GET /api/contracts": "Listar contratos (aceita filtros: client_id, status, start_date, end_date)",
                "POST /api/contracts": "Criar novo contrato",
                "GET /api/contracts/{id}": "Obter detalhes de um contrato",
                "PUT /api/contracts/{id}": "Atualizar um contrato",
                "DELETE /api/contracts/{id}": "Deletar um contrato"
            },
            "consultants": {
                "GET /api/consultants": "Listar consultores agrupados por contrato (aceita filtro: contract_id)",
                "POST /api/consultants": "Criar novo consultor",
                "GET /api/consultants/{id}": "Obter detalhes de um consultor",
                "PUT /api/consultants/{id}": "Atualizar um consultor",
                "DELETE /api/consultants/{id}": "Deletar um consultor"
            }
        },
        "authentication": {
            "type": "JWT Bearer Token",
            "header": "Authorization: Bearer {token}",
            "how_to_get_token": "POST /api/auth/login with username and password"
        },
        "example_requests": {
            "login": {
                "url": "POST /api/auth/login",
                "body": {
                    "username": "admin",
                    "password": "admin123"
                },
                "response": {
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                    "user": {
                        "id": "uuid",
                        "username": "admin",
                        "email": "admin@coddfy.com",
                        "role": "admin"
                    }
                }
            },
            "get_dashboard": {
                "url": "GET /api/dashboard",
                "headers": {
                    "Authorization": "Bearer {your-token}"
                },
                "response": {
                    "stats": {
                        "active_contracts": 3,
                        "inactive_contracts": 1,
                        "allocated_consultants": 6,
                        "average_feedback": 91.5
                    }
                }
            }
        }
    }

