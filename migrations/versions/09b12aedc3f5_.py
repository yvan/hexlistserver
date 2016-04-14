"""empty message

Revision ID: 09b12aedc3f5
Revises: None
Create Date: 2016-04-13 18:31:37.539357

"""

# revision identifiers, used by Alembic.
revision = '09b12aedc3f5'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hex_objects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('image_path', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('hex_links',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('hex_object_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['hex_object_id'], ['hex_objects.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('hex_links')
    op.drop_table('hex_objects')
    ### end Alembic commands ###
