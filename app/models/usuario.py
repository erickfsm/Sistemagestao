from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime 

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    role = db.Column(db.String(20), default='agente', nullable=False)
    
    role = db.Column(db.String(20), default='agente', nullable=False) 

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'login': self.login,
            'ativo': self.ativo,
            'role': self.role 
        }

    def __repr__(self):
        return f"<Usuario {self.id} - {self.nome} - Role: {self.role}>"