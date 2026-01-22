"""
Views de Contratos
Endpoints CRUD para gestão de contratos
"""
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from backend.models import Contract, Client, Installment, ContractStatus
from backend.schemas import ContractSchema, ContractCreateSchema
import json
from datetime import datetime


@view_defaults(renderer='json')
class ContractViews:
    """Classe de views para gestão de contratos"""
    
    def __init__(self, request):
        self.request = request
        self.db = request.dbsession
    
    @view_config(route_name='contracts', request_method='GET')
    def list_contracts(self):
        """
        GET /api/contracts
        Lista todos os contratos com filtros opcionais
        
        Query params:
            - client_id: Filtrar por cliente (UUID)
            - status: Filtrar por status (ativo, inativo, a_vencer)
            - start_date: Data inicial do período
            - end_date: Data final do período
        
        Returns:
            Lista de contratos com dados relacionados
        """
        query = self.db.query(Contract)
        
        # Filtros opcionais
        client_id = self.request.params.get('client_id')
        if client_id:
            query = query.filter(Contract.client_id == client_id)
        
        status = self.request.params.get('status')
        if status:
            try:
                query = query.filter(Contract.status == ContractStatus(status))
            except ValueError:
                pass
        
        start_date = self.request.params.get('start_date')
        if start_date:
            try:
                start = datetime.fromisoformat(start_date)
                query = query.filter(Contract.end_date >= start)
            except ValueError:
                pass
        
        end_date = self.request.params.get('end_date')
        if end_date:
            try:
                end = datetime.fromisoformat(end_date)
                query = query.filter(Contract.end_date <= end)
            except ValueError:
                pass
        
        # Ordena por data de criação
        contracts = query.order_by(Contract.created_at.desc()).all()
        
        # Serializa os dados
        schema = ContractSchema(many=True)
        return {'contracts': schema.dump(contracts)}
    
    @view_config(route_name='contract', request_method='GET')
    def get_contract(self):
        """
        GET /api/contracts/{id}
        Retorna detalhes de um contrato específico
        
        Returns:
            Dados completos do contrato incluindo parcelas e consultores
        """
        contract_id = self.request.matchdict['id']
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        
        if not contract:
            return Response(
                json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        schema = ContractSchema()
        return schema.dump(contract)
    
    @view_config(route_name='contracts', request_method='POST')
    def create_contract(self):
        """
        POST /api/contracts
        Cria um novo contrato
        
        Body:
            - name: Nome do contrato
            - client_id: ID do cliente
            - total_value: Valor total
            - status: Status (opcional)
            - end_date: Data de vencimento
        
        Returns:
            Dados do contrato criado
        """
        try:
            # Valida os dados de entrada
            schema = ContractCreateSchema()
            data = schema.load(self.request.json_body)
            
            # Verifica se o cliente existe
            client = self.db.query(Client).filter(Client.id == data['client_id']).first()
            if not client:
                return Response(
                    json.dumps({'error': 'Cliente não encontrado'}),
                    status=404,
                    content_type='application/json'
                )
            
            # Cria o contrato
            contract = Contract(
                name=data['name'],
                client_id=data['client_id'],
                total_value=data['total_value'],
                responsible_name=data['responsible_name'],
                payment_method=data['payment_method'],
                billed_value=0,
                balance=data['total_value'],
                status=ContractStatus(data.get('status', ContractStatus.ATIVO.value)),
                end_date=data['end_date']
            )
            
            self.db.add(contract)
            self.db.flush()
            
            # Serializa os dados do contrato
            result_schema = ContractSchema()
            contract_data = result_schema.dump(contract)
            
            return Response(
                json.dumps(contract_data).encode('utf-8'),
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
    
    @view_config(route_name='contract', request_method='PUT')
    def update_contract(self):
        """
        PUT /api/contracts/{id}
        Atualiza um contrato existente
        
        Body:
            Campos a serem atualizados
        
        Returns:
            Dados do contrato atualizado
        """
        contract_id = self.request.matchdict['id']
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        
        if not contract:
            return Response(
                json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            data = self.request.json_body
            
            # Atualiza campos permitidos
            if 'name' in data:
                contract.name = data['name']
            if 'total_value' in data:
                contract.total_value = data['total_value']
            if 'status' in data:
                contract.status = ContractStatus(data['status'])
            if 'end_date' in data:
                contract.end_date = datetime.fromisoformat(data['end_date'])
            
            # Recalcula o balance
            contract.balance = contract.total_value - contract.billed_value
            
            self.db.flush()
            
            # Serializa os dados
            schema = ContractSchema()
            return schema.dump(contract)
            
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
    
    @view_config(route_name='contract', request_method='DELETE')
    def delete_contract(self):
        """
        DELETE /api/contracts/{id}
        Remove um contrato
        
        Returns:
            Mensagem de confirmação
        """
        contract_id = self.request.matchdict['id']
        contract = self.db.query(Contract).filter(Contract.id == contract_id).first()
        
        if not contract:
            return Response(
                json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        try:
            self.db.delete(contract)
            return {'message': 'Contrato removido com sucesso'}
        except Exception as e:
            self.db.rollback()
            return Response(
                json.dumps({'error': str(e)}).encode('utf-8'),
                status=400,
                charset='utf-8',
                content_type='application/json'
            )

