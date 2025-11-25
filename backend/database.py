"""
Configuração do banco de dados SQLAlchemy
Define a sessão do banco e a base dos modelos
"""
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from zope.sqlalchemy import register

# Base declarativa para todos os models
Base = declarative_base()

# Session maker - será configurado no main
DBSession = scoped_session(sessionmaker())


def get_engine(settings, prefix='sqlalchemy.'):
    """
    Cria o engine do SQLAlchemy a partir das configurações
    
    Args:
        settings: Dicionário com as configurações da aplicação
        prefix: Prefixo das chaves de configuração do SQLAlchemy
    
    Returns:
        Engine do SQLAlchemy configurado
    """
    return engine_from_config(settings, prefix, poolclass=pool.NullPool)


def get_session_factory(engine):
    """
    Cria uma factory de sessões
    
    Args:
        engine: Engine do SQLAlchemy
    
    Returns:
        Factory de sessões configurada
    """
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Cria uma sessão gerenciada por transaction manager
    
    Args:
        session_factory: Factory de sessões
        transaction_manager: Gerenciador de transações do Pyramid
    
    Returns:
        Sessão do banco de dados
    """
    dbsession = session_factory()
    register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    Configura o banco de dados na aplicação Pyramid
    Esta função é chamada automaticamente pelo Pyramid
    
    Args:
        config: Configurator do Pyramid
    """
    settings = config.get_settings()
    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # Cria o engine
    engine = get_engine(settings)
    
    # Cria a factory de sessões
    session_factory = get_session_factory(engine)
    
    # Registra a factory no configurator
    config.registry['dbsession_factory'] = session_factory

    # Adiciona uma request method para obter a sessão do banco
    config.add_request_method(
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )

