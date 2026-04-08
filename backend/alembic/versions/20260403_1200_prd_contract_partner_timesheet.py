"""PRD: contract type/hours, partner logo_url, timesheet filled_at"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260403_1200_prd_api'
down_revision: Union[str, None] = '20260205_0915_add_ts_created'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contracts', sa.Column('contract_type', sa.String(length=50), nullable=True))
    op.add_column(
        'contracts',
        sa.Column('estimated_monthly_hours', sa.Numeric(precision=10, scale=2), nullable=True),
    )
    op.add_column('contracts', sa.Column('duration_months', sa.Integer(), nullable=True))
    op.add_column(
        'contracts',
        sa.Column('total_hours_contracted', sa.Numeric(precision=12, scale=2), nullable=True),
    )
    op.add_column('partners', sa.Column('logo_url', sa.String(length=500), nullable=True))
    op.add_column('timesheets', sa.Column('filled_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('timesheets', 'filled_at')
    op.drop_column('partners', 'logo_url')
    op.drop_column('contracts', 'total_hours_contracted')
    op.drop_column('contracts', 'duration_months')
    op.drop_column('contracts', 'estimated_monthly_hours')
    op.drop_column('contracts', 'contract_type')
