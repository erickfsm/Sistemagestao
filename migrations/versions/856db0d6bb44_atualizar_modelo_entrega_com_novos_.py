"""Atualizar modelo Entrega com novos campos

Revision ID: 856db0d6bb44
Revises: b2ec09a46ce7
Create Date: 2025-07-20 02:10:07.498670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '856db0d6bb44'
down_revision = 'b2ec09a46ce7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('entregas', schema=None) as batch_op:
        batch_op.alter_column('VLTOTAL',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=False)
        batch_op.alter_column('TOTPESO',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('entregas', schema=None) as batch_op:
        batch_op.alter_column('TOTPESO',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=False)
        batch_op.alter_column('VLTOTAL',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=False)

    # ### end Alembic commands ###
