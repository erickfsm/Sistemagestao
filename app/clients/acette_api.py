import logging
from .brudam_base_api import BrudamBaseAPI
from config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class AcetteAPI(BrudamBaseAPI):
    def __init__(self):
        super().__init__(
            login_url=Config.ACETTE_LOGIN_URL,
            user=Config.ACETTE_USER,
            password=Config.ACETTE_PASS,
            tracking_url_base=Config.ACETTE_TRACKING_URL
        )
        self.name = "ACETTE"
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    def rastrear_nf(self, chave_nfe: str, include_comprovante: bool = False) -> dict | None:
        api_response = self._execute_tracking_request(chave_nfe, include_comprovante)
        
        if api_response:
            return self._processar_dados_rastreamento(api_response)
        
        return {"status": "Falha", "message": f"Falha na requisição Acette para chave {chave_nfe}."}

    def _processar_dados_rastreamento(self, api_response: dict) -> dict:
        rastreamento_padronizado = {
            "status": "Desconhecido",
            "documento": {
                "chave_nfe": None,
                "nro_nf": None,
                "remetente": None,
                "destinatario": None
            },
            "eventos": [],
            "comprovante_link": None
        }
        
        brudam_data = api_response.get("data", api_response)

        if brudam_data.get("nfe"):
            nfe_data = brudam_data["nfe"]
            rastreamento_padronizado["documento"]["nro_nf"] = nfe_data.get("numero")
            rastreamento_padronizado["documento"]["chave_nfe"] = nfe_data.get("chave")
            rastreamento_padronizado["documento"]["remetente"] = nfe_data.get("remetente")
            rastreamento_padronizado["documento"]["destinatario"] = nfe_data.get("destinatario")

        ocorrencias = brudam_data.get("ocorrencias")
        if isinstance(ocorrencias, list):
            for ocorrencia in ocorrencias:
                data_hora_str = ocorrencia.get("data_ocorrencia")
                data_hora_iso = None
                try:
                    data_hora_obj = datetime.fromisoformat(data_hora_str)
                    data_hora_iso = data_hora_obj.isoformat()
                except (ValueError, TypeError):
                    logger.warning(f"Formato de data_hora Acette inválido: {data_hora_str}")
                    data_hora_iso = data_hora_str

                rastreamento_padronizado["eventos"].append({
                    "data_hora": ocorrencia.get("data_ocorrencia"),
                    "data_hora_iso": data_hora_iso,
                    "descricao": ocorrencia.get("descricao_ocorrencia"),
                    "codigo_ocorrencia": ocorrencia.get("codigo_ocorrencia"),
                    "filial": ocorrencia.get("filial_ocorrencia"),
                    "cidade": ocorrencia.get("cidade_ocorrencia")
                })
            
            if rastreamento_padronizado["eventos"]:
                ultimo_evento_desc = rastreamento_padronizado["eventos"][-1].get("descricao", "").upper()
                if "ENTREGUE" in ultimo_evento_desc:
                    rastreamento_padronizado["status"] = "ENTREGUE"
                elif "SAIDA PARA ENTREGA" in ultimo_evento_desc:
                    rastreamento_padronizado["status"] = "EM ROTA DE ENTREGA"
                else:
                    rastreamento_padronizado["status"] = "EM TRÂNSITO"

        return rastreamento_padronizado