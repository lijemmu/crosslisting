"""added columns for country and first/last name

Revision ID: c185e2950045
Revises: fe6880ffd570
Create Date: 2022-07-29 18:54:34.132058

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c185e2950045'
down_revision = 'fe6880ffd570'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('first_name', sa.String(), nullable=False))
    op.add_column('user', sa.Column('last_name', sa.String(), nullable=False))
    op.add_column('user', sa.Column('country', sa.String(), nullable=False))
    op.alter_column('user', 'profile_pic',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
    op.drop_constraint('user_username_key', 'user', type_='unique')
    op.drop_column('user', 'username')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', sa.VARCHAR(length=20), autoincrement=False, nullable=False))
    op.create_unique_constraint('user_username_key', 'user', ['username'])
    op.alter_column('user', 'profile_pic',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
    op.drop_column('user', 'country')
    op.drop_column('user', 'last_name')
    op.drop_column('user', 'first_name')
    # ### end Alembic commands ###