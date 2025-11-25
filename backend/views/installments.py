"""
Views de Parcelas/Faturamento
Endpoints CRUD para gestão de parcelas de contratos
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy import func, Integer
from sqlalchemy.exc import IntegrityError
from backend.models import Installment, Contract, ContractStatus
from backend.schemas import InstallmentSchema
import json
from datetime import datetime


@view_defaults(renderer='json')
class InstallmentViews:
    """Classe de views para gestão de parcelas"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
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
        query = self.db.query(Installment).join(Contract)
        
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
        # Total faturado (parcelas pagas)
        total_billed = self.db.query(
            func.sum(Installment.value)
        ).filter(
            Installment.billed == True
        ).scalar() or 0
        
        # Total pendente (parcelas não pagas)
        total_pending = self.db.query(
            func.sum(Installment.value)
        ).filter(
            Installment.billed == False
        ).scalar() or 0
        
        # Total geral
        total = float(total_billed) + float(total_pending)
        
        # Contagem de parcelas
        count_billed = self.db.query(Installment).filter(
            Installment.billed == True
        ).count()
        
        count_pending = self.db.query(Installment).filter(
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
        ).filter(
            Contract.status == ContractStatus.ATIVO
        ).group_by(
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
        
        return {
            'total_billed': float(total_billed),
            'total_pending': float(total_pending),
            'total': total,
            'count_billed': count_billed,
            'count_pending': count_pending,
            'percentage_billed': (float(total_billed) / total * 100) if total > 0 else 0,
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
            
            # Cria a parcela
            installment = Installment(
                contract_id=data['contract_id'],
                month=data['month'],
                value=data['value'],
                billed=data.get('billed', False)
            )
            
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
        
        try:
            data = self.request.json_body
            
            # Atualiza campos permitidos
            if 'month' in data:
                installment.month = data['month']
            if 'value' in data:
                installment.value = data['value']
            if 'billed' in data:
                installment.billed = data['billed']
            
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

