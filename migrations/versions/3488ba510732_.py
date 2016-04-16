"""empty message

Revision ID: 3488ba510732
Revises: 31f26c2a700f
Create Date: 2016-04-16 00:19:51.342054

"""

# revision identifiers, used by Alembic.
revision = '3488ba510732'
down_revision = '31f26c2a700f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hex_objects', sa.Column('user_object_id', sa.Integer(), nullable=True))
    op.drop_constraint('hex_objects_user_id_fkey', 'hex_objects', type_='foreignkey')
    op.create_foreign_key(None, 'hex_objects', 'user_objects', ['user_object_id'], ['id'])
    op.drop_column('hex_objects', 'user_id')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hex_objects', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'hex_objects', type_='foreignkey')
    op.create_foreign_key('hex_objects_user_id_fkey', 'hex_objects', 'user_objects', ['user_id'], ['id'])
    op.drop_column('hex_objects', 'user_object_id')
    ### end Alembic commands ###
