import requests
import json
import logging
from urllib.parse import urljoin

from config.settings import settings

logger = logging.getLogger(__name__)

class BrudamBaseAPI:
    def __init__(self, login_url: str, user: str, password: str, tracking_url_base: str):
        self.login_url = login_url
        self.user = user
        self.password = password
        self.tracking_url_base = tracking_url_base
        self.token = None

        logging.getLogger(__name__).setLevel(logging.DEBUG) 

    def _get_token(self) -> str | None:
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "usuario": self.user, 
            "senha": self.password
        }

        try:
            logger.info(f"Tentando obter token Brudam em: {self.login_url}")
            response = requests.post(self.login_url, headers=headers, data=json.dumps(payload), timeout=10)
            response.raise_for_status() 
            data = response.json()

            token_key_path = ["access_key"] 
            token = data
            for key in token_key_path:
                token = token.get(key)
                if token is None: break

            self.token = token
        
            if self.token:
                logger.info("Token Brudam obtido com sucesso.")
                return self.token
            else:
                logger.error(f"Token não encontrado na resposta Brudam. Resposta: {data}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição ao obter token Brudam: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON ao obter token Brudam: {e} - Resposta: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter token Brudam: {e}")
            return None

    def _execute_tracking_request(self, chave: str, include_comprovante: bool = False) -> dict | None:
 
        if not self.token:
            logger.debug("Token Brudam não disponível. Chamando _get_token()...")
            if not self._get_token():
                logger.error("Não foi possível obter o token Brudam. Abortando rastreamento.")
                return None
        
        from config.settings import settings as current_settings
        full_url = f"{self.tracking_url_base}{chave}"
        if include_comprovante:
            from config.settings import settings as current_settings 
            comprovante_param = current_settings.BRUDAM_COMPROVANTE_PARAM
            if comprovante_param:
                full_url += comprovante_param
            else:
                logger.warning("Parâmetro COMPROVATE_BRUDAM não configurado no .env.")


        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}" 
        }

        try:
            logger.debug(f"Requisição Brudam Tracking URL: {full_url}, Headers: {headers}")
            response = requests.get(full_url, headers=headers, timeout=10)
            logger.debug(f"Resposta Brudam Tracking Status: {response.status_code}, Texto: {response.text}")
            response.raise_for_status() 
            data = response.json()
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de requisição Brudam para chave {chave}: {e}")
            if response.status_code == 401:
                logger.warning("Token Brudam expirado ou inválido. Tentando renovar...")
                self.token = None 
                return self._execute_tracking_request(chave, include_comprovante) 
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON Brudam para chave {chave}: {e} - Resposta: {response.text}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao rastrear Brudam para chave {chave}: {e}")
            return None