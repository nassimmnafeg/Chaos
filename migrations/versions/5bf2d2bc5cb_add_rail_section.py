"""Add rail section table

Revision ID: 5bf2d2bc5cb
Revises: 6b24727c1bb
Create Date: 2021-01-22 13:59:47.907869

"""

# revision identifiers, used by Alembic.
revision = '5bf2d2bc5cb'
down_revision = '6b24727c1bb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('rail_section',
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('line_object_id', postgresql.UUID(), nullable=True),
    sa.Column('start_object_id', postgresql.UUID(), nullable=False),
    sa.Column('end_object_id', postgresql.UUID(), nullable=False),
    sa.Column('blocked_stop_areas', sa.Text(), nullable=False),
    sa.Column('route_patterns', sa.Text(), nullable=False),
    sa.Column('object_id', postgresql.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['line_object_id'], [u'pt_object.id'], ),
    sa.ForeignKeyConstraint(['object_id'], [u'pt_object.id'], ),
    sa.ForeignKeyConstraint(['start_object_id'], [u'pt_object.id'], ),
    sa.ForeignKeyConstraint(['end_object_id'], [u'pt_object.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.execute("COMMIT")  # See https://bitbucket.org/zzzeek/alembic/issue/123
    op.execute("ALTER TYPE pt_object_type ADD VALUE 'rail_section'")


def downgrade():
    op.drop_table('rail_section')
    op.execute("ALTER TABLE pt_object ALTER COLUMN type TYPE text")
    op.execute("DELETE FROM pt_object WHERE  type='rail_section'")
    op.execute("DROP TYPE pt_object_type")
    op.execute("CREATE TYPE pt_object_type AS ENUM ('network', 'stop_area', 'line', 'line_section','route', 'stop_point')")
    op.execute("ALTER TABLE pt_object ALTER COLUMN type TYPE pt_object_type USING type::pt_object_type")
