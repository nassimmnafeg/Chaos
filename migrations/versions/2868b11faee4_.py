"""Associate line_section and stop_areas

Revision ID: 2868b11faee4
Revises: 3963a075ac12
Create Date: 2014-09-05 16:12:12.042936

"""

# revision identifiers, used by Alembic.
revision = '2868b11faee4'
down_revision = '3963a075ac12'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('associate_line_section_via_object',
    sa.Column('line_section_id', postgresql.UUID(), nullable=True),
    sa.Column('stop_area_object_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['line_section_id'], ['line_section.id'], ),
    sa.ForeignKeyConstraint(['stop_area_object_id'], ['pt_object.id'], ),
    sa.PrimaryKeyConstraint('line_section_id', 'stop_area_object_id', name='line_section_stop_area_object_pk')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('associate_line_section_via_object')
    ### end Alembic commands ###