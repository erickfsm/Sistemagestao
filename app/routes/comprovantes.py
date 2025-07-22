import os
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from app.extensions import db
from app.models.comprovante import Comprovante
from app.models.entrega import Entrega
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from datetime import datetime, date
from app.utils.decorators import role_required

comprovante_bp = Blueprint('comprovantes', __name__, url_prefix='/api/comprovantes')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@comprovante_bp.route('/upload', methods=['POST'])
@jwt_required()
@role_required(['agente', 'motorista', 'admin'])
def upload_comprovante():
    motorista_id_str = get_jwt_identity()

    if motorista_id_str is None:
        return jsonify({'message': 'Erro de autenticação: ID do motorista não encotrado no token.'}), 401
        
    motorista_id = int(motorista_id_str)

    if 'file' not in request.files:
        return jsonify({'message': 'Nenhum arquivo enviado na requisição.'}), 400
    
    file = request.files['file']
    entrega_id_str = request.form.get('entrega_id')

    if not entrega_id_str:
        return jsonify({'message': 'ID da entrega é obrigatório.'}), 400
    
    try:
        entrega_id = int(entrega_id_str)
    except ValueError:
        return jsonify({'message': 'ID da entrega inválido. Deve ser um numero.'}), 400

    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'message': 'Entrega não encontrada.'}), 404

    if file.filename == '':
        return jsonify({'message': 'Nenhum arquivo selecionado.'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"message": "Tipo de arquivo não permitido."}), 400

    filename = secure_filename(file.filename)
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{motorista_id}_{filename}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)

    file.save(filepath)

    novo_comprovante = Comprovante(
        entrega_id=entrega_id,
        motorista_id=motorista_id,
        tipo='assinatura',
        caminho_arquivo=filepath,
        data_envio=datetime.utcnow()
    )
    db.session.add(novo_comprovante)
    db.session.commit()

    return jsonify({
        'message': 'Comprovante enviado com sucesso.',
        'comprovante': novo_comprovante.to_dict(),
    }), 201

@comprovante_bp.route('/<int:comprovante_id>/download', methods=['GET'])
@jwt_required()
@jwt_required(['agente', 'motorista', 'admin'])
def download_comprovante(comprovante_id):
    current_motorista_id_str = get_jwt_identity()
    current_motorista_id = int(current_motorista_id_str)

    comprovante = Comprovante.query.get(comprovante_id)
    if not comprovante:
        return jsonify({'message': 'Comprovante não encontrado.'}), 404
    
    if comprovante.motorista_id != current_motorista_id:
        return jsonify({'message': 'Você não tem permiissão para acessar este comprovante.'}), 403
    
    directory = os.path.dirname(comprovante.caminho_arquivo)
    filename = os.path.basename(comprovante.caminho_arquivo)

    return send_from_directory(directory, filename, as_attachment=False)

@comprovante_bp.route('/<int:comprovante_id>', methods=['GET'])
@jwt_required()
@role_required(['agente', 'motorista', 'admin'])
def buscar_comprovante_por_id(comprovante_id):
    motorista_id_str = get_jwt_identity()
    motorista_id = int(motorista_id_str)

    comprovante = Comprovante.query.get(comprovante_id)
    if not comprovante:
        return jsonify({"message": "Comprovante não encontrado."}), 404
    
    if comprovante.motorista_id != motorista_id:
        return jsonify({"message": "Você não tem permissão para acessar este comprovante."}), 403

    return jsonify(comprovante.to_dict()), 200

@comprovante_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin'])
def listar_todos_comprovantes():
    comprovantes = Comprovante.query.all()
    if not comprovantes:
        return jsonify({"message": "Nenhum comprovante encontrado."}), 404
    
    return jsonify([comprovante.to_dict() for comprovante in comprovantes]), 200

@comprovante_bp.route('/<int:comprovante_id>', methods=['PATCH'])
@jwt_required()
@role_required(['agente', 'admin', 'motorista'])
def atualizar_comprovante(comprovante_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role')

    comprovante = Comprovante.query.get(comprovante_id)
    if not comprovante:
        return jsonify({"message": "Comprovante não encontrado."}), 404

    if user_role == 'motorista' and comprovante.motorista_id != current_user_id:
         return jsonify({"message": "Permissão negada. Você só pode atualizar seus próprios comprovantes."}), 403

    data = request.get_json()

    if 'tipo' in data:
        comprovante.tipo = data['tipo']

    comprovante.data_atualizacao = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "message": "Comprovante atualizado com sucesso!",
        "comprovante": comprovante.to_dict()
    }), 200

@comprovante_bp.route('/<int:comprovante_id>', methods=['DELETE'])
@jwt_required()
@role_required(['admin'])
def deletar_comprovante(comprovante_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role')

    comprovante = Comprovante.query.get(comprovante_id)
    if not comprovante:
        return jsonify({"message": "Comprovante não encontrado."}), 404
    
    if user_role == 'agente' and comprovante.motorista_id != current_user_id: 
         return jsonify({"message": "Permissão negada. Agentes só podem deletar os próprios comprovantes."}), 403

    filepath = comprovante.caminho_arquivo
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"DEBUG: Arquivo {filepath} removido do sistema de arquivos.")
        except OSError as e:

            print(f"ERRO: Não foi possível remover o arquivo {filepath}: {e}")
            return jsonify({"message": f"Erro ao deletar arquivo: {e}"}), 500

    db.session.delete(comprovante)
    db.session.commit()

    return jsonify({"message": "Comprovante deletado com sucesso!"}), 200