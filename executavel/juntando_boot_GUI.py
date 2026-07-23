import webbrowser
import pyautogui
import tkinter as tk
from tkinter import ttk
import glob
import time
import os

root = tk.Tk()

root.title('Bot de automação GUI')

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_icone = os.path.join(diretorio_atual, '..', 'assets', 'icone.png')

try:
    icone = tk.PhotoImage(file=caminho_icone)
    root.iconphoto(False, icone)
except Exception as e:
    print(f"Não foi possível carregar o ícone .png: {e}")

largura = 600
altura = 400

pos_x = (root.winfo_screenwidth() // 2) - (largura // 2)
pos_y = (root.winfo_screenheight() // 2) - (altura // 2)

root.geometry(f'{largura}x{altura}+{pos_x}+{pos_y}')


root.resizable(0,0)
root.attributes('-topmost', 1)

ttk.Label(root, text='GUI - da automação').pack(pady=5)

tk.Label(root, text='Digite a URL (ex: https://exemplo.com):').pack()
link_entry = ttk.Entry(root, width=50)
link_entry.pack(pady=5)

tk.Label(root, text='Digite o e-mail Microsoft:').pack()
email_entry = ttk.Entry(root, width=50)
email_entry.pack(pady=5)

tk.Label(root, text='Digite a senha:').pack()
senha_entry = ttk.Entry(root, show='*', width=50)
senha_entry.pack(pady=5)

tk.Label(root, text='Digite a quantidade de células por linha:').pack()
celulas_entry = ttk.Entry(root, width=50)
celulas_entry.pack(pady=5)


def abrindo_excel(url):
    webbrowser.open(url)

def tratando_Login(email, senha):
    time.sleep(5)
    pyautogui.write(email)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.hotkey('ctrl', 'backspace')
    pyautogui.write(senha)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(2)
    pyautogui.press('enter')

arquivos_txt = sorted(glob.glob('*.txt'))

def processar_arquivo_txt(arquivos_txt, colunas_por_linha):
    time.sleep(3) 
    pyautogui.click(x=500, y=500) 
    time.sleep(1) 
    pyautogui.hotkey('ctrl', 'home')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(0.3)
    pyautogui.press('enter')

    coluna_atual = 0
    for caminho_arquivo in arquivos_txt:    
        with open(caminho_arquivo, 'r', encoding='utf8') as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                            
                pyautogui.write(linha)
                time.sleep(0.3)
            
                coluna_atual += 1
            
                if coluna_atual >= colunas_por_linha:
                    pyautogui.press('enter')  
                    pyautogui.press('home')  
                    coluna_atual = 0
                else:
                    pyautogui.press('tab')   
                time.sleep(0.3)
    return "Processamento de todos os arquivos concluído!"

def executar_automacao():
    url = link_entry.get()
    email = email_entry.get()
    senha = senha_entry.get()
    
    
    try:
        colunas_por_linha = int(celulas_entry.get())
    except ValueError:
        colunas_por_linha = 5  # Valor padrão de segurança

    if url:
        abrindo_excel(url)
        tratando_Login(email, senha)
        processar_arquivo_txt(arquivos_txt, colunas_por_linha)

style = ttk.Style()
style.theme_use('default')  

style.configure(
    'BotaoVerde.TButton',
    background='#28a745',  
    foreground='white',     
    font=('Helvetica', 10, 'bold'),
    borderwidth=0,
    focusthickness=0
)

style.map(
    'BotaoVerde.TButton',
    background=[('active', '#218838')]  
)

iniciar = ttk.Button(root, text='Iniciar', command=executar_automacao, style='BotaoVerde.TButton')
iniciar.pack(pady=15)

root.mainloop()
