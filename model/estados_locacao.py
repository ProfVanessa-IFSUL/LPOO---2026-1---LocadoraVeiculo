"""
Padrão de Projeto State aplicado ao ciclo de vida da Locação.

Diagrama de transições:

    ┌──────────────┐    locar()    ┌─────────────-┐    devolver() ┌──────────────┐
    │  Reservado   │──────────────>│   Locado     │──────────────>│  Devolvida   │
    │  State       │               │   State      │               │  State       │
    └──────┬───────┘               └─────────────-┘               └──────────────┘
           │                                                       (estado final)
           │ cancelar()
           ▼
    ┌──────────────┐
    │  Cancelada   │
    │  State       │
    └──────────────┘
     (estado final)

Comparação com a abordagem anterior (strings + if/elif):

    ANTES (sem State):                         DEPOIS (com State):
    ──────────────────────                     ──────────────────────
    def locar(self, id):                       def locar(self, id):
        loc = dao.buscar(id)                       loc = dao.buscar(id)
        if loc.status != "reservado":              loc.estado_atual.locar()
            return False, "Erro..."                # A regra está DENTRO do estado!
        ...

    Cada nova ação exige adicionar mais        Cada novo estado é uma classe isolada.
    if/elif em TODOS os métodos.               Adicionar estados não altera código existente.

Analogia com estados_veiculo.py:
    - VeiculoState -> LocacaoState
    - DisponivelState -> ReservadoState
    - AlugadoState -> LocadoState
    - A diferença é que aqui temos estados TERMINAIS (Devolvida/Cancelada)
"""
from abc import ABC, abstractmethod
from datetime import date

class LocacaoState(ABC):
    """
    Classe abstrata base para os estados de uma Locação.
    
    Cada estado concreto implementa as 3 ações possíveis (locar, devolver, cancelar)
    e define o que acontece quando o usuário tenta executar cada ação.
    
    O atributo 'locacao' é uma referência ao objeto Locacao que possui este estado,
    permitindo que o próprio estado faça a transição (self.locacao.estado_atual = NovoState).
    """
    def __init__(self, locacao):
        """
        Recebe a referência para o objeto Locacao 'dono' deste estado.
        Isso permite que o estado mude o "ponteiro" estado_atual da locação.
        """
        self.locacao = locacao

    @property
    def locacao(self):
        return self.__locacao

    @locacao.setter
    def locacao(self, valor):
        self.__locacao = valor

    @abstractmethod
    def locar(self) -> tuple:
        """Ação: tentar retirar o veículo (reservado -> locado)."""
        pass

    @abstractmethod
    def devolver(self) -> tuple:
        """Ação: devolver o veículo (locado -> devolvida)."""
        pass

    @abstractmethod
    def cancelar(self) -> tuple:
        """Ação: cancelar a locação (reservado -> cancelada)."""
        pass

    @abstractmethod
    def exibir_dados(self) -> str:
        """Retorna string formatada com informações específicas deste estado."""
        pass

    @abstractmethod
    def get_nome(self) -> str:
        """Retorna o nome do estado para persistência no banco de dados."""
        pass
    


class ReservadoState(LocacaoState):
    """
    ESTADO: RESERVADO
    Estado inicial de uma locação.
    O cliente fez a reserva, mas ainda não retirou o veículo.
    Transições permitidas: locar() -> LocadoState, cancelar() -> CanceladaState
    """

    def locar(self) -> tuple:
        """
        Transição: Reservado -> Locado.
        O cliente está retirando o veículo = ação: muda o estado.
        """
        # O próprio estado faz a transição (mesmo padrão de estados_veiculo.py)
        self.locacao.estado_atual = LocadoState(self.locacao)
        return True, f"Veículo {self.locacao.veiculo.placa} retirado com sucesso! Status: LOCADO"

    def devolver(self) -> tuple:
        """Bloqueio: não se pode devolver um veículo que ainda não foi retirado."""
        return False, "Operação inválida: o veículo ainda não foi retirado (status: RESERVADO)"

    def cancelar(self) -> tuple:
        """
        Transição: Reservado -> Cancelada.
        Cancelamento só é permitido antes da retirada do veículo.
        """
        self.locacao.estado_atual = CanceladaState(self.locacao)
        return True, f"Locação cancelada com sucesso"

    def exibir_dados(self) -> str:
        """Exibe: data início, data fim prevista, valor estimado."""
        loc = self.locacao
        info = f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
        if loc.data_fim:
            info += f"Data de Fim Prevista: {loc.data_fim.strftime('%d/%m/%Y')}\n"
            # Calcula valor estimado usando Strategy (sem alterar o objeto)
            dias = (loc.data_fim - loc.data_inicio).days
            if dias <= 0:
                dias = 1
            valor_estimado = loc.estrategia.calcular_diarias(loc.veiculo, dias)
            info += f"Valor Estimado: R$ {valor_estimado:.2f}"
        else:
            info += "Data de Fim: Não definida"
        return info

    def get_nome(self) -> str:
        return "reservado"
    

class LocadoState(LocacaoState):
    """
    ESTADO: LOCADO
    O veículo foi efetivamente retirado pelo cliente.
    Única ação possível: devolver.
    Transições permitidas: devolver() -> DevolvidaState
    """

    def locar(self) -> tuple:
        """Bloqueio: o veículo já está com o cliente."""
        return False, "Operação inválida: o veículo já está locado (em uso pelo cliente)"

    def devolver(self) -> tuple:
        """
        Transição: Locado -> Devolvida.
        Calcula o valor final usando a Strategy e registra a data de devolução.
        """
        loc = self.locacao
        # Define data de devolução como hoje
        data_devolucao = date.today()
        loc.data_fim = data_devolucao

        # Calcula valor total usando a Strategy configurada
        valor_total = loc.calcular_valor_locacao()
        loc.valor_total = valor_total

        # Transição de estado
        loc.estado_atual = DevolvidaState(loc)

        # Monta mensagem de devolução com detalhes
        dias = (data_devolucao - loc.data_inicio).days
        if dias <= 0:
            dias = 1
        msg = (f"Devolução registrada!\n\n"
               f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
               f"Data de Devolução: {data_devolucao.strftime('%d/%m/%Y')}\n"
               f"Número de Diárias: {dias}\n"
               f"Valor Total: R$ {valor_total:.2f}")
        return True, msg

    def cancelar(self) -> tuple:
        """Bloqueio: não se pode cancelar uma locação que já está em andamento."""
        return False, "Operação inválida: o veículo já foi retirado. Para encerrar, utilize 'Devolver'"

    def exibir_dados(self) -> str:
        """Exibe: data início, data fim prevista, valor estimado."""
        loc = self.locacao
        info = f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
        if loc.data_fim:
            info += f"Data de Fim Prevista: {loc.data_fim.strftime('%d/%m/%Y')}\n"
            dias = (loc.data_fim - loc.data_inicio).days
            if dias <= 0:
                dias = 1
            valor_estimado = loc.estrategia.calcular_diarias(loc.veiculo, dias)
            info += f"Valor Estimado: R$ {valor_estimado:.2f}"
        else:
            info += "Data de Fim: Não definida"
        return info

    def get_nome(self) -> str:
        return "locado"


# ======================================================================
# ESTADO: DEVOLVIDA (estado terminal — nenhuma transição permitida)
# O veículo foi devolvido, o valor foi calculado. Locação encerrada.
# ======================================================================
class DevolvidaState(LocacaoState):
    """
    Estado terminal: locação encerrada com sucesso.
    Nenhuma ação é permitida — apenas visualização.
    """

    def locar(self) -> tuple:
        return False, "Operação inválida: esta locação já foi encerrada (veículo devolvido)"

    def devolver(self) -> tuple:
        return False, "Operação inválida: o veículo já foi devolvido"

    def cancelar(self) -> tuple:
        return False, "Operação inválida: não é possível cancelar uma locação já finalizada"

    def exibir_dados(self) -> str:
        """Exibe: data início, data devolução, nº diárias, valor total."""
        loc = self.locacao
        dias = (loc.data_fim - loc.data_inicio).days if loc.data_fim else 0
        if dias <= 0:
            dias = 1
        info = f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
        info += f"Data de Devolução: {loc.data_fim.strftime('%d/%m/%Y')}\n"
        info += f"Número de Diárias: {dias}\n"
        if loc.valor_total:
            info += f"Valor Total: R$ {loc.valor_total:.2f}"
        return info

    def get_nome(self) -> str:
        return "devolvida"


class CanceladaState(LocacaoState):
    """
    ESTADO: CANCELADA
    Estado terminal: locação cancelada.
    A reserva foi cancelada antes da retirada do veículo.
    Nenhuma ação é permitida — apenas visualização.
    """

    def locar(self) -> tuple:
        return False, "Operação inválida: esta locação foi cancelada"

    def devolver(self) -> tuple:
        return False, "Operação inválida: esta locação foi cancelada"

    def cancelar(self) -> tuple:
        return False, "Operação inválida: a locação já está cancelada"

    def exibir_dados(self) -> str:
        """Exibe: informações básicas + indicação de cancelamento."""
        loc = self.locacao
        info = f"Data de Início: {loc.data_inicio.strftime('%d/%m/%Y')}\n"
        if loc.data_fim:
            info += f"Data de Fim: {loc.data_fim.strftime('%d/%m/%Y')}\n"
        info += " Esta locação foi CANCELADA — valor não aplicável."
        return info

    def get_nome(self) -> str:
        return "cancelada"


# ======================================================================
# FUNÇÃO UTILITÁRIA: Converter nome (string do BD) -> objeto State
# ======================================================================
def criar_estado_por_nome(nome_status: str, locacao):
    """
    Factory simples que converte a string armazenada no BD 
    no objeto State correspondente.
    
    Usado pelo DAO ao reconstruir objetos Locacao a partir do banco.
    
    Parâmetros:
        nome_status: string do BD ('reservado', 'locado', 'devolvida', 'cancelada')
        locacao: referência ao objeto Locacao que possuirá este estado
    """
    mapa = {
        'reservado': ReservadoState,
        'locado':    LocadoState,
        'devolvida': DevolvidaState,
        'cancelada': CanceladaState,
    }
    classe_estado = mapa.get(nome_status, ReservadoState)
    return classe_estado(locacao)
