"""
Views de Clientes
Endpoints CRUD para gestão de clientes
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from backend.models import Client
from backend.schemas import ClientSchema
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
        Lista todos os clientes
        
        Returns:
            Lista de clientes
        """
        clients = self.db.query(Client).order_by(Client.name).all()
        
        schema = ClientSchema(many=True)
        return {'clients': schema.dump(clients)}
    
    @view_config(route_name='client', request_method='GET')
    def get_client(self):
        """
        GET /api/clients/{id}
        Retorna detalhes de um cliente específico
        
        Returns:
            Dados do cliente
        """
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
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
        
        Returns:
            Dados do cliente criado
        """
        try:
            # Valida os dados de entrada
            schema = ClientSchema()
            data = schema.load(self.request.json_body)
            
            # Cria o cliente
            client = Client(name=data['name'])
            
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
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            
            if 'name' in data:
                client.name = data['name']
            
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
        client_id = self.request.matchdict['id']
        client = self.db.query(Client).filter(Client.id == client_id).first()
        
        if not client:
            return Response(
                json.dumps({'error': 'Cliente não encontrado'}).encode('utf-8'),
                status=404,
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


