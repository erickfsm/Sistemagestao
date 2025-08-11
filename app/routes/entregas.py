from datetime import datetime, date, timedelta
from workalendar.america import Brazil
from flask import Blueprint, current_app, request, jsonify
from app.extensions import db
from app.jobs import tarefa_rastreamento_especifico 
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.rastreamento import Rastreamento
from app.utils.decorators import role_required
import pandas as pd
import io
import re

from app.models.motorista import Motorista
from app.models.comprovante import Comprovante
from app.models.entrega import Entrega
from app.models.devolucao import Devolucao

entrega_bp = Blueprint('entregas', __name__, url_prefix='/api/entregas')

def extrair_numero_dias(prazo_str: str) -> int | None:
    if not isinstance(prazo_str, str):
        return None
    match = re.search(r'\d+', prazo_str)
    if match:
        return int(match.group())
    return None

def calcular_data_final_util(data_inicial: date, quantidade_dias_uteis: int, feriados_customizados: list[date] = None) -> date | None:
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

def safe_date_converter(date_val, format_str='%Y-%m-%d %H:%M:%S'):
    if isinstance(date_val, (int, float)):
        return pd.to_datetime(date_val, unit='D', origin='1899-12-30').to_pydatetime()
    elif isinstance(date_val, date) and not isinstance(date_val, datetime):
        return datetime.combine(date_val, datetime.min.time())
    elif isinstance(date_val, str):
        return datetime.strptime(date_val, format_str)
    else:
        return date_val

def criar_entrega_com_dados(data: dict):
    dt_fat = safe_date_converter(data['DTFAT'])
    dt_carregamento = safe_date_converter(data['DTCARREGAMENTO'])

    data_finalizacao = None
    if data.get('DATAFINALIZACAO'):
        data_finalizacao = safe_date_converter(data['DATAFINALIZACAO'])
    
    agendamento = None
    if data.get('AGENDAMENTO'):
        agendamento = safe_date_converter(data['AGENDAMENTO'])

    previsao_entrega = None
    if dt_carregamento and 'PRAZOENTREGA' in data and isinstance(data['PRAZOENTREGA'], int):
        data_prev_entrega_date = calcular_data_final_util(
            data_inicial=dt_carregamento.date(),
            quantidade_dias_uteis=data['PRAZOENTREGA']
        )
        if data_prev_entrega_date:
            previsao_entrega = datetime.combine(data_prev_entrega_date, dt_carregamento.time())
    else:
        raise ValueError('DTCARREGAMENTO ou PRAZOENTREGA inválidos.')

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
    
    nova_entrega.definir_previsao_entrega()
    db.session.add(nova_entrega)
    return nova_entrega

@entrega_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['agente', 'admin'])
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
        nova_entrega = criar_entrega_com_dados(data)
        db.session.commit()
        return jsonify({"message": "Entrega criada com sucesso!", "entrega": nova_entrega.to_dict()}), 201
    except ValueError as ve:
        db.session.rollback()
        return jsonify({"message": f"Erro de formato de dados: {str(ve)}. Verifique tipos e formatos de data (YYYY-MM-DD HH:MM:SS)."}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erro ao criar entrega: {str(e)}"}), 500

@entrega_bp.route('/importar-excel', methods=['POST'])
@jwt_required()
@role_required(['admin'])
def importar_excel():
    if 'file' not in request.files:
        return jsonify({"mensagem": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"mensagem": "Nenhum arquivo selecionado"}), 400
    
    filename_lower = file.filename.lower()
    df = None

    try:
        if filename_lower.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file, engine='openpyxl')
        elif filename_lower.endswith('.csv'):
            file_stream = io.StringIO(file.stream.read().decode('utf-8'))
            df = pd.read_csv(file_stream)
        else:
            return jsonify({"message": "Formato de arquivo não suportado. Use .xlsx, .xls ou .csv."}), 400
       
    except Exception as e:
        return jsonify({"mensagem": f"Erro ao ler o arquivo: {str(e)}"}), 500
    
    try:
        required_excel_cols = ["CODFILIAL", "DTFAT", "DTCARREGAMENTO", "ROMANEIO", "TIPOVENDA", 
                              "NUMNOTA", "NUMPED", "CODCLI", "CLIENTE", "MUNICIPIO", "UF", 
                              "VLTOTAL", "NUMVOLUME", "TOTPESO", "PRAZOENTREGA", "CHAVENFE", "CODFORNECFRETE"]
        
        if not all(col in df.columns for col in required_excel_cols):
            missing_cols = [col for col in required_excel_cols if col not in df.columns]
            return jsonify({"mensagem": f"Arquivo Excel não possui todas as colunas obrigatórias. Faltando: {', '.join(missing_cols)}"}), 400

        entregas_importadas = []
        for index, row in df.iterrows():
            data_entrega = row.to_dict()
            
            if Entrega.query.filter_by(CHAVENFE=data_entrega['CHAVENFE']).first():
                continue

            for date_field in ['DTFAT', 'DTCARREGAMENTO', 'DATAFINALIZACAO', 'AGENDAMENTO']:
                if isinstance(data_entrega.get(date_field), datetime):
                    data_entrega[date_field] = data_entrega[date_field].strftime('%Y-%m-%d %H:%M:%S')

            nova_entrega = Entrega(
                CODFILIAL=row['CODFILIAL'],
                DTFAT=pd.to_datetime(row['DTFAT']),
                DTCARREGAMENTO=pd.to_datetime(row['DTCARREGAMENTO']),
                ROMANEIO=row['ROMANEIO'],
                TIPOVENDA=row['TIPOVENDA'],
                NUMNOTA=row['NUMNOTA'],
                NUMPED=row['NUMPED'],
                CODCLI=row['CODCLI'],
                CLIENTE=row['CLIENTE'],
                MUNICIPIO=row['MUNICIPIO'],
                UF=row['UF'],
                VLTOTAL=row['VLTOTAL'],
                NUMVOLUME=row['NUMVOLUME'],
                TOTPESO=row['TOTPESO'],
                PRAZOENTREGA=row['PRAZOENTREGA'],
                CHAVENFE=row['CHAVENFE'],
                transportadora_cod=int(row['CODFORNECFRETE']),
                TRANSPORTADORA=row['TRANSPORTADORA']
            )
           
            db.session.add(nova_entrega) 
        
        db.session.commit()
        
        return jsonify({"mensagem": f"{len(df)} linhas processadas. Entregas novas e atualizadas foram salvas."}), 200

    except KeyError as e:
        db.session.rollback()
        return jsonify({"mensagem": f"Erro de processamento: a coluna {str(e)} não foi encontrada no arquivo."}), 500
    except Exception as e:
        db.session.rollback()
        print(f"ERRO COMPLETO: {e}") 
        return jsonify({"mensagem": f"Erro ao processar o arquivo: {str(e)}"}), 500

@entrega_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@role_required(['agente', 'admin', 'motorista'])
def buscar_entrega_por_id(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'error': 'Entrega não encontrada'}), 404
    return jsonify(entrega.to_dict()), 200

@entrega_bp.route('/previsao/<int:entrega_id>', methods=['POST'])
@jwt_required()
@role_required(['agente', 'admin'])
def calcular_e_salva_previsao_entrega(entrega_id):
    entrega = Entrega.query.get(entrega_id)
    if not entrega:
        return jsonify({'error': 'Entrega não encontrada'}), 404

    feriados_adicionais = [
        date(2025, 1, 1),
        date(2025, 11, 20)
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
            return jsonify({"erro": f'Erro ao salvar previsão no banco de dados: {e}'}), 500
    else:
        response_data['error'] = 'Erro ao calcular a data de previsão de entrega.'
        return jsonify(response_data), 500
        
@entrega_bp.route('/finalizar/<int:entrega_id>', methods=['PATCH'])
@jwt_required()
@role_required(['motorista', 'agente', 'admin'])
def finalizar_entrega(entrega_id):
    entrega = Entrega.query.get_or_404(entrega_id)
    
    comprovante_existente = Comprovante.query.filter_by(entrega_id=id).first()
    if not comprovante_existente:
        return jsonify({"erro": "Anexo do canhoto ou ressalva é obrigatório para finalizar."}), 400

    devolucao_existente = Devolucao.query.filter_by(entrega_id=id).first()
    if devolucao_existente:
        print(f"A entrega {id} está sendo finalizada e possui uma devolução associada.")
        pass

    entrega.data_finalizacao = datetime.utcnow()
    entrega.status = "Finalizada com Devolução" if devolucao_existente else "Finalizada com Sucesso"
    
    db.session.commit()

    return jsonify({"mensagem": "Entrega finalizada com sucesso."}), 200
    
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
    num_nota = request.args.get('num_nota', type=int)
    transportadora = request.args.get('transportadora')
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    if status:
        query = query.filter_by(STATUS=status)

    if num_nota:
        query = query.filter_by(NUMNOTA=num_nota)

    if transportadora:
        query = query.filter(Entrega.TRANSPORTADORA.ilike(f'%{transportadora}%'))

    if data_inicial_str:
        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d').date()
            query = query.filter(Entrega.DTFAT >= data_inicial)
        except ValueError:
            return jsonify({"message": "Formato de data_inicial inválido. Use YYYY-MM-DD."}), 400

    if data_final_str:
        try:
            data_final = datetime.strptime(data_final_str, '%Y-%m-%d').date()
            data_final_inclusive = data_final + timedelta(days=1)
            query = query.filter(Entrega.DTFAT < data_final_inclusive)
        except ValueError:
            return jsonify({"message": "Formato de data_final inválido. Use YYYY-MM-DD."}), 400
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    entregas = pagination.items

    feriados_adicionais = [
        date(2025, 11, 20)
    ]

    entregas_json = []
    for entrega in entregas:
        if entrega is not None:
            entregas_json.append(entrega.to_dict(feriados_customizados=feriados_adicionais))

    if not entregas_json:
        return jsonify([]), 200

    return jsonify(entregas_json), 200


@entrega_bp.route('/<int:entrega_id>/atualizar-rastreamento', methods=['POST'])
@jwt_required()
def atualizar_rastreamento_manual(entrega_id):
    try:
        tarefa_rastreamento_especifico(current_app._get_current_object(), entrega_id)
        
        entrega_atualizada = Entrega.query.get(entrega_id)
        if entrega_atualizada:
            return jsonify({
                "mensagem": "Rastreamento atualizado com sucesso.",
                "status": entrega_atualizada.status 
            }), 200
        else:
             return jsonify({"mensagem": "Atualização solicitada, mas a entrega não foi encontrada."}), 404

    except Exception as e:
        print(f"Erro inesperado ao atualizar rastreamento para entrega {entrega_id}: {e}")
        return jsonify({"erro": "Ocorreu um erro interno ao processar a solicitação."}), 500
    

@entrega_bp.route('/<int:entrega_id>/devolucoes', methods=['GET'])
@jwt_required()
def get_devolucoes_por_entrega(entrega_id):
    devolucoes = Devolucao.query.filter_by(entrega_id=entrega_id).all()
    return jsonify([d.to_dict() for d in devolucoes])

@entrega_bp.route('/<int:entrega_id>/rastreamento', methods=['GET'])
@jwt_required()
def get_rastreamento_por_entrega(entrega_id):
    rastreamentos = Rastreamento.query.filter_by(entrega_id=entrega_id).order_by(Rastreamento.timestamp.desc()).all()
    return jsonify([r.to_dict() for r in rastreamentos])