"""event

Revision ID: 14c970aeaad6
Revises: 41e20938e9b1
Create Date: 2024-09-19 17:20:02.532366

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "14c970aeaad6"
down_revision: Union[str, None] = "41e20938e9b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("messages")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "messages",
        sa.Column("id", sa.UUID(), autoincrement=False, nullable=False),
        sa.Column("event_name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint("id", name="messages_pkey"),
    )
    # ### end Alembic commands ###