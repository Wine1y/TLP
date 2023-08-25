"""float_energy

Revision ID: 7366e7421d8a
Revises: 9b64b16dd3a9
Create Date: 2023-08-25 17:48:13.882868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7366e7421d8a'
down_revision: Union[str, None] = '9b64b16dd3a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.alter_column("users", "energy", type_=sa.types.FLOAT)
    except sa.exc.OperationalError:
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("energy", type_=sa.types.FLOAT)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    try:
        op.alter_column("users", "energy", type_=sa.types.Integer)
    except sa.exc.OperationalError:
        with op.batch_alter_table("users") as batch_op:
            batch_op.alter_column("energy", type_=sa.types.Integer)
    # ### end Alembic commands ###
