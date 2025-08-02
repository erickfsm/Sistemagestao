from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.models import usuario, motorista

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login_unificado():
    data = request.get_json()
    login = data.get('login')
    senha = data.get('senha')

    if not login or not senha:
        return jsonify({"mensagem": "Login e senha são obrigatórios"}), 400

    usuario = usuario.query.filter_by(login=login).first()
    if usuario and usuario.check_password(senha):
        access_token = create_access_token(identity=login, additional_claims={"role": usuario.role})
        return jsonify(access_token=access_token), 200

    motorista = motorista.query.filter_by(login=login).first()
    if motorista and motorista.check_password(senha):
        access_token = create_access_token(identity=login, additional_claims={"role": "motorista"})
        return jsonify(access_token=access_token), 200

    return jsonify({"mensagem": "Login ou senha incorretos"}), 401