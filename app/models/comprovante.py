from main import db

class Comprovante(db.Model):
    __tablename__ = 'comprovantes'

    id = db.Column(db.Integer, primary_key=True)
    entrega_id = db.Column(db.Integer, db.ForeignKey('entregas.id'))
    tipo = db.Column(db.String(50), nullable=False)  # ex: 'foto', 'assinatura', 'documento'
    caminho_arquivo = db.Column(db.String(300), nullable=False)
    data_envio = db.Column(db.DateTime)