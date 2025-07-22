from app.extensions import db
from datetime import datetime, date, timedelta
from workalendar.america import Brazil

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
    PREVISAOENTREGA = db.Column(db.DateTime, nullable=False)
    DATAFINALIZACAO = db.Column(db.DateTime, nullable=True)
    STATUS = db.Column(db.String(20), nullable=True)
    DIASATRASO = db.Column(db.Integer, nullable=True)
    PRAZOMEDIO = db.Column(db.Integer, nullable=True)
    AGENDAMENTO = db.Column(db.DateTime, nullable=True)
    DEVOLUCAO = db.Column(db.Boolean, nullable=False, default=False)
    motorista_id = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    motorista_responsavel = db.relationship('Motorista', backref=db.backref('entregas_atribuidas', lazy=True))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    motorista = db.relationship('Motorista', backref=db.backref('entregas', lazy=True))


    def _get_working_days_between(self, start_dt: datetime, end_dt: datetime, feriados_customizados: list[date] = None) -> int:
        if not start_dt or not end_dt:
            return None

        start_date_only = start_dt.date()
        end_date_only = end_dt.date()

        if end_date_only < start_date_only:
           return 0
    
        cal = Brazil()

        temp_cal = Brazil()
        if feriados_customizados:
           for holiday_date in feriados_customizados:
               if isinstance(holiday_date, date):
                  temp_cal.add_holiday((holiday_date.year, holiday_date.month, holiday_date.day, "Feriado Customizado"))

        current_date = start_date_only
        working_days_count = 0
        while current_date <= end_date_only:
            is_holiday_custom = False
            if feriados_customizados:
                is_holiday_custom = current_date in feriados_customizados

            if temp_cal.is_working_day(current_date) and not is_holiday_custom:
                working_days_count += 1
            current_date += timedelta(days=1)
        return working_days_count

    def to_dict(self, feriados_customizados: list[date] = None  ):
        today = datetime.now().date()
        data = {
            'motorista_id': self.motorista_id,
        }
        if self.motorista_responsavel:
            data['motorista_nome'] = self.motorista_responsavel.nome
            return data

        status = None
        if self.DTCARREGAMENTO and self.DTCARREGAMENTO.year < 2023:
            status = 'Carregamento Pendente'
        elif self.DATAFINALIZACAO:
            data_comparacao_prazo = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
            if data_comparacao_prazo and self.DATAFINALIZACAO.date() <= data_comparacao_prazo.date():
                status = 'Entrega Concluída - No prazo'
            else: 
                status = 'Entrega Concluída - Fora do prazo'
        else: 
            data_comparacao_prazo = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA
            if data_comparacao_prazo and data_comparacao_prazo.date() >= today:
                status = 'Entrega Pendente - No prazo'
            else:
                status = 'Entrega Pendente - Fora do prazo'
        
        dias_atraso = None
        data_referencia_atraso = self.AGENDAMENTO if self.AGENDAMENTO else self.PREVISAOENTREGA

        if data_referencia_atraso: 
            if self.DATAFINALIZACAO:
                if self.DATAFINALIZACAO.date() > data_referencia_atraso.date():
                    dias_atraso = self._get_working_days_between(data_referencia_atraso, self.DATAFINALIZACAO, feriados_customizados)
                else: 
                    dias_atraso = 0
            else:
                if today > data_referencia_atraso.date():
                    dias_atraso = self._get_working_days_between(data_referencia_atraso, datetime.combine(today, date.min.time()), feriados_customizados)
                else: 
                    dias_atraso = 0

        prazo_medio = None
        if self.DTCARREGAMENTO: 
            if self.DATAFINALIZACAO:
                prazo_medio = self._get_working_days_between(self.DTCARREGAMENTO, self.DATAFINALIZACAO, feriados_customizados)
            else:
                prazo_medio = self._get_working_days_between(self.DTCARREGAMENTO, datetime.combine(today, date.min.time()), feriados_customizados)
        
        return {
            'id': self.id,
            'CODFILIAL': self.CODFILIAL,
            'DTFAT': self.DTFAT.strftime('%d/%m/%Y %H:%M:%S') if self.DTFAT else None,
            'DTCARREGAMENTO': self.DTCARREGAMENTO.strftime('%d/%m/%Y %H:%M:%S') if self.DTCARREGAMENTO else None,
            'ROMANEIO': self.ROMANEIO,
            'TIPOVENDA': self.TIPOVENDA,
            'NUMNOTA': self.NUMNOTA,
            'NUMPED': self.NUMPED,
            'CODCLI': self.CODCLI,
            'CLIENTE': self.CLIENTE,
            'MUNICIPIO': self.MUNICIPIO,
            'UF': self.UF,
            'EMAIL': self.EMAIL,
            'TELCOM': self.TELCOM,
            'EMAIL_1': self.EMAIL_1,
            'CODFORNECFRETE': self.CODFORNECFRETE,
            'TRANSPORTADORA': self.TRANSPORTADORA,
            'VL_TOTAL': float(self.VL_TOTAL) if self.VL_TOTAL is not None else None,
            'NUMVOLUME': self.NUMVOLUME,
            'TOTPESO': float(self.TOTPESO) if self.TOTPESO is not None else None,
            'PRAZOENTREGA': self.PRAZOENTREGA, # Int
            'CHAVENFE': self.CHAVENFE,
            'PREVISAOENTREGA': self.PREVISAOENTREGA.strftime('%d/%m/%Y %H:%M:%S') if self.PREVISAOENTREGA else None, # DateTime
            'DATAFINALIZACAO': self.DATAFINALIZACAO.strftime('%d/%m/%Y %H:%M:%S') if self.DATAFINALIZACAO else None, # DateTime
            'AGENDAMENTO': self.AGENDAMENTO.strftime('%d/%m/%Y %H:%M:%S') if self.AGENDAMENTO else None, # DateTime
            'DEVOLUCAO': self.DEVOLUCAO, # Boolean
            # Dinamically calculated fields
            'STATUS': status,
            'DIASATRASO': dias_atraso,
            'PRAZOMEDIO': prazo_medio,
        }

    def __repr__(self):
        return f'<Entrega {self.id} - Cliente: {self.CLIENTE}>'