from app.extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import ForeignKey
from workalendar.america import Brazil

ENTREGAS_STATUS = (
    'ENTREGA_PENDENTE',
    'ENTREGUE_AGUARDANDO_COMPROVANTE',
    'ENTREGA_FINALIZADA',
    'DEVOLUCAO_PARCIAL',
    'DEVOLUCAO_TOTAL',
)

class Entrega(db.Model):
    __tablename__ = 'entregas'

    id = db.Column(db.Integer, primary_key=True)
    CODFILIAL = db.Column(db.Integer, nullable=False)
    DTFAT = db.Column(db.DateTime, nullable=False)
    DTCARREGAMENTO = db.Column(db.DateTime, nullable=False)
    ROMANEIO = db.Column(db.Integer, nullable=False)
    TIPOVENDA = db.Column(db.Integer, nullable=False)
    NUMNOTA = db.Column(db.Integer, nullable=False)
    NUMPED = db.Column(db.Integer, nullable=False)
    CODCLI = db.Column(db.Integer, nullable=False)
    CLIENTE = db.Column(db.String(200), nullable=False)
    MUNICIPIO = db.Column(db.String(50), nullable=False)
    UF = db.Column(db.String(2), nullable=False)
    EMAIL = db.Column(db.String(100), nullable=True)
    TELCOM = db.Column(db.String(20), nullable=True)
    EMAIL_1 = db.Column(db.String(100), nullable=True)
    TRANSPORTADORA = db.Column(db.String(200), nullable=False)
    VLTOTAL = db.Column(db.Float(10, 2), nullable=False)
    NUMVOLUME = db.Column(db.Integer, nullable=False)
    TOTPESO = db.Column(db.Float(10, 2), nullable=False)
    PRAZOENTREGA = db.Column(db.Integer, nullable=False)
    CHAVENFE = db.Column(db.String(44), nullable=False)
    PREVISAOENTREGA = db.Column(db.DateTime, nullable=True)
    DATAFINALIZACAO = db.Column(db.DateTime, nullable=True)
    STATUS = db.Column(ENUM(*ENTREGAS_STATUS, name='entregas_status_enum', create_type=False), default='ENTREGA_PENDENTE', nullable=False)
    DIASATRASO = db.Column(db.Integer, nullable=True)
    PRAZOMEDIO = db.Column(db.Integer, nullable=True)
    AGENDAMENTO = db.Column(db.DateTime, nullable=True)
    DEVOLUCAO = db.Column(db.Boolean, nullable=False, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    transportadora_cod = db.Column("CODFORNECFRETE", db.Integer, ForeignKey('transportadora.codfornecfrete'))
    transportadora = db.relationship('Transportadora', back_populates='entregas', foreign_keys=[transportadora_cod])
    
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=True)
    motorista = db.relationship('Motorista', backref=db.backref('entregas', lazy=True))

    comprovantes = db.relationship('Comprovante', backref='entrega', lazy=True, cascade="all, delete-orphan")
    devolucoes = db.relationship('Devolucao', backref='entrega', lazy=True, cascade="all, delete-orphan")
    rastreamentos = db.relationship('Rastreamento', backref='entrega', lazy=True, cascade="all, delete-orphan")

    def _get_working_days_between(self, start_dt: datetime, end_dt: datetime, feriados_customizados: list[date] = None) -> int:
        if not start_dt or not end_dt:
            return 0
        start_date_only = start_dt.date()
        end_date_only = end_dt.date()
        if end_date_only < start_date_only:
            return 0
        cal = Brazil()

        return cal.get_working_days_delta(start_date_only, end_date_only)

    def calcular_status(self, feriados_customizados: list[date] = None):
        if not self.DTCARREGAMENTO:
            return 'Saida do CD Pendente'
        elif self.DATAFINALIZACAO:
            data_comparacao_prazo = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
            if data_comparacao_prazo and self.DATAFINALIZACAO.date() <= data_comparacao_prazo.date():
                return 'Entrega Concluída - No prazo'
            else:
                return 'Entrega Concluída - Fora do prazo'
        else: 
            data_comparacao_prazo = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
            if data_comparacao_prazo and data_comparacao_prazo.date() >= datetime.now().date():
                return 'Entrega Pendente - No prazo'
            else:
                return 'Entrega Pendente - Fora do prazo'
    
    def calcular_dias_atraso(self, feriados_customizados: list[date] = None):
        today = datetime.now()
        dias_atraso = 0
        data_referencia_atraso = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
        if not data_referencia_atraso:
            return 0
            
        data_final = self.DATAFINALIZACAO if self.DATAFINALIZACAO else today

        if data_final.date() > data_referencia_atraso.date():
            dias_atraso = self._get_working_days_between(data_referencia_atraso, data_final, feriados_customizados)
            
        return dias_atraso

    def calcular_prazo_medio(self, feriados_customizados: list[date] = None):
        if not self.DTCARREGAMENTO:
            return 0
        
        data_final = self.DATAFINALIZACAO if self.DATAFINALIZACAO else datetime.now()
        prazo_medio = self._get_working_days_between(self.DTCARREGAMENTO, data_final, feriados_customizados)
        return prazo_medio
    
    def to_dict(self, feriados_customizados: list[date] = None):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        for key, value in data.items():
            if isinstance(value, (datetime, date)):
                data[key] = value.isoformat()
        
        data['STATUS'] = self.calcular_status(feriados_customizados)
        data['DIASATRASO'] = self.calcular_dias_atraso(feriados_customizados)
        data['PRAZOMEDIO'] = self.calcular_prazo_medio(feriados_customizados)

        if self.motorista:
            data['motorista_nome'] = self.motorista.nome
        else:
            data['motorista_nome'] = None

        return data

    def __repr__(self):
        return f'<Entrega {self.NUMNOTA}>'