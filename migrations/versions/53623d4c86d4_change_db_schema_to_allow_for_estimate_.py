"""Change db schema to allow for estimate pins

Revision ID: 53623d4c86d4
Revises: eec4e83beadf
Create Date: 2020-09-28 23:14:01.042543

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '53623d4c86d4'
down_revision = 'eec4e83beadf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('country',
    sa.Column('country_id', postgresql.UUID(), nullable=False),
    sa.Column('country_name', sa.String(length=128), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('country_id')
    )
    op.add_column('airtable_source', sa.Column('country_id', postgresql.UUID(), nullable=True))
    op.drop_column('airtable_source', 'country')
    op.add_column('city', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('city', sa.Column('longitude', sa.Float(), nullable=True))
    op.add_column('state', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('state', sa.Column('longitude', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('state', 'longitude')
    op.drop_column('state', 'latitude')
    op.drop_column('city', 'longitude')
    op.drop_column('city', 'latitude')
    op.add_column('airtable_source', sa.Column('country', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.drop_column('airtable_source', 'country_id')
    op.drop_table('country')
    # ### end Alembic commands ###
