from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class Motorista(db.Model):
    __tablename__ = 'motoristas'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(500), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=db.func.current_timestamp())
    data_atualizacao = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    comprovantes = db.relationship('Comprovante', back_populates='motorista', lazy='dynamic')
    devolucoes = db.relationship('Devolucao', back_populates='motorista', lazy='dynamic')
    entregas = db.relationship('Entrega', back_populates='motorista', lazy='dynamic')

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'login': self.login,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat()
        }
    
    def __repr__(self):
        return f'<Motorista {self.id} - {self.nome}>'