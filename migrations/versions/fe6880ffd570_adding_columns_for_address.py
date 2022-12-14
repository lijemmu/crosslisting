"""adding columns for address

Revision ID: fe6880ffd570
Revises: 
Create Date: 2022-07-28 20:07:55.118031

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe6880ffd570'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # adds new columns with nullable = true
    op.add_column('user', sa.Column('street_address', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('address_line2', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('city', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('state', sa.String(length=30), nullable=True))
    op.add_column('user', sa.Column('zipcode', sa.String(length=20), nullable=True))

    # sets value for empty columns
    op.execute("UPDATE \"user\" SET street_address = 'blank address'")
    op.execute("UPDATE \"user\" SET address_line2 = 'blank line 2'")
    op.execute("UPDATE \"user\" SET city = 'blank city'")
    op.execute("UPDATE \"user\" SET state = 'blank state'")
    op.execute("UPDATE \"user\" SET zipcode = 'blank zipcode'")

    # update columns to nullable = False
    op.alter_column('user', 'street_address', nullable=False)
    op.alter_column('user', 'city', nullable=False)
    op.alter_column('user', 'state', nullable=False)
    op.alter_column('user', 'zipcode', nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'zipcode')
    op.drop_column('user', 'state')
    op.drop_column('user', 'city')
    op.drop_column('user', 'address_line2')
    op.drop_column('user', 'street_address')
    # ### end Alembic commands ###
