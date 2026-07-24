import glob
import os
import time
import webbrowser
from urllib.parse import urlparse

import pyautogui
import tkinter as tk
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tkinter import ttk


root = tk.Tk()
root.title("Bot de automação GUI")

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
CAMINHO_ICONE = os.path.join(DIRETORIO_ATUAL, "..", "..", "assets", "icone.png")

try:
    icone = tk.PhotoImage(file=CAMINHO_ICONE)
    root.iconphoto(False, icone)
except Exception as erro:
    print(f"Não foi possível carregar o ícone .png: {erro}")

largura = 600
altura = 400

pos_x = (root.winfo_screenwidth() // 2) - (largura // 2)
pos_y = (root.winfo_screenheight() // 2) - (altura // 2)

root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
root.resizable(False, False)
root.attributes("-topmost", 1)

ttk.Label(root, text="GUI - da automação").pack(pady=5)

tk.Label(root, text="Digite a URL do Excel Online:").pack()
link_entry = ttk.Entry(root, width=50)
link_entry.pack(pady=5)

tk.Label(root, text="Digite o e-mail Microsoft:").pack()
email_entry = ttk.Entry(root, width=50)
email_entry.pack(pady=5)

tk.Label(root, text="Digite a senha:").pack()
senha_entry = ttk.Entry(root, show="*", width=50)
senha_entry.pack(pady=5)

tk.Label(root, text="Digite a quantidade de células por linha:").pack()
celulas_entry = ttk.Entry(root, width=50)
celulas_entry.pack(pady=5)


def abrindo_excel(url):
    webbrowser.open(url)

def dominio_de_identidade_microsoft(url):
    host = urlparse(url).netloc.lower().split(":")[0]
    dominios = (
        "login.microsoftonline.com",
        "login.microsoft.com",
        "login.live.com",
    )
    return any(host == dominio or host.endswith(f".{dominio}") for dominio in dominios)

def verificar_pagina_autenticacao_microsoft(url):
    """Verifica a URL do navegador visível, que é o navegador usado pelo bot.

    Não usa outro navegador em modo headless: ele não compartilha os cookies
    da sessão corporativa e poderia detectar um login inexistente na planilha.
    """
    try:
        time.sleep(5)
        pyautogui.hotkey("ctrl", "l")
        pyautogui.hotkey("ctrl", "c")
        time.sleep(0.2)
        url_atual = root.clipboard_get().strip()
        pyautogui.press("esc")
    except tk.TclError:
        pyautogui.press("esc")
        print("Não foi possível ler a URL do navegador visível; login ignorado.")
        return False

    eh_autenticacao = dominio_de_identidade_microsoft(url_atual)
    if not eh_autenticacao:
        print(f"URL atual não é autenticação Microsoft: {url_atual}")
    return eh_autenticacao


def tratando_login(email, senha):
    time.sleep(5)
    pyautogui.write(email)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(2)
    pyautogui.hotkey("ctrl", "backspace")
    pyautogui.write(senha)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(2)
    pyautogui.press("enter")


arquivos_txt = sorted(glob.glob(os.path.join(DIRETORIO_ATUAL, "*.txt")))


def processar_arquivo_txt(arquivos, colunas_por_linha):
    time.sleep(3)
    pyautogui.click(x=500, y=500)
    time.sleep(1)
    pyautogui.hotkey("ctrl", "home")
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(0.3)
    pyautogui.press("enter")

    coluna_atual = 0
    for caminho_arquivo in arquivos:
        with open(caminho_arquivo, "r", encoding="utf8") as arquivo:
            for linha in arquivo:
                linha = linha.strip()
                pyautogui.write(linha)
                time.sleep(0.3)
                coluna_atual += 1

                if coluna_atual >= colunas_por_linha:
                    pyautogui.press("enter")
                    pyautogui.press("home")
                    coluna_atual = 0
                else:
                    pyautogui.press("tab")
                time.sleep(0.3)

    return "Processamento de todos os arquivos concluído!"


def executar_automacao():
    url = link_entry.get().strip()
    email = email_entry.get()
    senha = senha_entry.get()

    try:
        colunas_por_linha = int(celulas_entry.get())
    except ValueError:
        colunas_por_linha = 9

    if not url:
        print("Informe uma URL.")
        return

    abrindo_excel(url)
    precisa_autenticar = verificar_pagina_autenticacao_microsoft(url)

    if precisa_autenticar:
        tratando_login(email, senha)
    else:
        print("A página não é uma autenticação Microsoft; login ignorado.")

    processar_arquivo_txt(arquivos_txt, colunas_por_linha)


style = ttk.Style()
style.theme_use("default")
style.configure(
    "BotaoVerde.TButton",
    background="#28a745",
    foreground="white",
    font=("Helvetica", 10, "bold"),
    borderwidth=0,
    focusthickness=0,
)
style.map("BotaoVerde.TButton", background=[("active", "#218838")])

iniciar = ttk.Button(
    root,
    text="Iniciar",
    command=executar_automacao,
    style="BotaoVerde.TButton",
)
iniciar.pack(pady=15)

root.mainloop()
