# Programa Principal
import tkinter as tk                 # Usamos Tkinter para fazer a interface gráfica.
from tkinter import messagebox       # Usamos messagebox para exibir mensagens ao usuário.
from tkinter import scrolledtext     # Usamos scrolledtext para caso tenhamos longos resultados.
from bs4 import BeautifulSoup        # Usamos BeautifulSoup para ler os dados do Arquivo HTML.
import glob                          # Usamos glob para localizar os arquivos HTML.  
import subprocess                    # Usamos subprocess para executar o comando no CMD.

def iniciar_diagnostico():
    
    # Primeira ação do programa será executar o comando no CMD.
    botao_iniciar.pack_forget()

    label_status.pack(pady=10)
    label_status.config(text="Iniciando o diagnóstico...")
    
    janela.after(2000, mostrar_resultado) 
    
def mostrar_resultado():
    
    label_status.pack_forget()

    texto_resultado.pack(pady=20)
    texto_resultado.insert(tk.END, "Diagnóstico concluído!\nResultados aparecerão aqui:\n", "center")


    # Configuração da interface gráfica.
janela = tk.Tk()
janela.title("PowerSave")
janela.geometry("600x400")
janela.configure(bg="#2f3136")

# Configuração do botão para iniciar o diagnóstico.
botao_iniciar = tk.Button(janela, text="Iniciar Diagnóstico", 
                          width=30, height=4, fg="white", bg="#7289da",
                          command=iniciar_diagnostico, 
                          font=("Arial", 15, "bold"))

botao_iniciar.place(relx=0.5, rely=0.5, anchor='center')

# Configurando a área do resultado.
texto_resultado = scrolledtext.ScrolledText(
    janela, 
    width=60, 
    height=15, 
    font=("Arial", 15, "bold"),
    bg="#23272a",
    fg="white",
    insertbackground="white",
)
texto_resultado.tag_configure("center", justify='center')


# Configurando o label dos status.
label_status = tk.Label(janela,
                        text="",
                        fg="white",
                        bg="#2f3136", 
                        font=("Arial", 18, "bold")
)

label_status.pack(pady=10)

janela.mainloop()