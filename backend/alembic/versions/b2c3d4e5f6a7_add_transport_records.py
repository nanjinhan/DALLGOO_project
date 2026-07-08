"""add transport_records

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-08 05:30:00.000000

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: str | None = 'a1b2c3d4e5f6'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'transport_records',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('patient_name', sa.String(length=50), nullable=False),
        sa.Column('from_hospital', sa.String(length=120), nullable=False),
        sa.Column('to_hospital', sa.String(length=120), nullable=False),
        sa.Column('distance_km', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration_min', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('crew', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('detail', sa.Text(), nullable=False),
        sa.Column('image_name', sa.String(length=255), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_transport_records_user_id'),
        'transport_records',
        ['user_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_transport_records_user_id'), table_name='transport_records')
    op.drop_table('transport_records')
