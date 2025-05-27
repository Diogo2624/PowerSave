# Programa Principal

import tkinter as tk                 # Usamos Tkinter para fazer a interface gráfica.
from tkinter import messagebox       # Usamos messagebox para exibir mensagens ao usuário.
from tkinter import scrolledtext     # Usamos scrolledtext para caso tenhamos longos resultados.
from bs4 import BeautifulSoup        # Usamos BeautifulSoup para ler os dados do Arquivo HTML.
import glob                          # Usamos glob para localizar os arquivos HTML.  
import subprocess                    # Usamos subprocess para executar o comando no CMD.
import os                            # Usamos os para poder navegar pelo windows.
import itertools                     # Vamos usar o itertools para criar uma barra de carregamento do progresso.
from tkinter import ttk              # Usamos ttk para criar uma barra de carregamento.

spinner = itertools.cycle(['|', '/', '-', '\\'])
animando = False

# Função para animar o spinner.

def animar_spinner():
    if animando:
        label_status.config(text=f"Iniciando o diagnóstico... {next(spinner)}")
        janela.after(200, animar_spinner) 


# Função para iniciar o diagnóstico.

def iniciar_diagnostico():

    global animando
    animando = True

    botao_iniciar.config(state=tk.DISABLED)     # Após o clique, o botão é desativado para evitar erros.
    botao_iniciar.pack_forget()
    
    barra_progresso.pack(pady=10)
    barra_progresso.start(10)
    
    animar_spinner()

    pasta_usuario = os.path.expanduser("~")
    caminho_relatorio = os.path.join(pasta_usuario, "battery-report.html")

    try:
        # Aqui ele vai executar o comando no CMD, o comando utilizado é o "/batteryreport"
        
        subprocess.run(["powercfg", "/batteryreport", "/output", caminho_relatorio], check=True)
    
    except subprocess.CalledProcessError as e:
        
        # Se ocorrer algum erro durante a execução do comando, exibe uma mensagem de erro.
        
        barra_progresso.stop()
        barra_progresso.pack_forget()
        messagebox.showerror("Erro", f"Erro ao gerar o relatório: {e}")
        return
    
    janela.after(2000, lambda: mostrar_resultado(caminho_relatorio)) 
    
def mostrar_resultado(caminho_relatorio):

    global animando
    animando = False       # Para a função do spinner.
    
    barra_progresso.stop()
    barra_progresso.pack_forget()

    # Verifica se o relatório foi gerado.

    if not os.path.exists(caminho_relatorio):
        texto_resultado.pack(pady=20)
        texto_resultado.delete(1.0, tk.END)
        texto_resultado.insert(tk.END, "Relatório não encontrado. Execute o diagnóstico novamente.", "center")
        return
    try:
        with open(caminho_relatorio, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler o relatório: {e}")
        return

    titulo = soup.title.string if soup.title else "Relatório sem título"

    texto_resultado.pack(pady=20)
    texto_resultado.delete(1.0, tk.END) 
    texto_resultado.insert(tk.END, f"Diagnóstico concluído!\n{titulo}:\n\n", "center")
    texto_resultado.insert(tk.END, "Relatório gerado e analisado com sucesso!\n\n", "center")

    label_status.config(text="Diagnóstico concluído!", fg="green", font=("Arial", 18, "bold"))


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

# Barra de progresso.

barra_progresso = ttk.Progressbar(janela, orient="horizontal", length=400, mode="indeterminate")

janela.mainloop()