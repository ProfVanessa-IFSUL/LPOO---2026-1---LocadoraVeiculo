"""
LocacaoController — Camada de controle para operações de Locação.

Agora utiliza o Padrão State: em vez de verificar strings de status com if/elif,
delega as decisões de transição ao próprio objeto Locacao (que delega ao seu estado).

Comparação:
    ANTES (sem State \ usando Enum):                       DEPOIS (com State):
    ──────────────────                       ──────────────────
    if locacao.status != "reservado":        sucesso, msg = locacao.tentar_locar()
        return False, "Erro..."              # O estado sabe se pode ou não!
    dao.atualizar_status(id, "locado")       if sucesso: dao.atualizar(locacao)
"""
from datetime import datetime, date
from dao.locacao_dao import LocacaoDAO
from dao.veiculo_dao import VeiculoDAO
from model.locacao import Locacao
from model.LocacaoStrategy import CalculoPadraoStrategy, CalculoVIPStrategy


class LocacaoController:
    def __init__(self):
        self.locacao_dao = LocacaoDAO()
        self.veiculo_dao = VeiculoDAO()

    # =====================================================================
    # AÇÕES DO USUÁRIO — Agora delegam ao State Pattern
    # =====================================================================

    def criar_reserva(self, placa: str, data_inicio_str: str, data_fim_str: str, estrategia_str: str = "padrao"):
        """
        Cria uma nova reserva (estado inicial: ReservadoState).
        Validações de negócio: datas futuras, veículo existente.
        """
        if not placa or not data_inicio_str or not data_fim_str:
            return False, "Preencha todos os campos obrigatórios"
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()

            if data_inicio < date.today():
                return False, "Data de início não pode ser no passado"
            if data_fim < data_inicio:
                return False, "Data de fim deve ser igual ou posterior à data de início"

            veiculo = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado"

            estrategia = CalculoVIPStrategy() if estrategia_str.lower() == 'vip' else CalculoPadraoStrategy()

            # Cria locação — o construtor automaticamente define ReservadoState
            locacao = Locacao(veiculo=veiculo, data_inicio=data_inicio,
                              data_fim=data_fim, estrategia=estrategia,
                              status="reservado")

            return self.locacao_dao.salvar(locacao)

        except ValueError:
            return False, "Formato de data inválido. Use dd/mm/aaaa"
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def locar(self, id_locacao: int):
        """
        Tenta mudar o estado para Locado.
        
        STATE PATTERN: A validação está DENTRO do estado!
        - Se estado atual for ReservadoState → transição acontece → retorna sucesso
        - Se for qualquer outro → retorna erro com mensagem específica do estado
        
        O Controller não precisa saber qual é o estado atual — apenas delega.
        """
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada"

        # DELEGA ao estado: locacao.tentar_locar() chama estado_atual.locar()
        sucesso, msg = locacao.locar()

        if sucesso:
            # Persiste a mudança de estado no BD
            self.locacao_dao.atualizar_status(id_locacao, locacao.status,
                                              valor_total=locacao.valor_total,
                                              data_fim=locacao.data_fim)
        return sucesso, msg

    def devolver(self, id_locacao: int):
        """
        Tenta devolver o veículo.
        
        STATE PATTERN: O LocadoState.devolver() faz TUDO internamente:
        - Calcula o valor usando Strategy
        - Define data de devolução
        - Faz a transição para DevolvidaState
        - Retorna mensagem formatada com detalhes
        """
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada"

        # DELEGA ao estado: se for LocadoState, calcula valor e transiciona
        sucesso, msg = locacao.devolver()

        if sucesso:
            # Persiste estado, valor_total e data_fim no BD
            self.locacao_dao.atualizar_status(id_locacao, locacao.status,
                                              valor_total=locacao.valor_total,
                                              data_fim=locacao.data_fim)
        return sucesso, msg

    def cancelar(self, id_locacao: int):
        """
        Tenta cancelar a locação.
        
        STATE PATTERN: ReservadoState.cancelar() → transição para CanceladaState
        Qualquer outro estado → retorna mensagem de erro específica.
        """
        locacao = self.locacao_dao.buscar_por_id(id_locacao)
        if not locacao:
            return False, "Locação não encontrada"

        # DELEGA ao estado
        sucesso, msg = locacao.cancelar()

        if sucesso:
            self.locacao_dao.atualizar_status(id_locacao, locacao.status,
                                              valor_total=None,
                                              data_fim=locacao.data_fim)
        return sucesso, msg

    # =====================================================================
    # AÇÕES DO ADMINISTRADOR (sem restrições rígidas)
    # =====================================================================

    def salvar_locacao_admin(self, placa, data_inicio_str, data_fim_str, status, estrategia_str="padrao", valor_total_str=None):
        """Cria locação sem restrições do Usuário (admin pode usar datas passadas, qualquer status)."""
        if not placa or not data_inicio_str:
            return False, "Placa e data de início são obrigatórios"
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date() if data_fim_str else None
            if data_fim and data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim"

            veiculo = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado"

            estrategia = CalculoVIPStrategy() if estrategia_str.lower() == 'vip' else CalculoPadraoStrategy()
            valor_total = float(valor_total_str.replace(',', '.')) if valor_total_str else None

            # Admin pode definir qualquer status — o construtor cria o State correspondente
            locacao = Locacao(veiculo=veiculo, data_inicio=data_inicio, data_fim=data_fim,
                              estrategia=estrategia, status=status, valor_total=valor_total)

            # Se status é 'devolvida' e o admin não informou valor, calcula automaticamente
            if status == 'devolvida' and valor_total is None and data_fim:
                locacao.valor_total = locacao.calcular_valor_locacao()

            return self.locacao_dao.salvar(locacao)

        except ValueError:
            return False, "Formato de data inválido. Use dd/mm/aaaa"
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def atualizar_locacao_admin(self, id_locacao, placa, data_inicio_str, data_fim_str, status, estrategia_str="padrao", valor_total_str=None):
        """Atualiza locação existente (Admin, sem restrições rígidas)."""
        if not placa or not data_inicio_str:
            return False, "Placa e data de início são obrigatórios"
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date() if data_fim_str else None
            if data_fim and data_inicio > data_fim:
                return False, "Data de início deve ser anterior ou igual à data de fim"

            veiculo = self.veiculo_dao.buscar_por_placa(placa)
            if not veiculo:
                return False, f"Veículo com placa {placa} não encontrado"

            estrategia = CalculoVIPStrategy() if estrategia_str.lower() == 'vip' else CalculoPadraoStrategy()
            valor_total = float(valor_total_str.replace(',', '.')) if valor_total_str else None

            locacao = Locacao(veiculo=veiculo, data_inicio=data_inicio, data_fim=data_fim,
                              estrategia=estrategia, status=status, id=id_locacao, valor_total=valor_total)

            # Se status é 'devolvida' e o admin não informou valor, calcula automaticamente
            if status == 'devolvida' and valor_total is None and data_fim:
                locacao.valor_total = locacao.calcular_valor_locacao()

            return self.locacao_dao.atualizar(locacao)

        except ValueError:
            return False, "Formato de data inválido. Use dd/mm/aaaa"
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    # =====================================================================
    # OPERAÇÕES COMPARTILHADAS
    # =====================================================================

    def listar_locacoes(self):
        try:
            return self.locacao_dao.listar_todos()
        except Exception as e:
            print(f"Erro ao listar locações: {e}")
            return None

    def buscar_por_id(self, id_locacao: int):
        try:
            return self.locacao_dao.buscar_por_id(id_locacao)
        except Exception as e:
            print(f"Erro ao buscar locação: {e}")
            return None

    def remover_locacao(self, id_locacao: int):
        try:
            return self.locacao_dao.remover(id_locacao)
        except Exception as e:
            return False, f"Erro inesperado: {e}"

    def listar_veiculos_disponiveis(self, data_inicio_str: str, data_fim_str: str, categoria: str = None):
        """Busca veículos disponíveis no período, usada pelo formulário de nova reserva."""
        try:
            data_inicio = datetime.strptime(data_inicio_str, "%d/%m/%Y").date()
            data_fim = datetime.strptime(data_fim_str, "%d/%m/%Y").date()
            cat = categoria if categoria and categoria != "Todas" else None
            return self.locacao_dao.buscar_veiculos_disponiveis(data_inicio, data_fim, cat)
        except ValueError:
            return []
        except Exception as e:
            print(f"Erro ao buscar veículos disponíveis: {e}")
            return []

# ---------- Filtrar por Placa ----------
    def listar_locacoes_por_placa(self, placa: str):
            """Retorna locações filtradas por placa do veículo (busca parcial, case-insensitive)."""
            try:
                return self.locacao_dao.listar_por_placa(placa)
            except Exception as e:
                print(f"Erro ao filtrar locações por placa: {e}")
                return []