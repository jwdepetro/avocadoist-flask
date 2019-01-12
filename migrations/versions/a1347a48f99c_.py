"""empty message

Revision ID: a1347a48f99c
Revises: 07605384c737
Create Date: 2018-11-11 20:09:00.098976

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1347a48f99c'
down_revision = '07605384c737'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('meta_description', sa.String(length=100000), nullable=True))
    op.add_column('post', sa.Column('meta_title', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'meta_title')
    op.drop_column('post', 'meta_description')
    # ### end Alembic commands ###