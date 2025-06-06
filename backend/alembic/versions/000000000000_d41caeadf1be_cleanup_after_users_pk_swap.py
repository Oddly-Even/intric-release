"""cleanup after users pk swap
Revision ID: d41caeadf1be
Revises: 4250ee2d2a02
Create Date: 2024-07-08 08:08:11.157419
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic
revision = 'd41caeadf1be'
down_revision = '4250ee2d2a02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'api_keys', ['user_id'])
    op.alter_column('assistants', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('files', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('groups', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('info_blobs', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.create_index(
        op.f('ix_info_blobs_user_id'), 'info_blobs', ['user_id'], unique=False
    )
    op.alter_column('jobs', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('services', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('sessions', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('widgets', 'user_id', existing_type=sa.UUID(), nullable=False)
    op.alter_column('workflows', 'user_id', existing_type=sa.UUID(), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('workflows', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('widgets', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('sessions', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('services', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('jobs', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.drop_index(op.f('ix_info_blobs_user_id'), table_name='info_blobs')
    op.alter_column('info_blobs', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('groups', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('files', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.alter_column('assistants', 'user_id', existing_type=sa.UUID(), nullable=True)
    op.drop_constraint(None, 'api_keys', type_='unique')
    # ### end Alembic commands ###
