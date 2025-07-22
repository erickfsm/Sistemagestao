from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.motorista import Motorista
from app.models.entrega import Entrega
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
from datetime import datetime, date
from app.utils.decorators import role_required

motorista_bp = Blueprint('motoristas', __name__, url_prefix='/api/motoristas')

@motorista_bp.route('/cadastro', methods=['POST'])
@jwt_required
@role_required(['agente', 'admin'])
def cadastrar_motorista():
    data = request.get_json()
    nome = data.get('nome')
    login = data.get('login')
    senha = data.get('senha')

    if not all([nome, login, senha]):
        return jsonify({'error': 'Todos os campos são obrigatórios.'}), 400
    if Motorista.query.filter_by(login=login).first():
        return jsonify({'error': 'Login já cadastrado.'}), 400
    
    novo_motorista = Motorista(nome=nome, login=login)
    novo_motorista.set_password(senha)

    db.session.add(novo_motorista)
    try:
        db.session.commit()
        return jsonify({'message': 'Motorista cadastrado com sucesso.', 'motorista': novo_motorista.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Erro ao cadastrar motorista.', 'details': str(e)}), 500
    
@motorista_bp.route('/login', methods=['POST'])
def login_motorista():
    data = request.get_json()
    login = data.get('login')
    senha = data.get('senha')

    motorista = Motorista.query.filter_by(login=login).first()

    if motorista and motorista.check_password(senha):
        access_token = create_access_token(identity=str(motorista.id))
        return jsonify(access_token=access_token, motorista=motorista.to_dict()), 200
    else:
        return jsonify({'error': 'Login ou senha inválidos.'}), 401
    
@motorista_bp.route('/perfil', methods=['GET'])
@jwt_required()
@role_required(['motorista', 'agente', 'admin'])
def perfil_motorista():
        current_motorista_id = get_jwt_identity()
        motorista = Motorista.query.get(current_motorista_id)

        if not motorista:
            return jsonify({'error': 'Motorista não encontrado.'}), 404

        return jsonify({'message': 'Dados do perfil do motorista', 'motorista': motorista.to_dict()}), 200

@motorista_bp.route('/minhas_entregas', methods=['GET'])
@jwt_required()
@role_required(['motorista'])
def minhas_entregas():
   
    motorista_logado_id_str = get_jwt_identity()
    motorista_logado_id = int(motorista_logado_id_str)

    entregas_atribuidas = Entrega.query.filter_by(motorista_id=motorista_logado_id).all()

    if not entregas_atribuidas:
        return jsonify({"message": "Nenhuma entrega atribuída a você no momento."}), 404

    feriados_adicionais = [
        date(2025, 11, 20)
    ]
    

    return jsonify([entrega.to_dict(feriados_customizados=feriados_adicionais) for entrega in entregas_atribuidas]), 200

@motorista_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin'])
def listar_todos_motoristas():
    motoristas = Motorista.query.all()
    if not motoristas:
        return jsonify({"message": "Nenhum motorista encontrado."}), 404
    
    return jsonify([motorista.to_dict() for motorista in motoristas]), 200
