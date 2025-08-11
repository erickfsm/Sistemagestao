from app.extensions import db
from datetime import datetime, date

class Devolucao(db.Model):
    __tablename__ = 'devolucoes'

    id = db.Column(db.Integer, primary_key=True)
    entrega_id = db.Column(db.Integer, db.ForeignKey('entregas.id'), nullable=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
 
    tipo_devolucao = db.Column(db.String(20), nullable=True)
    motivo = db.Column(db.String(255), nullable=True)
    observacoes = db.Column(db.String(500), nullable=True)
    data_devolucao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ativa')

    entrega = db.relationship('Entrega', back_populates='devolucoes')
    motorista = db.relationship('Motorista', back_populates='devolucoes')

    def to_dict(self):
        return {
            'id': self.id,
            'entrega_id': self.entrega_id,
            'motorista_id': self.motorista_id,
            'tipo_devolucao': self.tipo_devolucao,
            'motivo': self.motivo,
            'observacoes': self.observacoes,
            'data_devolucao': self.data_devolucao.strftime('%d/%m/%Y %H:%M:%S') if self.data_devolucao else None,
            'data_criacao': self.data_criacao.strftime('%Y-%m-%d %H:%M:%S'),
            'data_atualizacao': self.data_atualizacao.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }
    
    def __repr__(self):
        return f'<Devolucao {self.id} - Entrega: {self.entrega_id} - Status: {self.status}>'