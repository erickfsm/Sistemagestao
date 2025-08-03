import requests
import json
from config.settings import settings
from urllib.parse import quote_plus
import logging
from urllib.parse import quote_plus
from datetime import datetime, date

from src.utils.file_handler import download_and_save_comprovante

logger = logging.getLogger(__name__)

class EVSAPI:
    def __init__(self):
        self.login_url = settings.EVS_LOGIN_URL
        self.base_url = settings.EVS_BASE_API_URL
        self.api_version = settings.EVS_API_VERSION
        self.user = settings.EVS_USER
        self.senha = settings.EVS_PASS
        self.sigla = settings.EVS_SIGLA
        self.token = None

    def _get_token(self) -> str | None:
        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "name": self.user,
            "password": self.senha,
            "sigla": self.sigla
        }

        try:
            logger.info(f"Tentando obter token da EVS em: {self.login_url}")
            response = requests.post(self.login_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() 
            data = response.json()

            token_key = "token"
            self.token = data.get(token_key)

            if self.token:
                logger.info("Token EVS obtido com sucesso.")
                return self.token
            else:
                logger.error(f"Token não encontrado na resposta da EVS. Resposta: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição ao obter token da EVS: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON ao obter token da EVS: {e} - Resposta: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter token da EVS: {e}")
            return None

    def rastrear_nf(self, CHAVENFE: str) -> dict | None:
       
        if not self.token:
            logger.info("Token EVS não disponível. Tentando obter...")
            if not self._get_token():
                logger.error("Não foi possível obter o token EVS. Abortando rastreamento.")
                return None

        encoded_user = quote_plus(self.user)
        encoded_senha = quote_plus(self.senha) 

        full_url = (
            f"{self.base_url}{CHAVENFE}/"
            f"usuario/{self.user}/"
            f"senha/{encoded_senha}?"
            f"api-version={self.api_version}"
        )
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

        try:
            logger.info(f"Tentando rastrear NF {CHAVENFE} na EVS em: {full_url}")
            response = requests.get(full_url, headers=headers)
            response.raise_for_status() 
            data = response.json()
            
            return self._processar_dados_rastreamento(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição à API EVS para NF {CHAVENFE}: {e}")
            if response.status_code == 401:
                logging.warning("Token EVS expirado ou inválido. Tentando renovar...")
                self.token = None
            return None
        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON da API EVS para NF {CHAVENFE}: {e} - Resposta: {response.text}")
            return None
        except Exception as e:
            logging.error(f"Erro inesperado ao rastrear NF {CHAVENFE} na EVS: {e}")
            return None

    def _processar_dados_rastreamento(self, api_response: dict) -> dict:
       
        rastreamento_padronizado = {
            "status": "Desconhecido",
            "documento": { 
                "tipo_doc": None,
                "id_doc": None,
                "data_emissao": None,
                "nm_ch_nfe": None
            },
            "eventos": [], 
            "comprovante_link": None 
        }

        if api_response.get("DOCUMENTO"):
            doc_data = api_response["DOCUMENTO"]
            rastreamento_padronizado["documento"]["tipo_doc"] = doc_data.get("TIPO_DOC")
            rastreamento_padronizado["documento"]["id_doc"] = doc_data.get("ID_DOC")
            rastreamento_padronizado["documento"]["data_emissao"] = doc_data.get("DATA_EMISSAO")
            rastreamento_padronizado["documento"]["nm_ch_nfe"] = doc_data.get("NM_CH_NFe")
        
        eventos_api = api_response.get("EVENTOS")
        if isinstance(eventos_api, list):
            for evento_api in eventos_api:
                data_evento = evento_api.get("DATA")
                hora_evento = evento_api.get("HORA")
                
                data_hora_completa = None
                if data_evento and hora_evento:
                    try:
                        data_hora_obj = datetime.strptime(f"{data_evento} {hora_evento}", '%d/%m/%Y %H:%M')
                        data_hora_completa = data_hora_obj.isoformat()
                    except ValueError:
                        logger.warning(f"Formato de data/hora inválido para evento: {data_evento} {hora_evento}")
                        data_hora_completa = f"{data_evento} {hora_evento}" 

                rastreamento_padronizado["eventos"].append({
                    "tipo_evento": evento_api.get("TIPO_EVENTO"),
                    "id_evento": evento_api.get("ID_EVENTO"), 
                    "data": data_evento,
                    "hora": hora_evento,
                    "ocorrencia_codigo": evento_api.get("OCORRENCIA"), 
                    "tipo_origem": evento_api.get("TIPO"), 
                    "descricao": evento_api.get("DESCRICAO"),
                    "observacao": evento_api.get("OBSERVACAO"),
                    "recebedor": evento_api.get("RECEBEDOR"),
                    "data_hora_iso": data_hora_completa, 
                    "link_imagem_evento": evento_api.get("LINK_IMAGEM")
                })
            
            if rastreamento_padronizado["eventos"]:
                ultimo_evento = rastreamento_padronizado["eventos"][-1]
                rastreamento_padronizado["status"] = ultimo_evento.get("descricao", "Status Indisponível")
                ultima_descricao = ultimo_evento.get("descricao", "").upper()

                if "ENTREGA NORMAL" in ultima_descricao:
                    rastreamento_padronizado["status"] = "ENTREGUE"
                    if ultimo_evento.get("link_imagem_evento"):
                         link = ultimo_evento["link_imagem_evento"]
                         if not link.startswith("http://") and not link.startswith("https://"):
                             link = "https://" + link
                         rastreamento_padronizado["comprovante_link"] = link
                elif "EM ROTA" in ultima_descricao:
                    rastreamento_padronizado["status"] = "EM ROTA DE ENTREGA"
                elif "COLETA" in ultima_descricao:
                    rastreamento_padronizado["status"] = "EM COLETA"
                elif "TRANSFERENCIA" in ultima_descricao or "RECEBIDA" in ultima_descricao:
                    rastreamento_padronizado["status"] = "EM TRÂNSITO / RECEBIDA FILIAL"
                elif "EXTRAVIO" in ultima_descricao or "AVARIA" in ultima_descricao or "ROUBO" in ultima_descricao:
                    rastreamento_padronizado["status"] = "OCORRÊNCIA / PROBLEMA"
                else:
                    rastreamento_padronizado["status"] = "ANDAMENTO"

        return rastreamento_padronizado
