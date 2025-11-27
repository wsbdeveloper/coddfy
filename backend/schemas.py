"""
Schemas de validação usando Marshmallow
Define a estrutura de entrada/saída da API
"""
from marshmallow import Schema, fields, validate, validates, ValidationError
from marshmallow.fields import DateTime
from datetime import datetime
from backend.models import ContractStatus, UserRole


class FlexibleDateTime(fields.DateTime):
    """
    Campo DateTime que aceita múltiplos formatos:
    - ISO format (padrão)
    - dd/mm/yyyy
    - dd/mm/yyyy HH:MM:SS
    """
    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            # Tenta formato dd/mm/yyyy
            try:
                # Formato dd/mm/yyyy
                if len(value) == 10 and value.count('/') == 2:
                    return datetime.strptime(value, '%d/%m/%Y')
                # Formato dd/mm/yyyy HH:MM:SS
                elif len(value) > 10 and value.count('/') == 2:
                    return datetime.strptime(value, '%d/%m/%Y %H:%M:%S')
            except ValueError:
                pass
            
            # Tenta formato ISO (padrão)
            try:
                return super()._deserialize(value, attr, data, **kwargs)
            except ValidationError:
                raise ValidationError(f'Formato de data inválido. Use dd/mm/yyyy ou formato ISO.')
        
        return super()._deserialize(value, attr, data, **kwargs)


# Partner Schemas
class PartnerSchema(Schema):
    """Schema para serialização de parceiro"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class PartnerCreateSchema(Schema):
    """Schema para criação de parceiro"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))


# User Schemas
class UserSchema(Schema):
    """Schema para serialização de usuário"""
    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    role = fields.Method("get_role_value", validate=validate.OneOf([r.value for r in UserRole]))
    partner_id = fields.UUID(allow_none=True)
    partner = fields.Nested(PartnerSchema, dump_only=True)
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    def get_role_value(self, obj):
        """Retorna o valor do enum, não a representação"""
        if hasattr(obj, 'role'):
            if isinstance(obj.role, UserRole):
                return obj.role.value
            elif isinstance(obj.role, str):
                # Se já for string, verificar se é o valor correto
                return obj.role
        return str(obj.role) if obj.role else None


class UserLoginSchema(Schema):
    """Schema para login de usuário"""
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class UserCreateSchema(Schema):
    """Schema para criação de usuário"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    role = fields.Str(validate=validate.OneOf([r.value for r in UserRole]))
    partner_id = fields.UUID(allow_none=True)  # NULL para admin_global


# Client Schemas
class ClientSchema(Schema):
    """Schema para serialização de cliente"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    partner_id = fields.UUID(required=True)
    partner = fields.Nested(PartnerSchema, dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ClientCreateSchema(Schema):
    """Schema para criação de cliente"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    partner_id = fields.UUID(allow_none=True)  # Opcional, pode ser fornecido via partner (nome)
    partner = fields.Str(allow_none=True, validate=validate.Length(min=1, max=255))  # Nome do parceiro como alternativa


# Installment Schemas
class ContractSimpleSchema(Schema):
    """Schema simplificado de contrato para uso em nested relationships"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(dump_only=True)
    status = fields.Method("get_status_value", dump_only=True)
    
    def get_status_value(self, obj):
        """Retorna o valor do enum, não a representação"""
        if hasattr(obj, 'status'):
            if hasattr(obj.status, 'value'):
                return obj.status.value
            return str(obj.status)
        return None


class InstallmentSchema(Schema):
    """Schema para serialização de parcela"""
    id = fields.UUID(dump_only=True)
    contract_id = fields.UUID()
    contract = fields.Nested(ContractSimpleSchema, dump_only=True)
    month = fields.Str(required=True, validate=validate.Length(max=20))
    value = fields.Decimal(required=True, as_string=True)
    billed = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# Consultant Feedback Schemas
class ConsultantFeedbackSchema(Schema):
    """Schema para serialização de feedback de consultor"""
    id = fields.UUID(dump_only=True)
    consultant_id = fields.UUID(required=True)
    user_id = fields.UUID(dump_only=True)
    contract_id = fields.UUID(allow_none=True)
    comment = fields.Str(required=True, validate=validate.Length(min=1, max=2000))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    # Nested relationships
    user = fields.Nested(UserSchema, dump_only=True, only=('id', 'username', 'email'))


class ConsultantFeedbackCreateSchema(Schema):
    """Schema para criação de feedback de consultor"""
    consultant_id = fields.UUID(required=True)
    contract_id = fields.UUID(allow_none=True)
    comment = fields.Str(required=True, validate=validate.Length(min=1, max=2000))


# Consultant Schemas
class ConsultantSchema(Schema):
    """Schema para serialização de consultor"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    role = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    contract_id = fields.UUID()
    partner_id = fields.UUID(required=True)
    partner = fields.Nested(PartnerSchema, dump_only=True)
    feedback = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    feedback_comments = fields.Nested(ConsultantFeedbackSchema, many=True, dump_only=True)
    performance_color = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class ConsultantCreateSchema(Schema):
    """Schema para criação de consultor"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    role = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    contract_id = fields.UUID(required=True)
    partner_id = fields.UUID(allow_none=True)  # Opcional, será atribuído automaticamente
    feedback = fields.Int(required=True, validate=validate.Range(min=0, max=100))


# Contract Schemas
class ContractSchema(Schema):
    """Schema para serialização de contrato"""
    id = fields.UUID(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    client_id = fields.UUID(required=True)
    total_value = fields.Decimal(required=True, as_string=True)
    billed_value = fields.Decimal(as_string=True)
    balance = fields.Decimal(as_string=True)
    status = fields.Str(validate=validate.OneOf([s.value for s in ContractStatus]))
    end_date = fields.DateTime(required=True)
    billed_percentage = fields.Float(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Nested relationships
    client = fields.Nested(ClientSchema, dump_only=True)
    installments = fields.Nested(InstallmentSchema, many=True, dump_only=True)
    consultants = fields.Nested(ConsultantSchema, many=True, dump_only=True)


class ContractCreateSchema(Schema):
    """Schema para criação de contrato"""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    client_id = fields.UUID(required=True)
    total_value = fields.Decimal(required=True, as_string=True)
    status = fields.Str(validate=validate.OneOf([s.value for s in ContractStatus]))
    end_date = FlexibleDateTime(required=True)
    
    @validates('total_value')
    def validate_total_value(self, value):
        """Valida se o valor total é positivo"""
        if value <= 0:
            raise ValidationError('O valor total deve ser maior que zero')


# Dashboard Schemas
class DashboardStatsSchema(Schema):
    """Schema para estatísticas do dashboard"""
    active_contracts = fields.Int()
    inactive_contracts = fields.Int()
    allocated_consultants = fields.Int()
    average_feedback = fields.Float()
    total_contracts_value = fields.Decimal(as_string=True)
    total_billed_value = fields.Decimal(as_string=True)
    total_balance = fields.Decimal(as_string=True)


class ContractExpirySchema(Schema):
    """Schema para exibição de vigência de contratos"""
    id = fields.UUID()
    name = fields.Str()
    client_name = fields.Str()
    end_date = fields.DateTime()
    days_remaining = fields.Int()
    status = fields.Str()

