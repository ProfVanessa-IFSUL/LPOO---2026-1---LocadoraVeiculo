from model.locacao import *
from model.veiculo import *

carro = Carro(placa="ABC1#34", taxa_diaria=100)
locacao = Locacao(veiculo = carro, data_fim=None, data_inicio=None)