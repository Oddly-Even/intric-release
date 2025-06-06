"""change size tables type
Revision ID: c22bf19371cb
Revises: eb2ae95163b6
Create Date: 2025-02-05 17:55:41.383431
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = 'c22bf19371cb'
down_revision = 'eb2ae95163b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('groups', 'size', type_=sa.BigInteger())
    op.alter_column('websites', 'size', type_=sa.BigInteger())
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('websites', 'size', type_=sa.INTEGER())
    op.alter_column('groups', 'size', type_=sa.INTEGER())
    # ### end Alembic commands ###
