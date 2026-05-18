"""
JanelaCadastroLocacao — Formulário para criar/editar locação (visão Admin).
Permite configurar qualquer campo sem restrições rígidas de negócio.
Acessada a partir de JanelaListagemLocacoes (botões Novo/Editar).
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from control.locacao_controller import LocacaoController


class JanelaCadastroLocacao(tk.Toplevel):
    """Formulário de cadastro/edição de locação para Administrador."""

    def __init__(self, master=None, locacao_existente=None):
        super().__init__(master)
        self.locacao_existente = locacao_existente
        self.title("Editar Locação" if locacao_existente else "Nova Locação (Admin)")
        self.geometry("450x400")
        self.controller = LocacaoController()

        # --- Título ---
        texto = "Editar Locação" if locacao_existente else "Nova Locação (Admin)"
        tk.Label(self, text=texto, font=("Helvetica", 16, "bold")).pack(pady=10)

        # --- Campo: Placa do Veículo ---
        frame_placa = tk.Frame(self)
        frame_placa.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_placa, text="Placa Veículo:").pack(side="left")
        self.txt_placa = tk.Entry(frame_placa)
        self.txt_placa.pack(side="right", expand=True, fill="x")

        # --- Campo: Data Início (formato dd/mm/aaaa) ---
        frame_di = tk.Frame(self)
        frame_di.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_di, text="Data Início (dd/mm/aaaa):").pack(side="left")
        self.txt_data_inicio = tk.Entry(frame_di)
        self.txt_data_inicio.pack(side="right", expand=True, fill="x")

        # --- Campo: Data Fim ---
        frame_df = tk.Frame(self)
        frame_df.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_df, text="Data Fim (dd/mm/aaaa):").pack(side="left")
        self.txt_data_fim = tk.Entry(frame_df)
        self.txt_data_fim.pack(side="right", expand=True, fill="x")

        # --- Campo: Status (ComboBox) ---
        frame_status = tk.Frame(self)
        frame_status.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_status, text="Status:").pack(side="left")
        self.cb_status = ttk.Combobox(frame_status, values=["reservado", "locado", "devolvida", "cancelada"])
        self.cb_status.current(0)
        self.cb_status.pack(side="right", expand=True, fill="x")

        # --- Campo: Estratégia ---
        frame_estrat = tk.Frame(self)
        frame_estrat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_estrat, text="Estratégia:").pack(side="left")
        self.cb_estrategia = ttk.Combobox(frame_estrat, values=["padrao", "vip"])
        self.cb_estrategia.current(0)
        self.cb_estrategia.pack(side="right", expand=True, fill="x")

        # --- Campo: Valor Total (opcional, preenchido manualmente pelo admin) ---
        frame_valor = tk.Frame(self)
        frame_valor.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_valor, text="Valor Total (R$):").pack(side="left")
        self.txt_valor = tk.Entry(frame_valor)
        self.txt_valor.pack(side="right", expand=True, fill="x")

        # --- Botão Salvar/Atualizar ---
        texto_btn = "Atualizar" if locacao_existente else "Salvar"
        tk.Button(self, text=texto_btn, command=self.solicitar_cadastro).pack(pady=15)

        # --- Preencher campos se for edição ---
        if self.locacao_existente:
            loc = self.locacao_existente
            self.txt_placa.insert(0, loc.veiculo.placa)
            self.txt_data_inicio.insert(0, loc.data_inicio.strftime("%d/%m/%Y"))
            if loc.data_fim:
                self.txt_data_fim.insert(0, loc.data_fim.strftime("%d/%m/%Y"))
            self.cb_status.set(loc.status)
            # Determina nome da estratégia
            from model.LocacaoStrategy import CalculoVIPStrategy
            self.cb_estrategia.set('vip' if isinstance(loc.estrategia, CalculoVIPStrategy) else 'padrao')
            if loc.valor_total:
                self.txt_valor.insert(0, str(loc.valor_total))

    def solicitar_cadastro(self):
        """Coleta dados do formulário e envia ao Controller."""
        placa = self.txt_placa.get().strip().upper()
        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip() or None
        status = self.cb_status.get().strip()
        estrategia = self.cb_estrategia.get().strip()
        valor_total = self.txt_valor.get().strip() or None

        if self.locacao_existente:
            # Edição: chama atualizar_locacao_admin no Controller
            sucesso, msg = self.controller.atualizar_locacao_admin(
                self.locacao_existente.id, placa, data_inicio, data_fim, status, estrategia, valor_total)
        else:
            # Criação: chama salvar_locacao_admin no Controller
            sucesso, msg = self.controller.salvar_locacao_admin(
                placa, data_inicio, data_fim, status, estrategia, valor_total)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
        else:
            messagebox.showerror("Erro", msg, parent=self)

        self.destroy()
