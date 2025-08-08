import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class BrudamBaseAPI:
    def __init__(self, login_url: str, user: str, password: str, tracking_url_base: str):
        self.login_url = login_url
        self.user = user
        self.password = password
        self.tracking_url_base = tracking_url_base
        self.token = None
        self.name = "BrudamBase"

    def _obter_token(self) -> str | None:
        if self.token:
            return self.token
        
        headers = {'Content-Type': 'application/json'}
        payload = {"usuario": self.user, "senha": self.password}
        
        try:
            response = requests.post(self.login_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            self.token = response.json().get("token")
            logger.info(f"Token obtido com sucesso para a API {self.name}.")
            return self.token
        except requests.exceptions.RequestException as e:
            logger.error(f"Falha ao obter token para a API {self.name}: {e}")
            return None

    def _execute_tracking_request(self, chave_nfe: str, include_comprovante: bool = False) -> dict | None:
        token = self._obter_token()
        if not token:
            return None

        url = f"{self.tracking_url_base}/{chave_nfe}"
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 404:
                logger.warning(f"Nenhum dado de rastreamento encontrado para a chave {chave_nfe} na API {self.name}.")
                return None
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Falha na requisição de rastreamento para a chave {chave_nfe} na API {self.name}: {e}")
            return None