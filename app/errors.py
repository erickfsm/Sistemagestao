from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = jsonify({
            "error": e.description, 
            "code": e.code,
            "message": str(e)
        })
        response.status_code = e.code
        return response

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        print(f"ERRO INTERNO NÃO TRATADO: {e}")
        response = jsonify({
            "error": "Erro interno do servidor",
            "code": 500,
            "message": "Ocorreu um erro inesperado no servidor."
        })
        response.status_code = 500
        return response

    from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, JWTDecodeError
    from jwt.exceptions import ExpiredSignatureError
    @app.errorhandler(NoAuthorizationError)
    @app.errorhandler(InvalidHeaderError)
    @app.errorhandler(JWTDecodeError)
    @app.errorhandler(ExpiredSignatureError)
    def handle_jwt_exceptions(e):
        return jsonify({"error": "Erro de autenticação JWT", "message": str(e), "code": 401}), 401