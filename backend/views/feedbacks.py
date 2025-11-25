"""
Views para gerenciamento de feedbacks de consultores
Usuários podem criar feedbacks apenas para consultores do seu parceiro
"""
import json
from pyramid.view import view_config
from pyramid.response import Response
from backend.database import DBSession
from backend.models import ConsultantFeedback, Consultant, Contract
from backend.schemas import ConsultantFeedbackSchema, ConsultantFeedbackCreateSchema
from backend.auth_helpers import (
    require_authenticated, 
    get_current_user_from_request,
    can_access_resource,
    apply_partner_filter
)
from marshmallow import ValidationError


@view_config(route_name='feedbacks', request_method='GET', renderer='json')
def list_feedbacks(request):
    """
    Lista feedbacks de consultores
    Filtrado automaticamente por parceiro do usuário
    """
    # Verificar autenticação
    user = require_authenticated(request)
    
    # Query base
    query = DBSession.query(ConsultantFeedback).join(Consultant)
    
    # Aplicar filtro por parceiro
    query = apply_partner_filter(query, Consultant, user)
    
    # Filtros opcionais
    consultant_id = request.params.get('consultant_id')
    if consultant_id:
        query = query.filter(ConsultantFeedback.consultant_id == consultant_id)
    
    contract_id = request.params.get('contract_id')
    if contract_id:
        query = query.filter(ConsultantFeedback.contract_id == contract_id)
    
    feedbacks = query.order_by(ConsultantFeedback.created_at.desc()).all()
    
    # Serializar
    schema = ConsultantFeedbackSchema(many=True)
    return Response(
        body=json.dumps(schema.dump(feedbacks)).encode('utf-8'),
        status=200,
        content_type='application/json',
        charset='utf-8'
    )


@view_config(route_name='feedbacks', request_method='POST', renderer='json')
def create_feedback(request):
    """
    Cria um novo feedback para um consultor
    Usuário só pode criar feedback para consultores do seu parceiro
    """
    # Verificar autenticação
    user = require_authenticated(request)
    
    try:
        # Validar dados
        schema = ConsultantFeedbackCreateSchema()
        data = schema.load(request.json_body)
        
        # Verificar se o consultor existe
        consultant = DBSession.query(Consultant).filter_by(id=data['consultant_id']).first()
        if not consultant:
            return Response(
                body=json.dumps({'error': 'Consultor não encontrado'}).encode('utf-8'),
                status=404,
                content_type='application/json',
                charset='utf-8'
            )
        
        # Verificar se o usuário tem acesso ao consultor (mesmo parceiro)
        if not can_access_resource(user, consultant.partner_id):
            return Response(
                body=json.dumps({'error': 'Você não tem permissão para dar feedback a este consultor'}).encode('utf-8'),
                status=403,
                content_type='application/json',
                charset='utf-8'
            )
        
        # Se especificou contrato, verificar se o consultor está nesse contrato
        if data.get('contract_id'):
            contract = DBSession.query(Contract).filter_by(id=data['contract_id']).first()
            if not contract:
                return Response(
                    body=json.dumps({'error': 'Contrato não encontrado'}).encode('utf-8'),
                    status=404,
                    content_type='application/json',
                    charset='utf-8'
                )
            
            if str(consultant.contract_id) != str(data['contract_id']):
                return Response(
                    body=json.dumps({'error': 'Consultor não está alocado neste contrato'}).encode('utf-8'),
                    status=400,
                    content_type='application/json',
                    charset='utf-8'
                )
        
        # Criar feedback
        feedback = ConsultantFeedback(
            consultant_id=data['consultant_id'],
            user_id=user.id,
            contract_id=data.get('contract_id'),
            comment=data['comment']
        )
        DBSession.add(feedback)
        DBSession.flush()
        
        # Recarregar para pegar relacionamentos
        DBSession.refresh(feedback)
        
        # Serializar resposta
        result_schema = ConsultantFeedbackSchema()
        return Response(
            body=json.dumps(result_schema.dump(feedback)).encode('utf-8'),
            status=201,
            content_type='application/json',
            charset='utf-8'
        )
    
    except ValidationError as e:
        return Response(
            body=json.dumps({'error': 'Dados inválidos', 'details': e.messages}).encode('utf-8'),
            status=400,
            content_type='application/json',
            charset='utf-8'
        )


@view_config(route_name='feedback', request_method='GET', renderer='json')
def get_feedback(request):
    """
    Busca um feedback específico
    """
    # Verificar autenticação
    user = require_authenticated(request)
    
    feedback_id = request.matchdict['id']
    feedback = DBSession.query(ConsultantFeedback).join(Consultant).filter(
        ConsultantFeedback.id == feedback_id
    ).first()
    
    if not feedback:
        return Response(
            body=json.dumps({'error': 'Feedback não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    # Verificar acesso (mesmo parceiro)
    if not can_access_resource(user, feedback.consultant.partner_id):
        return Response(
            body=json.dumps({'error': 'Você não tem permissão para acessar este feedback'}).encode('utf-8'),
            status=403,
            content_type='application/json',
            charset='utf-8'
        )
    
    schema = ConsultantFeedbackSchema()
    return Response(
        body=json.dumps(schema.dump(feedback)).encode('utf-8'),
        status=200,
        content_type='application/json',
        charset='utf-8'
    )


@view_config(route_name='feedback', request_method='PUT', renderer='json')
def update_feedback(request):
    """
    Atualiza um feedback
    Apenas o autor do feedback pode atualizar
    """
    # Verificar autenticação
    user = require_authenticated(request)
    
    feedback_id = request.matchdict['id']
    feedback = DBSession.query(ConsultantFeedback).filter_by(id=feedback_id).first()
    
    if not feedback:
        return Response(
            body=json.dumps({'error': 'Feedback não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    # Apenas o autor pode atualizar
    if str(feedback.user_id) != str(user.id):
        return Response(
            body=json.dumps({'error': 'Você só pode editar seus próprios feedbacks'}).encode('utf-8'),
            status=403,
            content_type='application/json',
            charset='utf-8'
        )
    
    try:
        # Validar dados
        schema = ConsultantFeedbackCreateSchema()
        data = schema.load(request.json_body)
        
        # Atualizar apenas o comentário (não pode mudar consultor/contrato)
        feedback.comment = data['comment']
        DBSession.flush()
        
        # Serializar resposta
        result_schema = ConsultantFeedbackSchema()
        return Response(
            body=json.dumps(result_schema.dump(feedback)).encode('utf-8'),
            status=200,
            content_type='application/json',
            charset='utf-8'
        )
    
    except ValidationError as e:
        return Response(
            body=json.dumps({'error': 'Dados inválidos', 'details': e.messages}).encode('utf-8'),
            status=400,
            content_type='application/json',
            charset='utf-8'
        )


@view_config(route_name='feedback', request_method='DELETE', renderer='json')
def delete_feedback(request):
    """
    Deleta um feedback
    Apenas o autor do feedback ou admin pode deletar
    """
    # Verificar autenticação
    user = require_authenticated(request)
    
    feedback_id = request.matchdict['id']
    feedback = DBSession.query(ConsultantFeedback).filter_by(id=feedback_id).first()
    
    if not feedback:
        return Response(
            body=json.dumps({'error': 'Feedback não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    # Apenas o autor ou admin pode deletar
    from backend.models import UserRole
    is_author = str(feedback.user_id) == str(user.id)
    is_admin = user.role in [UserRole.ADMIN_GLOBAL, UserRole.ADMIN_PARTNER]
    
    if not (is_author or is_admin):
        return Response(
            body=json.dumps({'error': 'Você não tem permissão para deletar este feedback'}).encode('utf-8'),
            status=403,
            content_type='application/json',
            charset='utf-8'
        )
    
    try:
        DBSession.delete(feedback)
        DBSession.flush()
        
        return Response(
            body=json.dumps({'message': 'Feedback deletado com sucesso'}).encode('utf-8'),
            status=200,
            content_type='application/json',
            charset='utf-8'
        )
    
    except Exception as e:
        DBSession.rollback()
        return Response(
            body=json.dumps({'error': f'Erro ao deletar feedback: {str(e)}'}).encode('utf-8'),
            status=500,
            content_type='application/json',
            charset='utf-8'
        )





