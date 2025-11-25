"""
Configuração de rotas da aplicação
Define todos os endpoints da API
"""


def includeme(config):
    """
    Inclui as rotas na configuração do Pyramid
    
    Args:
        config: Configurator do Pyramid
    """
    # Prefixo da API
    config.add_route('api_home', '/api')
    config.add_route('api_docs', '/api/docs')
    
    # Swagger/OpenAPI
    config.add_route('swagger_ui', '/api/docs/swagger')
    config.add_route('openapi_spec', '/api/openapi.yaml')
    
    # Rotas de autenticação
    config.add_route('auth_login', '/api/auth/login')
    config.add_route('auth_register', '/api/auth/register')
    
    # Rotas do dashboard
    config.add_route('dashboard', '/api/dashboard')
    
    # Rotas de clientes
    config.add_route('clients', '/api/clients')
    config.add_route('client', '/api/clients/{id}')
    
    # Rotas de contratos
    config.add_route('contracts', '/api/contracts')
    config.add_route('contract', '/api/contracts/{id}')
    
    # Rotas de consultores
    config.add_route('consultants', '/api/consultants')
    config.add_route('consultant', '/api/consultants/{id}')
    
    # Rotas de parcelas/faturamento
    config.add_route('installments', '/api/installments')
    config.add_route('installments_summary', '/api/installments/summary')
    config.add_route('installment', '/api/installments/{id}')
    config.add_route('installment_mark_billed', '/api/installments/{id}/mark-billed')
    
    # Rotas de parceiros (apenas admin global)
    config.add_route('partners', '/api/partners')
    config.add_route('partner', '/api/partners/{id}')
    
    # Rotas de feedbacks de consultores
    config.add_route('feedbacks', '/api/feedbacks')
    config.add_route('feedback', '/api/feedbacks/{id}')

