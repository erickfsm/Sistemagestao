from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.devolucao import Devolucao
from app.models.entrega import Entrega
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
from app.utils.decorators import role_required

devolucao_bp = Blueprint('devolucoes', __name__, url_prefix='/api/devolucoes')

@devolucao_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['agente', 'motorista', 'admin'])
def registrar_devolucao():
    motorista_id_str = get_jwt_identity()
    motorista_id = int(motorista_id_str)

    data = request.get_json()

    required_fields = ['entrega_id', 'tipo_devolucao', 'motivo']
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Campo '{field}' é obrigatório."}), 400
    
    entrega_id = data.get('entrega_id')
    tipo_devolucao = data.get('tipo_devolucao')
    motivo = data.get('motivo')
    observacoes = data.get('observacoes')

    if tipo_devolucao not in ['Total', 'Parcial']:
        return jsonify({"message": "Tipo de devolução inválido. Use 'Total' ou 'Parcial'."}), 400
    
    entrega = Entrega.query.get(entrega_id)

    if not entrega:
        return jsonify({"message": "Entrega não encontrada."}), 404
    
    if entrega.motorista_id != motorista_id:
        return jsonify({"message": "Você não tem permissão para registrar devolução para esta entrega."}), 403
    
    try:
        nova_devolucao = Devolucao(
            entrega_id=entrega_id,
            motorista_id=motorista_id,
            tipo_devolucao=tipo_devolucao,
            motivo=motivo,
            observacoes=observacoes,
            data_devolucao=datetime.utcnow()
        )
        db.session.add(nova_devolucao)
        db.session.commit()

        if tipo_devolucao == 'Total':
            entrega.DEVOLUCAO = True
            db.session.add(entrega)
            db.session.commit()

        return jsonify({
            "message": "Devolução registrada com sucesso!",
            "devolucao": nova_devolucao.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao registrar devolução: {e}"}), 500
    
@devolucao_bp.route('/<int:devolucao_id>', methods=['GET'])
@jwt_required()
@role_required(['agente', 'motorista', 'admin'])
def buscar_devolucao_por_id(devolucao_id):
    devolucao = Devolucao.query.get(devolucao_id)
    if not devolucao: 
        return jsonify({"message": "Devolução não encotrada."}), 404
    
    current_motorista_id = int(get_jwt_identity())
    if devolucao.motorista_id != current_motorista_id:
        return jsonify({"message": "Você não tem permissão para ver esta devolução."}), 403
    
    return jsonify(devolucao.to_dict()), 200

@devolucao_bp.route('/por_entrega/<int:entrega_id>', methods=['GET'])
@jwt_required()
@role_required(['motorista', 'agente', 'admin'])
def listar_devolucoes_por_entrega(entrega_id):
    devolucoes = Devolucao.query.filter_by(entrega_id=entrega_id).all()
    if not devolucoes:
        return jsonify({"message": "Nenhuma devolução encontrada para esta entrega."}), 404
    
    return jsonify([devolucao.to_dict() for devolucao in devolucoes]), 200

@devolucao_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin'])
def listar_todas_devolucoes():
    devolucoes = Devolucao.query.all()
    if not devolucoes:
        return jsonify({"message": "Nenhuma devolução encontrada."}), 404
    
    return jsonify([devolucao.to_dict() for devolucao in devolucoes]), 200

@devolucao_bp.route('/<int:devolucao_id>/cancelar', methods=['PATCH'])
@jwt_required()
@role_required(['agente', 'admin', 'motorista'])
def cancelar_devolucao(devolucao_id):
    current_user_id = int(get_jwt_identity())
    claims = get_jwt()
    user_role = claims.get('role')

    devolucao = Devolucao.query.get(devolucao_id)
    if not devolucao:
        return jsonify({"message": "Devolução não encontrada."}), 404
    
    if devolucao.status == 'cancelada':
        return jsonify({"message": "Devolução já está cancelada."}), 400

    if devolucao.status == 'finalizada':
        return jsonify({"message": "Devolução finalizada não pode ser cancelada."}), 400

    devolucao.status = 'cancelada'
    devolucao.data_atualizacao = datetime.utcnow()

    db.session.add(devolucao)
    try:
        db.session.commit()

        from app.models.entrega import Entrega
        entrega = Entrega.query.get(devolucao.entrega_id)
        
        if entrega and devolucao.tipo_devolucao == 'Total' and not Entrega.query.filter_by(id=devolucao.entrega_id, DEVOLUCAO=True, status='ativa').first():
            entrega.DEVOLUCAO = False
            db.session.add(entrega)
            db.session.commit()

        return jsonify({
            "message": "Devolução cancelada com sucesso!",
            "devolucao": devolucao.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao cancelar devolução: {e}"}), 500
