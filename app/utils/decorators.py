from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def role_required(required_roles):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()

            if "role" not in claims or claims["role"] not in required_roles:
                return jsonify({"message": "Acesso negado: Você não tem a permissão necessária."}), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper