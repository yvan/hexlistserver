"""empty message

Revision ID: e1753cce6c25
Revises: 77792d0403d4
Create Date: 2016-06-11 16:18:46.411730

"""

# revision identifiers, used by Alembic.
revision = 'e1753cce6c25'
down_revision = '77792d0403d4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ios_hex_locations',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_object_id', sa.String(), nullable=True),
    sa.Column('hex_object_id', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['hex_object_id'], ['hex_objects.id'], ),
    sa.ForeignKeyConstraint(['user_object_id'], ['user_objects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ios_hex_locations')
    ### end Alembic commands ###