"""empty message

Revision ID: c93648f20c64
Revises: cde00db71228
Create Date: 2016-05-30 20:58:52.883495

"""

# revision identifiers, used by Alembic.
revision = 'c93648f20c64'
down_revision = 'cde00db71228'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('send_objects', 'location')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('send_objects', sa.Column('location', sa.VARCHAR(), autoincrement=False, nullable=True))
    ### end Alembic commands ###
