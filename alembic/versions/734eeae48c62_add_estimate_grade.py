"""add_estimate_grade

Revision ID: 734eeae48c62
Revises: 1bec6850df01
Create Date: 2020-08-14 12:16:22.848105

"""
from alembic import op
from sqlalchemy import Column, String


# revision identifiers, used by Alembic.
revision = '734eeae48c62'
down_revision = '1bec6850df01'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('airtable_source', Column('estimate_grade', String(32)))


def downgrade():
    op.drop_column('airtable_source', 'estimate_grade')
