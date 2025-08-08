from app.extensions import db
from datetime import datetime

class Rastreamento(db.Model):
    __tablename__ = 'rastreamento'
    
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status_descricao = db.Column(db.String(200), nullable=False)
    localizacao = db.Column(db.String(150), nullable=True)
    
    entrega_id = db.Column(db.Integer, db.ForeignKey('entregas.id'), nullable=False)
    
    def __repr__(self):
        return f'<Rastreamento {self.id} - {self.status_descricao}>'