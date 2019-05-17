"""log_disruption

Revision ID: 47373934eb62
Revises: 3f16aa47af6d
Create Date: 2019-05-15 15:03:57.200188

"""

# revision identifiers, used by Alembic.
revision = '47373934eb62'
down_revision = '3f16aa47af6d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


def upgrade():
    # create disruption table in history
    op.create_table(
        'disruption',
        sa.Column('id',                             sa.Integer(),   nullable=False, autoincrement=True),
        sa.Column('public_id',                      UUID(),         nullable=False),
        sa.Column('public_reference',               sa.Text(),      nullable=True),
        sa.Column('public_note',                    sa.Text(),      nullable=True),
        sa.Column('public_status',                  sa.Text(),      nullable=False),
        sa.Column('public_end_publication_date',    sa.DateTime(),  nullable=True),
        sa.Column('public_start_publication_date',  sa.DateTime(),  nullable=True),
        sa.Column('public_cause_id',                UUID(),         nullable=False),
        sa.Column('public_client_id',               UUID(),         nullable=False),
        sa.Column('public_contributor_id',          UUID(),         nullable=False),
        sa.Column('public_version',                 sa.Integer(),   nullable=False),
        sa.Column('public_created_at',              sa.DateTime(),  nullable=True),
        sa.Column('public_updated_at',              sa.DateTime(),  nullable=True),
        sa.PrimaryKeyConstraint('id'),
        schema='history'
    )

    # copy disruptions from public schema into history
    copy_table_query = (
        'INSERT INTO history.disruption ('
        '       public_id,'
        '       public_reference,'
        '       public_note,'
        '       public_status,'
        '       public_end_publication_date,'
        '       public_start_publication_date,'
        '       public_cause_id,'
        '       public_client_id,'
        '       public_contributor_id,'
        '       public_version,'
        '       public_created_at,'
        '       public_updated_at'
        ')'
        '   SELECT '
        '       id,'
        '       reference,'
        '       note,'
        '       status,'
        '       end_publication_date,'
        '       start_publication_date,'
        '       cause_id,'
        '       client_id,'
        '       contributor_id,'
        '       version,'
        '       created_at,'
        '       updated_at'
        '   FROM '
        '       public.disruption '
        '   WHERE '
        '       status != \'archived\''
        ';'
    )
    op.execute(copy_table_query)

    # create history logger function
    log_disruption_history_function = (
        'CREATE OR REPLACE FUNCTION log_disruption_history() RETURNS TRIGGER '
        'AS $log_disruption_history$ '
        '    BEGIN'
        '        INSERT INTO history.disruption ('
        '              public_id,'
        '              public_reference,'
        '              public_note,'
        '              public_status,'
        '              public_end_publication_date,'
        '              public_start_publication_date,'
        '              public_cause_id,'
        '              public_client_id,'
        '              public_contributor_id,'
        '              public_version'
        '        ) VALUES ('
        '              NEW.id,'
        '              NEW.reference,'
        '              NEW.note,'
        '              NEW.status,'
        '              NEW.end_publication_date,'
        '              NEW.start_publication_date,'
        '              NEW.cause_id,'
        '              NEW.client_id,'
        '              NEW.contributor_id,'
        '              NEW.version'
        '        );'
        '        RETURN NULL;'
        '    END;'
        ' $log_disruption_history$ LANGUAGE plpgsql;'
    )

    op.execute(log_disruption_history_function)

    # create history logger trigger
    create_disruption_history_trigger = (
        'CREATE TRIGGER log_disruption_history '
        '   AFTER INSERT OR UPDATE ON public.disruption '
        '       FOR EACH ROW EXECUTE PROCEDURE log_disruption_history()'
    )
    op.execute(create_disruption_history_trigger)


def downgrade():
    op.execute('DROP TRIGGER IF EXISTS log_disruption_history ON public.disruption')
    op.execute('DROP FUNCTION IF EXISTS public.log_disruption_history()')
    op.drop_table('disruption', schema='history')

