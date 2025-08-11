import requests
import json
import logging
from datetime import datetime
from urllib.parse import urljoin 

from config import Config

logger = logging.getLogger(__name__)

class SSWAPI:
    def __init__(self):
        self.base_url = Config.SSW_BASE_URL
        self.senha_ampla = Config.SSW_API_PASSWORD_AMPLA 
        self.senha_tg = Config.SSW_API_PASSWORD_TG 

    def rastrear_nf(self, num_nota: str, cnpj_filial: str, tipo_ssw_servico: str = "AMPLA") -> dict | None:
 
        full_url = self.base_url
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj_filial)) 

        senha_para_uso = None
        if tipo_ssw_servico.upper() == "AMPLA":
            senha_para_uso = self.senha_ampla
        elif tipo_ssw_servico.upper() == "TG":
            senha_para_uso = self.senha_tg
        else:
            logger.error(f"Tipo de serviço SSW '{tipo_ssw_servico}' inválido ou senha não configurada.")
            return {"status": "Falha", "message": f"Configuração de senha SSW para '{tipo_ssw_servico}' inválida."}

        if not senha_para_uso: 
            logger.error(f"Senha SSW não encontrada para o CNPJ de filial: {cnpj_filial} e tipo {tipo_ssw_servico}. Verifique seu .env.")
            return {"status": "Falha", "message": f"Senha SSW não configurada para o CNPJ {cnpj_filial} e tipo {tipo_ssw_servico}."}

        payload = {
            "cnpj": cnpj_limpo, 
            "senha": senha_para_uso,
            "nro_nf": num_nota
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"Tentando rastrear NF {num_nota} na SSW (CNPJ: {cnpj_filial}, usando credenciais AMPLA) em: {full_url}")
            response = requests.post(full_url, headers=headers, data=json.dumps(payload), timeout=10)
            response.raise_for_status() 
            data = response.json()
            
            return self._processar_dados_rastreamento(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição à API SSW para NF {num_nota} (CNPJ: {cnpj_filial}): {e} - Resposta: {response.text if response else 'N/A'}")
            return {"status": "Falha", "message": f"Erro de conexão/HTTP na SSW: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da API SSW para NF {num_nota} (CNPJ: {cnpj_filial}): {e} - Resposta: {response.text}")
            return {"status": "Falha", "message": f"Erro de JSON na SSW: {e}"}
        except Exception as e:
            logger.error(f"Erro inesperado ao rastrear NF {num_nota} (CNPJ: {cnpj_filial}): {e}")
            return {"status": "Falha", "message": f"Erro inesperado na SSW: {e}"}

    def _processar_dados_rastreamento(self, api_response: dict) -> dict:
        rastreamento_padronizado = {
            "status": "Desconhecido",
            "documento": { 
                "remetente": None,
                "destinatario": None,
                "nro_nf": None 
            },
            "eventos": [], 
            "comprovante_link": None 
        }

        if not api_response.get("success"):
            return {"status": "Erro API", "message": api_response.get("message", "Erro desconhecido da SSW.")}
        
        header_data = api_response.get("header")
        if header_data:
            rastreamento_padronizado["documento"]["remetente"] = header_data.get("remetente")
            rastreamento_padronizado["documento"]["destinatario"] = header_data.get("destinatario")
            
            comprovante_link_ssw = header_data.get("comprovante")
            if comprovante_link_ssw:
                if not comprovante_link_ssw.startswith("http://") and not comprovante_link_ssw.startswith("https://"):
                    comprovante_link_ssw = "https://" + comprovante_link_ssw 
                rastreamento_padronizado["comprovante_link"] = comprovante_link_ssw
        
        tracking_events = api_response.get("tracking")
        if isinstance(tracking_events, list):
            for evento_ssw in tracking_events:
                data_hora_str = evento_ssw.get("data_hora")
                data_hora_iso = None
                if data_hora_str:
                    try:
                        data_hora_obj = datetime.fromisoformat(data_hora_str) 
                        data_hora_iso = data_hora_obj.isoformat()
                    except ValueError:
                        logger.warning(f"Formato de data_hora SSW inválido para evento: {data_hora_str}")
                        data_hora_iso = data_hora_str

                rastreamento_padronizado["eventos"].append({
                    "data_hora": evento_ssw.get("data_hora"), 
                    "data_hora_iso": data_hora_iso, 
                    "dominio": evento_ssw.get("dominio"),
                    "filial": evento_ssw.get("filial"),
                    "cidade": evento_ssw.get("cidade"),
                    "ocorrencia": evento_ssw.get("ocorrencia"),
                    "codigo_ocorrencia": evento_ssw.get("codigo_ocorrencia"),
                    "descricao": evento_ssw.get("descricao"),
                    "tipo_evento_ssw": evento_ssw.get("tipo"),
                    "data_hora_efetiva": evento_ssw.get("data_hora_efetiva"),
                    "nome_recebedor": evento_ssw.get("nome_recebedor"),
                    "nro_doc_recebedor": evento_ssw.get("nro_doc_recebedor")
                })
            
            if rastreamento_padronizado["eventos"]:
                ultimo_evento = rastreamento_padronizado["eventos"][-1]
                ultima_ocorrencia = ultimo_evento.get("ocorrencia", "").upper()
                
                if "MERCADORIA ENTREGUE" in ultima_ocorrencia:
                    rastreamento_padronizado["status"] = "ENTREGUE"
                elif "SAIDA PARA ENTREGA" in ultima_ocorrencia:
                    rastreamento_padronizado["status"] = "EM ROTA DE ENTREGA"
                elif "SAIDA DE UNIDADE" in ultima_ocorrencia or "CHEGADA EM UNIDADE" in ultima_ocorrencia or "EM TRÂNSITO" in ultima_ocorrencia:
                    rastreamento_padronizado["status"] = "EM TRÂNSITO / RECEBIDA FILIAL"
                elif "DOCUMENTO DE TRANSPORTE EMITIDO" in ultima_ocorrencia or "COLETA REALIZADA" in ultima_ocorrencia:
                    rastreamento_padronizado["status"] = "EM COLETA / EMISSAO"
                elif "OCORRENCIA" in ultima_ocorrencia or "AVARIA" in ultima_ocorrencia or "EXTRAVIO" in ultima_ocorrencia:
                    rastreamento_padronizado["status"] = "OCORRÊNCIA / PROBLEMA"
                else:
                    rastreamento_padronizado["status"] = "ANDAMENTO"

        return rastreamento_padronizado