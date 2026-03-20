"""add groups and group members

Revision ID: 2f4d8e6a9b11
Revises: 687fc878c17b
Create Date: 2026-03-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f4d8e6a9b11"
down_revision: Union[str, None] = "687fc878c17b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "grupos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(), nullable=False),
        sa.Column("criado_por_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["criado_por_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grupos_id"), "grupos", ["id"], unique=False)
    op.create_index(op.f("ix_grupos_criado_por_id"), "grupos", ["criado_por_id"], unique=False)

    op.create_table(
        "grupo_membros",
        sa.Column("grupo_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("grupo_id", "user_id"),
    )

    op.add_column("items", sa.Column("grupo_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_items_grupo_id"), "items", ["grupo_id"], unique=False)
    op.create_foreign_key(
        "fk_items_grupo_id_grupos",
        "items",
        "grupos",
        ["grupo_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_items_grupo_id_grupos", "items", type_="foreignkey")
    op.drop_index(op.f("ix_items_grupo_id"), table_name="items")
    op.drop_column("items", "grupo_id")

    op.drop_table("grupo_membros")

    op.drop_index(op.f("ix_grupos_criado_por_id"), table_name="grupos")
    op.drop_index(op.f("ix_grupos_id"), table_name="grupos")
    op.drop_table("grupos")
