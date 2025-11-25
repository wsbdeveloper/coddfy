"""
Configuração do pshell (Pyramid Shell)
Permite interagir com a aplicação via shell interativo
"""
from backend.models import *  # noqa


def setup(env):
    """
    Configura o ambiente do pshell
    
    Args:
        env: Dicionário com o ambiente do shell
    """
    request = env['request']
    
    # Adiciona o dbsession ao ambiente
    env['db'] = request.dbsession
    
    # Adiciona os modelos ao ambiente
    env['User'] = User
    env['Client'] = Client
    env['Contract'] = Contract
    env['Installment'] = Installment
    env['Consultant'] = Consultant
    
    # Adiciona transaction ao ambiente
    import transaction
    env['transaction'] = transaction
    
    print("=" * 80)
    print("🐍 Coddfy Contracts Manager CCM - Interactive Shell")
    print("=" * 80)
    print("Available objects:")
    print("  - db: Database session")
    print("  - transaction: Transaction manager")
    print("  - Models: User, Client, Contract, Installment, Consultant")
    print("=" * 80)

















