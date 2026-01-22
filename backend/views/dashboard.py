"""
Views do Dashboard
Endpoints para exibir estatísticas consolidadas
"""
from pyramid.view import view_config
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.models import Contract, Consultant, ContractStatus, Installment, Client
from backend.auth_helpers import require_authenticated, apply_partner_filter
from backend.schemas import DashboardStatsSchema, ContractExpirySchema
from decimal import Decimal


@view_config(route_name='dashboard', request_method='GET', renderer='json')
def dashboard_view(request):
    """
    GET /api/dashboard
    Retorna visão geral consolidada dos contratos e consultores
    
    Returns:
        - stats: Estatísticas gerais
        - expiring_contracts: Contratos próximos do vencimento
        - financial_summary: Resumo financeiro
    """
    user = require_authenticated(request)
    db = request.dbsession
    
    # Estatísticas de contratos
    active_contracts_query = db.query(func.count(Contract.id)).join(Client).filter(
        Contract.status == ContractStatus.ATIVO
    )
    active_contracts = apply_partner_filter(active_contracts_query, Client, user).scalar() or 0
    
    inactive_contracts_query = db.query(func.count(Contract.id)).join(Client).filter(
        Contract.status == ContractStatus.INATIVO
    )
    inactive_contracts = apply_partner_filter(inactive_contracts_query, Client, user).scalar() or 0
    
    # Total de consultores alocados
    allocated_consultants_query = db.query(func.count(Consultant.id))
    allocated_consultants = apply_partner_filter(allocated_consultants_query, Consultant, user).scalar() or 0
    
    # Média de feedback
    average_feedback_query = db.query(func.avg(Consultant.feedback_score))
    average_feedback_result = apply_partner_filter(average_feedback_query, Consultant, user).scalar()
    average_feedback = float(average_feedback_result) if average_feedback_result else 0.0
    
    # Valores financeiros totais
    financial_data_query = db.query(
        func.sum(Contract.total_value),
        func.sum(Contract.billed_value),
        func.sum(Contract.balance)
    ).join(Client)
    financial_data = apply_partner_filter(financial_data_query, Client, user).first()
    
    total_value = financial_data[0] or Decimal('0')
    billed_value = financial_data[1] or Decimal('0')
    balance = financial_data[2] or Decimal('0')

    # Detalhamento financeiro baseado em parcelas
    paid_value_query = db.query(
        func.sum(Installment.value)
    ).join(Contract).join(Client).filter(
        Installment.payment_date.isnot(None)
    )
    paid_value = apply_partner_filter(paid_value_query, Client, user).scalar() or Decimal('0')

    pending_payment_query = db.query(
        func.sum(Installment.value)
    ).join(Contract).join(Client).filter(
        Installment.billing_date.isnot(None),
        Installment.payment_date.is_(None)
    )
    pending_payment = apply_partner_filter(pending_payment_query, Client, user).scalar() or Decimal('0')

    to_bill_query = db.query(
        func.sum(Installment.value)
    ).join(Contract).join(Client).filter(
        Installment.billing_date.is_(None)
    )
    to_bill = apply_partner_filter(to_bill_query, Client, user).scalar() or Decimal('0')
    
    # Contratos próximos do vencimento (próximos 30 dias)
    today = datetime.utcnow()
    thirty_days = today + timedelta(days=30)
    
    expiring_contracts_query = db.query(Contract).join(Client).filter(
        Contract.end_date <= thirty_days,
        Contract.end_date >= today,
        Contract.status == ContractStatus.ATIVO
    )
    expiring_contracts = apply_partner_filter(expiring_contracts_query, Client, user).order_by(
        Contract.end_date
    ).all()
    
    # Serializa contratos próximos do vencimento
    expiring_list = []
    for contract in expiring_contracts:
        days_remaining = (contract.end_date - today).days
        expiring_list.append({
            'id': str(contract.id),
            'name': contract.name,
            'client_name': contract.client.name,
            'end_date': contract.end_date.isoformat(),
            'days_remaining': days_remaining,
            'status': contract.status.value
        })
    
    # Monta a resposta
    stats_schema = DashboardStatsSchema()
    stats_data = stats_schema.dump({
        'active_contracts': active_contracts,
        'inactive_contracts': inactive_contracts,
        'allocated_consultants': allocated_consultants,
        'average_feedback': round(average_feedback, 2),
        'total_contracts_value': str(total_value),
        'total_billed_value': str(billed_value),
        'total_balance': str(balance)
    })
    
    return {
        'stats': stats_data,
        'expiring_contracts': expiring_list,
        'financial_summary': {
            'total_value': str(total_value),
            'billed_value': str(billed_value),
            'paid_value': str(paid_value),
            'pending_payment': str(pending_payment),
            'to_bill': str(to_bill),
            'balance': str(balance),
            'billed_percentage': round(float(billed_value / total_value * 100), 2) if total_value > 0 else 0
        }
    }

