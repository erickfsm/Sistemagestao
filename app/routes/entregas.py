from datetime import datetime, date
import re 
from workalendar.america import Brazil
from flask import Blueprint, request, jsonify
from app.models.comprovante import Comprovante
from app.models.entrega import Entrega
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.motorista import Motorista
from app.utils.decorators import role_required

entrega_bp = Blueprint('entregas', __name__, url_prefix='/api/entregas')

def extrair_numero_dias(prazo_str: str) -> int | None:
    """
    Extrai um numero inteiro de uma string que representa um prazo em dias.
    Exemplo: "5 dias" -> 5, "10 dias" -> 10
    """
    if not isinstance(prazo_str, str):
        return None
    match = re.search(r'\d+', prazo_str)
    if match:
        return int(match.group())
    return None

def calcular_data_final_util(data_inicial: date, quantidade_dias_uteis: int, feriados_customizados: list[date] = None) -> date | None:
    """
    Calcula a data final considerando apenas os dias úteis.
    """
    if not isinstance(data_inicial, date) or not isinstance(quantidade_dias_uteis, int) or quantidade_dias_uteis < 0:
        return None
    
    cal = Brazil()

    if feriados_customizados:
        for holiday_date in feriados_customizados:
            if isinstance(holiday_date, date):
                cal.add_holiday((holiday_date.year, holiday_date.month, holiday_date.day, "Feriado Customizado"))
            else:
                print(f'Feriado {holiday_date} não é uma data válida. Ignorando.')
   
    try:
        data_final = cal.add_working_days(data_inicial, quantidade_dias_uteis)
        return data_final
    except Exception as e:
        print(f'Erro ao calcular data final: {e}')
        return None

# --- Endpoints ---

@entrega_bp.route('/', methods=['POST'])
#@jwt_required
#@role_required(['agente', 'admin'])
def create_entrega():
    data = request.get_json()

    required_fields = [
        "CODFILIAL", "DTFAT", "DTCARREGAMENTO", "ROMANEIO", "TIPOVENDA", 
        "NUMNOTA", "NUMPED", "CODCLI", "CLIENTE", "MUNICIPIO", "UF", 
        "VLTOTAL", "NUMVOLUME", "TOTPESO", "PRAZOENTREGA", "CHAVENFE"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"Campo '{field}' é obrigatório."}), 400
    
    if Entrega.query.filter_by(CHAVENFE=data['CHAVENFE']).first():
        return jsonify({"message": "Chave NFe já cadastrada."}), 409

    try:

        dt_fat = datetime.strptime(data['DTFAT'], '%Y-%m-%d %H:%M:%S')
        dt_carregamento = datetime.strptime(data['DTCARREGAMENTO'], '%Y-%m-%d %H:%M:%S')

        data_finalizacao = None
        if data.get('DATAFINALIZACAO'):
            data_finalizacao = datetime.strptime(data['DATAFINALIZACAO'], '%Y-%m-%d %H:%M:%S')
        
        agendamento = None
        if data.get('AGENDAMENTO'):
            agendamento = datetime.strptime(data['AGENDAMENTO'], '%Y-%m-%d %H:%M:%S')

        previsao_entrega = None
        if dt_carregamento and 'PRAZOENTREGA' in data and isinstance(data['PRAZOENTREGA'], int):
            data_prev_entrega_date = calcular_data_final_util(
                data_inicial=dt_carregamento.date(),
                quantidade_dias_uteis=data['PRAZOENTREGA']
            )
            if data_prev_entrega_date:
                previsao_entrega = datetime.combine(data_prev_entrega_date, dt_carregamento.time())
        else:
            return jsonify({'message': 'PREVISAOENTREGA não pode ser calculada (DTCARREGAMENTO ou PRAZOENTREGA inválidos).'}), 400

        nova_entrega = Entrega(
            CODFILIAL=int(data['CODFILIAL']),
            DTFAT=dt_fat,
            DTCARREGAMENTO=dt_carregamento,
            ROMANEIO=int(data['ROMANEIO']),
            TIPOVENDA=int(data['TIPOVENDA']),
            NUMNOTA=int(data['NUMNOTA']),
            NUMPED=int(data['NUMPED']),
            CODCLI=int(data['CODCLI']),
            CLIENTE=str(data['CLIENTE']),
            MUNICIPIO=str(data['MUNICIPIO']),
            UF=str(data['UF']),
            EMAIL=data.get('EMAIL'),
            TELCOM=data.get('TELCOM'),
            EMAIL_1=data.get('EMAIL_1'),
            CODFORNECFRETE=data.get('CODFORNECFRETE'),
            TRANSPORTADORA=data.get('TRANSPORTADORA'),
            VLTOTAL=float(data['VLTOTAL']),
            NUMVOLUME=int(data['NUMVOLUME']),
            TOTPESO=float(data['TOTPESO']),
            PRAZOENTREGA=int(data['PRAZOENTREGA']),
            CHAVENFE=str(data['CHAVENFE']),
            DATAFINALIZACAO=data_finalizacao,
            AGENDAMENTO=agendamento,
            PREVISAOENTREGA=previsao_entrega,
            motorista_id=data.get('motorista_id')
        )
        
        if nova_entrega.CODFORNECFRETE is not None:
            nova_entrega.CODFORNECFRETE = int(nova_entrega.CODFORNECFRETE)
        if nova_entrega.motorista_id is not None:
            nova_entrega.motorista_id = int(nova_entrega.motorista_id)

        db.session.add(nova_entrega)
        db.session.commit()
        return jsonify({"message": "Entrega criada com sucesso!", "entrega": nova_entrega.to_dict()}), 201
    except ValueError as ve:
        db.session.rollback()

        return jsonify({"message": f"Erro de formato de dados: {str(ve)}. Verifique tipos e formatos de data (YYYY-MM-DD HH:MM:SS)."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao criar entrega: {str(e)}"}), 500

@entrega_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin', 'motorista'])
def buscar_entrega_por_id(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'error': 'Entrega não encontrada'}), 404
    return jsonify(entrega.to_dict()), 200

@entrega_bp.route('/previsao/<int:entrega_id>', methods=['POST'])
@jwt_required
@role_required(['agente', 'admin'])
def calcular_e_salva_previsao_entrega(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'error': 'Entrega não encontrada'}), 404

    feriados_adicionais = [
        date(2025, 1, 1),  # Exemplo de feriado adicional
        date(2025, 11, 20)  # Outro exemplo
    ]

    response_data = {}

    if not entrega.DTCARREGAMENTO:
        response_data['error'] = 'Data de carregamento não definida para a entrega.'
        return jsonify(response_data), 400
    
    data_carregamento_date = entrega.DTCARREGAMENTO.date()

    if not isinstance(entrega.PRAZOENTREGA, int):
        response_data['error'] = 'Prazo de entrega inválido (deve ser um número inteiro).'
        return jsonify(response_data), 400
    
    quantidade_dias = entrega.PRAZOENTREGA
    
    data_previsao_entrega = calcular_data_final_util(
        data_inicial=data_carregamento_date,
        quantidade_dias_uteis=quantidade_dias,
        feriados_customizados=feriados_adicionais
    )

    if data_previsao_entrega: 
        entrega.PREVISAOENTREGA = datetime.combine(data_previsao_entrega, datetime.min.time())
        db.session.add(entrega)
        try:
            db.session.commit()
            response_data = entrega.to_dict()
            response_data['messagem'] = 'Previsão de entrega calculada e salva com sucesso.'
            return jsonify(response_data), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": f"Erro ao salvar previsão no banco de dados: {e}"}), 500
    else:
        response_data['error'] = 'Erro ao calcular a data de previsão de entrega.'
        return jsonify(response_data), 500
        
@entrega_bp.route('/finalizar/<int:entrega_id>', methods=['PATCH'])
@jwt_required()
@role_required(['motorista', 'agente', 'admin'])
def finalizar_entrega(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'error': 'Entrega não encontrada'}), 404

    data_recebida = request.get_json()
    data_finalizacao_str = data_recebida.get('data_finalizacao')

    if not data_finalizacao_str:
        return jsonify({'error': 'Data de finalização é obrigatória.'}), 400
    try:
        finalizacao_dt = datetime.strptime(data_finalizacao_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD HH:MM:SS.'}), 400
    
    entrega.DATAFINALIZACAO = finalizacao_dt
    db.session.add(entrega)
    try:
        db.session.commit()
        return jsonify(entrega.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao finalizar entrega: {e}'}), 500
    
@entrega_bp.route('/<int:entrega_id>/comprovantes', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin', 'motorista'])
def listar_comprovantes_por_entrega(entrega_id):
    motorista_id = int(get_jwt_identity())
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'message': "Entrega não encotrada."}), 404
    
    if entrega.motorista_id != motorista_id:
        return jsonify({"message": "Você não tem permissão para listar comprovantes desta entrega."}), 403
    
    comprovantes_lista = entrega.comprovantes.all()

    if not comprovantes_lista:
        return jsonify({"message": "Nenhum comprovante encontrado para esta entrega."}), 404
    
    return jsonify([comprovante.to_dict() for comprovante in comprovantes_lista])

@entrega_bp.route('/int:entrega_id>/atribuir_motorista', methods=['PATCH'])
@jwt_required()
@role_required(['admin', 'agente'])
def atribuir_motorista_entrega(entrega_id):
    motorista_logado_id = get_jwt_identity()
    #if not verificar_role_admin_ou_agente(motorista_logado_id):
    #    return jsonify({"message": "Permissão negada. Apenas administradores/agentes podem atribuir entregas."}), 403

    data = request.get_json()
    motorista_id = data.get('motorista_id')

    if not motorista_id:
        return jsonify({"message": "ID do motorista é obrigatório para atribuição."}), 400
    
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({"message": "Entrega não encontrada."}), 404
    
    motorista = Motorista.query.get(motorista_id)
    if not motorista:
        return jsonify({"message": "Motorista não encontrado."}), 404

    entrega.motorista_id = motorista_id
    db.session.commit()

    return jsonify({
        "message":f"Entrega {entrega_id} atribuida com sucesso ao motorista {motorista_id}.",
        "entrega": entrega.to.dict()
    }), 200

@entrega_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin'])
def listar_todas_entregas():

    query = Entrega.query

    status = request.args.get('status')
    motorista_id = request.args.get('motorista_id', type=int)
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    # Adicione outros filtros conforme necessário, ex:

    if status:
        query = query.filter_by(STATUS=status)
    
    if motorista_id:
        query = query.filter_by(motorista_id=motorista_id)

    if data_inicial_str:
        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
            query = query.filter(Entrega.DATAINICIOPREVISAO >= data_inicial)
        except ValueError:
            return jsonify({"message": "Formato de data_inicial inválido. Use YYYY-MM-DD."}), 400

    if data_final_str:
        try:
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()
            query = query.filter(Entrega.DATAFINALPREVISAO <= data_final)
        except ValueError:
            return jsonify({"message": "Formato de data_final inválido. Use YYYY-MM-DD."}), 400
    
    entregas = query.all()

    if not entregas:
        return jsonify({"message": "Nenhuma entrega encontrada com os filtros especificados."}), 404
    
    feriados_adicionais = [
        date(2025, 11, 20)  #Dia da Consciência Negra
    ]

    return jsonify([entrega.to_dict(feriados_customizados=feriados_adicionais) for entrega in entregas]), 200
