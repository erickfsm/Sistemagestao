"""Criação das tabelas principais

Revision ID: 002c5e9cf216
Revises: 
Create Date: 2025-07-16 11:32:06.257634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002c5e9cf216'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('motoristas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=120), nullable=False),
    sa.Column('ativo', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('senha_hash', sa.String(length=128), nullable=False),
    sa.Column('tipo', sa.String(length=50), nullable=False),
    sa.Column('data_criacao', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('data_atualizacao', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('entregas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nf_numero', sa.String(length=50), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('data_prevista', sa.DateTime(), nullable=True),
    sa.Column('data_realizada', sa.DateTime(), nullable=True),
    sa.Column('motorista_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['motorista_id'], ['motoristas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comprovantes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entrega_id', sa.Integer(), nullable=True),
    sa.Column('arquivo_url', sa.String(length=255), nullable=True),
    sa.Column('data_anexo', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['entrega_id'], ['entregas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('devolucoes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('entrega_id', sa.Integer(), nullable=True),
    sa.Column('motivo', sa.String(length=255), nullable=True),
    sa.Column('data_retorno', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['entrega_id'], ['entregas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('devolucoes')
    op.drop_table('comprovantes')
    op.drop_table('entregas')
    op.drop_table('usuarios')
    op.drop_table('motoristas')
    # ### end Alembic commands ###
