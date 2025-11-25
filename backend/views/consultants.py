"""
Views de Consultores
Endpoints CRUD para gestão de consultores
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy import func
from backend.models import Consultant, Contract
from backend.schemas import ConsultantSchema
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
        contract_id = self.request.params.get('contract_id')
        
        if contract_id:
            # Filtra por contrato específico
            contracts = self.db.query(Contract).filter(
                Contract.id == contract_id
            ).all()
        else:
            # Busca todos os contratos com consultores
            contracts = self.db.query(Contract).join(Consultant).distinct().all()
        
        # Organiza os dados por contrato
        result = []
        for contract in contracts:
            consultants = self.db.query(Consultant).filter(
                Consultant.contract_id == contract.id
            ).all()
            
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
            - feedback: Percentual de avaliação (0-100)
        
        Returns:
            Dados do consultor criado
        """
        try:
            # Valida os dados de entrada
            schema = ConsultantSchema()
            data = schema.load(self.request.json_body)
            
            # Verifica se o contrato existe
            contract = self.db.query(Contract).filter(
                Contract.id == data['contract_id']
            ).first()
            if not contract:
                return Response(
                    json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                    status=404,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Cria o consultor
            consultant = Consultant(
                name=data['name'],
                role=data['role'],
                contract_id=data['contract_id'],
                feedback=data['feedback']
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
            if 'feedback' in data:
                if 0 <= data['feedback'] <= 100:
                    consultant.feedback = data['feedback']
                else:
                    raise ValueError('Feedback deve estar entre 0 e 100')
            
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

