"""Add user assignment type classification"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260204_1045_8d2d7f1c9abc'
down_revision: Union[str, None] = '8867367fbb0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    assignment_type_enum = sa.Enum('PARTNER', 'CLIENT', 'INTERNAL', name='userassignmenttype')
    assignment_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column('users', sa.Column('assignment_type', assignment_type_enum, nullable=False, server_default='PARTNER'))
    op.add_column('users', sa.Column('client_id', sa.UUID(), nullable=True))
    op.create_foreign_key(op.f('users_client_id_fkey'), 'users', 'clients', ['client_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint(op.f('users_client_id_fkey'), 'users', type_='foreignkey')
    op.drop_column('users', 'client_id')
    op.drop_column('users', 'assignment_type')
    sa.Enum('partner', 'client', 'internal', name='userassignmenttype').drop(op.get_bind(), checkfirst=True)

