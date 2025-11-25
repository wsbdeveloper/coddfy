"""
Views para gerenciamento de parceiros (Partners)
Apenas admin global pode acessar
"""
import json
from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError
from backend.models import Partner
from backend.schemas import PartnerSchema, PartnerCreateSchema
from backend.auth_helpers import require_admin_global
from marshmallow import ValidationError


@view_config(route_name='partners', request_method='GET', renderer='json')
def list_partners(request):
    """
    Lista todos os parceiros
    Apenas admin global pode acessar
    """
    # Verificar permissão
    require_admin_global(request)
    
    # Buscar todos os parceiros
    partners = request.dbsession.query(Partner).order_by(Partner.name).all()
    
    # Serializar
    schema = PartnerSchema(many=True)
    return Response(
        body=json.dumps(schema.dump(partners)).encode('utf-8'),
        status=200,
        content_type='application/json',
        charset='utf-8'
    )


@view_config(route_name='partners', request_method='POST', renderer='json')
def create_partner(request):
    """
    Cria um novo parceiro
    Apenas admin global pode acessar
    """
    # Verificar permissão
    require_admin_global(request)
    
    try:
        # Validar dados
        schema = PartnerCreateSchema()
        data = schema.load(request.json_body)
        
        # Criar parceiro
        partner = Partner(**data)
        request.dbsession.add(partner)
        request.dbsession.flush()
        
        # Serializar resposta
        result_schema = PartnerSchema()
        return Response(
            body=json.dumps(result_schema.dump(partner)).encode('utf-8'),
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
    except IntegrityError:
        request.dbsession.rollback()
        return Response(
            body=json.dumps({'error': 'Parceiro com este nome já existe'}).encode('utf-8'),
            status=409,
            content_type='application/json',
            charset='utf-8'
        )


@view_config(route_name='partner', request_method='GET', renderer='json')
def get_partner(request):
    """
    Busca um parceiro específico
    Apenas admin global pode acessar
    """
    # Verificar permissão
    require_admin_global(request)
    
    partner_id = request.matchdict['id']
    partner = request.dbsession.query(Partner).filter_by(id=partner_id).first()
    
    if not partner:
        return Response(
            body=json.dumps({'error': 'Parceiro não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    schema = PartnerSchema()
    return Response(
        body=json.dumps(schema.dump(partner)).encode('utf-8'),
        status=200,
        content_type='application/json',
        charset='utf-8'
    )


@view_config(route_name='partner', request_method='PUT', renderer='json')
def update_partner(request):
    """
    Atualiza um parceiro
    Apenas admin global pode acessar
    """
    # Verificar permissão
    require_admin_global(request)
    
    partner_id = request.matchdict['id']
    partner = request.dbsession.query(Partner).filter_by(id=partner_id).first()
    
    if not partner:
        return Response(
            body=json.dumps({'error': 'Parceiro não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    try:
        # Validar dados
        schema = PartnerCreateSchema()
        data = schema.load(request.json_body)
        
        # Atualizar campos
        for key, value in data.items():
            setattr(partner, key, value)
        
        request.dbsession.flush()
        
        # Serializar resposta
        result_schema = PartnerSchema()
        return Response(
            body=json.dumps(result_schema.dump(partner)).encode('utf-8'),
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
    except IntegrityError:
        request.dbsession.rollback()
        return Response(
            body=json.dumps({'error': 'Parceiro com este nome já existe'}).encode('utf-8'),
            status=409,
            content_type='application/json',
            charset='utf-8'
        )


@view_config(route_name='partner', request_method='DELETE', renderer='json')
def delete_partner(request):
    """
    Deleta um parceiro
    Apenas admin global pode acessar
    ATENÇÃO: Deletar um parceiro pode afetar muitos dados relacionados
    """
    # Verificar permissão
    require_admin_global(request)
    
    partner_id = request.matchdict['id']
    partner = request.dbsession.query(Partner).filter_by(id=partner_id).first()
    
    if not partner:
        return Response(
            body=json.dumps({'error': 'Parceiro não encontrado'}).encode('utf-8'),
            status=404,
            content_type='application/json',
            charset='utf-8'
        )
    
    try:
        # Verificar se há dados relacionados
        if partner.clients or partner.consultants or partner.users:
            return Response(
                body=json.dumps({
                    'error': 'Não é possível deletar parceiro com dados relacionados',
                    'details': {
                        'clients': len(partner.clients),
                        'consultants': len(partner.consultants),
                        'users': len(partner.users)
                    }
                }).encode('utf-8'),
                status=400,
                content_type='application/json',
                charset='utf-8'
            )
        
        request.dbsession.delete(partner)
        request.dbsession.flush()
        
        return Response(
            body=json.dumps({'message': 'Parceiro deletado com sucesso'}).encode('utf-8'),
            status=200,
            content_type='application/json',
            charset='utf-8'
        )
    
    except Exception as e:
        request.dbsession.rollback()
        return Response(
            body=json.dumps({'error': f'Erro ao deletar parceiro: {str(e)}'}).encode('utf-8'),
            status=500,
            content_type='application/json',
            charset='utf-8'
        )



