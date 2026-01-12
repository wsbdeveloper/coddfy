"""
Modelos de dados da aplicação
Define as tabelas do banco de dados usando SQLAlchemy
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Numeric, Boolean, 
    DateTime, ForeignKey, Enum as SQLEnum, TypeDecorator
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.database import Base
import enum
from sqlalchemy.types import TypeDecorator, String


# Enums
class ContractStatus(str, enum.Enum):
    """Status possíveis de um contrato"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    A_VENCER = "a_vencer"


class UserRole(str, enum.Enum):
    """Níveis de acesso do sistema"""
    ADMIN_GLOBAL = "admin_global"  # Admin que vê tudo
    ADMIN_PARTNER = "admin_partner"  # Admin de um parceiro específico
    USER_PARTNER = "user_partner"  # Usuário comum de um parceiro


class UserRoleType(TypeDecorator):
    impl = String(50)

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        # Armazena como string (nome do enum ou valor)
        return value.name if hasattr(value, "name") else str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        # Tenta converter para enum UserRole, caso exista; caso contrário retorna string
        try:
            return UserRole[value]
        except Exception:
            return value


# Models
class Partner(Base):
    """
    Modelo de parceiro
    Representa empresas parceiras que têm acesso segregado ao sistema
    """
    __tablename__ = 'partners'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_strategic = Column(Boolean, default=False, nullable=False)  # Estratégico ou não
    status = Column(String(50), default='active', nullable=False)   # Status livre (ex: active/inactive)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    users = relationship("User", back_populates="partner")
    clients = relationship("Client", back_populates="partner")
    consultants = relationship("Consultant", back_populates="partner")

    def __repr__(self):
        return f"<Partner(name='{self.name}')>"


class User(Base):
    """
    Modelo de usuário para autenticação
    Armazena credenciais e nível de acesso
    Usuários podem ser globais (partner_id = None) ou vinculados a um parceiro
    """
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(UserRoleType(), default=UserRole.USER_PARTNER, nullable=False)
    partner_id = Column(UUID(as_uuid=True), ForeignKey('partners.id'), nullable=True)  # NULL para admin global
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    partner = relationship("Partner", back_populates="users")
    feedbacks = relationship("ConsultantFeedback", back_populates="user")

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}', partner_id='{self.partner_id}')>"


class Client(Base):
    """
    Modelo de cliente
    Representa empresas/organizações que possuem contratos
    Cada cliente pertence a um parceiro específico
    """
    __tablename__ = 'clients'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    partner_id = Column(UUID(as_uuid=True), ForeignKey('partners.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    cnpj = Column(String(20), nullable=True, index=True)        # CNPJ
    razao_social = Column(String(255), nullable=True)           # Razão social
    
    # Relacionamentos
    partner = relationship("Partner", back_populates="clients")
    contracts = relationship("Contract", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(name='{self.name}', partner_id='{self.partner_id}')>"


class Contract(Base):
    """
    Modelo de contrato
    Armazena informações financeiras e de vigência dos contratos
    """
    __tablename__ = 'contracts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    client_id = Column(UUID(as_uuid=True), ForeignKey('clients.id'), nullable=False)
    total_value = Column(Numeric(15, 2), nullable=False)
    billed_value = Column(Numeric(15, 2), default=0, nullable=False)
    balance = Column(Numeric(15, 2), nullable=False)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.ATIVO, nullable=False)
    end_date = Column(DateTime, nullable=False)

    responsible_name = Column(String(255), nullable=True)            
    payment_method = Column(String(50), nullable=False, default='parcelado')  # 'a_vista' | 'parcelado' ou usar Enum

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    client = relationship("Client", back_populates="contracts")
    installments = relationship("Installment", back_populates="contract", cascade="all, delete-orphan")
    consultants = relationship("Consultant", back_populates="contract", cascade="all, delete-orphan")
    timesheets = relationship("Timesheet", back_populates="contract", cascade="all, delete-orphan")

    @property
    def billed_percentage(self):
        """Calcula o percentual faturado do contrato"""
        if self.total_value > 0:
            return float((self.billed_value / self.total_value) * 100)
        return 0.0

    def __repr__(self):
        return f"<Contract(name='{self.name}', status='{self.status}')>"


class Installment(Base):
    """
    Modelo de parcela
    Representa as parcelas mensais de um contrato
    """
    __tablename__ = 'installments'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False)
    month = Column(String(20), nullable=False)  # Ex: "Jan/25"
    value = Column(Numeric(15, 2), nullable=False)
    billed = Column(Boolean, default=False, nullable=False)
    
    # Campos de Nota Fiscal
    invoice_number = Column(String(100), nullable=True)  # Número da nota fiscal
    billing_date = Column(DateTime, nullable=True)  # Data de faturamento
    payment_term = Column(Integer, nullable=True)  # Prazo de pagamento (em dias)
    expected_payment_date = Column(DateTime, nullable=True)  # Data prevista do pagamento
    payment_date = Column(DateTime, nullable=True)  # Data do pagamento
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    contract = relationship("Contract", back_populates="installments")

    def __repr__(self):
        return f"<Installment(month='{self.month}', value={self.value}, billed={self.billed})>"


class Consultant(Base):
    """
    Modelo de consultor
    Armazena informações dos consultores alocados em contratos
    Cada consultor pertence a um parceiro específico
    """
    __tablename__ = 'consultants'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    role = Column(String(100), nullable=False)  # Cargo
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False)
    partner_id = Column(UUID(as_uuid=True), ForeignKey('partners.id'), nullable=False)
    feedback_score = Column(Numeric(5, 2), nullable=True, default=0)
    photo_url = Column(String(500), nullable=True)  # URL da foto do consultor
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    contract = relationship("Contract", back_populates="consultants")
    partner = relationship("Partner", back_populates="consultants")
    feedback_comments = relationship("ConsultantFeedback", back_populates="consultant", cascade="all, delete-orphan")
    timesheets = relationship("Timesheet", back_populates="consultant", cascade="all, delete-orphan")  # <-- ADICIONADO

    @property
    def feedback(self):
        """Calcula o feedback médio baseado nos feedbacks numéricos"""
        if not self.feedback_comments:
            return 0
        
        # Filtra apenas feedbacks com rating
        ratings = [fb.rating for fb in self.feedback_comments if fb.rating is not None]
        
        if not ratings:
            return 0
        
        return round(sum(ratings) / len(ratings), 2)

    @property
    def performance_color(self):
        """Retorna a cor do desempenho baseado no feedback"""
        feedback_value = self.feedback
        if feedback_value >= 90:
            return "green"
        elif feedback_value >= 80:
            return "orange"
        else:
            return "red"

    def __repr__(self):
        return f"<Consultant(name='{self.name}', role='{self.role}', feedback={self.feedback}%)>"


class ConsultantFeedback(Base):
    """
    Modelo de feedback de consultor
    Armazena comentários/avaliações textuais e numéricas sobre consultores
    Apenas usuários do mesmo parceiro podem criar feedbacks
    """
    __tablename__ = 'consultant_feedbacks'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey('consultants.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=True)  # Feedback específico de um contrato
    comment = Column(String(2000), nullable=False)  # Texto do feedback
    rating = Column(Integer, nullable=True)  # Nota numérica (0-100) para cálculo da média
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    consultant = relationship("Consultant", back_populates="feedback_comments")
    user = relationship("User", back_populates="feedbacks")
    contract = relationship("Contract")

    def __repr__(self):
        return f"<ConsultantFeedback(consultant_id='{self.consultant_id}', user_id='{self.user_id}')>"


class Timesheet(Base):
    """
    Timesheet (anexo) validado pelo cliente
    """
    __tablename__ = 'timesheets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey('contracts.id'), nullable=False)
    consultant_id = Column(UUID(as_uuid=True), ForeignKey('consultants.id'), nullable=True)
    file_url = Column(String(1000), nullable=True)               # anexo (caminho/URL do excel)
    hours = Column(Numeric(10, 2), nullable=False, default=0)    # número de horas consumidas
    approver = Column(String(255), nullable=True)                # nome do aprovador
    approval_date = Column(DateTime, nullable=True)              # data da aprovação
    approved = Column(Boolean, default=False, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relacionamentos
    contract = relationship("Contract", back_populates="timesheets")
    consultant = relationship("Consultant", back_populates="timesheets")

    def __repr__(self):
        return f"<Timesheet(contract_id='{self.contract_id}', hours_consumed={self.hours_consumed})>"

