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
from PIL import Image, ImageTk       # Utilizando PIL para colocar a logo do programa, e também para uma melhor qualidade de imagem.

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
    label_imagem.pack_forget()
    label_texto.pack_forget()        # Esconde a logo do programa.
    
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

def extrair_resultados(soup):                #Essa função vai extrair os dados necessários do relatório HTML.
    
    numero_ciclos = "Não encontrado"
    capacidade_design = "Não encontrado"
    capacidade_atual = "Não encontrado"

    tabelas = soup.find_all('table')

    # Aqui ele busca no relatório HTML as informações da capacidade de carga de fabrica e a capacidade de carga atual.
    for tabela in tabelas:
        if "installed batteries" in tabela.text or "bateria instaladas" in tabela.text.lower():
            linhas = tabela.find_all('tr')
            for linha in linhas:
                if "DESIGN CAPACITY" in linha.text or "Capacidade de projeto" in linha.text:
                    capacidade_design = linha.find_all('td')[-1].text.strip()
                if "FULL CHARGE CAPACITY" in linha.text or "Capacidade máxima de carga" in linha.text:
                    capacidade_atual = linha.find_all('td')[-1].text.strip()
        
        # Aqui ele busca o número de ciclos da bateria.
        if "Battery usage" in tabela.text or "Uso da bateria" in tabela.text:
            linhas = tabela.find_all('tr')
            for linha in linhas:
                if "Cycle Count" in linha.text or "Contagem de ciclos" in linha.text:
                    numero_ciclos = linha.find_all('td')[-1].text.strip()
        
    return numero_ciclos, capacidade_design, capacidade_atual



# Configuração da interface gráfica.

janela = tk.Tk()
janela.title("PowerSave")
janela.geometry("1000x600")
janela.configure(bg="#2f3136")

# icone da janela.
janela.iconbitmap("powersave.ico")

# Configuração da logo do programa.
imagem_logo = Image.open("logo.png")
imagem_logo = imagem_logo.resize((330, 165))
imagem_logo = ImageTk.PhotoImage(imagem_logo)

# Posicionando a logo.
label_imagem = tk.Label(janela, image=imagem_logo, bg="#2f3136")
label_imagem.pack(pady=50)

# Configuração do texto que fica entre o botão e a logo.

label_texto = tk.Label(janela,
                       text="Bem-vindo ao PowerSave!",
                       fg="white",
                       bg="#2f3136",
                       font=("Arial", 24, "bold"),
                       justify="center")
label_texto.pack(pady=10)

label_texto = tk.Label(janela,
                       text="Vamos avaliar a saúde da sua bateria?",
                       fg="white",
                       bg="#2f3136",
                       font=("Arial", 15),
                       justify="center")
label_texto.pack(pady=1)

# Configuração do botão para iniciar o diagnóstico.

botao_iniciar = tk.Button(janela, text="Iniciar Diagnóstico", 
                          width=20, height=3, fg="white", bg="#7289da",
                          command=iniciar_diagnostico, 
                          font=("Arial", 15, "bold"))

botao_iniciar.pack(pady=50)

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