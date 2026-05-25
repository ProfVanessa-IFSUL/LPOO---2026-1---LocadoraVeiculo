"""
JanelaListagemLocacoes — Tela do Administrador (CRUD Completo de Locações).
Permite: Novo, Editar, Remover, Ver Detalhes sem restrições de negócio.
Acessada via Menu Cadastro → Locações (Admin).
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import ttk, messagebox
from control.locacao_controller import LocacaoController


class JanelaListagemLocacoes(tk.Toplevel):
    """Tela de listagem e CRUD completo de locações (visão Administrador)."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Locações — Administrador")
        self.geometry("900x450")

        # Controller: intermedia View ↔ DAO
        self.controller = LocacaoController()

        self.criar_widgets()
        self.carregar_dados()

    def criar_widgets(self):
        """Monta os widgets da tela: título, tabela (Treeview) e botões de ação."""
        # --- Título ---
        lbl_titulo = tk.Label(self, text="Gerenciamento de Locações (Admin)", font=("Helvetica", 16, "bold"))
        lbl_titulo.pack(pady=10)
        
        # --- Frame de Filtro por Placa ---
        frame_filtro = tk.Frame(self)
        frame_filtro.pack(fill="x", padx=20, pady=(0, 5))

        tk.Label(frame_filtro, text="Filtrar por Placa:").pack(side="left", padx=(0, 5))
        self.var_filtro_placa = tk.StringVar()
        self.var_filtro_placa.trace_add("write", lambda *args: self.filtrar_por_placa())
        self.entry_filtro_placa = tk.Entry(frame_filtro, width=20, textvariable=self.var_filtro_placa)
        self.entry_filtro_placa.pack(side="left", padx=(0, 5))

        tk.Button(frame_filtro, text="Filtrar", width=8, command=self.filtrar_por_placa).pack(side="left", padx=2)
        tk.Button(frame_filtro, text="Limpar", width=8, command=self.limpar_filtro).pack(side="left", padx=2)

        '''
        Usuário digita "AB" -> Entry atualiza StringVar -> var_filtro_placa = "AB" -> trace_add detecta a escrita
        -> lambda chama filtrar_por_placa() -> Tabela é atualizada com os resultados

        '''
        
        

        # --- Frame da Treeview com Scrollbar ---
        frame_tree = tk.Frame(self)
        frame_tree.pack(expand=True, fill="both", padx=20, pady=10)

        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side="right", fill="y")

        # Colunas da tabela de locações
        colunas = ("ID", "Veículo", "Data Início", "Data Fim", "Status", "Valor Total")
        self.tree = ttk.Treeview(frame_tree, columns=colunas, show="headings", yscrollcommand=scrollbar.set)

        # Configura cabeçalhos e larguras
        self.tree.heading("ID", text="ID")
        self.tree.column("ID", anchor="center", width=50)
        self.tree.heading("Veículo", text="Veículo (Placa)")
        self.tree.column("Veículo", anchor="center", width=120)
        self.tree.heading("Data Início", text="Data Início")
        self.tree.column("Data Início", anchor="center", width=100)
        self.tree.heading("Data Fim", text="Data Fim")
        self.tree.column("Data Fim", anchor="center", width=100)
        self.tree.heading("Status", text="Status")
        self.tree.column("Status", anchor="center", width=100)
        self.tree.heading("Valor Total", text="Valor Total")
        self.tree.column("Valor Total", anchor="center", width=120)

        self.tree.pack(expand=True, fill="both")
        scrollbar.config(command=self.tree.yview)

        # --- Frame de Botões ---
        frame_botoes = tk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=5)

        tk.Button(frame_botoes, text="Novo", width=10, command=self.abrir_novo).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Editar", width=10, command=self.abrir_editar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Ver Detalhes", width=12, command=self.ver_detalhes).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Remover", width=10, command=self.remover_locacao).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Fechar", width=10, command=self.destroy).pack(side="right", padx=5)

    # ------------------------------------------------------------------
    # AÇÕES DOS BOTÕES
    # ------------------------------------------------------------------
    def abrir_novo(self):
        """Abre o formulário de cadastro de locação em modo criação."""
        from view.locacao_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self)
        # wait_window: trava a listagem até o formulário fechar
        self.wait_window(janela)
        self.carregar_dados()

    def abrir_editar(self):
        """Abre o formulário em modo edição com os dados da locação selecionada."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para editar.", parent=self)
            return

        id_locacao = int(self.tree.item(selecionado[0])['values'][0])
        locacao = self.controller.buscar_por_id(id_locacao)
        if not locacao:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)
            return

        from view.locacao_view import JanelaCadastroLocacao
        janela = JanelaCadastroLocacao(self, locacao_existente=locacao)
        self.wait_window(janela)
        self.carregar_dados()

    def ver_detalhes(self):
        """Exibe as informações detalhadas da locação selecionada."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para visualizar.", parent=self)
            return

        id_locacao = int(self.tree.item(selecionado[0])['values'][0])
        locacao = self.controller.buscar_por_id(id_locacao)
        if locacao:
            # Usa o método exibir_dados() do Model que varia conforme o status
            messagebox.showinfo("Detalhes da Locação", locacao.exibir_dados(), parent=self)
        else:
            messagebox.showerror("Erro", "Locação não encontrada.", parent=self)

    def remover_locacao(self):
        """Remove a locação selecionada após confirmação."""
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione uma locação para remover.", parent=self)
            return

        id_locacao = int(self.tree.item(selecionado[0])['values'][0])
        resposta = messagebox.askyesno("Confirmar Exclusão",
                                        f"Tem certeza que deseja remover a locação #{id_locacao}?", parent=self)
        if resposta:
            sucesso, msg = self.controller.remover_locacao(id_locacao)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=self)
                self.carregar_dados()
            else:
                messagebox.showerror("Erro", msg, parent=self)

    # ------------------------------------------------------------------
    # CARREGAR DADOS NA TREEVIEW
    # ------------------------------------------------------------------
    def carregar_dados(self, locacoes=None):
        """Limpa e recarrega locações na tabela.
        
        Args:
            locacoes: lista opcional de objetos Locacao. Se None, busca todas do BD.
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        if locacoes is None:
            locacoes = self.controller.listar_locacoes()

        if locacoes is None:
            messagebox.showerror("Erro", "Erro ao carregar locações.", parent=self)
            return

        for loc in locacoes:
            # Formata datas e valor para exibição
            dt_inicio = loc.data_inicio.strftime("%d/%m/%Y") if loc.data_inicio else ""
            dt_fim = loc.data_fim.strftime("%d/%m/%Y") if loc.data_fim else "—"
            valor = f"R$ {loc.valor_total:.2f}".replace('.', ',') if loc.valor_total else "—"

            self.tree.insert("", "end", values=(
                loc.id,
                loc.veiculo.placa,
                dt_inicio,
                dt_fim,
                loc.status.capitalize(),
                valor
            ))

    # ------------------------------------------------------------------
    # FILTRO POR PLACA
    # ------------------------------------------------------------------
    def filtrar_por_placa(self):
        """Filtra a tabela pelas locações do veículo cuja placa contém o texto digitado."""
        placa = self.entry_filtro_placa.get().strip()
        if not placa:
            # Campo vazio: carrega tudo
            self.carregar_dados()
            return
        locacoes = self.controller.listar_locacoes_por_placa(placa)
        self.carregar_dados(locacoes)

    def limpar_filtro(self):
        """Limpa o campo de filtro e restaura a listagem completa."""
        self.entry_filtro_placa.delete(0, tk.END)
        self.carregar_dados()
