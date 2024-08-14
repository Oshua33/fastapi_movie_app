"""drop description and parent_id columns, add genre column

Revision ID: 95492db036f6
Revises: b7f04d813486
Create Date: 2024-08-03 03:49:48.665238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '95492db036f6'
down_revision: Union[str, None] = 'b7f04d813486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop column description in movies table
    op.drop_column('movies', 'description')

    # Drop column parent_id in comments table
    op.drop_column('comments', 'parent_id')

    # Add column genre in movies table
    op.add_column('movies', sa.Column('genre', sa.String, nullable=True))



def downgrade() -> None:
    # Add column description back to movies table
    op.add_column('movies', sa.Column('description', sa.String, nullable=True))

    # Add column parent_id back to comments table
    op.add_column('comments', sa.Column('parent_id', sa.Integer, nullable=True))

    # Drop column genre from movies table
    op.drop_column('movies', 'genre')