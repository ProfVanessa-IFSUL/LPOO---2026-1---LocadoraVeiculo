from datetime import date, datetime
from .veiculo import Veiculo


class Locacao:
    def __init__(self, veiculo: Veiculo, data_inicio: date, data_fim: date):
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
    
    
    @property
    def veiculo(self):
        return self.__veiculo
    
    @veiculo.setter
    def veiculo(self, obj):
        if(obj is not None):
            self.__veiculo = obj
        else:
            raise Exception("Objeto Veículo obrigatório!!!")
        
    def calcular_valor_locacao(self) -> float:
        pass

