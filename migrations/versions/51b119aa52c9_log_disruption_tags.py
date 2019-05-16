"""log disruption_tags

Revision ID: 51b119aa52c9
Revises: 2d837cad5355
Create Date: 2019-05-15 16:22:19.359522

"""

# revision identifiers, used by Alembic.
revision = '51b119aa52c9'
down_revision = '2d837cad5355'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    op.create_table(
        'associate_disruption_tag',
        sa.Column('id',              sa.Integer(),  nullable=False, autoincrement=True),
        sa.Column('tag_id',          sa.Integer(),  nullable=False),
        sa.Column('disruption_id',   sa.Integer(),  nullable=False),
        sa.PrimaryKeyConstraint('id'),
        schema='history'
    )

    # create history logger function
    log_associate_disruption_tag_history_function = (
        'CREATE OR REPLACE FUNCTION log_associate_disruption_tag_history() RETURNS TRIGGER '
        'AS $log_associate_disruption_tag_history$ '
        ' DECLARE '
        '   tag_id int;'
        '   disruption_id int;'
        ''
        '    BEGIN'
        '       tag_id = (SELECT id FROM history.tag AS ht WHERE ht.public_id = NEW.tag_id ORDER BY ht.id DESC LIMIT 1);'
        '       disruption_id = (SELECT id FROM history.disruption AS hd WHERE hd.public_id = NEW.disruption_id ORDER BY hd.id DESC LIMIT 1);'
        ''
        '       INSERT INTO history.associate_disruption_tag (tag_id, disruption_id) VALUES (tag_id, disruption_id);'
        '       RETURN NULL;'
        '    END;'
        ' $log_associate_disruption_tag_history$ LANGUAGE plpgsql;'
    )

    op.execute(log_associate_disruption_tag_history_function)

    # create history logger trigger
    create_associate_disruption_tag_history_trigger = (
        'CREATE TRIGGER log_associate_disruption_tag_history '
        '   AFTER INSERT OR UPDATE ON public.associate_disruption_tag '
        '       FOR EACH ROW EXECUTE PROCEDURE log_associate_disruption_tag_history()'
    )
    op.execute(create_associate_disruption_tag_history_trigger)


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS log_associate_disruption_tag_history ON public.associate_disruption_tag')
    op.execute('DROP FUNCTION IF EXISTS public.log_associate_disruption_tag_history()')
    op.drop_table('associate_disruption_tag', schema='history')
