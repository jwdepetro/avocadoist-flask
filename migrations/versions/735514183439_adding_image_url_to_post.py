"""adding image_url to post

Revision ID: 735514183439
Revises: d87130c5bce9
Create Date: 2018-09-27 21:12:35.866232

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '735514183439'
down_revision = 'd87130c5bce9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('image_url', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'image_url')
    # ### end Alembic commands ###
