"""
Views de Parcelas/Faturamento
Endpoints CRUD para gestão de parcelas de contratos
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy import func, Integer
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from backend.models import Installment, Contract, ContractStatus, Client, UserRole
from backend.auth_helpers import require_authenticated, apply_partner_filter, can_access_resource
from backend.schemas import InstallmentSchema
import json
from datetime import datetime


@view_defaults(renderer='json')
class InstallmentViews:
    """Classe de views para gestão de parcelas"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession

    def _apply_partner_filter(self, query, user):
        role_value = user.role.value if hasattr(user.role, "value") else user.role
        if role_value == UserRole.ADMIN_GLOBAL or role_value == 'admin_global':
            return query
        query = query.join(Contract).join(Client)
        return apply_partner_filter(query, Client, user)
    
    @view_config(route_name='installments', request_method='GET')
    def list_installments(self):
        """
        GET /api/installments
        Lista todas as parcelas com filtros opcionais
        
        Query params:
            - contract_id: Filtrar por contrato (UUID)
            - billed: Filtrar por status (true/false)
            - month: Filtrar por mês (ex: "Jan/25")
            - year: Filtrar por ano no mês (ex: "25" para 2025)
        
        Returns:
            Lista de parcelas com dados do contrato
        """
        user = require_authenticated(self.request)
        query = self.db.query(Installment).options(
            joinedload(Installment.contract)
        )
        
        # Filtros opcionais
        contract_id = self.request.params.get('contract_id')
        if contract_id:
            query = query.filter(Installment.contract_id == contract_id)
        
        billed = self.request.params.get('billed')
        if billed is not None:
            billed_bool = billed.lower() in ('true', '1', 'yes')
            query = query.filter(Installment.billed == billed_bool)
        
        month = self.request.params.get('month')
        if month:
            query = query.filter(Installment.month == month)
        
        year = self.request.params.get('year')
        if year:
            query = query.filter(Installment.month.like(f'%/{year}'))
        
        # Aplica filtro por parceiro (usuários não-admin só veem parcelas do seu parceiro)
        query = self._apply_partner_filter(query, user)
        
        # Ordena por mês (mais recente primeiro) e depois por criação
        installments = query.order_by(
            Installment.month.desc(),
            Installment.created_at.desc()
        ).all()
        
        # Serializa os dados
        schema = InstallmentSchema(many=True)
        return {'installments': schema.dump(installments)}
    
    @view_config(route_name='installments_summary', request_method='GET')
    def get_summary(self):
        """
        GET /api/installments/summary
        Retorna resumo financeiro das parcelas
        
        Returns:
            Estatísticas de faturamento
        """
        user = require_authenticated(self.request)
        
        # Total faturado (parcelas pagas)
        total_billed = self.db.query(
            func.sum(Installment.value)
        )
        total_billed = self._apply_partner_filter(total_billed, user).filter(
            Installment.billed == True
        ).scalar() or 0
        
        # Total pendente (parcelas não pagas)
        total_pending = self.db.query(
            func.sum(Installment.value)
        )
        total_pending = self._apply_partner_filter(total_pending, user).filter(
            Installment.billed == False
        ).scalar() or 0
        
        # Total geral
        total = float(total_billed) + float(total_pending)

        # Total inadimplente (parcelas com data prevista vencida e sem pagamento)
        today = datetime.utcnow()
        overdue_filter = (
            Installment.expected_payment_date.isnot(None),
            Installment.expected_payment_date < today,
            Installment.payment_date.is_(None)
        )

        total_overdue = self.db.query(
            func.sum(Installment.value)
        )
        total_overdue = self._apply_partner_filter(total_overdue, user).filter(
            *overdue_filter
        ).scalar() or 0

        count_overdue = self._apply_partner_filter(self.db.query(Installment), user).filter(
            *overdue_filter
        ).count()
        
        # Contagem de parcelas
        count_billed = self._apply_partner_filter(self.db.query(Installment), user).filter(
            Installment.billed == True
        ).count()
        
        count_pending = self._apply_partner_filter(self.db.query(Installment), user).filter(
            Installment.billed == False
        ).count()
        
        # Parcelas por contrato
        installments_by_contract = self.db.query(
            Contract.id,
            Contract.name,
            func.count(Installment.id).label('total_installments'),
            func.sum(Installment.value).label('total_value'),
            func.sum(
                func.cast(Installment.billed, Integer) * Installment.value
            ).label('billed_value')
        ).join(
            Installment, Contract.id == Installment.contract_id
        ).join(
            Client, Contract.client_id == Client.id
        ).filter(
            Contract.status == ContractStatus.ATIVO
        )
        installments_by_contract = apply_partner_filter(installments_by_contract, Client, user).group_by(
            Contract.id, Contract.name
        ).all()
        
        contracts_data = []
        for row in installments_by_contract:
            contracts_data.append({
                'contract_id': str(row.id),
                'contract_name': row.name,
                'total_installments': row.total_installments,
                'total_value': float(row.total_value or 0),
                'billed_value': float(row.billed_value or 0),
                'pending_value': float((row.total_value or 0) - (row.billed_value or 0))
            })

        overdue_rows = self.db.query(
            Contract.id.label('contract_id'),
            Contract.name.label('contract_name'),
            Client.id.label('client_id'),
            Client.name.label('client_name'),
            func.count(Installment.id).label('overdue_installments'),
            func.sum(Installment.value).label('overdue_value')
        ).join(
            Installment, Contract.id == Installment.contract_id
        ).join(
            Client, Contract.client_id == Client.id
        ).filter(
            *overdue_filter
        )
        overdue_rows = apply_partner_filter(overdue_rows, Client, user).group_by(
            Contract.id, Contract.name, Client.id, Client.name
        ).order_by(
            Client.name, Contract.name
        ).all()

        overdue_contracts = []
        for row in overdue_rows:
            overdue_contracts.append({
                'client_id': str(row.client_id),
                'client_name': row.client_name,
                'contract_id': str(row.contract_id),
                'contract_name': row.contract_name,
                'overdue_installments': row.overdue_installments,
                'overdue_value': float(row.overdue_value or 0)
            })
        
        return {
            'total_billed': float(total_billed),
            'total_pending': float(total_pending),
            'total': total,
            'count_billed': count_billed,
            'count_pending': count_pending,
            'percentage_billed': (float(total_billed) / total * 100) if total > 0 else 0,
            'total_overdue': float(total_overdue),
            'count_overdue': count_overdue,
            'overdue_contracts': overdue_contracts,
            'contracts': contracts_data
        }
    
    @view_config(route_name='installment', request_method='GET')
    def get_installment(self):
        """
        GET /api/installments/{id}
        Retorna detalhes de uma parcela específica
        
        Returns:
            Dados da parcela com informações do contrato
        """
        user = require_authenticated(self.request)
        installment_id = self.request.matchdict['id']
        installment = self.db.query(Installment).options(
            joinedload(Installment.contract)
        ).filter(
            Installment.id == installment_id
        ).first()
        
        if not installment:
            return Response(
                json.dumps({'error': 'Parcela não encontrada'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, installment.contract.client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para acessar esta parcela'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        schema = InstallmentSchema()
        return schema.dump(installment)
    
    @view_config(route_name='installments', request_method='POST')
    def create_installment(self):
        """
        POST /api/installments
        Cria uma nova parcela
        
        Body:
            {
                "contract_id": "uuid",
                "month": "Jan/25",
                "value": 10000.00,
                "billed": false
            }
        
        Returns:
            Dados da parcela criada
        """
        try:
            user = require_authenticated(self.request)
            data = self.request.json_body
            
            # Valida se o contrato existe
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
            
            if not can_access_resource(user, contract.client.partner_id):
                return Response(
                    json.dumps({'error': 'Você não tem permissão para criar parcelas para este contrato'}).encode('utf-8'),
                    status=403,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            # Cria a parcela
            installment = Installment(
                contract_id=data['contract_id'],
                month=data['month'],
                value=data['value'],
                billed=False,
                invoice_number=data.get('invoice_number'),
                billing_date=data.get('billing_date'),
                payment_term=data.get('payment_term'),
                expected_payment_date=data.get('expected_payment_date'),
                payment_date=data.get('payment_date')
            )
            
            # Associa o contrato diretamente para garantir o relacionamento
            installment.contract = contract
            
            self.db.add(installment)
            self.db.flush()
            
            # Atualiza o billed_value e balance do contrato
            self._update_contract_billed_value(contract)
            
            # Serializa os dados da parcela
            result_schema = InstallmentSchema()
            installment_data = result_schema.dump(installment)
            
            return Response(
                json.dumps(installment_data).encode('utf-8'),
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
    
    @view_config(route_name='installment_mark_billed', request_method='PATCH')
    def mark_as_billed(self):
        """
        PATCH /api/installments/{id}/mark-billed
        Marca uma parcela como faturada/paga
        
        Body:
            {
                "billed": true
            }
        
        Returns:
            Dados da parcela atualizada
        """
        user = require_authenticated(self.request)
        installment_id = self.request.matchdict['id']
        installment = self.db.query(Installment).options(
            joinedload(Installment.contract)
        ).filter(
            Installment.id == installment_id
        ).first()
        
        if not installment:
            return Response(
                json.dumps({'error': 'Parcela não encontrada'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, installment.contract.client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para atualizar esta parcela'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            installment.billed = data.get('billed', True)
            
            self.db.flush()
            
            # Atualiza o billed_value e balance do contrato
            self._update_contract_billed_value(installment.contract)
            
            # Serializa os dados
            schema = InstallmentSchema()
            return schema.dump(installment)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='installment', request_method='PUT')
    def update_installment(self):
        """
        PUT /api/installments/{id}
        Atualiza uma parcela existente
        
        Body:
            Campos a serem atualizados
        
        Returns:
            Dados da parcela atualizada
        """
        user = require_authenticated(self.request)
        installment_id = self.request.matchdict['id']
        installment = self.db.query(Installment).options(
            joinedload(Installment.contract)
        ).filter(
            Installment.id == installment_id
        ).first()
        
        if not installment:
            return Response(
                json.dumps({'error': 'Parcela não encontrada'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, installment.contract.client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para atualizar esta parcela'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            
            # Atualiza campos permitidos
            if 'month' in data:
                installment.month = data['month']
            if 'value' in data:
                installment.value = data['value']
            if 'billed' in data:
                installment.billed = data['billed']
            if 'invoice_number' in data:
                installment.invoice_number = data['invoice_number']
            if 'billing_date' in data:
                installment.billing_date = data['billing_date']
            if 'payment_term' in data:
                installment.payment_term = data['payment_term']
            if 'expected_payment_date' in data:
                installment.expected_payment_date = data['expected_payment_date']
            if 'payment_date' in data:
                installment.payment_date = data['payment_date']
            
            self.db.flush()
            
            # Atualiza o billed_value e balance do contrato
            self._update_contract_billed_value(installment.contract)
            
            # Serializa os dados
            schema = InstallmentSchema()
            return schema.dump(installment)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='installment', request_method='DELETE')
    def delete_installment(self):
        """
        DELETE /api/installments/{id}
        Remove uma parcela
        
        Returns:
            Mensagem de confirmação
        """
        user = require_authenticated(self.request)
        installment_id = self.request.matchdict['id']
        installment = self.db.query(Installment).filter(
            Installment.id == installment_id
        ).first()
        
        if not installment:
            return Response(
                json.dumps({'error': 'Parcela não encontrada'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        if not can_access_resource(user, installment.contract.client.partner_id):
            return Response(
                json.dumps({'error': 'Você não tem permissão para deletar esta parcela'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            contract = installment.contract
            self.db.delete(installment)
            self.db.flush()
            
            # Atualiza o billed_value e balance do contrato
            self._update_contract_billed_value(contract)
            
            return {'message': 'Parcela removida com sucesso'}
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                charset='utf-8',
                content_type='application/json'
            )
    
    def _update_contract_billed_value(self, contract):
        """
        Método auxiliar para atualizar o valor faturado do contrato
        Soma todas as parcelas marcadas como 'billed=True'
        """
        total_billed = self.db.query(
            func.sum(Installment.value)
        ).filter(
            Installment.contract_id == contract.id,
            Installment.billed == True
        ).scalar() or 0
        
        contract.billed_value = total_billed
        contract.balance = contract.total_value - contract.billed_value

