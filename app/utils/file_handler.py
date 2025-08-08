import requests
import os
from werkzeug.utils import secure_filename
from flask import current_app
from ..extensions import db

def baixar_e_salvar_comprovante(entrega_id: int, url_comprovante: str):

    from ..models import Comprovante

    if not url_comprovante:
        return None

    try:
        if Comprovante.query.filter_by(entrega_id=entrega_id).first():
            print(f"Comprovante para a entrega {entrega_id} já existe.")
            return None

        response = requests.get(url_comprovante, stream=True, timeout=20)
        response.raise_for_status()

        base_filename = os.path.basename(url_comprovante).split('?')[0]
        filename = f"comprovante_{entrega_id}_{secure_filename(base_filename)}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        file_path = os.path.join(upload_folder, filename)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        novo_comprovante = Comprovante(
            entrega_id=entrega_id,
            nome_arquivo=filename,
            caminho_arquivo=file_path
        )
        db.session.add(novo_comprovante)
        db.session.commit()
        
        print(f"Comprovante para a entrega {entrega_id} baixado e salvo com sucesso.")
        return novo_comprovante

    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o comprovante da URL {url_comprovante}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao salvar o comprovante para a entrega {entrega_id}: {e}")
        db.session.rollback()
        return None