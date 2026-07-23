import tkinter as tk
from tkinter import ttk

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
   #antes de abrir a janela salvar o arquivo
   #criar variaveis e loop para enquanto o usuario disser "sim" o programa salvar o nome do programa{numero do pct}
   tela_f = tk.Tk()

   tela_f.title('confirmação')

   mensagem = ttk.Label(tela_f, text='Vai inserir mais algum pct na planilha?')
   mensagem.pack()

   

   tela_f.mainloop()

enviar = ttk.Button(root2, text='Salvar paciente', command=janela_confirmacao)
enviar.pack()



root2.mainloop()
