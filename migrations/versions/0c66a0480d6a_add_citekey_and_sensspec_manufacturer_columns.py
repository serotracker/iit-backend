"""add citekey and senspec manufacturer columns

Revision ID: 0c66a0480d6a
Revises: 527670956fe7
Create Date: 2021-05-16 15:39:28.445332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c66a0480d6a'
down_revision = '527670956fe7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('research_source', sa.Column('sensspec_from_manufacturer', sa.Boolean(), nullable=True))
    op.add_column('research_source', sa.Column('zotero_citation_key', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('research_source', 'zotero_citation_key')
    op.drop_column('research_source', 'sensspec_from_manufacturer')
    # ### end Alembic commands ###
