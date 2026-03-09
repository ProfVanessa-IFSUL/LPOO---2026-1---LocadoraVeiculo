from datetime import date, datetime
from .veiculo import Veiculo
from .ExcecoesPersonalizadas import DataInvalidaError
from .LocacaoStrategy import *


class Locacao:

    def __init__(self, veiculo: Veiculo, data_inicio: date=datetime.now().date(), data_fim: date=None, estrategia:CalculoLocacaoStrategy = CalculoPadraoStrategy()):
        self.__data_inicio = None
        self.__data_fim = None
        
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estrategia = estrategia
    
    @property
    def veiculo(self):
        return self.__veiculo
    
    @veiculo.setter
    def veiculo(self, obj: Veiculo):
        if(obj is not None):
            self.__veiculo = obj
        else:
            raise Exception("Objeto Veículo obrigatório!!!")
        
    @property
    def data_inicio(self):
        return self.__data_inicio
    
    @data_inicio.setter
    def data_inicio(self, data_inicio: date):
        if self.data_fim is not None and data_inicio > self.data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        elif data_inicio is None:
            raise DataInvalidaError("Data de início é obrigatória!")
        self.__data_inicio = data_inicio
    
    @property
    def data_fim(self):
        if self.__data_fim is not None:
            return self.__data_fim
        else:
            return None
    
    @data_fim.setter
    def data_fim(self, data_fim: date):
        if data_fim is not None and self.data_inicio > data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        self.__data_fim = data_fim
        
    def calcular_valor_locacao(self) -> float:
        if self.data_fim is None:
            self.data_fim = date.today()
        
        dias = (self.data_fim - self.data_inicio).days
        if dias <= 0:
            dias = 1
               
        valor_total = self.estrategia.calcular_diarias(self.veiculo, dias)
        return float(valor_total)

