from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.usuario import Usuario 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.decorators import role_required

usuario_bp = Blueprint('usuarios', __name__, url_prefix='/api/usuarios')

@usuario_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()

    nome = data.get('nome')
    email = data.get('email')
    login = data.get('login')
    senha = data.get('senha')
    role = data.get('role', 'agente')

    if not all([nome, login, senha]):
        return jsonify({"message": "Todos os campos (nome, login e senha) são obrigatórios."}), 400

    # Validações básicas

    if Usuario.query.filter_by(login=login).first():
        return jsonify({"message": "Login já cadastrado."}), 409
    
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"message": "Email já cadastrado."}), 409

    if role not in ['motorista', 'agente', 'admin']:
        return jsonify({"message": "Role inválido. Roles permitidos: motorista, agente, admin."}), 400

    novo_usuario = Usuario(nome=nome, login=login, email=email, role=role)
    novo_usuario.set_password(senha)

    db.session.add(novo_usuario)
    try:
        db.session.commit()
        return jsonify({"message": "Usuário cadastrado com sucesso!", "user": novo_usuario.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cadastrar usuário: {e}"}), 500

@usuario_bp.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    login = data.get('login')
    senha = data.get('senha')

    usuario = Usuario.query.filter_by(login=login).first()

    if usuario and usuario.check_password(senha):
        additional_claims = {"role": usuario.role}
        access_token = create_access_token(identity=str(usuario.id), additional_claims=additional_claims) 
        
        return jsonify(access_token=access_token, user=usuario.to_dict()), 200
    else:
        return jsonify({"message": "Login ou senha inválidos."}), 401

@usuario_bp.route('/perfil', methods=['GET'])
@jwt_required() 
def perfil_usuario():
    current_user_id = get_jwt_identity()
    usuario = Usuario.query.get(current_user_id)

    if not usuario:
        return jsonify({"message": "Usuário não encontrado."}), 404
        
    return jsonify({"message": "Dados do perfil do usuário", "user": usuario.to_dict()}), 200

@usuario_bp.route('/admin_teste', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def admin_teste():
    claims = get_jwt()
    return jsonify({"message": f"Bem-vindo, Admin! Suas claims: {claims}"}), 200

@usuario_bp.route('/agente_ou_admin_teste', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin'])
def agente_ou_admin_teste():
    claims = get_jwt()
    return jsonify({"message": f"Bem-vindo, Agente/Admin! Suas claims: {claims}"}), 200

@usuario_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['admin'])
def listar_todos_usuarios():
    usuarios = Usuario.query.all()
    if not usuarios:
        return jsonify({"message": "Nenhum usuário encontrado."}), 404
    
    return jsonify([usuario.to_dict() for usuario in usuarios]), 200