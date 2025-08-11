from app.extensions import db
from datetime import datetime, date

class Comprovante(db.Model):
    __tablename__ = 'comprovantes'

    id = db.Column(db.Integer, primary_key=True)
    entrega_id = db.Column(db.Integer, db.ForeignKey('entregas.id'), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    caminho_arquivo = db.Column(db.String(255), nullable=False)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    entrega = db.relationship('Entrega', back_populates='comprovantes')
    motorista = db.relationship('Motorista',  back_populates='comprovantes')

    def to_dict(self):
        return {
            'id': self.id,
            'entrega_id': self.entrega_id,
            'motorista_id': self.motorista_id,
            'tipo': self.tipo,
            'caminho_arquivo': self.caminho_arquivo,
            'data_envio': self.data_envio.strftime('%d/%m/%Y %H:%M:%S') if self.data_envio else None
        }
    
    def __repr__(self):
        return f'<Comprovante {self.id} - Entrega {self.entrega_id}>'