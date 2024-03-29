"""moving subgroup var

Revision ID: 6d154dc9fa83
Revises: d09ee853c6fa
Create Date: 2021-05-20 22:54:32.100983

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d154dc9fa83'
down_revision = 'd09ee853c6fa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dashboard_source', sa.Column('subgroup_var', sa.String(), nullable=True))
    op.drop_column('research_source', 'subgroup_var')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('research_source', sa.Column('subgroup_var', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('dashboard_source', 'subgroup_var')
    # ### end Alembic commands ###
