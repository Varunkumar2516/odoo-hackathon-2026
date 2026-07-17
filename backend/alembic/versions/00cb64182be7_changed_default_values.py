"""Changed Default Values

Revision ID: 00cb64182be7
Revises: 626a8fa832d5
Create Date: 2026-07-16 23:27:01.279874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '00cb64182be7'
down_revision: Union[str, Sequence[str], None] = '626a8fa832d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # =========================
    # USERS
    # =========================
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=True,
    )

    # =========================
    # DRIVERS
    # =========================
    op.alter_column(
        "drivers",
        "safety_score",
        existing_type=sa.Float(),
        server_default=sa.text("100.0"),
        existing_nullable=True,
    )

    op.alter_column(
        "drivers",
        "status",
        existing_type=sa.String(length=30),
        server_default=sa.text("'Available'"),
        existing_nullable=False,
    )

    op.alter_column(
        "drivers",
        "updated_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=True,
    )

    # =========================
    # VEHICLES
    # =========================
    op.alter_column(
        "vehicles",
        "odometer_km",
        existing_type=sa.Float(),
        server_default=sa.text("0"),
        existing_nullable=False,
    )

    op.alter_column(
        "vehicles",
        "status",
        existing_type=sa.String(length=30),
        server_default=sa.text("'Available'"),
        existing_nullable=False,
    )

    op.alter_column(
        "vehicles",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=True,
    )

    op.alter_column(
        "vehicles",
        "updated_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=True,
    )

    # =========================
    # TRIPS
    # =========================
    op.alter_column(
        "trips",
        "status",
        existing_type=sa.String(length=30),
        server_default=sa.text("'Draft'"),
        existing_nullable=False,
    )

    op.alter_column(
        "trips",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("CURRENT_TIMESTAMP"),
        existing_nullable=True,
    )

    # =========================
    # MAINTENANCE LOGS
    # =========================
    op.alter_column(
        "maintenance_logs",
        "cost",
        existing_type=sa.Float(),
        server_default=sa.text("0"),
        existing_nullable=False,
    )

    op.alter_column(
        "maintenance_logs",
        "status",
        existing_type=sa.String(length=30),
        server_default=sa.text("'Active'"),
        existing_nullable=False,
    )


def downgrade() -> None:
    # USERS
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )

    # DRIVERS
    op.alter_column(
        "drivers",
        "safety_score",
        existing_type=sa.Float(),
        server_default=None,
    )

    op.alter_column(
        "drivers",
        "status",
        existing_type=sa.String(length=30),
        server_default=None,
    )

    op.alter_column(
        "drivers",
        "updated_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )

    # VEHICLES
    op.alter_column(
        "vehicles",
        "odometer_km",
        existing_type=sa.Float(),
        server_default=None,
    )

    op.alter_column(
        "vehicles",
        "status",
        existing_type=sa.String(length=30),
        server_default=None,
    )

    op.alter_column(
        "vehicles",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )

    op.alter_column(
        "vehicles",
        "updated_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )

    # TRIPS
    op.alter_column(
        "trips",
        "status",
        existing_type=sa.String(length=30),
        server_default=None,
    )

    op.alter_column(
        "trips",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
    )

    # MAINTENANCE LOGS
    op.alter_column(
        "maintenance_logs",
        "cost",
        existing_type=sa.Float(),
        server_default=None,
    )

    op.alter_column(
        "maintenance_logs",
        "status",
        existing_type=sa.String(length=30),
        server_default=None,
    )