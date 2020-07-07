"""first migration

Revision ID: 1bec6850df01
Revises: 
Create Date: 2020-07-06 22:30:10.323318

"""
from alembic import op
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '1bec6850df01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create airtable source table
    op.create_table('airtable_source',
                    Column('source_id', UUID(as_uuid=True), primary_key=True, nullable=False),
                    Column('source_name', String(128), nullable=True),
                    Column('publication_date', DateTime())
    pass


def downgrade():
    pass
