import tkinter as tk
from tkinter import ttk

root2 = tk.Tk()

root2.title('New note block')

tk.Label(root2, text='insira as informações para inserir na planilha').pack()
entrada_texto = ttk.Entry(root2, width=50)
entrada_texto.pack(ipadx=20, ipady=30)

root2.mainloop()
