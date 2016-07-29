"""empty message

Revision ID: cabb20223338
Revises: 60c17f103996
Create Date: 2016-07-28 16:21:23.161520

"""

# revision identifiers, used by Alembic.
revision = 'cabb20223338'
down_revision = '60c17f103996'

from alembic import op
import sqlalchemy as sa

# this upgrade will allow us to delete a hex with all its
# associated data
def upgrade():
    # drop the constraint on hex_objects link_objects, send_objects, and ios_hex_locations
    op.drop_constraint('link_objects_hex_object_id_fkey', 'link_objects', type="foreignkey")
    op.drop_constraint('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', type="foreignkey")
    op.drop_constraint('send_objects_hex_object_id_fkey', 'send_objects', type="foreignkey")

    # create a new constraint with cascade
    op.create_foreign_key('link_objects_hex_object_id_fkey', 'link_objects', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('send_objects_hex_object_id_fkey', 'send_objects', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')

def downgrade():
    # drop the constraint on hex_objects link_objects, send_objects, and ios_hex_locations
    op.drop_constraint('link_objects_hex_object_id_fkey', 'link_objects', type="foreignkey")
    op.drop_constraint('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', type="foreignkey")
    op.drop_constraint('send_objects_hex_object_id_fkey', 'send_objects', type="foreignkey")

    # create a new constraint with cascade
    op.create_foreign_key('link_objects_hex_object_id_fkey', 'link_objects', 'hex_objects', ['hex_object_id'], ['id'])
    op.create_foreign_key('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', 'hex_objects', ['hex_object_id'])
    op.create_foreign_key('send_objects_hex_object_id_fkey', 'send_objects', 'hex_objects', ['hex_object_id'], ['id'])

