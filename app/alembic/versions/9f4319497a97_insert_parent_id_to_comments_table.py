"""Insert parent_id to comments table

Revision ID: 9f4319497a97
Revises: 74ea4518d2df
Create Date: 2024-08-02 04:54:31.769521

"""
from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '9f4319497a97'
down_revision: Union[str, None] = '74ea4518d2df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('comments', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_parent_comment', 'comments', 'comments', ['parent_id'], ['id'])

def downgrade() -> None:
    op.drop_constraint('fk_parent_comment', 'comments', type_='foreignkey')
    op.drop_column('comments', 'parent_id')
