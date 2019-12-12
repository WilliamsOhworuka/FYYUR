"""empty message

Revision ID: c7a9711e64f4
Revises: 8aa275bb9d4d
Create Date: 2019-12-10 18:59:43.144972

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c7a9711e64f4'
down_revision = '8aa275bb9d4d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
    op.drop_column('Artist', 'genre')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('genre', postgresql.ARRAY(sa.VARCHAR(length=120)), autoincrement=False, nullable=True))
    op.drop_column('Artist', 'genres')
    # ### end Alembic commands ###