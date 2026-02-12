"""
Helpers de autorização para multi-tenancy
Funções para validar permissões e aplicar filtros automáticos por parceiro
"""
import uuid

from pyramid.httpexceptions import HTTPForbidden, HTTPUnauthorized
from sqlalchemy.orm import Query
from backend.models import UserRole, User, Partner


def get_current_user_from_request(request):
    """
    Extrai o usuário atual do request (definido pelo JWT)
    Retorna o objeto User ou None
    """
    # Decodificar JWT do header Authorization
    from backend.auth import AuthService
    
    auth_header = request.headers.get('Authorization')
    token = AuthService.get_token_from_header(auth_header)
    
    if not token:
        return None
    
    payload = AuthService.decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get('user_id')
    if not user_id:
        return None

    if isinstance(user_id, str):
        try:
            user_id = uuid.UUID(user_id)
        except ValueError:
            return None
    
    user = request.dbsession.query(User).filter_by(id=user_id).first()
    return user


def require_admin_global(request):
    """
    Verifica se o usuário é admin global
    Lança HTTPForbidden se não for
    """
    user = get_current_user_from_request(request)
    if not user or user.role != UserRole.ADMIN_GLOBAL:
        raise HTTPForbidden(
            json={'error': 'Acesso negado. Requer permissão de administrador global.'}
        )
    return user


def require_admin(request):
    """
    Verifica se o usuário é admin (global ou de parceiro)
    Lança HTTPForbidden se não for
    """
    user = get_current_user_from_request(request)
    if not user or user.role not in [UserRole.ADMIN_GLOBAL, UserRole.ADMIN_PARTNER]:
        raise HTTPForbidden(
            json={'error': 'Acesso negado. Requer permissão de administrador.'}
        )
    return user


def require_authenticated(request):
    """
    Verifica se o usuário está autenticado
    Lança HTTPUnauthorized se não estiver
    """
    user = get_current_user_from_request(request)
    if not user:
        raise HTTPUnauthorized(
            json={'error': 'Autenticação necessária.'}
        )
    return user


def apply_partner_filter(query: Query, model_class, user: User):
    """
    Aplica filtro automático de parceiro em uma query
    
    Args:
        query: Query do SQLAlchemy
        model_class: Classe do modelo que tem partner_id
        user: Usuário fazendo a requisição
    
    Returns:
        Query filtrada por parceiro (se necessário)
    
    Regras:
        - Admin global: vê tudo (sem filtro)
        - Admin de parceiro / Usuário comum: vê apenas seu parceiro
    """
    # Admin global vê tudo
    if user.role == UserRole.ADMIN_GLOBAL:
        return query
    
    # Outros usuários veem apenas dados do seu parceiro
    if not user.partner_id:
        # Usuário sem parceiro não deve ver nada
        return query.filter(model_class.id == None)  # Sempre falso
    
    return query.filter(model_class.partner_id == user.partner_id)


def can_create_partner_resource(user: User, resource_partner_id: str = None):
    """
    Verifica se o usuário pode criar um recurso para um parceiro específico
    
    Args:
        user: Usuário fazendo a requisição
        resource_partner_id: ID do parceiro do recurso (None para auto-detect)
    
    Returns:
        bool: True se pode criar
        
    Regras:
        - Admin global: pode criar para qualquer parceiro
        - Admin/usuário de parceiro: pode criar apenas para seu próprio parceiro
    """
    if user.role == UserRole.ADMIN_GLOBAL:
        return True
    
    # Se não especificou parceiro, usar o do usuário
    if not resource_partner_id:
        resource_partner_id = user.partner_id
    
    # Usuários de parceiro só podem criar para seu próprio parceiro
    return str(user.partner_id) == str(resource_partner_id)


def can_access_resource(user: User, resource_partner_id: str):
    """
    Verifica se o usuário pode acessar um recurso de um parceiro específico
    
    Args:
        user: Usuário fazendo a requisição
        resource_partner_id: ID do parceiro do recurso
    
    Returns:
        bool: True se pode acessar
        
    Regras:
        - Admin global: pode acessar qualquer recurso
        - Admin/usuário de parceiro: pode acessar apenas recursos do seu parceiro
    """
    if user.role == UserRole.ADMIN_GLOBAL:
        return True
    
    print(f"User: {user.partner_id}, Resource: {resource_partner_id}")
    return str(user.partner_id) == str(resource_partner_id)


def can_manage_users(user: User):
    """
    Verifica se o usuário pode gerenciar outros usuários
    
    Returns:
        bool: True se pode gerenciar
        
    Regras:
        - Admin global: pode gerenciar qualquer usuário
        - Admin de parceiro: pode gerenciar usuários do seu parceiro
        - Usuário comum: não pode gerenciar
    """
    return user.role in [UserRole.ADMIN_GLOBAL, UserRole.ADMIN_PARTNER]


def auto_assign_partner(user: User, data: dict):
    """
    Atribui automaticamente o partner_id aos dados se necessário
    
    Args:
        user: Usuário fazendo a requisição
        data: Dicionário com os dados (será modificado in-place)
    
    Returns:
        dict: Dados com partner_id atribuído
        
    Regras:
        - Admin global: usa o partner_id fornecido (se houver)
        - Admin/usuário de parceiro: força o uso do seu partner_id
    """
    if user.role == UserRole.ADMIN_GLOBAL:
        # Admin global pode especificar qualquer parceiro
        # Se não especificou, não força nada
        return data
    
    # Usuários de parceiro sempre usam seu próprio parceiro
    if user.partner_id:
        data['partner_id'] = user.partner_id
    return data



