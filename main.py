import tkinter as tk
import sys
import os

# Adiciona o diretório raiz ao sys.path para garantir que os módulos sejam encontrados
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from view.veiculo_list_view import JanelaListagemVeiculos
from model.veiculo import VeiculoFactory, Categoria
import view.veiculo_list_view as list_view

def popular_dados_iniciais():
    """Popula a lista com alguns dados iniciais para testar a interface."""
    v1 = VeiculoFactory.criar_veiculo("carro", "ABC1D23", Categoria.ECONOMICO, 150.0)
    v2 = VeiculoFactory.criar_veiculo("motorhome", "XYZ9A99", Categoria.EXECUTIVO, 300.0)
    list_view.lista_veiculos.extend([v1, v2])

if __name__ == "__main__":
    #popular_dados_iniciais()
    
    root = tk.Tk()
    root.withdraw() # Esconde a janela principal do Tkinter raiz vazia
    
    app = JanelaListagemVeiculos(master=root)
    # Quando a janela do Toplevel for fechada, encerra o programa
    app.protocol("WM_DELETE_WINDOW", root.destroy)
    
    root.mainloop()
