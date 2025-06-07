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

# Função para definir os dados da bateria.

def analisar_dados(ciclos, capacidade_projeto, capacidade_maxima):
    try:
        if ciclos == "Não encontrado" or capacidade_projeto == "Não encontrado" or capacidade_maxima == "Não encontrado":
            return ("ERRO", "Dados insuficientes para análise: um ou mais valores não foram encontrados.", "red")

        try:
            ciclos = int(ciclos)
            capacidade_projeto_valor = int(''.join(filter(str.isdigit, capacidade_projeto)))
            capacidade_maxima_valor = int(''.join(filter(str.isdigit, capacidade_maxima)))
        except ValueError as e:
            return ("ERRO", f"Erro na conversão dos dados: {e}", "red")
        
        degradacao = capacidade_maxima_valor / capacidade_projeto_valor

        if ciclos >= 40:
            return ("DESGASTADA", f"Sua bateria está DESGASTADA apresentando muitos ciclos de uso, que significa que a\n bateria foi muito utilizada. Apresentando um número de ciclos de {ciclos}, normalmente uma\n bateria saudável tem entre 10 a 40 ciclos, é recomendado fazer a TROCA da bateria.", "orange")
        elif ciclos < 10 and degradacao < 0.7:
            return ("DEFEITO DE FABRICAÇÃO", f"Sua bateria aparenta estar com DEFEITO DE FABRICAÇÃO\n já que ela não apresenta ter sido muito utilizada com número de ciclos de {ciclos}, o ciclo de bateria\n representa a quantidade de carga e descarga total da bateria,\n sua bateria foi projetada para suportar {capacidade_projeto} \ne atualmente está suportando {capacidade_maxima}, o que indica um defeito de fabricação,\n é recomendado entrar em contato com o fabricante.", "red")
        else:
            return ("NORMAL", f"A saúde da sua bateria é considerada NORMAL.\n Com {ciclos} ciclos de uso, ela está operando dentro dos parâmetros esperados para uma bateria em boas condições.\n Sua capacidade máxima atual é de {capacidade_maxima}.", "green")

    except Exception as e:
        return ("ERRO", f"Erro na análise dos dados: {e}", "red")

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
    animando = False  # Para a função do spinner.

    barra_progresso.stop()
    barra_progresso.pack_forget()

    texto_resultado.config(state=tk.NORMAL)
    texto_resultado.delete(1.0, tk.END)

    if not os.path.exists(caminho_relatorio):
        texto_resultado.insert(tk.END, "Relatório não encontrado. Execute o diagnóstico novamente.", "center")
        texto_resultado.config(state=tk.DISABLED)
        return

    try:
        with open(caminho_relatorio, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao ler o relatório: {e}")
        texto_resultado.config(state=tk.DISABLED)
        return

    titulo = soup.title.string if soup.title else "Relatório sem título"

    texto_resultado.pack(pady=20)
    
    texto_resultado.insert(tk.END, f"Diagnóstico concluído!\n{titulo}:\n\n", ("center", "fonte_grande"))
    texto_resultado.insert(tk.END, "Relatório gerado e analisado com sucesso!\n\n", ("center", "fonte_grande"))

    label_status.config(text="Diagnóstico concluído!", fg="green", font=("Arial", 18, "bold"))

    numero_ciclos, capacidade_design, capacidade_atual = extrair_resultados(soup)
    
    texto_resultado.insert(tk.END, f"Número de ciclos: {numero_ciclos}\n")
    texto_resultado.insert(tk.END, f"Capacidade de projeto: {capacidade_design}\n")
    texto_resultado.insert(tk.END, f"Capacidade atual: {capacidade_atual}\n")

    if "Não encontrado" in (numero_ciclos, capacidade_design, capacidade_atual):
        texto_resultado.insert(tk.END, "\nDados incompletos ou inválidos extraídos do relatório.\n", "center")
        label_status.config(text="Erro na extração", fg="red", font=("Arial", 18, "bold"))
        texto_resultado.config(state=tk.DISABLED)
        return

    status, mensagem, cor = analisar_dados(numero_ciclos, capacidade_design, capacidade_atual)

    # Inserimos o texto "Status: " normalmente.
    texto_resultado.insert(tk.END, "\nStatus: ", "center")
    
    # Verificamos o status e aplicamos a tag de cor correspondente APENAS à palavra do status.
    tag_cor = ""
    if status == "DESGASTADA":
        tag_cor = "cor_desgastada"
    elif status == "NORMAL":
        tag_cor = "cor_normal"
    elif status == "DEFEITO DE FABRICAÇÃO":
        tag_cor = "cor_defeito"

    # Inserimos a palavra do status com a tag de cor e a tag de centralização
    if tag_cor:
        texto_resultado.insert(tk.END, status, (tag_cor, "center"))
    else:
        # Se for um status inesperado ou de erro, insere sem cor especial
        texto_resultado.insert(tk.END, status, "center")

    texto_resultado.insert(tk.END, f"\n\n{mensagem}\n", "center")

    label_status.config(text=f"Diagnóstico: {status}", fg=cor, font=("Arial", 18, "bold"))
    
    texto_resultado.config(state=tk.DISABLED)

def extrair_resultados(soup):
    numero_ciclos = "Não encontrado"
    capacidade_design = "Não encontrado"
    capacidade_atual = "Não encontrado"

    tabelas = soup.find_all('table')

    for tabela in tabelas:
        linhas = tabela.find_all('tr')
        for linha in linhas:
            colunas = linha.find_all('td')
            if len(colunas) >= 2:
                chave = colunas[0].get_text(strip=True).upper()
                valor = colunas[1].get_text(strip=True)

                if "DESIGN CAPACITY" in chave:
                    capacidade_design = valor
                elif "FULL CHARGE CAPACITY" in chave:
                    capacidade_atual = valor
                elif "CYCLE COUNT" in chave:
                    numero_ciclos = valor

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
    width=80, 
    height=35, 
    font=("Arial", 15, "bold"),
    bg="#23272a",
    fg="white",
    insertbackground="white",
)
texto_resultado.tag_configure("center", justify='center')

# Aqui definimos nossas tags de estilo. Damos um nome a cada tag e configuramos suas propriedades (cor do texto e fonte).
texto_resultado.tag_configure("cor_desgastada", foreground="orange", font=("Arial", 15, "bold"))
texto_resultado.tag_configure("cor_normal", foreground="#32CD32", font=("Arial", 15, "bold")) 
texto_resultado.tag_configure("cor_defeito", foreground="red", font=("Arial", 15, "bold"))

# Tag para a fonte dos títulos e mensagens principais.
texto_resultado.tag_configure("fonte_grande", font=("Arial", 18, "bold"))

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