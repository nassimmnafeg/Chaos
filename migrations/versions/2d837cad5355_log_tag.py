"""log tag

Revision ID: 2d837cad5355
Revises: 47373934eb62
Create Date: 2019-05-15 15:49:08.934797

"""

# revision identifiers, used by Alembic.
revision = '2d837cad5355'
down_revision = '47373934eb62'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    # create tag table in history
    op.create_table(
        'tag',
        sa.Column('id',                 sa.Integer(),   nullable=False, autoincrement=True),
        sa.Column('public_id',          UUID(),         nullable=False),
        sa.Column('public_name',        sa.Text(),      nullable=False),
        sa.Column('public_is_visible',  sa.Boolean(),   nullable=False),
        sa.Column('public_client_id',   UUID(),         nullable=False),
        sa.Column('public_created_at',  sa.DateTime(),  nullable=False),
        sa.Column('public_updated_at',  sa.DateTime(),  nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='history'
    )

    # copy active tags from public schema in order to find public id
    copy_table_query = (
        'INSERT INTO history.tag ('
        '   public_id,'
        '   public_name,'
        '   public_is_visible,'
        '   public_client_id,'
        '   public_created_at,'
        '   public_updated_at'
        ')'
        '   SELECT '
        '       id,'
        '       name,'
        '       True,'
        '       client_id,'
        '       created_at,'
        '       updated_at'
        '   FROM '
        '       public.tag '
        '   WHERE '
        '       is_visible = True'
        ';'
    )
    op.execute(copy_table_query)

    # create history logger function
    log_tag_history_function = (
        'CREATE OR REPLACE FUNCTION log_tag_history() RETURNS TRIGGER '
        'AS $log_tag_history$ '
        '    BEGIN'
        '        INSERT INTO history.tag ('
        '              public_id,'
        '              public_name,'
        '              public_is_visible,'
        '              public_client_id,'
        '              public_created_at,'
        '              public_updated_at'
        '        ) VALUES ('
        '              NEW.id,'
        '              NEW.name,'
        '              NEW.is_visible,'
        '              NEW.client_id,'
        '              NEW.created_at,'
        '              NEW.updated_at'
        '        );'
        '        RETURN NULL;'
        '    END;'
        ' $log_tag_history$ LANGUAGE plpgsql;'
    )

    op.execute(log_tag_history_function)

    # create history logger trigger
    create_tag_history_trigger = (
        'CREATE TRIGGER log_tag_history '
        '   AFTER INSERT OR UPDATE ON public.tag '
        '       FOR EACH ROW EXECUTE PROCEDURE log_tag_history()'
    )
    op.execute(create_tag_history_trigger)


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS log_tag_history ON public.tag')
    op.execute('DROP FUNCTION IF EXISTS public.log_tag_history()')
    op.drop_table('tag', schema='history')
