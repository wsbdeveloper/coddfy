"""add timesheet created_at column"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260205_0915_add_ts_created'
down_revision: Union[str, None] = '20260204_1045_8d2d7f1c9abc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'timesheets',
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )


def downgrade() -> None:
    op.drop_column('timesheets', 'created_at')

