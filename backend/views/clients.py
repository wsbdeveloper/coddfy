"""
Views de Clientes
Endpoints CRUD para gestão de clientes
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from backend.models import Client, Partner
from backend.schemas import ClientSchema, ClientCreateSchema
from backend.auth_helpers import require_authenticated, auto_assign_partner, apply_partner_filter, can_access_resource
import json


@view_defaults(renderer='json')
class ClientViews:
    """Classe de views para gestão de clientes"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
    @view_config(route_name='clients', request_method='GET')
    def list_clients(self):
        """
        GET /api/clients
        Lista todos os clientes (filtrados por parceiro se necessário)
        
        Returns:
            Lista de clientes com informações do parceiro
        """
        user = require_authenticated(self.request)
        query = self.db.query(Client).options(joinedload(Client.partner))
        
        # Aplica filtro de parceiro se necessário
        query = apply_partner_filter(query, Client, user)
        
        clients = query.order_by(Client.name).all()
        
        schema = ClientSchema(many=True)
        return {'clients': schema.dump(clients)}
    
    @view_config(route_name='client', request_method='GET')
    def get_client(self):
        """
        GET /api/clients/{id}
        Retorna detalhes de um cliente específico
        
        Returns:
            Dados do cliente com informações do parceiro
        """
        user = require_authenticated(self.request)
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).options(joinedload(Client.partner)).filter(
            Client.id == client_id
        ).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para acessar este cliente'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        schema = ClientSchema()
        return schema.dump(client)
    
    @view_config(route_name='clients', request_method='POST')
    def create_client(self):
        """
        POST /api/clients
        Cria um novo cliente
        
        Body:
            - name: Nome do cliente
            - partner_id: ID do parceiro (opcional)
            - partner: Nome do parceiro (opcional, alternativa ao partner_id)
        
        Returns:
            Dados do cliente criado
        """
        try:
            user = require_authenticated(self.request)
            
            # Valida os dados de entrada
            schema = ClientCreateSchema()
            data = schema.load(self.request.json_body)
            
            # Se forneceu nome do parceiro, busca o ID
            if 'partner' in data and data['partner']:
                partner = self.db.query(Partner).filter(Partner.name == data['partner']).first()
                if not partner:
                    return Response(
                        json.dumps({'error': f'Parceiro "{data["partner"]}" não encontrado'}).encode('utf-8'),
                        status=404,
                        content_type='application/json',
                        charset='utf-8'
                    )
                data['partner_id'] = partner.id
            
            # Atribui partner_id automaticamente baseado no usuário se não foi fornecido
            data = auto_assign_partner(user, data)
            
            # Verifica se o partner_id foi definido
            if not data.get('partner_id'):
                return Response(
                    json.dumps({'error': 'partner_id é obrigatório'}).encode('utf-8'),
                    status=400,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Verifica se o parceiro existe
            partner = self.db.query(Partner).filter(Partner.id == data['partner_id']).first()
            if not partner:
                return Response(
                    json.dumps({'error': 'Parceiro não encontrado'}).encode('utf-8'),
                    status=404,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Cria o cliente
            client = Client(
                name=data['name'],
                partner_id=data['partner_id'],
                cnpj=data.get('cnpj'),
                razao_social=data.get('razao_social')
            )
            
            self.db.add(client)
            self.db.flush()
            
            # Serializa os dados do cliente
            result_schema = ClientSchema()
            client_data = result_schema.dump(client)
            
            return Response(
                json.dumps(client_data).encode('utf-8'),
                status=201,
                content_type='application/json',
                charset='utf-8'
            )
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='client', request_method='PUT')
    def update_client(self):
        """
        PUT /api/clients/{id}
        Atualiza um cliente existente
        
        Body:
            - name: Novo nome do cliente
        
        Returns:
            Dados do cliente atualizado
        """
        user = require_authenticated(self.request)
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para atualizar este cliente'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            
            if 'name' in data:
                client.name = data['name']
            if 'cnpj' in data:
                client.cnpj = data['cnpj']
            if 'razao_social' in data:
                client.razao_social = data['razao_social']
            
            self.db.flush()
            
            schema = ClientSchema()
            return schema.dump(client)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='client', request_method='DELETE')
    def delete_client(self):
        """
        DELETE /api/clients/{id}
        Remove um cliente
        
        Returns:
            Mensagem de confirmação
        """
        user = require_authenticated(self.request)
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para deletar este cliente'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            # Verifica se tem contratos associados
            if client.contracts:
                return Response(
                    json.dumps({'error': 'Não é possível excluir cliente com contratos associados'}).encode('utf-8'),
                    status=400,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            self.db.delete(client)
            return {'message': 'Cliente removido com sucesso'}
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )


