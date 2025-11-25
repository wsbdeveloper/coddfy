"""
View para health check
Usado por serviços de deploy para verificar se a aplicação está rodando
"""
from pyramid.view import view_config
from pyramid.response import Response


@view_config(route_name='health', renderer='json', request_method='GET')
def health_check(request):
    """
    Endpoint de health check
    Retorna status da aplicação
    """
    return {
        'status': 'ok',
        'service': 'portal-coddfy-backend',
        'version': '1.0.0'
    }

