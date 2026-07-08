"""add transport guardian fields and comments

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-07-08 06:30:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: str | None = 'b2c3d4e5f6a7'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'transport_records',
        sa.Column('guardian_name', sa.String(length=50), nullable=False, server_default=''),
    )
    op.add_column(
        'transport_records',
        sa.Column('guardian_code', sa.String(length=12), nullable=False, server_default=''),
    )
    op.create_table(
        'transport_comments',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.BigInteger(), nullable=False),
        sa.Column('guardian_name', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('medical', sa.Integer(), nullable=True),
        sa.Column('driving', sa.Integer(), nullable=True),
        sa.Column('hygiene', sa.Integer(), nullable=True),
        sa.Column('recommend', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['record_id'], ['transport_records.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_transport_comments_record_id'),
        'transport_comments',
        ['record_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_transport_comments_record_id'), table_name='transport_comments')
    op.drop_table('transport_comments')
    op.drop_column('transport_records', 'guardian_code')
    op.drop_column('transport_records', 'guardian_name')
