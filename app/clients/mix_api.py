import requests
import json
import logging
from datetime import datetime
from urllib.parse import urljoin 

from config.settings import settings 

logger = logging.getLogger(__name__)

class MIXAPI:
    def __init__(self):
        self.login_url = settings.MIX_LOGIN_URL
        self.tracking_url = settings.MIX_TRACKING_URL
        self.auth = settings.MIX_AUTH_BASE64
        self.token = None

    def _get_token(self) -> str | None:

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.auth
        }
        payload = {

            "CodWebService": 3

        }

        try:
            logger.info(f"Tentando obter token da MIX em: {self.login_url}")
            response = requests.post(self.login_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()

            token_key_path = ["SdtRetornoEasyToken", "TokenWebService"]
            token = data
            for key in token_key_path:
                token = token.get(key)
                if token is None: break

            self.token = token

            if self.token:
                logger.info("Token MIX obtido com sucesso.")
                return self.token
            else:
                logger.error(f"Token não encontrado na resposta da MIX. Resposta: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição ao obter token da MIX: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON ao obter token da MIX: {e} - Resposta: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter token da MIX: {e}")
            return None

    def rastrear_nf(self, cte_number: str) -> dict | None:
        if not self.token:
            logger.info("Token MIX não disponível. Tentando obter...")
            if not self._get_token():
                logger.error("Não foi possível obter o token MIX. Abortando rastreamento.")
                return None

        headers = {
            "Content-Type": "application/json", 
        }

        payload = {
            "TokenWebService":"4650e988-881c-4c28-9c1d-b782e60cc066",
            "TipoConsulta":2,
            "CNPJ":0,
            "String":"31250212047164000153550010002405921190676623"
        }
        
        try:
            logger.info(f"Tentando rastrear CTe {cte_number} na MIX em: {self.tracking_url}")
            response = requests.post(self.tracking_url, headers=headers, json=payload) 
            response.raise_for_status()
            data = response.json()
            
            return self._processar_dados_rastreamento(data)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição à API MIX para CTe {cte_number}: {e}")
            if response.status_code == 401:
                logger.warning("Token MIX expirado ou inválido. Tentando renovar...")
                self.token = None 
                return self.rastrear_nf(cte_number)
            return {"status": "Falha", "message": f"Erro de conexão/HTTP na MIX: {e}"}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON da API MIX para CTe {cte_number}: {e} - Resposta: {response.text}")
            return {"status": "Falha", "message": f"Erro de JSON na MIX: {e}"}
        except Exception as e:
            logger.error(f"Erro inesperado ao rastrear CTe {cte_number} na MIX: {e}")
            return {"status": "Falha", "message": f"Erro inesperado na MIX: {e}"}

    def _processar_dados_rastreamento(self, api_response: dict) -> dict:
        rastreamento_padronizado = {
            "status": "Desconhecido",
            "documento": { 
                "ct_numero": None, 
                "remetente": None,
                "destinatario": None,
                "data_emissao_ct": None
            },
            "eventos": [], 
            "comprovante_link": None 
        }

        # ADAPTE TODO O PROCESSAMENTO ABAIXO PARA O FORMATO REAL DA RESPOSTA DA MIX
        # Exemplo: A MIX pode retornar algo como {"consultaCTeResult": {...}}
        # Supondo que a resposta principal esteja em 'consultaCTeResult'
        mix_result = api_response.get("consultaCTeResult", api_response)

        # Processa dados do documento/CTe
        if mix_result.get("nrCt"):
            rastreamento_padronizado["documento"]["ct_numero"] = mix_result.get("nrCt")
            rastreamento_padronizado["documento"]["remetente"] = mix_result.get("nmRemetente")
            rastreamento_padronizado["documento"]["destinatario"] = mix_result.get("nmDestinatario")
            rastreamento_padronizado["documento"]["data_emissao_ct"] = mix_result.get("dtEmissao")

        # Processa eventos (Ex: se os eventos estiverem em 'historicoOcorrencias')
        eventos_mix = mix_result.get("historicoOcorrencias")
        if isinstance(eventos_mix, list):
            for evento in eventos_mix:
                data_hora_str = f"{evento.get('dataOcorrencia')} {evento.get('horaOcorrencia')}"
                data_hora_iso = None
                try:
                    data_hora_obj = datetime.strptime(data_hora_str, '%d/%m/%Y %H:%M') 
                    data_hora_iso = data_hora_obj.isoformat()
                except ValueError:
                    logger.warning(f"Formato de data/hora MIX inválido: {data_hora_str}")
                    data_hora_iso = data_hora_str

                rastreamento_padronizado["eventos"].append({
                    "data": evento.get("dataOcorrencia"),
                    "hora": evento.get("horaOcorrencia"),
                    "descricao": evento.get("descricaoOcorrencia"),
                    "local": evento.get("localOcorrencia"),
                    "data_hora_iso": data_hora_iso
                })
            
            if rastreamento_padronizado["eventos"]:
                ultimo_evento_desc = rastreamento_padronizado["eventos"][-1].get("descricao", "").upper()
                if "ENTREGUE" in ultimo_evento_desc:
                    rastreamento_padronizado["status"] = "ENTREGUE"
                elif "EM ROTA" in ultimo_evento_desc:
                    rastreamento_padronizado["status"] = "EM ROTA DE ENTREGA"
                else:
                    rastreamento_padronizado["status"] = "ANDAMENTO"

        return rastreamento_padronizado