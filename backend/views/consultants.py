"""
Views de Consultores
Endpoints CRUD para gestão de consultores
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from backend.models import Consultant, Contract, Partner, Client, UserRole, ConsultantFeedback
from backend.schemas import ConsultantSchema, ConsultantCreateSchema
from backend.auth_helpers import require_authenticated, auto_assign_partner, apply_partner_filter, can_access_resource
import json


@view_defaults(renderer='json')
class ConsultantViews:
    """Classe de views para gestão de consultores"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
    @view_config(route_name='consultants', request_method='GET')
    def list_consultants(self):
        """
        GET /api/consultants
        Lista todos os consultores agrupados por contrato
        
        Query params:
            - contract_id: Filtrar por contrato específico (UUID)
        
        Returns:
            Lista de contratos com seus consultores e estatísticas
        """
        user = require_authenticated(self.request)
        contract_id = self.request.params.get('contract_id')
        
        query = self.db.query(Contract).join(Client)
        if contract_id:
            query = query.filter(Contract.id == contract_id)
        else:
            query = query.join(Consultant).distinct()
        
        query = apply_partner_filter(query, Client, user)
        contracts = query.all()
        
        # Organiza os dados por contrato
        result = []
        for contract in contracts:
            consultants_query = self.db.query(Consultant).filter(
                Consultant.contract_id == contract.id
            )
            consultants_query = apply_partner_filter(consultants_query, Consultant, user)
            consultants = consultants_query.all()
            
            if not consultants:
                continue
            
            # Calcula estatísticas do grupo
            total_consultants = len(consultants)
            average_feedback = sum(c.feedback for c in consultants) / total_consultants if total_consultants > 0 else 0
            
            # Serializa consultores
            consultant_schema = ConsultantSchema(many=True)
            consultants_data = consultant_schema.dump(consultants)
            
            result.append({
                'contract_id': str(contract.id),
                'contract_name': contract.name,
                'client_name': contract.client.name,
                'total_consultants': total_consultants,
                'average_feedback': round(average_feedback, 2),
                'consultants': consultants_data
            })
        
        return {'groups': result}
    
    @view_config(route_name='consultant', request_method='GET')
    def get_consultant(self):
        """
        GET /api/consultants/{id}
        Retorna detalhes de um consultor específico
        
        Returns:
            Dados completos do consultor
        """
        user = require_authenticated(self.request)
        consultant_id = self.request.matchdict['id']
        consultant = self.db.query(Consultant).filter(
            Consultant.id == consultant_id
        ).first()
        
        if not consultant:
            return Response(
                json.dumps({'error': 'Consultor não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, consultant.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para acessar este consultor'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        schema = ConsultantSchema()
        return schema.dump(consultant)
    
    @view_config(route_name='consultants', request_method='POST')
    def create_consultant(self):
        """
        POST /api/consultants
        Cria um novo consultor
        
        Body:
            - name: Nome do consultor
            - role: Cargo
            - contract_id: ID do contrato
            - partner_id: ID do parceiro (opcional, será atribuído automaticamente)
            - feedback: Percentual de avaliação (0-100)
        
        Returns:
            Dados do consultor criado
        """
        try:
            user = require_authenticated(self.request)
            
            # Valida os dados de entrada
            schema = ConsultantCreateSchema()
            data = schema.load(self.request.json_body)
            
            # Verifica se o contrato existe (com eager loading do client e partner)
            contract = self.db.query(Contract).options(
                joinedload(Contract.client).joinedload(Client.partner)
            ).filter(
                Contract.id == data['contract_id']
            ).first()
            if not contract:
                return Response(
                    json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                    status=404,
                    content_type='application/json',
                    charset='utf-8'
                )

            # Se informou client_id, garantir que o contrato pertence ao cliente
            if data.get('client_id'):
                if str(contract.client_id) != str(data['client_id']):
                    return Response(
                        json.dumps({'error': 'Contrato não pertence ao cliente informado'}).encode('utf-8'),
                        status=400,
                        content_type='application/json',
                        charset='utf-8'
                    )
            
            # O partner_id do consultor deve ser o mesmo do cliente do contrato
            # Busca o cliente diretamente se necessário
            if not contract.client:
                client = self.db.query(Client).filter(Client.id == contract.client_id).first()
                if not client:
                    return Response(
                        json.dumps({'error': 'Cliente do contrato não encontrado'}).encode('utf-8'),
                        status=404,
                        content_type='application/json',
                        charset='utf-8'
                    )
                partner_id = client.partner_id
            else:
                partner_id = contract.client.partner_id
            
            # Se ainda não tem partner_id, retorna erro
            if not partner_id:
                return Response(
                    json.dumps({'error': 'O contrato não possui um parceiro associado. Não é possível criar o consultor.'}).encode('utf-8'),
                    status=400,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Para usuários não-admin, verifica se o partner_id corresponde ao do usuário
            if user.role != UserRole.ADMIN_GLOBAL:
                if user.partner_id != partner_id:
                    return Response(
                        json.dumps({'error': 'Você não tem permissão para criar consultores para este parceiro'}).encode('utf-8'),
                        status=403,
                        content_type='application/json',
                        charset='utf-8'
                    )
            
            # Se o usuário forneceu um partner_id diferente, valida (apenas para admin global)
            if data.get('partner_id') and user.role == UserRole.ADMIN_GLOBAL:
                # Admin global pode especificar um partner_id diferente, mas valida
                provided_partner_id = data.get('partner_id')
                if provided_partner_id != partner_id:
                    # Admin global pode forçar um partner_id diferente, mas avisa
                    partner_id = provided_partner_id
            
            # Verifica se o parceiro existe
            partner = self.db.query(Partner).filter(Partner.id == partner_id).first()
            if not partner:
                return Response(
                    json.dumps({'error': 'Parceiro não encontrado'}).encode('utf-8'),
                    status=404,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Cria o consultor (garantindo que partner_id não é None)
            consultant = Consultant(
                name=data['name'],
                role=data['role'],
                contract_id=data['contract_id'],
                partner_id=partner_id,  # Usa a variável garantida não-None
                photo_url=data.get('photo_url')
            )
            
            self.db.add(consultant)
            self.db.flush()
            
            # Serializa os dados do consultor
            result_schema = ConsultantSchema()
            consultant_data = result_schema.dump(consultant)
            
            return Response(
                json.dumps(consultant_data).encode('utf-8'),
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
    
    @view_config(route_name='consultant', request_method='PUT')
    def update_consultant(self):
        """
        PUT /api/consultants/{id}
        Atualiza um consultor existente
        
        Body:
            Campos a serem atualizados
        
        Returns:
            Dados do consultor atualizado
        """
        consultant_id = self.request.matchdict['id']
        consultant = self.db.query(Consultant).filter(
            Consultant.id == consultant_id
        ).first()
        
        if not consultant:
            return Response(
                json.dumps({'error': 'Consultor não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            
            # Atualiza campos permitidos
            if 'name' in data:
                consultant.name = data['name']
            if 'role' in data:
                consultant.role = data['role']
            if 'photo_url' in data:
                consultant.photo_url = data['photo_url']
            
            self.db.flush()
            
            # Serializa os dados
            schema = ConsultantSchema()
            return schema.dump(consultant)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='consultant', request_method='DELETE')
    def delete_consultant(self):
        """
        DELETE /api/consultants/{id}
        Remove um consultor
        
        Returns:
            Mensagem de confirmação
        """
        consultant_id = self.request.matchdict['id']
        consultant = self.db.query(Consultant).filter(
            Consultant.id == consultant_id
        ).first()
        
        if not consultant:
            return Response(
                json.dumps({'error': 'Consultor não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            self.db.delete(consultant)
            return {'message': 'Consultor removido com sucesso'}
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )

