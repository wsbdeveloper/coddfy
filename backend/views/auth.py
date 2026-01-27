"""
Views de autenticação
Endpoints para login e gerenciamento de usuários
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from backend.models import User, UserRole
from backend.schemas import UserSchema, UserLoginSchema, UserCreateSchema
from backend.auth import AuthService
from backend.auth_helpers import require_admin_global
import json


@view_defaults(renderer='json')
class AuthViews:
    """Classe de views para autenticação"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
    @view_config(route_name='auth_login', request_method='POST')
    def login(self):
        """
        POST /api/auth/login
        Autentica um usuário e retorna um token JWT
        
        Body:
            - username: Nome de usuário
            - password: Senha
        
        Returns:
            - token: Token JWT
            - user: Dados do usuário
        """
        try:
            # Valida os dados de entrada
            schema = UserLoginSchema()
            data = schema.load(self.request.json_body)
            # Busca o usuário no banco
            user = self.db.query(User).filter(
                User.username == data['username']
            ).first()
            
            if not user or not user.is_active:
                return Response(
                    json.dumps({'error': 'Credenciais inválidas'}).encode('utf-8'),
                    status=401,
                    content_type='application/json; charset=utf-8'
                )
            
            # Verifica a senha
            if not AuthService.verify_password(data['password'], user.password_hash):
                return Response(
                    json.dumps({'error': 'Credenciais inválidas'}).encode('utf-8'),
                    status=401,
                    content_type='application/json; charset=utf-8'
                )
            
            # Cria o token
            token = AuthService.create_token(user)
            
            # Serializa os dados do usuário
            user_schema = UserSchema()
            user_data = user_schema.dump(user)
            return {
                'token': token,
                'user': user_data
            }
            
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json; charset=utf-8'
            )
    
    @view_config(route_name='auth_register', request_method='POST')
    def register(self):
        """
        POST /api/auth/register
        Registra um novo usuário
        
        Body:
            - username: Nome de usuário
            - email: Email
            - password: Senha
            - role: Role (opcional, padrão: leitura)
        
        Returns:
            - user: Dados do usuário criado
        """
        try:
            require_admin_global(self.request)
            # Valida os dados de entrada
            schema = UserCreateSchema()
            data = schema.load(self.request.json_body)
            
            # Cria o hash da senha
            password_hash = AuthService.hash_password(data['password'])
            
            role_input = data.get('role', UserRole.USER_PARTNER.value)
            if isinstance(role_input, str):
                role_input = role_input.lower()
            role_enum = UserRole(role_input)
            user = User(
                username=data['username'],
                email=data['email'],
                password_hash=password_hash,
                role=role_enum
            )
            
            self.db.add(user)
            self.db.flush()
            
            # Serializa os dados do usuário
            user_schema = UserSchema()
            user_data = user_schema.dump(user)
            
            return Response(
                json.dumps({'user': user_data}).encode('utf-8'),
                status=201,
                content_type='application/json; charset=utf-8'
            )
            
        except IntegrityError:
            self.db.rollback()
            return Response(
                json.dumps({'error': 'Usuário ou email já existe'}).encode('utf-8'),
                status=400,
                content_type='application/json; charset=utf-8'
            )
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json; charset=utf-8'
            )

    @view_config(route_name='auth_users', request_method='GET')
    def list_users(self):
        """
        GET /api/auth/users
        Lista todos os usuários (apenas admin global)
        """
        try:
            require_admin_global(self.request)
            schema = UserSchema(many=True)
            users = self.db.query(User).order_by(User.username).options(
                # garante partner carregado para exibir na listagem
                joinedload(User.partner)
            ).all()
            return {'users': schema.dump(users)}
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json; charset=utf-8'
            )

