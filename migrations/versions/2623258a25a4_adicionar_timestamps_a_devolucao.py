"""Adicionar timestamps a Devolucao

Revision ID: 2623258a25a4
Revises: 8c1feb8ae0fd
Create Date: 2025-07-20 16:18:49.274353

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2623258a25a4'
down_revision = '8c1feb8ae0fd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('devolucoes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('data_criacao', sa.DateTime(), nullable=False))
        batch_op.add_column(sa.Column('data_atualizacao', sa.DateTime(), nullable=False))

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

    with op.batch_alter_table('devolucoes', schema=None) as batch_op:
        batch_op.drop_column('data_atualizacao')
        batch_op.drop_column('data_criacao')

    # ### end Alembic commands ###
