"""empty message

Revision ID: dcbf3a9eb09e
Revises: cabb20223338
Create Date: 2016-08-06 18:14:54.231226

"""

# revision identifiers, used by Alembic.
revision = 'dcbf3a9eb09e'
down_revision = 'cabb20223338'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', type_='foreignkey')
    op.create_foreign_key(None, 'ios_hex_locations', 'hex_objects', ['hex_object_id'], ['id'])
    op.drop_constraint('link_objects_hex_object_id_fkey', 'link_objects', type_='foreignkey')
    op.create_foreign_key(None, 'link_objects', 'hex_objects', ['hex_object_id'], ['id'])
    op.drop_constraint('send_objects_hex_object_id_fkey', 'send_objects', type_='foreignkey')
    op.create_foreign_key(None, 'send_objects', 'hex_objects', ['hex_object_id'], ['id'])
    op.add_column('user_objects', sa.Column('email', sa.String(length=128), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_objects', 'email')
    op.drop_constraint(None, 'send_objects', type_='foreignkey')
    op.create_foreign_key('send_objects_hex_object_id_fkey', 'send_objects', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'link_objects', type_='foreignkey')
    op.create_foreign_key('link_objects_hex_object_id_fkey', 'link_objects', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint(None, 'ios_hex_locations', type_='foreignkey')
    op.create_foreign_key('ios_hex_locations_hex_object_id_fkey', 'ios_hex_locations', 'hex_objects', ['hex_object_id'], ['id'], ondelete='CASCADE')
    ### end Alembic commands ###