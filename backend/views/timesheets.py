"""
Views de Timesheets/Histórico de Faturamentos
Endpoints CRUD para gestão de timesheets
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.orm import joinedload
from backend.models import Timesheet, Contract, Consultant, Client
from backend.schemas import TimesheetSchema, TimesheetCreateSchema
from backend.auth_helpers import require_authenticated, can_access_resource, apply_partner_filter
import json


@view_defaults(renderer='json')
class TimesheetViews:
    """Classe de views para gestão de timesheets"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
    @view_config(route_name='timesheets', request_method='GET')
    def list_timesheets(self):
        """
        GET /api/timesheets
        Lista todos os timesheets com filtros opcionais
        
        Query params:
            - contract_id: Filtrar por contrato (UUID)
            - consultant_id: Filtrar por consultor (UUID)
        
        Returns:
            Lista de timesheets
        """
        user = require_authenticated(self.request)
        
        query = self.db.query(Timesheet).options(
            joinedload(Timesheet.contract).joinedload(Contract.client)
        )
        
        # Filtros opcionais
        contract_id = self.request.params.get('contract_id')
        if contract_id:
            query = query.filter(Timesheet.contract_id == contract_id)
        
        consultant_id = self.request.params.get('consultant_id')
        if consultant_id:
            query = query.filter(Timesheet.consultant_id == consultant_id)
        
        # Aplicar filtro por parceiro (usuários não-admin só veem timesheets dos seus contratos)
        if user.role.value != 'admin_global':
            query = query.join(Contract).join(Client)
            query = apply_partner_filter(query, Client, user)
        
        # Ordena por data de criação (mais recente primeiro)
        timesheets = query.order_by(Timesheet.created_at.desc()).all()
        
        # Serializa os dados
        schema = TimesheetSchema(many=True)
        return {'timesheets': schema.dump(timesheets)}
    
    @view_config(route_name='timesheet', request_method='GET')
    def get_timesheet(self):
        """
        GET /api/timesheets/{id}
        Retorna detalhes de um timesheet específico
        
        Returns:
            Dados completos do timesheet
        """
        user = require_authenticated(self.request)
        
        timesheet_id = self.request.matchdict['id']
        timesheet = self.db.query(Timesheet).options(
            joinedload(Timesheet.contract).joinedload(Contract.client)
        ).filter(
            Timesheet.id == timesheet_id
        ).first()
        
        if not timesheet:
            return Response(
                json.dumps({'error': 'Timesheet não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        # Verificar acesso (mesmo parceiro)
        if user.role.value != 'admin_global':
            if not can_access_resource(user, timesheet.contract.client.partner_id):
                return Response(
                    json.dumps({'error': 'Você não tem permissão para acessar este timesheet'}).encode('utf-8'),
                    status=403,
                    content_type='application/json',
                    charset='utf-8'
                )
        
        schema = TimesheetSchema()
        return schema.dump(timesheet)
    
    @view_config(route_name='timesheets', request_method='POST')
    def create_timesheet(self):
        """
        POST /api/timesheets
        Cria um novo timesheet
        
        Body:
            - contract_id: ID do contrato
            - consultant_id: ID do consultor (opcional)
            - file_url: URL do arquivo Excel
            - hours: Número de horas consumidas
            - approver: Nome do aprovador
            - approval_date: Data da aprovação
        
        Returns:
            Dados do timesheet criado
        """
        user = require_authenticated(self.request)
        
        try:
            # Valida os dados de entrada
            schema = TimesheetCreateSchema()
            data = schema.load(self.request.json_body)
            
            # Verifica se o contrato existe
            contract = self.db.query(Contract).options(
                joinedload(Contract.client)
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
            
            # Verificar acesso (mesmo parceiro)
            if user.role.value != 'admin_global':
                if not can_access_resource(user, contract.client.partner_id):
                    return Response(
                        json.dumps({'error': 'Você não tem permissão para criar timesheets para este contrato'}).encode('utf-8'),
                        status=403,
                        content_type='application/json',
                        charset='utf-8'
                    )
            
            # Se especificou consultor, verificar se existe e pertence ao contrato
            consultant_id = data.get('consultant_id')
            if consultant_id:
                consultant = self.db.query(Consultant).filter(
                    Consultant.id == consultant_id,
                    Consultant.contract_id == data['contract_id']
                ).first()
                
                if not consultant:
                    return Response(
                        json.dumps({'error': 'Consultor não encontrado ou não pertence a este contrato'}).encode('utf-8'),
                        status=400,
                        content_type='application/json',
                        charset='utf-8'
                    )
            
            # Cria o timesheet
            timesheet = Timesheet(
                contract_id=data['contract_id'],
                consultant_id=data.get('consultant_id'),
                file_url=data.get('file_url'),
                hours=data.get('hours') or 0,
                approver=data.get('approver'),
                approval_date=data.get('approval_date')
            )
            
            self.db.add(timesheet)
            self.db.flush()
            
            # Serializa os dados do timesheet
            result_schema = TimesheetSchema()
            timesheet_data = result_schema.dump(timesheet)
            
            return Response(
                json.dumps(timesheet_data).encode('utf-8'),
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
    
    @view_config(route_name='timesheet', request_method='PUT')
    def update_timesheet(self):
        """
        PUT /api/timesheets/{id}
        Atualiza um timesheet existente
        
        Body:
            Campos a serem atualizados
        
        Returns:
            Dados do timesheet atualizado
        """
        user = require_authenticated(self.request)
        
        timesheet_id = self.request.matchdict['id']
        timesheet = self.db.query(Timesheet).options(
            joinedload(Timesheet.contract).joinedload(Contract.client)
        ).filter(
            Timesheet.id == timesheet_id
        ).first()
        
        if not timesheet:
            return Response(
                json.dumps({'error': 'Timesheet não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        # Verificar acesso (mesmo parceiro)
        if user.role.value != 'admin_global':
            if not can_access_resource(user, timesheet.contract.client.partner_id):
                return Response(
                    json.dumps({'error': 'Você não tem permissão para atualizar este timesheet'}).encode('utf-8'),
                    status=403,
                    content_type='application/json',
                    charset='utf-8'
                )
        
        try:
            data = self.request.json_body
            
            # Atualiza campos permitidos
            if 'file_url' in data:
                timesheet.file_url = data['file_url']
            if 'hours' in data:
                timesheet.hours = data['hours'] or 0
            if 'approver' in data:
                timesheet.approver = data['approver']
            if 'approval_date' in data:
                timesheet.approval_date = data['approval_date']
            if 'consultant_id' in data:
                if data['consultant_id']:
                    consultant = self.db.query(Consultant).filter(
                        Consultant.id == data['consultant_id'],
                        Consultant.contract_id == timesheet.contract_id
                    ).first()
                    if not consultant:
                        return Response(
                            json.dumps({'error': 'Consultor não encontrado ou não pertence a este contrato'}).encode('utf-8'),
                            status=400,
                            content_type='application/json',
                            charset='utf-8'
                        )
                timesheet.consultant_id = data['consultant_id']
            
            self.db.flush()
            
            # Serializa os dados
            schema = TimesheetSchema()
            return schema.dump(timesheet)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='timesheet', request_method='DELETE')
    def delete_timesheet(self):
        """
        DELETE /api/timesheets/{id}
        Remove um timesheet
        
        Returns:
            Mensagem de confirmação
        """
        user = require_authenticated(self.request)
        
        timesheet_id = self.request.matchdict['id']
        timesheet = self.db.query(Timesheet).options(
            joinedload(Timesheet.contract).joinedload(Contract.client)
        ).filter(
            Timesheet.id == timesheet_id
        ).first()
        
        if not timesheet:
            return Response(
                json.dumps({'error': 'Timesheet não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        # Verificar acesso (mesmo parceiro)
        if user.role.value != 'admin_global':
            if not can_access_resource(user, timesheet.contract.client.partner_id):
                return Response(
                    json.dumps({'error': 'Você não tem permissão para deletar este timesheet'}).encode('utf-8'),
                    status=403,
                    content_type='application/json',
                    charset='utf-8'
                )
        
        try:
            self.db.delete(timesheet)
            return {'message': 'Timesheet removido com sucesso'}
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                charset='utf-8',
                content_type='application/json'
            )

