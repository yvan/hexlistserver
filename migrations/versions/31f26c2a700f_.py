"""empty message

Revision ID: 31f26c2a700f
Revises: 4c2c29343aca
Create Date: 2016-04-15 11:13:58.711566

"""

# revision identifiers, used by Alembic.
revision = '31f26c2a700f'
down_revision = '4c2c29343aca'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_constraint('hex_objects_user_id_fkey', 'hex_objects', type_='foreignkey')
    op.drop_constraint('hex_objects_owner_id_fkey', 'hex_objects', type_='foreignkey')
    op.drop_table('users')
    op.create_foreign_key(None, 'hex_objects', 'user_objects', ['user_id'], ['id'])
    op.create_foreign_key(None, 'hex_objects', 'user_objects', ['owner_id'], ['id'])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'hex_objects', type_='foreignkey')
    op.drop_constraint(None, 'hex_objects', type_='foreignkey')
    op.create_foreign_key('hex_objects_owner_id_fkey', 'hex_objects', 'users', ['owner_id'], ['id'])
    op.create_foreign_key('hex_objects_user_id_fkey', 'hex_objects', 'users', ['user_id'], ['id'])
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    op.drop_table('user_objects')
    ### end Alembic commands ###
