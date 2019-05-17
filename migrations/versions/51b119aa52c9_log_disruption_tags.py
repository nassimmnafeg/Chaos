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
        sa.Column('triggered_by',    sa.Text(),     nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='history'
    )

    # create history logger function
    log_associate_disruption_tag_history_function = (
        'CREATE OR REPLACE FUNCTION log_associate_disruption_tag_history() RETURNS TRIGGER '
        'AS $log_associate_disruption_tag_history$ '
        ' DECLARE '
        '   history_tag_id int;'
        '   history_disruption_id int;'
        ''
        '    BEGIN'
        '       history_tag_id = (SELECT id FROM history.tag AS ht WHERE ht.public_id = NEW.tag_id ORDER BY ht.id DESC LIMIT 1);'
        '       history_disruption_id = (SELECT id FROM history.disruption AS hd WHERE hd.public_id = NEW.disruption_id ORDER BY hd.id DESC LIMIT 1);'
        '       '
        '       DELETE FROM history.associate_disruption_tag AS hadt WHERE hadt.disruption_id = history_disruption_id AND triggered_by = \'log_disruption_history_changing\';'
        '       INSERT INTO history.associate_disruption_tag (tag_id, disruption_id, triggered_by) VALUES (history_tag_id, history_disruption_id, \'log_associate_disruption_tag_history\');'
        '       RETURN NULL;'
        '    END;'
        ' $log_associate_disruption_tag_history$ LANGUAGE plpgsql;'
    )

    log_disruption_history_changing = (
        'CREATE OR REPLACE FUNCTION log_disruption_history_changing() RETURNS TRIGGER '
        'AS $BODY$ '
        ' DECLARE '
        '        disruption_tags_count int; '
        '        tag_id int; '
        '        disruption_id int; '
        ''
        '    BEGIN'
        '        disruption_id = NEW.ID;'
        '        disruption_tags_count = (SELECT COUNT(1) FROM history.associate_disruption_tag hadt WHERE hadt.disruption_id = NEW.ID);'
        '        IF disruption_tags_count <1 THEN'
        '            FOR tag_id IN SELECT id AS tag_id FROM history.tag AS ht WHERE ht.public_id IN ( SELECT padt.tag_id FROM public.associate_disruption_tag AS padt WHERE  padt.disruption_id = (SELECT hd.public_id FROM history.disruption AS hd WHERE hd.id = NEW.id)) LOOP'
        '                INSERT INTO history.associate_disruption_tag (tag_id, disruption_id, triggered_by) VALUES (tag_id, NEW.ID, \'log_disruption_history_changing\');'
        '            END LOOP;'
        '       END IF;'
        '       RETURN NULL;'
        '    END;'
        ' $BODY$ LANGUAGE plpgsql;'
    )

    op.execute(log_associate_disruption_tag_history_function)
    op.execute(log_disruption_history_changing)

    # create history logger trigger
    create_associate_disruption_tag_history_trigger = (
        'CREATE TRIGGER log_associate_disruption_tag_history '
        '   AFTER INSERT OR UPDATE ON public.associate_disruption_tag '
        '       FOR EACH ROW EXECUTE PROCEDURE log_associate_disruption_tag_history()'
    )
    op.execute(create_associate_disruption_tag_history_trigger)

    log_disruption_history_changing_trigger = (
        'CREATE TRIGGER log_disruption_history_changing '
        '   AFTER INSERT OR UPDATE ON history.disruption '
        '       FOR EACH ROW EXECUTE PROCEDURE log_disruption_history_changing()'
    )
    op.execute(log_disruption_history_changing_trigger)

def downgrade():
    op.execute('DROP TRIGGER IF EXISTS log_disruption_history_changing ON history.disruption')
    op.execute('DROP FUNCTION IF EXISTS history.log_disruption_history_changing()')
    op.execute('DROP TRIGGER IF EXISTS log_associate_disruption_tag_history ON public.associate_disruption_tag')
    op.execute('DROP FUNCTION IF EXISTS public.log_associate_disruption_tag_history()')
    op.drop_table('associate_disruption_tag', schema='history')
