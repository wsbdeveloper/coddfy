"""
Aplicação principal do Pyramid
Configura e inicializa a aplicação
"""
from pyramid.config import Configurator
from pyramid.renderers import JSON
import transaction
import decimal
import uuid
import os
    
from datetime import datetime
from backend.config import config as app_config


def decimal_adapter(obj, request):
    """Adapter para serializar Decimal em JSON"""
    return float(obj)


def uuid_adapter(obj, request):
    """Adapter para serializar UUID em JSON"""
    return str(obj)


def datetime_adapter(obj, request):
    """Adapter para serializar datetime em JSON"""
    return obj.isoformat()


def main(global_config, **settings):
    """
    Função principal que cria e configura a aplicação Pyramid.
    
    As configurações vêm do arquivo .ini, mas são sobrescritas por variáveis de ambiente.
    
    Args:
        global_config: Configuração global do PasteDeploy
        **settings: Configurações do arquivo .ini
    
    Returns:
        Aplicação WSGI configurada
    """
    # Sobrescreve settings com variáveis de ambiente (se existirem)
    # Isso permite que o .ini tenha valores padrão, mas o ambiente tenha prioridade
    
    # Database URL - prioridade: variável de ambiente > .ini
    if os.getenv('DATABASE_URL'):
        settings['sqlalchemy.url'] = os.getenv('DATABASE_URL')
    elif 'sqlalchemy.url' not in settings:
        # Fallback para config.py se não estiver em nenhum lugar
        settings['sqlalchemy.url'] = app_config.DATABASE_URL
    
    # JWT Secret - prioridade: variável de ambiente > .ini
    if os.getenv('JWT_SECRET'):
        settings['jwt.secret'] = os.getenv('JWT_SECRET')
    elif 'jwt.secret' not in settings or settings.get('jwt.secret') == 'your-secret-key-change-in-production':
        settings['jwt.secret'] = app_config.JWT_SECRET
    
    # JWT Algorithm
    if os.getenv('JWT_ALGORITHM'):
        settings['jwt.algorithm'] = os.getenv('JWT_ALGORITHM')
    elif 'jwt.algorithm' not in settings:
        settings['jwt.algorithm'] = app_config.JWT_ALGORITHM
    
    # JWT Expiration
    if os.getenv('JWT_EXPIRATION_HOURS'):
        hours = int(os.getenv('JWT_EXPIRATION_HOURS'))
        settings['jwt.expiration'] = str(hours * 3600)
    elif 'jwt.expiration' not in settings:
        settings['jwt.expiration'] = str(app_config.JWT_EXPIRATION_HOURS * 3600)
    
    # CORS Origins - prioridade: variável de ambiente > .ini
    if os.getenv('CORS_ORIGINS'):
        # CORS_ORIGINS pode vir separado por vírgula, converter para espaço (formato do Pyramid)
        cors_origins = os.getenv('CORS_ORIGINS').replace(',', ' ')
        settings['cors.allow_origins'] = cors_origins
    elif 'cors.allow_origins' not in settings:
        settings['cors.allow_origins'] = ' '.join(app_config.CORS_ORIGINS)
    
    config = Configurator(settings=settings)
    
    # Configura o JSON renderer com adapters customizados
    json_renderer = JSON()
    json_renderer.add_adapter(decimal.Decimal, decimal_adapter)
    json_renderer.add_adapter(uuid.UUID, uuid_adapter)
    json_renderer.add_adapter(datetime, datetime_adapter)
    config.add_renderer('json', json_renderer)
    
    # Inclui o gerenciamento de transações
    config.include('pyramid_tm')
    
    # Inclui configuração do banco de dados
    config.include('.database')
    
    # Inclui as rotas
    config.include('.routes')
    
    # Configura CORS - Handler para preflight requests
    from pyramid.response import Response
    
    def get_allowed_origins():
        """Retorna lista de origens permitidas"""
        origins_str = config.registry.settings.get('cors.allow_origins', '')
        if origins_str:
            return [o.strip() for o in origins_str.split() if o.strip()]
        return []
    
    def is_origin_allowed(origin):
        """Verifica se a origem está permitida"""
        if not origin:
            return False
        allowed_origins = get_allowed_origins()
        
        # Verifica correspondência exata
        if origin in allowed_origins or '*' in allowed_origins:
            return True
        
        # Verifica padrões com wildcard (ex: *.vercel.app)
        import fnmatch
        for pattern in allowed_origins:
            if '*' in pattern and fnmatch.fnmatch(origin, pattern):
                return True
        
        return False
    
    def cors_preflight_handler(request):
        """Handler para requisições OPTIONS (CORS preflight)"""
        origin = request.headers.get('Origin')
        
        # Verifica se a origem está permitida
        if is_origin_allowed(origin):
            response = Response()
            response.status_code = 200
            response.headers.update({
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600'
            })
            return response
        else:
            response = Response()
            response.status_code = 403
            return response
    
    # Adiciona view para OPTIONS em todas as rotas da API
    config.add_view(
        cors_preflight_handler,
        route_name='api_home',
        request_method='OPTIONS'
    )
    
    # Adiciona view global para OPTIONS
    config.add_notfound_view(
        cors_preflight_handler,
        request_method='OPTIONS'
    )
    
    # Adiciona subscriber para adicionar headers CORS em todas as respostas
    def add_cors_headers(event):
        """Adiciona headers CORS em todas as respostas"""
        request = event.request
        response = event.response
        
        origin = request.headers.get('Origin')
        
        # Sempre adiciona headers CORS se a origem estiver permitida
        if is_origin_allowed(origin):
            response.headers.update({
                'Access-Control-Allow-Origin': origin,
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            })
    
    config.add_subscriber(add_cors_headers, 'pyramid.events.NewResponse')
    
    # Adicionar subscriber para decodificar JWT e adicionar ao request
    def add_jwt_to_request(event):
        """Adiciona informações do JWT ao request"""
        request = event.request
        from backend.auth import AuthService
        
        auth_header = request.headers.get('Authorization')
        token = AuthService.get_token_from_header(auth_header)
        
        if token:
            payload = AuthService.decode_token(token)
            if payload:
                # Adiciona os claims do JWT ao request
                request.jwt_claims = payload
            else:
                request.jwt_claims = {}
        else:
            request.jwt_claims = {}
    
    config.add_subscriber(add_jwt_to_request, 'pyramid.events.NewRequest')
    
    # Scan para encontrar views decoradas
    config.scan('.views')
    
    return config.make_wsgi_app()

