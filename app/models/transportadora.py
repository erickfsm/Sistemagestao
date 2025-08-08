from app.extensions import db

class Transportadora(db.Model):
    __tablename__ = 'transportadora'
    codfornecfrete = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    api_identifier = db.Column(db.String(50), nullable=True)

    api_config_key = db.Column(db.String(50), unique=True, nullable=True)

    entregas = db.relationship('Entrega', back_populates='transportadora', foreign_keys='Entrega.transportadora_cod')

    def __repr__(self):
        return f'<Transportadora {self.nome}>'