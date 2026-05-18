"""
main.py — Ponto de entrada da aplicação Locadora de Veículos.

Cria a JanelaPrincipal (tk.Tk) com barra de menus (tk.Menu):
    Menu Cadastro:
        └── Veículo         -> abre JanelaListagemVeiculos (CRUD já existente)
        └── Locações (Admin) -> abre JanelaListagemLocacoes (CRUD completo)
    Menu Ação:
        └── Locar Veículo   -> abre JanelaLocacaoUsuario (ações operacionais)

Regras de hierarquia:
    - JanelaPrincipal é a ÚNICA instância de tk.Tk() em toda a aplicação.
    - Todas as demais telas são tk.Toplevel, abertas como filhas.
"""
import tkinter as tk
import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir que os módulos sejam encontrados
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class JanelaPrincipal(tk.Tk):
    """
    Janela principal da aplicação — contém apenas a barra de menus.
    Todas as funcionalidades são acessadas via submenus que abrem Toplevel.
    """

    def __init__(self):
        super().__init__()
        self.title("Locadora de Veículos — LPOO 2026/1")
        self.geometry("500x300")

        # --- Barra de Menus (tk.Menu) ---
        barra_menu = tk.Menu(self)
        self.config(menu=barra_menu)

        # --- Menu: Cadastro ---
        # Contém os CRUDs de entidades (Veículo e Locações/Admin)
        menu_cadastro = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Cadastro", menu=menu_cadastro)
        
        # Submenu: Veículo -> abre a tela de CRUD de Veículos (já existente)
        menu_cadastro.add_command(label="Veículo", command=self.abrir_veiculos)
        
        # Submenu: Locações (Admin) -> abre a tela de CRUD de Locações (Admin)
        menu_cadastro.add_command(label="Locações (Admin)", command=self.abrir_locacoes_admin)

        # --- Menu: Ação ---
        # Contém as operações do dia-a-dia da locadora
        menu_acao = tk.Menu(barra_menu, tearoff=0)
        barra_menu.add_cascade(label="Ação", menu=menu_acao)
        
        # Submenu: Locar Veículo -> abre a tela do Usuário
        menu_acao.add_command(label="Locar Veículo", command=self.abrir_locacao_usuario)

        # --- Label informativa na janela principal ---
        lbl_info = tk.Label(
            self,
            text="Bem-vindo à Locadora de Veículos!\n\n"
                 "Use a barra de menus acima para navegar:\n\n"
                 "menu Cadastro -> Veículo / Locações (Admin)\n"
                 "menu Ação -> Locar Veículo",
            font=("Helvetica", 12),
            justify="center"
        )
        lbl_info.pack(expand=True)

    # ------------------------------------------------------------------
    # MÉTODOS QUE ABREM AS TELAS (Toplevel)
    # ------------------------------------------------------------------

    def abrir_veiculos(self):
        """Abre a JanelaListagemVeiculos (CRUD de Veículos — já implementada)."""
        from view.veiculo_list_view import JanelaListagemVeiculos
        JanelaListagemVeiculos(master=self)

    def abrir_locacoes_admin(self):
        """Abre a JanelaListagemLocacoes (CRUD completo de Locações — Admin)."""
        from view.locacao_list_view import JanelaListagemLocacoes
        JanelaListagemLocacoes(master=self)

    def abrir_locacao_usuario(self):
        """Abre a JanelaLocacaoUsuario (operações de locação — Usuário)."""
        from view.locacao_usuario_view import JanelaLocacaoUsuario
        JanelaLocacaoUsuario(master=self)


# ------------------------------------------------------------------
# PONTO DE ENTRADA DA APLICAÇÃO
# ------------------------------------------------------------------
if __name__ == "__main__":
    app = JanelaPrincipal()
    app.mainloop()
