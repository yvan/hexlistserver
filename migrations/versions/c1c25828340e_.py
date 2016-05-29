"""empty message

Revision ID: c1c25828340e
Revises: 2b3fb49d49c1
Create Date: 2016-05-29 15:06:18.733088

"""

# revision identifiers, used by Alembic.
revision = 'c1c25828340e'
down_revision = '2b3fb49d49c1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ios_hex_locations',
    sa.Column('hex_object_id', sa.String(), nullable=False),
    sa.Column('location', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['hex_object_id'], ['hex_objects.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('hex_object_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ios_hex_locations')
    ### end Alembic commands ###
