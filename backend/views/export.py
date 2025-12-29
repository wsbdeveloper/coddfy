"""
Views de Exportação
Endpoints para exportar dados em CSV/Excel e PDF
"""
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.orm import joinedload
from backend.models import Installment, Contract, Client
from backend.auth_helpers import require_authenticated, apply_partner_filter
import json
import csv
import io
from datetime import datetime


@view_config(route_name='export_installments_csv', request_method='GET')
def export_installments_csv(request):
    """
    GET /api/installments/export/csv
    Exporta parcelas para CSV/Excel
    
    Query params:
        - contract_id: Filtrar por contrato (UUID)
        - billed: Filtrar por status (true/false)
        - start_date: Data inicial
        - end_date: Data final
    
    Returns:
        Arquivo CSV
    """
    user = require_authenticated(request)
    db = request.dbsession
    
    # Query base
    query = db.query(Installment).options(
        joinedload(Installment.contract).joinedload(Contract.client)
    )
    
    # Filtros opcionais
    contract_id = request.params.get('contract_id')
    if contract_id:
        query = query.filter(Installment.contract_id == contract_id)
    
    billed = request.params.get('billed')
    if billed is not None:
        billed_bool = billed.lower() in ('true', '1', 'yes')
        query = query.filter(Installment.billed == billed_bool)
    
    # Aplicar filtro por parceiro (usuários não-admin só veem parcelas dos seus contratos)
    if user.role.value != 'admin_global':
        query = query.join(Contract).join(Client)
        query = apply_partner_filter(query, Client, user)
    
    # Ordena por mês
    installments = query.order_by(Installment.month.desc()).all()
    
    # Cria o CSV em memória
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Cabeçalho
    writer.writerow([
        'Contrato',
        'Cliente',
        'Mês',
        'Valor',
        'Faturado',
        'Número NF',
        'Data Faturamento',
        'Prazo Pagamento (dias)',
        'Data Prevista Pagamento',
        'Data Pagamento'
    ])
    
    # Dados
    for installment in installments:
        writer.writerow([
            installment.contract.name if installment.contract else '',
            installment.contract.client.name if installment.contract and installment.contract.client else '',
            installment.month,
            str(installment.value),
            'Sim' if installment.billed else 'Não',
            installment.invoice_number or '',
            installment.billing_date.strftime('%d/%m/%Y') if installment.billing_date else '',
            str(installment.payment_term) if installment.payment_term else '',
            installment.expected_payment_date.strftime('%d/%m/%Y') if installment.expected_payment_date else '',
            installment.payment_date.strftime('%d/%m/%Y') if installment.payment_date else ''
        ])
    
    # Prepara resposta
    csv_data = output.getvalue()
    output.close()
    
    filename = f'faturamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    response = Response(
        body=csv_data.encode('utf-8-sig'),  # utf-8-sig para Excel reconhecer UTF-8
        content_type='text/csv; charset=utf-8-sig',
        charset='utf-8-sig'
    )
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@view_config(route_name='export_installments_pdf', request_method='GET')
def export_installments_pdf(request):
    """
    GET /api/installments/export/pdf
    Exporta parcelas para PDF
    
    Query params:
        - contract_id: Filtrar por contrato (UUID)
        - billed: Filtrar por status (true/false)
        - start_date: Data inicial
        - end_date: Data final
    
    Returns:
        Arquivo PDF
    """
    user = require_authenticated(request)
    db = request.dbsession
    
    # Query base
    query = db.query(Installment).options(
        joinedload(Installment.contract).joinedload(Contract.client)
    )
    
    # Filtros opcionais
    contract_id = request.params.get('contract_id')
    if contract_id:
        query = query.filter(Installment.contract_id == contract_id)
    
    billed = request.params.get('billed')
    if billed is not None:
        billed_bool = billed.lower() in ('true', '1', 'yes')
        query = query.filter(Installment.billed == billed_bool)
    
    # Aplicar filtro por parceiro (usuários não-admin só veem parcelas dos seus contratos)
    if user.role.value != 'admin_global':
        query = query.join(Contract).join(Client)
        query = apply_partner_filter(query, Client, user)
    
    # Ordena por mês
    installments = query.order_by(Installment.month.desc()).all()
    
    # Gera HTML simples para PDF (pode ser melhorado com biblioteca como reportlab)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Relatório de Faturamento</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #333;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            .footer {{
                margin-top: 30px;
                text-align: right;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <h1>Relatório de Faturamento</h1>
        <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        <table>
            <thead>
                <tr>
                    <th>Contrato</th>
                    <th>Cliente</th>
                    <th>Mês</th>
                    <th>Valor</th>
                    <th>Faturado</th>
                    <th>Número NF</th>
                    <th>Data Faturamento</th>
                    <th>Prazo (dias)</th>
                    <th>Data Prevista</th>
                    <th>Data Pagamento</th>
                </tr>
            </thead>
            <tbody>
    """
    
    total_value = 0
    for installment in installments:
        total_value += float(installment.value)
        html_content += f"""
                <tr>
                    <td>{installment.contract.name if installment.contract else ''}</td>
                    <td>{installment.contract.client.name if installment.contract and installment.contract.client else ''}</td>
                    <td>{installment.month}</td>
                    <td>R$ {installment.value:,.2f}</td>
                    <td>{'Sim' if installment.billed else 'Não'}</td>
                    <td>{installment.invoice_number or ''}</td>
                    <td>{installment.billing_date.strftime('%d/%m/%Y') if installment.billing_date else ''}</td>
                    <td>{installment.payment_term or ''}</td>
                    <td>{installment.expected_payment_date.strftime('%d/%m/%Y') if installment.expected_payment_date else ''}</td>
                    <td>{installment.payment_date.strftime('%d/%m/%Y') if installment.payment_date else ''}</td>
                </tr>
        """
    
    html_content += f"""
            </tbody>
            <tfoot>
                <tr>
                    <td colspan="3"><strong>Total</strong></td>
                    <td><strong>R$ {total_value:,.2f}</strong></td>
                    <td colspan="6"></td>
                </tr>
            </tfoot>
        </table>
        <div class="footer">
            <p>Total de registros: {len(installments)}</p>
        </div>
    </body>
    </html>
    """
    
    # Retorna HTML (em produção, pode usar weasyprint ou reportlab para gerar PDF real)
    # Por enquanto, retornamos HTML que pode ser convertido para PDF no frontend
    filename = f'faturamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    response = Response(
        body=html_content.encode('utf-8'),
        content_type='text/html; charset=utf-8',
        charset='utf-8'
    )
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response

