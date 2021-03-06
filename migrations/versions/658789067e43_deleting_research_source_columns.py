"""deleting research source columns

Revision ID: 658789067e43
Revises: 91e8600aac0d
Create Date: 2021-01-31 19:25:15.695362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '658789067e43'
down_revision = '91e8600aac0d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('research_source', 'genpop')
    op.drop_column('research_source', 'jbi_7')
    op.drop_column('research_source', 'gbd_subregion')
    op.drop_column('research_source', 'average_age')
    op.drop_column('research_source', 'jbi_8')
    op.drop_column('research_source', 'jbi_6')
    op.drop_column('research_source', 'test_validation')
    op.drop_column('research_source', 'lmic_hic')
    op.drop_column('research_source', 'measure_of_age')
    op.drop_column('research_source', 'gbd_region')
    op.drop_column('research_source', 'age_variation')
    op.drop_column('research_source', 'subgroup_cat')
    op.drop_column('research_source', 'jbi_5')
    op.drop_column('research_source', 'jbi_3')
    op.drop_column('research_source', 'subgroup_var')
    op.drop_column('research_source', 'ind_eval_lab')
    op.drop_column('research_source', 'jbi_4')
    op.drop_column('research_source', 'jbi_2')
    op.drop_column('research_source', 'age_variation_measure')
    op.drop_column('research_source', 'jbi_1')
    op.drop_column('research_source', 'sampling_type')
    op.drop_column('research_source', 'jbi_9')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('research_source', sa.Column('jbi_9', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('sampling_type', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_1', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('age_variation_measure', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_2', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_4', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('ind_eval_lab', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('subgroup_var', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_3', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_5', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('subgroup_cat', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('age_variation', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('gbd_region', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('measure_of_age', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('lmic_hic', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('test_validation', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_6', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_8', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('average_age', sa.VARCHAR(length=256), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('gbd_subregion', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('jbi_7', sa.VARCHAR(length=16), autoincrement=False, nullable=True))
    op.add_column('research_source', sa.Column('genpop', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
