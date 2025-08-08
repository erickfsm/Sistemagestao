import os
from flask import Flask
from .extensions import db, migrate, jwt, cors, scheduler
from .jobs import tarefa_de_verificacao_diaria
from config import Config
from .errors import register_error_handlers


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)
    
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(app.config['COMPROVANTES_DIR'])
    except OSError:
        pass

    from .routes.auth import auth_bp
    from .routes.entregas import entrega_bp
    from .routes.comprovantes import comprovante_bp
    from .routes.motoristas import motorista_bp
    from .routes.devolucoes import devolucao_bp
    from .routes.usuarios import usuario_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(entrega_bp, url_prefix='/api/entregas')
    app.register_blueprint(comprovante_bp, url_prefix='/api/comprovantes')
    app.register_blueprint(motorista_bp, url_prefix='/api/motoristas')
    app.register_blueprint(devolucao_bp, url_prefix='/api/devolucoes')
    app.register_blueprint(usuario_bp, url_prefix='/api/usuarios')

    register_error_handlers(app)

    if not scheduler.running:
        scheduler.add_job(
            id='tarefa_verificacao_diaria',
            func=tarefa_de_verificacao_diaria,
            trigger='cron',
            hour=1,
            minute=0,
            args=[app, scheduler],
            replace_existing=True
        )
        scheduler.start()

    return app