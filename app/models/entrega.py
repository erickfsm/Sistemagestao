from app.extensions import db
from datetime import datetime, date, timedelta
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
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
    CODFORNECFRETE = db.Column(db.Integer, nullable=False)
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
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=True)
    motorista_responsavel = db.relationship('Motorista', backref=db.backref('entregas_atribuidas', lazy=True), overlaps="entregas")
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    motorista = db.relationship('Motorista', backref=db.backref('entregas', lazy=True), overlaps="entregas_atribuidas")

    def _get_working_days_between(self, start_dt: datetime, end_dt: datetime, feriados_customizados: list[date] = None) -> int:
        if not start_dt or not end_dt:
            return None
        start_date_only = start_dt.date()
        end_date_only = end_dt.date()
        if end_date_only < start_date_only:
           return 0
        cal = Brazil()
        holidays_list = [h[0] for h in cal.holidays(start_date_only.year)]
        if feriados_customizados:
            holidays_list.extend(feriados_customizados)
        
        current_date = start_date_only
        working_days_count = 0
        while current_date <= end_date_only:
            is_working = cal.is_working_day(current_date) and current_date not in holidays_list
            if is_working:
                working_days_count += 1
            current_date += timedelta(days=1)
        return working_days_count

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
        today = datetime.now().date()
        dias_atraso = 0
        data_referencia_atraso = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
        if data_referencia_atraso: 
            if self.DATAFINALIZACAO:
                if self.DATAFINALIZACAO.date() > data_referencia_atraso.date():
                    dias_atraso = self._get_working_days_between(data_referencia_atraso, self.DATAFINALIZACAO, feriados_customizados)
                else: 
                    dias_atraso = 0
            else:
                if today > data_referencia_atraso.date():
                    dias_atraso = self._get_working_days_between(data_referencia_atraso, datetime.combine(today, datetime.min.time()), feriados_customizados)
                else: 
                    dias_atraso = 0
        return dias_atraso

    def calcular_prazo_medio(self, feriados_customizados: list[date] = None):
        today = datetime.now().date()
        prazo_medio = 0
        if self.DTCARREGAMENTO: 
            if self.DATAFINALIZACAO:
                prazo_medio = self._get_working_days_between(self.DTCARREGAMENTO, self.DATAFINALIZACAO, feriados_customizados)
            else:
                prazo_medio = self._get_working_days_between(self.DTCARREGAMENTO, datetime.combine(today, datetime.min.time()), feriados_customizados)
        return prazo_medio
    
    def to_dict(self, feriados_customizados: list[date] = None):
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(value, date):
                data[key] = value.strftime('%Y-%m-%d')
        
        data['STATUS'] = self.calcular_status(feriados_customizados)
        data['DIASATRASO'] = self.calcular_dias_atraso(feriados_customizados)
        data['PRAZOMEDIO'] = self.calcular_prazo_medio(feriados_customizados)

        if self.motorista_responsavel:
            data['motorista_nome'] = self.motorista_responsavel.nome
        else:
            data['motorista_nome'] = None

        return data

    def __repr__(self):
        return f'<Entrega {self.id} - Cliente: {self.CLIENTE}>'