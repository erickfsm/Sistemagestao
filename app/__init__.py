import os
from flask import Flask
from config import Config
from app.routes.entregas import entrega_bp
from app.extensions import db, migrate, jwt
from app.models import (entrega, motorista, comprovante, devolucao)
from app.errors import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['DEBUG'] = True
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    register_error_handlers

    from app.routes.entregas import entrega_bp
    app.register_blueprint(entrega_bp)
    
    from app.routes.comprovantes import comprovante_bp
    app.register_blueprint(comprovante_bp)

    from app.routes.motoristas import motorista_bp
    app.register_blueprint(motorista_bp)

    from app.routes.devolucoes import devolucao_bp
    app.register_blueprint(devolucao_bp)

    from app.routes.usuarios import usuario_bp
    app.register_blueprint(usuario_bp)

    if __name__ == '__main__':
        app.run(debug=True)

    return app