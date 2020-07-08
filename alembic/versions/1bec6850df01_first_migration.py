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
                    Column('publication_date', DateTime()),
                    Column('first_author', String(64)),
                    Column('url', String(128)),
                    Column('source_type', String(64)),
                    Column('source_publisher', String(64)),
                    Column('summary', String(256)),
                    Column('study_type', String(128)),
                    Column('study_status', String(32)),
                    Column('country', String(32)),
                    Column('lead_organization', String(64)),
                    Column('sampling_start_date', DateTime),
                    Column('sampling_end_date', DateTime),
                    Column('sex', String(16)),
                    Column('sampling_method', String(128)),
                    Column('sensitivity', Float),
                    Column('specificity', Float),
                    Column('include_in_n', Boolean),
                    Column('denominator_value', Integer),
                    Column('numerator_value', Integer),
                    Column('numerator_definition', String(128)),
                    Column('serum_pos_prevalence', Float),
                    Column('overall_risk_of_bias', String(16)),
                    Column('isotype_igg', Boolean),
                    Column('isotype_igm', Boolean),
                    Column('isotype_iga', Boolean),
                    Column('created_at', DateTime))

    # Create city table
    op.create_table('city',
                    Column('city_id', UUID, primary_key=True),
                    Column('city_name', String(64)),
                    Column('created_at', DateTime))

    # Create state table
    op.create_table('state',
                    Column('state_id', UUID, primary_key=True),
                    Column('state_name', String(64)),
                    Column('created_at', DateTime))

    # Create age table
    op.create_table('age',
                    Column('age_id', UUID, primary_key=True),
                    Column('age_name', String(32)),
                    Column('created_at', DateTime))

    # Create population_group table
    op.create_table('population_group',
                    Column('population_group_id', UUID, primary_key=True),
                    Column('population_group_name', String(64)),
                    Column('created_at', DateTime))

    # Create test_manufacturer table
    op.create_table('test_manufacturer',
                    Column('test_manufacturer_id', UUID, primary_key=True),
                    Column('test_manufacturer_name', String(64)),
                    Column('created_at', DateTime))

    # Create approving_regulator table
    op.create_table('approving_regulator',
                    Column('approving_regulator_id', UUID, primary_key=True),
                    Column('approving_regulator_name', String(128)),
                    Column('created_at', DateTime))

    # Create test_type table
    op.create_table('test_type',
                    Column('test_type_id', UUID, primary_key=True),
                    Column('test_type_name', String(64)),
                    Column('created_at', DateTime))

    # Create specimen_type table
    op.create_table('specimen_type',
                    Column('specimen_type_id', UUID, primary_key=True),
                    Column('specimen_type_name', String(32)),
                    Column('created_at', DateTime))

    # Create city_bridge table
    op.create_table('city_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('city_id', UUID),
                    Column('created_at', DateTime))

    # Create state_bridge table
    op.create_table('state_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('state_id', UUID),
                    Column('created_at', DateTime))

    # Create age_bridge table
    op.create_table('age_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('age_id', UUID),
                    Column('created_at', DateTime))

    # Create population_group_bridge table
    op.create_table('population_group_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('population_group_id', UUID),
                    Column('created_at', DateTime))

    # Create test_manufacturer_bridge table
    op.create_table('test_manufacturer_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('test_manufacturer_id', UUID),
                    Column('created_at', DateTime))

    # Create approving_regulator_bridge table
    op.create_table('approving_regulator_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('approving_regulator_id', UUID),
                    Column('created_at', DateTime))

    # Create test_type_bridge table
    op.create_table('test_type_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('test_type_id', UUID),
                    Column('created_at', DateTime))

    # Create specimen_type_bridge table
    op.create_table('specimen_type_bridge',
                    Column('id', UUID, primary_key=True),
                    Column('source_id', UUID),
                    Column('specimen_type_id', UUID),
                    Column('created_at', DateTime))



def downgrade():
    # Drop all created tables
    tables = ('airtable_source', 'city', 'state', 'age', 'population_group', 'test_manufacturer', 'approving_regulator',
              'test_type', 'specimen_type', 'city_bridge', 'state_bridge', 'age_bridge', 'population_group_bridge',
              'test_manufacturer_bridge', 'approving_regulator_bridge', 'test_type_bridge', 'specimen_type_bridge')
    for table in tables:
        op.drop_table(table)
