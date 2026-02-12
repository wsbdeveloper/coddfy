"""
Views de Timesheets/Histórico de Faturamentos
Endpoints CRUD para gestão de timesheets
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response, FileResponse
from sqlalchemy.orm import joinedload
from backend.models import Timesheet, Contract, Consultant, Client
from backend.schemas import TimesheetSchema, TimesheetCreateSchema
from backend.auth_helpers import require_authenticated, can_access_resource, apply_partner_filter
from backend.storage import get_timesheet_file_path, save_timesheet_file
from backend.logging_config import log_exception
from marshmallow import ValidationError
import json
import uuid


@view_defaults(renderer='json')
class TimesheetViews:
    """Classe de views para gestão de timesheets"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession

    def _parse_uuid(self, value):
        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError:
                return None
        return None
    
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

    def _parse_timesheet_payload(self):
        file_upload = None
        if self.request.content_type and self.request.content_type.startswith('multipart/form-data'):
            payload = {k: v for k, v in self.request.POST.items() if k != 'timesheet_file'}
            file_upload = self.request.POST.get('timesheet_file')
        else:
            payload = self.request.json_body
        return payload, file_upload
    
    @view_config(route_name='timesheet', request_method='GET')
    def get_timesheet(self):
        """
        GET /api/timesheets/{id}
        Retorna detalhes de um timesheet específico
        
        Returns:
            Dados completos do timesheet
        """
        user = require_authenticated(self.request)
        
        timesheet_id = self._parse_uuid(self.request.matchdict.get('id'))
        if not timesheet_id:
            return Response(
                json.dumps({'error': 'ID de timesheet inválido'}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
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
            schema = TimesheetCreateSchema()
            payload, file_upload = self._parse_timesheet_payload()
            data = schema.load(payload)

            if file_upload is not None and hasattr(file_upload, 'file'):
                stored_name = save_timesheet_file(file_upload)
                data['file_url'] = stored_name
            
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
            
        except ValidationError as e:
            return Response(
                json.dumps({'error': 'Dados inválidos', 'details': e.messages}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
        except Exception as e:
            self.db.rollback()
            log_exception("failed to create timesheet", exc=e, context={'user_id': str(user.id)})
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
        
        timesheet_id = self._parse_uuid(self.request.matchdict.get('id'))
        if not timesheet_id:
            return Response(
                json.dumps({'error': 'ID de timesheet inválido'}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
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
            payload, file_upload = self._parse_timesheet_payload()
            schema = TimesheetCreateSchema(partial=True)
            data = schema.load(payload)

            if file_upload is not None and hasattr(file_upload, 'file'):
                stored_name = save_timesheet_file(file_upload)
                data['file_url'] = stored_name
            
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
            
        except ValidationError as e:
            return Response(
                json.dumps({'error': 'Dados inválidos', 'details': e.messages}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
        except Exception as e:
            self.db.rollback()
            log_exception("failed to update timesheet", exc=e, context={'user_id': str(user.id), 'timesheet_id': str(timesheet_id)})
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
        
        timesheet_id = self._parse_uuid(self.request.matchdict.get('id'))
        if not timesheet_id:
            return Response(
                json.dumps({'error': 'ID de timesheet inválido'}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
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
            log_exception("failed to delete timesheet", exc=e, context={'user_id': str(user.id), 'timesheet_id': str(timesheet_id)})
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                charset='utf-8',
                content_type='application/json'
            )

    @view_config(route_name='timesheet_file', request_method='GET')
    def download_timesheet(self):
        user = require_authenticated(self.request)
        timesheet_id = self._parse_uuid(self.request.matchdict.get('id'))
        if not timesheet_id:
            return Response(
                json.dumps({'error': 'ID de timesheet inválido'}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
        timesheet = self.db.query(Timesheet).options(
            joinedload(Timesheet.contract).joinedload(Contract.client)
        ).filter(
            Timesheet.id == timesheet_id
        ).first()

        if not timesheet or not timesheet.file_url:
            return Response(
                json.dumps({'error': 'Arquivo de timesheet não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )

        if user.role.value != 'admin_global':
            if not can_access_resource(user, timesheet.contract.client.partner_id):
                return Response(
                    json.dumps({'error': 'Você não tem permissão para acessar este arquivo'}).encode('utf-8'),
                    status=403,
                    content_type='application/json',
                    charset='utf-8'
                )

        file_path = get_timesheet_file_path(timesheet.file_url)
        if not file_path.exists():
            return Response(
                json.dumps({'error': 'Arquivo ausente no servidor'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )

        response = FileResponse(
            str(file_path),
            request=self.request,
            content_type='application/octet-stream'
        )
        response.headers['Content-Disposition'] = f'attachment; filename="{file_path.name}"'
        return response

