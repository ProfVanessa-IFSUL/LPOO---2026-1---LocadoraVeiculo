from datetime import date, datetime
from .veiculo import Veiculo
from .ExcecoesPersonalizadas import DataInvalidaError
from .LocacaoStrategy import *


    
class Locacao:
    """
    Classe modelo que representa uma Locação de veículo.
    
    Ciclo de vida de uma locação (status):
        reservado -> locado -> devolvida
        reservado -> cancelada
        
        
    Utiliza o Padrão de Projeto STATE para gerenciar o ciclo de vida:
    
        ┌───────────┐  locar()  ┌─────────┐  devolver()  ┌───────────┐
        │ Reservado  │────────▶│  Locado  │────────────▶│ Devolvida │
        └─────┬─────┘          └─────────┘              └───────────┘
              │ cancelar()
              ▼
        ┌───────────┐
        │ Cancelada │
        └───────────┘
    
    Comparação — ANTES (strings + if/elif) vs DEPOIS (State Pattern):
    
        ANTES:                                    DEPOIS:
        ─────                                     ──────
        if self.status == "reservado":            self.estado_atual.locar()
            ...                                   # O estado sabe o que fazer!
        elif self.status == "locado":
            return False, "Erro..."
        elif self.status == "devolvida":
            return False, "Erro..."
    
    Atributos:
        id: identificador único no BD (None para locações novas)
        veiculo: objeto Veiculo associado à locação
        data_inicio: data de início da locação (obrigatória)
        data_fim: data de fim prevista ou data de devolução efetiva
        estrategia: estratégia de cálculo de valor (Strategy Pattern)
        estado_atual : estado atual da locação ('reservado', 'locado', 'devolvida', 'cancelada')
        estado_atual : objeto State que controla o ciclo de vida (State Pattern)
        valor_total: valor final calculado na devolução (None até devolver)
    """
    def __init__(self, veiculo: Veiculo, data_inicio: date=datetime.now().date(), data_fim: date=None, estrategia:CalculoLocacaoStrategy = CalculoPadraoStrategy(),status: str = "reservado", id: int = None,
                 valor_total: float = None):
        self.__data_inicio = None
        self.__data_fim = None
        
        # Atributo id: mapeia o loc_id do banco de dados
        # É None quando a locação ainda não foi salva no BD
        self.id = id
        
        
        
        self.veiculo = veiculo
        self.data_inicio = data_inicio
        self.data_fim = data_fim
        self.estrategia = estrategia
        
        # STATE PATTERN: Cria o objeto de estado baseado na string recebida.
        # A função criar_estado_por_nome() converte "reservado" → ReservadoState, etc.
        # Isso é necessário porque o BD armazena strings, não objetos.
        # Import local (lazy) para evitar importação circular com estados_locacao.py
        from .estados_locacao import criar_estado_por_nome
        self.estado_atual = criar_estado_por_nome(status, self)
        
        # Valor total: preenchido somente após a devolução
        self.valor_total = valor_total
    
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
    
    
    @property
    def estado_atual(self):
        """Retorna o objeto State atual da locação."""
        return self._estado_atual

    @estado_atual.setter
    def estado_atual(self, novo_estado):
        """
        Atualiza o estado da locação.
        Chamado tanto pelo construtor quanto pelas transições internas dos estados.
        """
        self._estado_atual = novo_estado
    
    @property
    def status(self) -> str:
        """
        PROPERTY CALCULADA: status (para compatibilidade com Views e DAO)
        Retorna o nome do estado como string (ex: 'reservado', 'locado').
        Usado pelo DAO para persistir no BD e pelas Views para exibição.
        Delega para o método get_nome() do estado atual.
        """
        if self._estado_atual:
            return self._estado_atual.get_nome()
        return "reservado"


    # AÇÕES DELEGADAS AO ESTADO (State Pattern)
    def locar(self) -> tuple:
        """
        Retirar o veículo. Delega a decisão ao estado atual.
        Se o estado for ReservadoState → transição para LocadoState.
        Se o estado for outro → retorna erro com mensagem específica.
        """
        return self.estado_atual.locar()

    def devolver(self) -> tuple:
        """
        Devolver o veículo. Delega a decisão ao estado atual.
        Se o estado for LocadoState → calcula valor e transição para DevolvidaState.
        Se o estado for outro → retorna erro com mensagem específica.
        """
        return self.estado_atual.devolver()

    def cancelar(self) -> tuple:
        """
        Cancelar a locação. Delega a decisão ao estado atual.
        Se o estado for ReservadoState → transição para CanceladaState.
        Se o estado for outro → retorna erro com mensagem específica.
        """
        return self.estado_atual.cancelar()
    
    def exibir_dados(self) -> str:
        """
        Retorna uma string formatada com as informações da locação.
        
        DELEGA ao estado atual: cada estado sabe quais informações exibir.
        Isso elimina o if/elif que existia antes — agora cada State
        tem seu próprio método exibir_dados() com a lógica específica.
        """
        # Cabeçalho comum a todos os estados
        info = f"Locação #{self.id}\n"
        info += f"Veículo: {self.veiculo.placa} ({self.veiculo.__class__.__name__})\n"
        info += f"Status: {self.status.upper()}\n"
        info += "─" * 30 + "\n"
        
        # Corpo: DELEGADO ao estado atual (State Pattern)
        info += self.estado_atual.exibir_dados()
        
        return info