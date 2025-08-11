import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from flask import current_app

from app.extensions import db
from app.models.comprovante import Comprovante
from app.models.devolucao import Devolucao
from app.models.entrega import Entrega
from app.models.motorista import Motorista
from app.models.rastreamento import Rastreamento
from app.models.transportadora import Transportadora
from app.models.usuario import Usuario

config = context.config
config.set_main_option('sqlalchemy.url', current_app.config.get('SQLALCHEMY_DATABASE_URI'))

if config.config_file_name:
    fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

target_metadata = db.metadata

def get_engine():
    try:
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError):
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    try:
        return get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
    except AttributeError:
        return str(get_engine().url).replace('%', '%%')

config.set_main_option('sqlalchemy.url', get_engine_url())

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('Nenhuma alteração no esquema detectada.')

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            process_revision_directives=process_revision_directives,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    logger.info("Executando migrações no modo offline...")
    run_migrations_offline()
else:
    logger.info("Executando migrações no modo online...")
    run_migrations_online()