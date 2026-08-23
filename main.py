import os
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from core.pacientes import (
    garantir_pasta,
    ler_paciente,
    listar_arquivos_txt,
    mover_processados,
    salvar_paciente,
)
from core.web_automation import (
    ErroDeLogin,
    abrir_planilha,
    aguardar_planilha_carregar,
    fazer_login,
    iniciar_navegador,
    preencher_pacientes,
)
# Pasta onde as enfermeiras salvam os pacientes
PASTA_ATENDIMENTO = os.path.join(os.path.expanduser("~"), "Desktop", "atendimento_rodada")
class JanelaTextoLivre:
    def __init__(
        self, janela_pai: tk.Tk, ao_salvar, titulo: str, prefixo_arquivo: str
    ) -> None:
        self.ao_salvar = ao_salvar
        self.prefixo_arquivo = prefixo_arquivo

        self.janela = tk.Toplevel(janela_pai)
        self.janela.title(titulo)
        self.janela.resizable(False, False)
        self.janela.transient(janela_pai)
        self.janela.grab_set()  # foca essa janela até o usuário terminar

        largura, altura = 460, 380
        pos_x = janela_pai.winfo_x() + 60
        pos_y = janela_pai.winfo_y() + 40
        self.janela.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        ttk.Label(
            self.janela,
            text="Digite as informações — cada linha vira uma célula da\n"
                 "planilha, na ordem em que aparece. Deixe uma linha em\n"
                 "branco para pular uma célula.",
        ).pack(anchor="w", padx=14, pady=(14, 6))

        self.caixa_texto = tk.Text(self.janela, width=52, height=14)
        self.caixa_texto.pack(padx=14, pady=4)
        self.caixa_texto.focus_set()

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "BotaoVerde.TButton",
            background="#28a745",
            foreground="white",
            font=("Helvetica", 10, "bold"),
            borderwidth=0,
            relief="flat",
            focuscolor="",

        )
        estilo.map(
            "BotaoVerde.TButton",
            background=[("active", "#218838")],
            foreground=[("active", "white")],
        )

        ttk.Button(
            self.janela,
            text="Adicionar à fila",
            command=self._salvar,
            style="BotaoVerde.TButton",
        ).pack(pady=14)

    def _salvar(self) -> None:
        texto = self.caixa_texto.get("1.0", tk.END).rstrip("\n")

        if not texto.strip():
            messagebox.showwarning("Campo vazio", "Digite alguma informação antes de adicionar.")
            return

        linhas = texto.split("\n")

        garantir_pasta(PASTA_ATENDIMENTO)
        base = self.prefixo_arquivo + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho = salvar_paciente(PASTA_ATENDIMENTO, base, linhas)

        messagebox.showinfo(
            "Registro salvo", f"Arquivo criado:\n{os.path.basename(caminho)}"
        )
        self.ao_salvar()
        self.janela.destroy()


class JanelaPrincipal:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Automação de Atendimento - Gestantes")

        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        caminho_icone = os.path.join(diretorio_atual, "assets", "icone.png")
        try:
            icone = tk.PhotoImage(file=caminho_icone)
            self.root.iconphoto(False, icone)
        except Exception:
            pass  # ícone é só estético, não impede o programa de funcionar

        largura, altura = 620, 480
        pos_x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")
        self.root.resizable(False, False)

        self._montar_widgets()

    def _montar_widgets(self) -> None:
        ttk.Label(
            self.root,
            text="Automação de preenchimento - Atendimento de Gestantes",
            font=("Helvetica", 11, "bold"),
        ).pack(pady=(12, 4))

        ttk.Label(self.root, text="Link da planilha (SharePoint / Excel Online):").pack()
        self.campo_url = ttk.Entry(self.root, width=70)
        self.campo_url.pack(pady=4)

        ttk.Label(self.root, text="E-mail Microsoft:").pack()
        self.campo_email = ttk.Entry(self.root, width=50)
        self.campo_email.pack(pady=4)

        ttk.Label(self.root, text="Senha:").pack()
        self.campo_senha = ttk.Entry(self.root, show="*", width=50)
        self.campo_senha.pack(pady=4)

        ttk.Label(self.root, text="Quantidade de células por linha (padrão: 5):").pack()
        self.campo_colunas = ttk.Entry(self.root, width=10)
        self.campo_colunas.insert(0, "5")
        self.campo_colunas.pack(pady=4)

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure(
            "BotaoVerde.TButton",
            background="#28a745",
            foreground="white",
            font=("Helvetica", 10, "bold"),
            borderwidth=0,
            relief="flat",
            focuscolor="",
        )
        estilo.map(
            "BotaoVerde.TButton",
            background=[("active", "#218838")],
            foreground=[("active", "white")],
        )
        estilo.configure(
            "BotaoAzul.TButton",
            background="#0d6efd",
            foreground="white",
            font=("Helvetica", 10, "bold"),
            borderwidth=0,
            relief="flat",
            focuscolor="",
        )
        estilo.map(
            "BotaoAzul.TButton",
            background=[("active", "#0b5ed7")],
            foreground=[("active", "white")],
        )

        linha_botoes = ttk.Frame(self.root)
        linha_botoes.pack(pady=10)

        self.botao_registro_livre = ttk.Button(
            linha_botoes,
            text="+ Inserir paciente",
            command=self._abrir_janela_registro_livre,
            style="BotaoAzul.TButton",
        )
        self.botao_registro_livre.grid(row=0, column=0, padx=6)

        self.botao_iniciar = ttk.Button(
            linha_botoes,
            text="Iniciar automação",
            command=self._ao_clicar_iniciar,
            style="BotaoVerde.TButton",
        )
        self.botao_iniciar.grid(row=0, column=1, padx=6)

        self.rotulo_pendentes = ttk.Label(self.root, text="")
        self.rotulo_pendentes.pack()
        self._atualizar_contagem_pendentes()

        ttk.Label(self.root, text="Status:").pack(anchor="w", padx=12)
        self.caixa_status = tk.Text(self.root, height=10, width=74, state="disabled")
        self.caixa_status.pack(padx=12, pady=(2, 12))

    def _atualizar_contagem_pendentes(self) -> None:
        garantir_pasta(PASTA_ATENDIMENTO)
        quantidade = len(listar_arquivos_txt(PASTA_ATENDIMENTO))
        if quantidade == 0:
            texto = "Nenhum paciente na fila."
        elif quantidade == 1:
            texto = "1 paciente na fila."
        else:
            texto = f"{quantidade} pacientes na fila."
        self.rotulo_pendentes.configure(text=texto)

    def _abrir_janela_registro_livre(self) -> None:
        JanelaTextoLivre(
            self.root,
            ao_salvar=self._atualizar_contagem_pendentes,
            titulo="Inserir paciente",
            prefixo_arquivo="paciente",
        )

    def _log(self, mensagem: str) -> None:
        """Escreve uma linha na caixa de status (thread-safe via `after`)."""
        def escrever():
            self.caixa_status.configure(state="normal")
            self.caixa_status.insert(tk.END, mensagem + "\n")
            self.caixa_status.see(tk.END)
            self.caixa_status.configure(state="disabled")
        self.root.after(0, escrever)

    def _ao_clicar_iniciar(self) -> None:
        url = self.campo_url.get().strip()
        email = self.campo_email.get().strip()
        senha = self.campo_senha.get()

        try:
            colunas_por_linha = int(self.campo_colunas.get())
        except ValueError:
            colunas_por_linha = 5

        # Apaga a senha do campo assim que ela é lida 
        self.campo_senha.delete(0, tk.END)

        if not url or not email or not senha:
            messagebox.showwarning(
                "Campos obrigatórios",
                "Preencha o link da planilha, o e-mail e a senha antes de iniciar.",
            )
            return

        self.botao_iniciar.configure(state="disabled")
        thread = threading.Thread(
            target=self._executar_automacao,
            args=(url, email, senha, colunas_por_linha),
            daemon=True,
        )
        thread.start()

    def _executar_automacao(
        self, url: str, email: str, senha: str, colunas_por_linha: int
    ) -> None:
        driver = None
        try:
            garantir_pasta(PASTA_ATENDIMENTO)
            arquivos = listar_arquivos_txt(PASTA_ATENDIMENTO)

            if not arquivos:
                self._log(
                    f"[AVISO] Nenhum arquivo .txt encontrado em: {PASTA_ATENDIMENTO}"
                )
                return

            self._log(f"[OK] {len(arquivos)} paciente(s) encontrado(s).")

            self._log("[..] Abrindo o navegador (Edge)...")
            driver = iniciar_navegador()

            self._log("[..] Abrindo a planilha...")
            abrir_planilha(driver, url)

            self._log("[..] Fazendo login...")
            fazer_login(driver, email, senha)
            self._log("[OK] Login concluído.")

            self._log("[..] Aguardando a planilha carregar...")
            aguardar_planilha_carregar(driver)

            self._log("[..] Preenchendo os dados dos pacientes...")
            linhas_por_paciente = [ler_paciente(caminho) for caminho in arquivos]
            total = preencher_pacientes(driver, linhas_por_paciente, colunas_por_linha)

            pasta_destino = mover_processados(arquivos, PASTA_ATENDIMENTO)

            self._log(f"[OK] {total} paciente(s) processado(s) com sucesso!")
            self._log(f"[OK] Arquivos movidos para: {pasta_destino}")
            self.root.after(
                0,
                lambda: messagebox.showinfo(
                    "Concluído", f"{total} paciente(s) processado(s) com sucesso!"
                ),
            )

        except ErroDeLogin as erro:
            self._log(f"[ERRO] Falha no login: {erro}")
            self.root.after(0, lambda: messagebox.showerror("Erro de login", str(erro)))

        except Exception as erro:  # captura ampla de propósito: é a GUI final
            self._log(f"[ERRO] {erro}")
            self.root.after(0, lambda: messagebox.showerror("Erro", str(erro)))

        finally:
            self.root.after(0, lambda: self.botao_iniciar.configure(state="normal"))
            self.root.after(0, self._atualizar_contagem_pendentes)
            
    def executar(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    JanelaPrincipal().executar()
