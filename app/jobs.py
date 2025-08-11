from datetime import datetime, date
from flask import Flask
from config import Config
from app.extensions import db
from .models import Entrega, Rastreamento

from .clients.acette_api import AcetteAPI
from .clients.evs_api import EVSAPI
from .clients.mix_api import MIXAPI
from .clients.ssw_api import SSWAPI

API_CLIENTS = {
    'ACETTE': AcetteAPI,
    'EVS': EVSAPI,
    'MIX': MIXAPI,
    'SSW': SSWAPI
 
}

def tarefa_rastreamento_especifico(app: Flask, entrega_id: int):
    with app.app_context():
        print(f"Executando rastreamento agendado para a entrega ID: {entrega_id}")
        entrega = db.session.get(Entrega, entrega_id)

        if not entrega or entrega.DATAFINALIZACAO:
            print(f"Entrega {entrega_id} já finalizada ou não encontrada. Cancelando rastreamento.")
            return

        identifier = entrega.transportadora.api_identifier if entrega.transportadora else None
        ApiClientClass = API_CLIENTS.get(identifier)

        if not ApiClientClass:
            print(f"Nenhum cliente de API encontrado para a entrega {entrega_id}. Pulando.")
            return

        try:
            api_client = ApiClientClass()
            dados_padronizados = api_client.rastrear_nf(entrega.CHAVENFE)
 
            if identifier == 'SSW':
                cnpj_filial = Config.FILIAL_CNPJ_MAP.get(entrega.CODFILIAL)
                tipo_servico = entrega.transportadora.api_config_key

                if not cnpj_filial or not tipo_servico:
                    print(f"CNPJ da filial ou tipo de serviço SSW não configurado para entrega {entrega.id}")
                    return

                dados_padronizados = api_client.rastrear_nf(
                    num_nota=entrega.NUMNOTA,
                    cnpj_filial=cnpj_filial,
                    tipo_ssw_servico=tipo_servico
                )
            else:
                dados_padronizados = api_client.rastrear_nf(chave_nfe=entrega.CHAVENFE)

            if dados_padronizados and dados_padronizados.get("eventos"):
                Rastreamento.query.filter_by(entrega_id=entrega_id).delete()
                for evento in dados_padronizados["eventos"]:
                    novo_evento = Rastreamento(
                        entrega_id=entrega_id,
                        timestamp=evento.get("data_hora_iso"),
                        status_descricao=evento.get("descricao"),
                        localizacao=evento.get("cidade")
                    )
                    db.session.add(novo_evento)
                
                entrega.status = dados_padronizados.get("status", entrega.status)
                db.session.commit()
                print(f"Rastreamento da entrega {entrega_id} atualizado com sucesso.")
        except Exception as e:
            print(f"Erro ao processar a API para a entrega {entrega_id}: {e}")

def tarefa_de_verificacao_diaria(app: Flask, scheduler):
    with app.app_context():
        from .models import Entrega, Rastreamento
        from . import scheduler
        
        hoje = date.today()
        print(f"[{hoje}] Procurando por entregas com previsão para hoje...")

        entregas_para_hoje_ou_atrasadas = Entrega.query.filter(
            db.func.date(Entrega.PREVISAOENTREGA) <= hoje,
            Entrega.DATAFINALIZACAO.is_(None)
        ).all()
        
        print(f"Encontradas {len(entregas_para_hoje_ou_atrasadas)} entregas para agendar rastreamento hoje.")

        for entrega in entregas_para_hoje_ou_atrasadas:
            print(f"Agendando rastreamentos para a entrega ID: {entrega.id} às 11:30, 16:00 e 17:30.")
            job_id_base = f"entrega_{entrega.id}"
            if scheduler.get_job(f"{job_id_base}_1130"): scheduler.remove_job(f"{job_id_base}_1130")
            if scheduler.get_job(f"{job_id_base}_1600"): scheduler.remove_job(f"{job_id_base}_1600")
            if scheduler.get_job(f"{job_id_base}_1730"): scheduler.remove_job(f"{job_id_base}_1730")
            
            scheduler.add_job(tarefa_rastreamento_especifico, 'cron', hour=11, minute=30, args=[app, entrega.id], id=f"{job_id_base}_1130")
            scheduler.add_job(tarefa_rastreamento_especifico, 'cron', hour=16, minute=0, args=[app, entrega.id], id=f"{job_id_base}_1600")
            scheduler.add_job(tarefa_rastreamento_especifico, 'cron', hour=17, minute=30, args=[app, entrega.id], id=f"{job_id_base}_1730")