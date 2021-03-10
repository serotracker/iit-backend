"""adding date_created and last_modified_time

Revision ID: 637c0739c860
Revises: 768541e19c09
Create Date: 2021-03-07 13:41:46.386979

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '637c0739c860'
down_revision = '768541e19c09'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('research_source', sa.Column('date_created', sa.DateTime(), nullable=True))
    op.add_column('research_source', sa.Column('last_modified_time', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('research_source', 'last_modified_time')
    op.drop_column('research_source', 'date_created')
    # ### end Alembic commands ###
