from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import date, datetime

class Rastreamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entrega_id = db.Column(db.Integer, db.ForeignKey('entrega.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_descricao = db.Column(db.String(200), nullable=False)
    localizacao = db.Column(db.String(150), nullable=True) # Opcional: cidade/estado do evento

    def to_dict(self):
        return {
            'id': self.id,
            'entrega_id': self.entrega_id,
            'timestamp': self.timestamp.isoformat(),
            'status_descricao': self.status_descricao,
            'localizacao': self.localizacao
        }