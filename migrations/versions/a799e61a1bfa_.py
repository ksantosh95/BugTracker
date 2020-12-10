"""empty message

Revision ID: a799e61a1bfa
Revises: 905e3242e3d5
Create Date: 2020-12-09 23:56:04.024836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a799e61a1bfa'
down_revision = '905e3242e3d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notification',
    sa.Column('n_id', sa.Integer(), nullable=False),
    sa.Column('t_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('n_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('n_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notification')
    # ### end Alembic commands ###
