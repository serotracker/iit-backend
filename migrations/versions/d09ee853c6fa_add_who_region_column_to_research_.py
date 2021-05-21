"""Add who region column to research source tbl

Revision ID: d09ee853c6fa
Revises: 0c66a0480d6a
Create Date: 2021-05-18 15:37:13.971917

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd09ee853c6fa'
down_revision = '0c66a0480d6a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('research_source', sa.Column('who_region', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('research_source', 'who_region')
    # ### end Alembic commands ###