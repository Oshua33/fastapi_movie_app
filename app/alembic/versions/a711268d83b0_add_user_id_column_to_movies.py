"""Add user_id column to movies

Revision ID: a711268d83b0
Revises: 
Create Date: 2024-07-23 17:13:20.460382

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a711268d83b0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the user_id column to the movies table
    op.add_column('movies', sa.Column('user_id', sa.Integer(), nullable=True))
    # Optionally, add a foreign key constraint
    op.create_foreign_key('fk_movies_user', 'movies', 'users', ['user_id'], ['id'])

def downgrade() -> None:
    # Drop the foreign key constraint if it was added
    op.drop_constraint('fk_movies_user', 'movies', type_='foreignkey')
    # Remove the user_id column from the movies table
    op.drop_column('movies', 'user_id')