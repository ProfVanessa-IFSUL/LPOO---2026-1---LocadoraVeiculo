"""
JanelaLocacaoUsuario — Tela do Usuário da Locadora.
Permite ações operacionais: Nova Reserva, Locar, Devolver, Cancelar, Ver Detalhes.
Cada ação valida o status corrente da locação selecionada.
Acessada via Menu Ação → Locar Veículo.
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from control.locacao_controller import LocacaoController


class JanelaLocacaoUsuario(tk.Toplevel):
    """Tela de operações de locação para o Usuário (com regras de negócio)."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locação de Veículos — Usuário")
        self.geometry("900x450")

        self.controller = LocacaoController()

        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        """Monta a interface: título, tabela de locações e botões de ação."""
        # --- Título ---
        tk.Label(self, text="Minhas Locações", font=("Helvetica", 16, "bold")).pack(pady=10)

        # --- Treeview ---
        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        colunas = ("ID", "Veículo", "Data Início", "Data Fim", "Status")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)

        self.tree.heading("ID", text="ID")
        self.tree.column("ID", anchor="center", width=50)
        self.tree.heading("Veículo", text="Veículo (Placa)")
        self.tree.column("Veículo", anchor="center", width=130)
        self.tree.heading("Data Início", text="Data Início")
        self.tree.column("Data Início", anchor="center", width=110)
        self.tree.heading("Data Fim", text="Data Fim")
        self.tree.column("Data Fim", anchor="center", width=110)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", anchor="center", width=110)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # --- Botões de Ação ---
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_botoes, text="Nova Reserva", width=12, command=self.abrir_nova_reserva).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Locar", width=10, command=self.acao_locar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Devolver", width=10, command=self.acao_devolver).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Cancelar", width=10, command=self.acao_cancelar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Ver Detalhes", width=12, command=self.ver_detalhes).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # AÇÕES
    # ------------------------------------------------------------------
    def abrir_nova_reserva(self):
        """Abre o formulário de nova reserva com validações de negócio."""
        from view.nova_reserva_view import JanelaNovaReserva
        janela = JanelaNovaReserva(self)
        # wait_window: aguarda o formulário fechar antes de recarregar
        self.wait_window(janela)
        self.carregar_dados()

    def _obter_id_selecionado(self, acao_nome: str):
        """Método auxiliar: retorna o ID da locação selecionada ou mostra aviso."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", f"Selecione uma locação para {acao_nome}.", parent=self)
            return None
        return int(self.tree.item(selecionado[0])['values'][0])

    def acao_locar(self):
        """Ação: muda status de 'reservado' → 'locado'."""
        id_loc = self._obter_id_selecionado("locar")
        if id_loc is None:
            return
        sucesso, msg = self.controller.locar(id_loc)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def acao_devolver(self):
        """Ação: muda status de 'locado' → 'devolvida' e exibe valor calculado."""
        id_loc = self._obter_id_selecionado("devolver")
        if id_loc is None:
            return
        sucesso, msg = self.controller.devolver(id_loc)
        if sucesso:
            # msg contém os detalhes da devolução (diárias, valor total)
            messagebox.showinfo("Devolução Realizada", msg, parent=self)
            self.carregar_dados()
        else:
            messagebox.showerror("Erro", msg, parent=self)

    def acao_cancelar(self):
        """Ação: muda status de 'reservado' → 'cancelada'."""
        id_loc = self._obter_id_selecionado("cancelar")
        if id_loc is None:
            return
        # Pede confirmação antes de cancelar
        resposta = messagebox.askyesno("Confirmar Cancelamento",
                                        f"Tem certeza que deseja cancelar a locação #{id_loc}?", parent=self)
        if resposta:
            sucesso, msg = self.controller.cancelar(id_loc)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)

    def ver_detalhes(self):
        """Exibe informações da locação conforme seu status (via Model.exibir_dados)."""
        id_loc = self._obter_id_selecionado("visualizar")
        if id_loc is None:
            return
        locacao = self.controller.buscar_por_id(id_loc)
        if locacao:
            messagebox.showinfo("Detalhes da Locação", locacao.exibir_dados(), parent=self)
        else:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)

    # ------------------------------------------------------------------
    # CARREGAR DADOS
    # ------------------------------------------------------------------
    def carregar_dados(self):
        """Limpa e recarrega todas as locações na tabela."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        locacoes = self.controller.listar_locacoes()
        if locacoes is None:
            messagebox.showerror("Erro", "Erro ao carregar locações.", parent=self)
            return

        for loc in locacoes:
            dt_inicio = loc.data_inicio.strftime("%d/%m/%Y") if loc.data_inicio else ""
            dt_fim = loc.data_fim.strftime("%d/%m/%Y") if loc.data_fim else "—"

            self.tree.insert("", "end", values=(
                loc.id,
                loc.veiculo.placa,
                dt_inicio,
                dt_fim,
                loc.status.capitalize()
            ))
