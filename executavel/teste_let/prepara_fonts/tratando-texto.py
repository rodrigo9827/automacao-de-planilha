import tkinter as tk
from tkinter import ttk
import os
import pyautogui

root2 = tk.Tk()

root2.title('New note block')

pct = ttk.Label(root2, text='Insira as informações do atendimento')
pct.pack()

frame = ttk.Frame(root2)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
barra_rolagem = ttk.Scrollbar(frame)
barra_rolagem.pack(side=tk.RIGHT, fill=tk.Y)

texto = tk.Text(frame, height=20)
texto.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
texto['yscrollcommand']=barra_rolagem.set

barra_rolagem.config(command=texto.yview)

texto.insert(tk.END, "\n")

def janela_confirmacao():
      
   def Salvar_paciente():
       valor_fixo = "paciente"
       contador = 1
       while os.path.exists(f"{valor_fixo}_{contador}.txt"):
           contador += 1
       nome_arquivo = f"{valor_fixo}_{contador}.txt"
       with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
           conteudo = texto.get("1.0", tk.END)
           arquivo.write(conteudo)
   Salvar_paciente()

   tela_f = tk.Toplevel(root2)

   tela_f.title('confirmação')

   mensagem = ttk.Label(tela_f, text='Vai inserir mais algum pct na planilha?')
   mensagem.pack()

   def executar_apos_destruicao():
       pyautogui.press('tab')
       root2.after(200, lambda: pyautogui.hotkey('ctrl', 'a'))
       root2.after(400, lambda: pyautogui.press('backspace'))

   def destruir_e_executar():
       tela_f.destroy()
       root2.after(300, executar_apos_destruicao)

   def botao_sim_click():
       destruir_e_executar()


   def botao_nao_click(): #arrumar para salvar o arquivo e abrir a tela de inserção de dados, para inserir mais um paciente
       destruir_e_executar()
       exit()

   botao_sim = ttk.Button(tela_f, text='Sim', command=botao_sim_click)
   botao_sim.pack()

   botao_nao = ttk.Button(tela_f, text='Não', command=botao_nao_click)
   botao_nao.pack()

         

enviar = ttk.Button(root2, text='Salvar paciente', command=janela_confirmacao)
enviar.pack()


root2.mainloop()
