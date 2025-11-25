"""
Serviços de autenticação JWT
Gerencia tokens, hash de senhas e permissões
"""
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from backend.config import config
from backend.models import User, UserRole


class AuthService:
    """Serviço de autenticação com JWT"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Gera hash bcrypt da senha
        
        Args:
            password: Senha em texto plano
            
        Returns:
            Hash da senha
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        
        Args:
            password: Senha em texto plano
            password_hash: Hash da senha armazenado
            
        Returns:
            True se a senha está correta, False caso contrário
        """
        password_bytes = password.encode('utf-8')
        password_hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, password_hash_bytes)
    
    @staticmethod
    def create_token(user: User) -> str:
        """
        Cria um token JWT para o usuário
        
        Args:
            user: Objeto User do banco de dados
            
        Returns:
            Token JWT em string
        """
        expiration = datetime.utcnow() + timedelta(hours=config.JWT_EXPIRATION_HOURS)
        
        payload = {
            'user_id': str(user.id),
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'exp': expiration,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            config.JWT_SECRET,
            algorithm=config.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict]:
        """
        Decodifica e valida um token JWT
        
        Args:
            token: Token JWT em string
            
        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(
                token,
                config.JWT_SECRET,
                algorithms=[config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            # Token expirado
            return None
        except jwt.InvalidTokenError:
            # Token inválido
            return None
    
    @staticmethod
    def get_token_from_header(authorization_header: str) -> Optional[str]:
        """
        Extrai o token do header Authorization
        
        Args:
            authorization_header: Valor do header Authorization
            
        Returns:
            Token se presente, None caso contrário
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    @staticmethod
    def check_permission(user_role: str, required_role: UserRole) -> bool:
        """
        Verifica se o usuário tem permissão baseado no role
        
        Args:
            user_role: Role do usuário
            required_role: Role mínimo necessário
            
        Returns:
            True se tem permissão, False caso contrário
        """
        role_hierarchy = {
            UserRole.LEITURA: 1,
            UserRole.GESTOR: 2,
            UserRole.ADMIN: 3
        }
        
        user_level = role_hierarchy.get(UserRole(user_role), 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level


# Função auxiliar para extrair informações do usuário do request
def get_user_from_request(request):
    """
    Extrai e valida o usuário do token no request
    
    Args:
        request: Request do Pyramid
        
    Returns:
        Dicionário com dados do usuário ou None
    """
    auth_header = request.headers.get('Authorization')
    token = AuthService.get_token_from_header(auth_header)
    
    if not token:
        return None
    
    payload = AuthService.decode_token(token)
    return payload















