"""add vaccination policy column

Revision ID: 3d3b45cb6ce4
Revises: 70bae1ca82e9
Create Date: 2021-05-02 18:56:00.708275

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d3b45cb6ce4'
down_revision = '70bae1ca82e9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dashboard_source', sa.Column('vaccination_policy', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dashboard_source', 'vaccination_policy')
    # ### end Alembic commands ###