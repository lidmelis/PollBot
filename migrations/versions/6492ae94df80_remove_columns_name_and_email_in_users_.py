"""remove_columns_name_and_email_in_users_table

Revision ID: 6492ae94df80
Revises: 588a63aaf2ff
Create Date: 2025-02-03 19:10:34.764542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6492ae94df80'
down_revision: Union[str, None] = '588a63aaf2ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Удаляем столбцы name и email
    op.drop_column('users', 'name')
    op.drop_column('users', 'email')

def downgrade():
    # Восстанавливаем удаленные столбцы с их исходными параметрами
    op.add_column('users',
        sa.Column('name', sa.String(), nullable=False)
    )
    op.add_column('users',
        sa.Column('email', sa.String(), unique=True, index=True, nullable=False)
    )
