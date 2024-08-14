"""Insert created_at  to comments table

Revision ID: b7f04d813486
Revises: 9f4319497a97
Create Date: 2024-08-02 06:30:33.511134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7f04d813486'
down_revision: Union[str, None] = '9f4319497a97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('comments', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))

def downgrade() -> None:
    op.drop_column('comments', 'created_at')