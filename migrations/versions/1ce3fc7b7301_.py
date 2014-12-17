"""Create a table contributor and add a new column contributor_id in disruption

Revision ID: 1ce3fc7b7301
Revises: 49de30166071
Create Date: 2014-12-03 12:41:13.239210

"""

# revision identifiers, used by Alembic.
revision = '1ce3fc7b7301'
down_revision = '49de30166071'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid
from datetime import datetime


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('contributor',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('id', postgresql.UUID(), nullable=False),
    sa.Column('contributor_code', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('contributor_code')
    )
    op.add_column(u'disruption', sa.Column('client_id', postgresql.UUID(), sa.ForeignKey('client.id')))
    op.add_column(u'disruption', sa.Column('contributor_id', postgresql.UUID(), sa.ForeignKey('contributor.id')))

    #Insert a contributor with code = 'contributor1' and update contributor_id
    #of the table disruption.
    connection = op.get_bind()
    op.execute("INSERT INTO contributor (created_at, id, contributor_code) VALUES ('{}', '{}', '{}')".
               format(datetime.utcnow(), str(uuid.uuid1()), 'contributor1'))
    result = connection.execute("select id from client where client_code = '{}'".format('trans'))
    row = result.first()
    if row and row['id']:
        op.execute("update disruption set client_id='{}'".format(row['id']))

    #Fetch the client with code 'trans' and update client_id in the table disruption
    result = connection.execute('select id from contributor')
    row = result.first()
    if row and row['id']:
        op.execute("update disruption set contributor_id='{}'".format(row['id']))

    #Modifiy the property of the following columns to NOT NULL
    op.execute("ALTER TABLE disruption ALTER COLUMN client_id SET NOT NULL")
    op.execute("ALTER TABLE disruption ALTER COLUMN contributor_id SET NOT NULL")
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'disruption', 'contributor_id')
    op.drop_column(u'disruption', 'client_id')
    op.drop_table('contributor')
    ### end Alembic commands ###
