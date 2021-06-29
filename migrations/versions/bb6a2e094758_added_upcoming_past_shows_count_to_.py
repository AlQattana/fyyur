"""added upcoming/past shows count to artist table

Revision ID: bb6a2e094758
Revises: 5c6858ffb706
Create Date: 2021-06-22 13:58:44.239127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb6a2e094758'
down_revision = '5c6858ffb706'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('upcoming_shows_count', sa.Integer(), nullable=True))
    op.add_column('artist', sa.Column('past_shows_count', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artist', 'past_shows_count')
    op.drop_column('artist', 'upcoming_shows_count')
    # ### end Alembic commands ###
