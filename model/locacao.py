from datetime import date, datetime
from .veiculo import Veiculo
from .ExcecoesPersonalizadas import DataInvalidaError

class Locacao:
    def __init__(self, veiculo: Veiculo, data_inicio: date = datetime.now().date(), data_fim: date = None):
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
        if self.data_inicio > self.data_fim:
            raise DataInvalidaError("Data de início não pode ser posterior à data de fim.")
        
        dias = (self.data_fim - self.data_inicio).days
        if dias <= 0:
            dias = 1
            
        if self.veiculo.taxa_diaria <= 0:
            raise ValueError("A taxa diária do veículo deve ser maior que zero.")
            
        if getattr(self.veiculo, 'valor_seguro', -1) < 0:
            raise ValueError("O valor do seguro do veículo deve ser válido (maior ou igual a zero).")
            
        valor_total = (dias * self.veiculo.taxa_diaria) + self.veiculo.valor_seguro
        return float(valor_total)

