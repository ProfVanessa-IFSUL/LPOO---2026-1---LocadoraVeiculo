"""
JanelaNovaReserva — Formulário para criar nova reserva (visão Usuário).
Aplica validações de negócio: datas futuras, veículos disponíveis por período.
Acessada a partir de JanelaLocacaoUsuario (botão Nova Reserva).
"""
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from control.locacao_controller import LocacaoController


class JanelaNovaReserva(tk.Toplevel):
    """Formulário de nova reserva com filtro dinâmico de veículos disponíveis."""

    def __init__(self, master=None):
        super().__init__(master)
        self.title("Nova Reserva")
        self.geometry("450x400")
        self.controller = LocacaoController()

        tk.Label(self, text="Nova Reserva", font=("Helvetica", 16, "bold")).pack(pady=10)

        # --- Data Início ---
        frame_di = tk.Frame(self)
        frame_di.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_di, text="Data Início (dd/mm/aaaa):").pack(side="left")
        self.txt_data_inicio = tk.Entry(frame_di)
        self.txt_data_inicio.pack(side="right", expand=True, fill="x")
        # Preenche com a data de hoje como sugestão
        self.txt_data_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))

        # --- Data Fim ---
        frame_df = tk.Frame(self)
        frame_df.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_df, text="Data Fim (dd/mm/aaaa):").pack(side="left")
        self.txt_data_fim = tk.Entry(frame_df)
        self.txt_data_fim.pack(side="right", expand=True, fill="x")

        # --- Categoria (filtro) ---
        frame_cat = tk.Frame(self)
        frame_cat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_cat, text="Categoria:").pack(side="left")
        self.cb_categoria = ttk.Combobox(frame_cat, values=["Todas", "ECONOMICO", "EXECUTIVO"])
        self.cb_categoria.current(0)
        self.cb_categoria.pack(side="right", expand=True, fill="x")

        # --- Botão para buscar veículos disponíveis ---
        tk.Button(self, text="Buscar Veículos Disponíveis", command=self.buscar_disponiveis).pack(pady=5)

        # --- Veículo Disponível (ComboBox populada dinamicamente) ---
        frame_veiculo = tk.Frame(self)
        frame_veiculo.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_veiculo, text="Veículo Disponível:").pack(side="left")
        self.cb_veiculo = ttk.Combobox(frame_veiculo, state="readonly")
        self.cb_veiculo.pack(side="right", expand=True, fill="x")

        # --- Estratégia de Cálculo ---
        frame_estrat = tk.Frame(self)
        frame_estrat.pack(pady=5, fill="x", padx=20)
        tk.Label(frame_estrat, text="Tipo de Cliente:").pack(side="left")
        self.cb_estrategia = ttk.Combobox(frame_estrat, values=["padrao", "vip"])
        self.cb_estrategia.current(0)
        self.cb_estrategia.pack(side="right", expand=True, fill="x")

        # --- Botão Confirmar Reserva ---
        tk.Button(self, text="Confirmar Reserva", command=self.confirmar_reserva).pack(pady=15)

        # Armazena a lista de veículos disponíveis para referência
        self.veiculos_disponiveis = []

    def buscar_disponiveis(self):
        """
        Consulta veículos disponíveis no período informado (Parte 4 da atividade).
        Popula o ComboBox de veículos com os resultados filtrados.
        """
        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()

        if not data_inicio or not data_fim:
            messagebox.showwarning("Aviso", "Preencha as datas de início e fim.", parent=self)
            return

        categoria = self.cb_categoria.get().strip()

        # Consulta via Controller → DAO (com filtro de sobreposição de datas)
        self.veiculos_disponiveis = self.controller.listar_veiculos_disponiveis(
            data_inicio, data_fim, categoria
        )

        if self.veiculos_disponiveis:
            # Popula o ComboBox com "Placa — Tipo (Categoria)" para facilitar a escolha
            opcoes = [f"{v.placa} — {v.__class__.__name__} ({v.categoria})"
                      for v in self.veiculos_disponiveis]
            self.cb_veiculo.config(values=opcoes)
            self.cb_veiculo.current(0)
        else:
            self.cb_veiculo.config(values=["Nenhum veículo disponível"])
            self.cb_veiculo.current(0)
            messagebox.showinfo("Informação", "Nenhum veículo disponível no período e categoria informados.", parent=self)

    def confirmar_reserva(self):
        """Coleta dados e cria a reserva via Controller (com validações de negócio)."""
        data_inicio = self.txt_data_inicio.get().strip()
        data_fim = self.txt_data_fim.get().strip()
        estrategia = self.cb_estrategia.get().strip()

        # Verifica se um veículo válido foi selecionado
        veiculo_sel = self.cb_veiculo.get()
        if not veiculo_sel or "Nenhum" in veiculo_sel:
            messagebox.showwarning("Aviso", "Selecione um veículo disponível. Use 'Buscar Veículos Disponíveis'.", parent=self)
            return

        # Extrai a placa do texto selecionado ("ABC1D23 — Carro (ECONOMICO)")
        placa = veiculo_sel.split(" — ")[0].strip()

        # Chama o Controller para criar a reserva (aplica regras de negócio)
        sucesso, msg = self.controller.criar_reserva(placa, data_inicio, data_fim, estrategia)

        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.destroy()
        else:
            messagebox.showerror("Erro", msg, parent=self)
