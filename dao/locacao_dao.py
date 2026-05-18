"""
LocacaoDAO — Data Access Object para a entidade Locação.
Estende GenericDAO, implementando os métodos abstratos de CRUD.
Fluxo MVC: View → Controller → DAO → Banco de Dados
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import date
from model.locacao import Locacao
from model.veiculo import VeiculoFactory
from model.LocacaoStrategy import CalculoPadraoStrategy, CalculoVIPStrategy
from dao.db_config import DatabaseConfig
from dao.generic_dao import GenericDAO


class LocacaoDAO(GenericDAO):
    def __init__(self):
        self.conexao = DatabaseConfig.get_connection()

    def _linha_para_locacao(self, linha):
        """Converte tupla do BD em objeto Locacao (ordem: id,placa,dt_ini,dt_fim,status,valor,estrat,tipo,cat,taxa)."""
        # linha[1] = vei_placa (vem do JOIN), linha[7]=vei_tipo, linha[8]=vei_categoria, linha[9]=vei_taxa_diaria
        veiculo = VeiculoFactory.criar_veiculo(linha[7], linha[1], linha[8], float(linha[9]))
        estrategia = CalculoVIPStrategy() if linha[6] == 'vip' else CalculoPadraoStrategy()
        return Locacao(veiculo=veiculo, data_inicio=linha[2], data_fim=linha[3],
                       estrategia=estrategia, status=linha[4], id=linha[0],
                       valor_total=float(linha[5]) if linha[5] else None)

    # ---------- CRUD: Salvar ----------
    def salvar(self, locacao: Locacao):
        if not self.conexao:
            raise Exception("Sem conexão com o BD")
        cursor = None
        try:
            cursor = self.conexao.cursor()
            # Subquery converte placa → vei_id na hora do INSERT
            query = """INSERT INTO tb_locacoes 
                (loc_veiculo_id, loc_data_inicio, loc_data_fim, loc_status, loc_valor_total, loc_estrategia) 
                VALUES ((SELECT vei_id FROM tb_veiculos WHERE vei_placa = %s), %s, %s, %s, %s, %s) RETURNING loc_id"""
            nome_estrat = 'vip' if isinstance(locacao.estrategia, CalculoVIPStrategy) else 'padrao'
            cursor.execute(query, (locacao.veiculo.placa, locacao.data_inicio, locacao.data_fim,
                                   locacao.status, locacao.valor_total, nome_estrat))
            locacao.id = cursor.fetchone()[0]
            self.conexao.commit()
            return True, f"Locação #{locacao.id} cadastrada com sucesso"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao inserir locação: {e}"
        finally:
            if cursor: cursor.close()

    # ---------- CRUD: Listar Todos ----------
    def listar_todos(self):
        if not self.conexao:
            return []
        cursor = None
        try:
            cursor = self.conexao.cursor()
            # JOIN via vei_id; SELECT traz vei_placa na posição [1] para manter compatibilidade
            query = """SELECT l.loc_id, v.vei_placa, l.loc_data_inicio, l.loc_data_fim,
                       l.loc_status, l.loc_valor_total, l.loc_estrategia,
                       v.vei_tipo, v.vei_categoria, v.vei_taxa_diaria
                FROM tb_locacoes l
                INNER JOIN tb_veiculos v ON l.loc_veiculo_id = v.vei_id
                ORDER BY l.loc_id DESC"""
            cursor.execute(query)
            return [self._linha_para_locacao(linha) for linha in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar locações: {e}")
            return []
        finally:
            if cursor: cursor.close()

    # ---------- CRUD: Remover ----------
    def remover(self, id_locacao: int):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("DELETE FROM tb_locacoes WHERE loc_id = %s", (id_locacao,))
            self.conexao.commit()
            return True, f"Locação #{id_locacao} removida com sucesso"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao remover locação: {e}"
        finally:
            if cursor: cursor.close()

    # ---------- CRUD: Atualizar ----------
    def atualizar(self, locacao: Locacao):
        if not self.conexao:
            return False, "Sem conexão com o BD"
        cursor = None
        try:
            cursor = self.conexao.cursor()
            nome_estrat = 'vip' if isinstance(locacao.estrategia, CalculoVIPStrategy) else 'padrao'
            # Subquery converte placa → vei_id na hora do UPDATE
            query = """UPDATE tb_locacoes SET loc_veiculo_id=(SELECT vei_id FROM tb_veiculos WHERE vei_placa=%s),
                    loc_data_inicio=%s, loc_data_fim=%s, loc_status=%s, loc_valor_total=%s, loc_estrategia=%s
                    WHERE loc_id=%s"""
            cursor.execute(query, (locacao.veiculo.placa, locacao.data_inicio, locacao.data_fim,
                                   locacao.status, locacao.valor_total, nome_estrat, locacao.id))
            self.conexao.commit()
            return True, f"Locação #{locacao.id} atualizada com sucesso"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao atualizar locação: {e}"
        finally:
            if cursor: cursor.close()

    # ---------- Buscar por ID ----------
    def buscar_por_id(self, id_locacao: int):
        if not self.conexao:
            return None
        cursor = None
        try:
            cursor = self.conexao.cursor()
            query = """SELECT l.loc_id, v.vei_placa, l.loc_data_inicio, l.loc_data_fim,
                       l.loc_status, l.loc_valor_total, l.loc_estrategia,
                       v.vei_tipo, v.vei_categoria, v.vei_taxa_diaria
                FROM tb_locacoes l
                INNER JOIN tb_veiculos v ON l.loc_veiculo_id = v.vei_id
                WHERE l.loc_id = %s"""
            cursor.execute(query, (id_locacao,))
            linha = cursor.fetchone()
            return self._linha_para_locacao(linha) if linha else None
        except Exception as e:
            print(f"Erro ao buscar locação #{id_locacao}: {e}")
            return None
        finally:
            if cursor: cursor.close()

    # ---------- Atualizar Status ----------
    def atualizar_status(self, id_locacao: int, novo_status: str, 
                         valor_total: float = None, data_fim: date = None):
        """Atualiza status, valor_total e data_fim de uma locação (usado por Locar/Devolver/Cancelar)."""
        if not self.conexao:
            return False, "Sem conexão com o BD"
        cursor = None
        try:
            cursor = self.conexao.cursor()
            cursor.execute("""UPDATE tb_locacoes SET loc_status=%s, loc_valor_total=%s, loc_data_fim=%s
                           WHERE loc_id=%s""", (novo_status, valor_total, data_fim, id_locacao))
            self.conexao.commit()
            return True, f"Status da locação #{id_locacao} atualizado para '{novo_status}'"
        except Exception as e:
            self.conexao.rollback()
            return False, f"Erro ao atualizar status: {e}"
        finally:
            if cursor: cursor.close()

    # ---------- Buscar Veículos Disponíveis (Parte 4) ----------
    def buscar_veiculos_disponiveis(self, data_inicio: date, data_fim: date, categoria: str = None):
        """Retorna veículos SEM locações ativas (reservado/locado) no período informado."""
        if not self.conexao:
            return []
        cursor = None
        try:
            cursor = self.conexao.cursor()
            # Subquery usa vei_id para verificar sobreposição de datas
            query = """SELECT vei_tipo, vei_placa, vei_categoria, vei_taxa_diaria
                FROM tb_veiculos
                WHERE vei_id NOT IN (
                    SELECT loc_veiculo_id FROM tb_locacoes
                    WHERE loc_status IN ('reservado', 'locado')
                      AND loc_data_inicio <= %s AND (loc_data_fim >= %s OR loc_data_fim IS NULL)
                )"""
            params = [data_inicio, data_fim]
            if categoria:
                query += " AND vei_categoria = %s"
                params.append(categoria)
            query += " ORDER BY vei_placa"
            cursor.execute(query, params)
            return [VeiculoFactory.criar_veiculo(l[0], l[1], l[2], float(l[3])) for l in cursor.fetchall()]
        except Exception as e:
            print(f"Erro ao buscar veículos disponíveis: {e}")
            return []
        finally:
            if cursor: cursor.close()
