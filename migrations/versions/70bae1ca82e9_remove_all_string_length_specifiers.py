"""remove all String() length specifiers

Revision ID: 70bae1ca82e9
Revises: fe611d0aed1c
Create Date: 2021-04-24 10:52:00.049145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '70bae1ca82e9'
down_revision = 'fe611d0aed1c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('antibody_target', 'antibody_target_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('city', 'city_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('city', 'state_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('country', 'country_iso3',
               existing_type=sa.VARCHAR(length=4),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('country', 'country_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'age',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'estimate_grade',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'first_author',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'isotype_comb',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'lead_organization',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'overall_risk_of_bias',
               existing_type=sa.VARCHAR(length=16),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'population_group',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'sampling_method',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'sex',
               existing_type=sa.VARCHAR(length=16),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'source_publisher',
               existing_type=sa.VARCHAR(length=256),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'source_type',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'specimen_type',
               existing_type=sa.VARCHAR(length=64),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'study_type',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'test_type',
               existing_type=sa.VARCHAR(length=256),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('state', 'state_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    op.alter_column('test_manufacturer', 'test_manufacturer_name',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('test_manufacturer', 'test_manufacturer_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('state', 'state_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'test_type',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=256),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'study_type',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'specimen_type',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'source_type',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'source_publisher',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=256),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'sex',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=16),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'sampling_method',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'population_group',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'overall_risk_of_bias',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=16),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'lead_organization',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'isotype_comb',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=32),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'first_author',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'estimate_grade',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=32),
               existing_nullable=True)
    op.alter_column('dashboard_source', 'age',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=64),
               existing_nullable=True)
    op.alter_column('country', 'country_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('country', 'country_iso3',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=4),
               existing_nullable=True)
    op.alter_column('city', 'state_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('city', 'city_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    op.alter_column('antibody_target', 'antibody_target_name',
               existing_type=sa.String(),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)
    # ### end Alembic commands ###
