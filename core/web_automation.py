import time
from dataclasses import dataclass

import pyperclip
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# IDs padrão da página de login da Microsoft (login.microsoftonline.com).
ID_CAMPO_EMAIL = "i0116"
ID_BOTAO_AVANCAR = "idSIButton9"
ID_CAMPO_SENHA = "i0118"
ID_BOTAO_ENTRAR = "idSIButton9"  # mesmo id é reaproveitado na tela de senha
ID_BOTAO_MANTER_CONECTADO = "idSIButton9"  # e na tela "Continuar conectado?"

TEMPO_ESPERA_PADRAO = 20  # segundos máximos esperando cada elemento aparecer
TEMPO_ESPERA_DETECCAO_LOGIN = 12  # segundos para decidir se precisa logar
class ErroDeLogin(Exception):
    '''Erro específico para falha de autenticação (senha errada, etc.).'''


@dataclass
class ResultadoAutomacao:
    sucesso: bool
    mensagem: str
    pacientes_processados: int = 0


def iniciar_navegador() -> webdriver.Edge:
    #Abre uma janela do Edge controlada pelo Selenium.

    
    opcoes = EdgeOptions()
    opcoes.add_argument("--start-maximized")
    # Evita o popup nativo do Edge perguntando "salvar senha?"
    opcoes.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    })
    return webdriver.Edge(options=opcoes)


def abrir_planilha(driver: webdriver.Edge, url: str) -> None:
    driver.get(url)


def fazer_login(driver: webdriver.Edge, email: str, senha: str) -> None:
    #Preenche e-mail e senha na tela de login da Microsoft.
    espera = WebDriverWait(driver, TEMPO_ESPERA_PADRAO)
    try:
        campo_email = WebDriverWait(driver, TEMPO_ESPERA_DETECCAO_LOGIN).until(
            EC.visibility_of_element_located((By.ID, ID_CAMPO_EMAIL))
        )
    except TimeoutException:
        return  #confirma se já estava logado 

    campo_email.clear()
    campo_email.send_keys(email)

    espera.until(
        EC.element_to_be_clickable((By.ID, ID_BOTAO_AVANCAR))
    ).click()

    campo_senha = espera.until(
        EC.visibility_of_element_located((By.ID, ID_CAMPO_SENHA))
    )
    campo_senha.clear()
    campo_senha.send_keys(senha)

    espera.until(
        EC.element_to_be_clickable((By.ID, ID_BOTAO_ENTRAR))
    ).click()

    try:
        botao_manter = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.ID, ID_BOTAO_MANTER_CONECTADO))
        )
        botao_manter.click()
    except TimeoutException:
        pass  # tela não apareceu — tudo bem, segue o jogo

    # Confirma que não sobrou um campo de senha na tela (= login falhou)
    time.sleep(2)
    campos_senha_restantes = driver.find_elements(By.ID, ID_CAMPO_SENHA)
    if campos_senha_restantes and campos_senha_restantes[0].is_displayed():
        raise ErroDeLogin(
            "A página de login ainda está pedindo senha. "
            "Confira se o e-mail e a senha estão corretos."
        )


def aguardar_planilha_carregar(driver: webdriver.Edge, timeout: int = 60) -> None:
    # Espera a interface do Excel Online terminar de carregar.

    espera = WebDriverWait(driver, timeout)
    espera.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(4)  # margem de segurança para o canvas terminar de desenhar


def focar_grade_planilha(driver: webdriver.Edge) -> None:
    # Garante que o foco do teclado está na grade de células, não em
    # outro elemento da página (como a caixa de busca do Excel Online).
    #
    # Clicar no <body> inteiro usa o CENTRO desse elemento como ponto
    # de clique — dependendo do tamanho da janela, esse centro pode
    # cair sobre a caixa de busca no canto superior da tela, em vez de
    # cair na planilha. A correção: apertar Esc primeiro (fecha
    # qualquer busca ou painel já aberto) e clicar especificamente no
    # elemento <canvas> da grade — é ali que o Excel Online desenha as
    # células.
    acoes = ActionChains(driver)
    acoes.send_keys(Keys.ESCAPE)
    acoes.perform()
    time.sleep(0.5)

    canvases = driver.find_elements(By.TAG_NAME, "canvas")
    if not canvases:
        driver.find_element(By.TAG_NAME, "body").click()
        return

    # A grade da planilha é, disparado, o maior canvas da página
    grade = max(canvases, key=lambda c: c.size["width"] * c.size["height"])
    grade.click()


def texto_seguro_para_celula(valor: str) -> str:
    # Prepara o texto para não ser interpretado errado pelo Excel:
    #
    # 1) Se começar com =, +, -, @ ou tab, o Excel tenta interpretar
    #    como FÓRMULA em vez de texto (ex: uma observação "-controlar
    #    pressão" viraria erro #NAME? na planilha).
    # 2) Se for só dígitos e tiver mais de 11 caracteres, o Excel
    #    converte automaticamente para número e pode exibir em notação
    #    científica ou perder os últimos dígitos — um problema real
    #    para CNS, que tem 15 dígitos.
    #
    # A correção para os dois casos é a mesma, e é o mesmo truque que
    # qualquer pessoa usa manualmente no Excel: um apóstrofo no início
    # força a célula a ser tratada como texto puro, sem alterar o que
    # é exibido.
    if not valor:
        return valor
    if valor[0] in ("=", "+", "-", "@", "\t"):
        return "'" + valor
    if valor.isdigit() and len(valor) > 11:
        return "'" + valor
    return valor


CONTEUDO_SENTINELA = "__AUTOMACAO_SENTINELA_VAZIA__"


def ler_conteudo_celula_atual(driver: webdriver.Edge) -> str:
    # Lê o conteúdo da célula atualmente selecionada, via copiar/colar.
    #
    # Como a grade do Excel Online é desenhada em canvas (sem
    # elementos de célula individuais na página), não dá pra ler o
    # texto diretamente do HTML. Em vez disso, usamos o próprio
    # mecanismo de copiar (Ctrl+C) do Excel: colocamos um valor
    # "sentinela" na área de transferência do Windows antes, copiamos
    # a célula, e conferimos o que voltou. Se ainda for a sentinela, o
    # Ctrl+C não funcionou por algum motivo (tratamos como erro, não
    # como "vazio" — mais seguro do que arriscar sobrescrever dados).
    pyperclip.copy(CONTEUDO_SENTINELA)
    time.sleep(0.2)

    acoes = ActionChains(driver)
    acoes.key_down(Keys.CONTROL).send_keys("c").key_up(Keys.CONTROL)
    acoes.perform()
    time.sleep(0.4)

    conteudo = pyperclip.paste()
    if conteudo == CONTEUDO_SENTINELA:
        raise RuntimeError(
            "Não foi possível ler o conteúdo da célula atual (a cópia "
            "não funcionou). Confira se a janela do Excel Online está "
            "em primeiro plano e tente novamente."
        )
    return conteudo.strip()


def _mover_cursor(driver: webdriver.Edge, tecla: str) -> None:
    acoes = ActionChains(driver)
    acoes.send_keys(tecla)
    acoes.perform()
    time.sleep(0.3)


def encontrar_proxima_linha_livre(driver: webdriver.Edge, limite: int = 500) -> None:
    # Posiciona o cursor na primeira linha realmente vazia da coluna A,
    # CONFERINDO o conteúdo de cada célula candidata (via
    # ler_conteudo_celula_atual) em vez de confiar cegamente em
    # atalhos de navegação — evita tanto sobrescrever dados existentes
    # quanto ir parar longe demais por causa de formatação ou de
    # colunas com dados descontínuos.

    acoes = ActionChains(driver)
    acoes.key_down(Keys.CONTROL).send_keys(Keys.HOME).key_up(Keys.CONTROL)
    acoes.perform()
    time.sleep(1)

    # Ctrl+End como ponto de partida rápido (mais perto do fim real
    # dos dados do que descer célula por célula desde a linha 1) —
    # nunca pula para o fim absoluto da planilha, ao contrário do
    # Ctrl+Down a partir do topo.
    acoes = ActionChains(driver)
    acoes.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL)
    acoes.perform()
    time.sleep(1)
    _mover_cursor(driver, Keys.HOME)

    # Se a célula atual estiver vazia (sobra de formatação além do
    # dado real), sobe célula por célula, CONFERINDO cada uma, até
    # achar conteúdo de verdade.
    tentativas = 0
    while not ler_conteudo_celula_atual(driver) and tentativas < limite:
        _mover_cursor(driver, Keys.UP)
        tentativas += 1

    # Agora desce a partir do último dado real, conferindo cada célula,
    # até achar a primeira que estiver de fato vazia — é aí que a
    # próxima linha de paciente vai ser escrita.
    _mover_cursor(driver, Keys.DOWN)
    tentativas = 0
    while ler_conteudo_celula_atual(driver) and tentativas < limite:
        _mover_cursor(driver, Keys.DOWN)
        tentativas += 1


def preencher_pacientes(
    driver: webdriver.Edge,
    linhas_por_paciente: list[list[str]],
    colunas_por_linha: int,
    ir_para_proxima_linha_livre: bool = True,
    on_log=None,
) -> int:
    # Digita os dados de todos os pacientes na planilha aberta.
    #
    # on_log: função opcional chamada com mensagens de aviso (ex: para
    # mostrar na tela do programa). Pode ser None.

    if colunas_por_linha < 1:
        colunas_por_linha = 5

    focar_grade_planilha(driver)
    time.sleep(1)

    if ir_para_proxima_linha_livre:
        encontrar_proxima_linha_livre(driver)

    total_processados = 0
    coluna_atual = 0
    for indice, linhas in enumerate(linhas_por_paciente):
        # Garante que CADA PACIENTE comece numa linha nova da planilha.
        #
        # Bug anterior: o programa só pulava de linha quando o número
        # de células do paciente atual era um múltiplo exato de
        # "colunas_por_linha". Se um paciente tivesse, por exemplo, 4
        # linhas de texto numa planilha configurada para 5 células por
        # linha, o próximo paciente começava a ser escrito na 5ª
        # coluna da MESMA linha do paciente anterior, misturando os
        # dados dos dois. Agora, se o cursor não estiver no início de
        # uma linha (coluna_atual != 0) ao começar um novo paciente,
        # o programa força um Enter+Home antes de continuar.
        if indice > 0 and coluna_atual != 0:
            acoes = ActionChains(driver)
            acoes.send_keys(Keys.ENTER).send_keys(Keys.HOME)
            acoes.perform()
            time.sleep(0.3)
            coluna_atual = 0

        if on_log and len(linhas) != colunas_por_linha:
            on_log(
                f"[AVISO] Paciente {indice + 1} tem {len(linhas)} linha(s), "
                f"mas a planilha está configurada para {colunas_por_linha} "
                f"célula(s) por linha — confira se o dado ficou na coluna certa."
            )

        for celula in linhas:
            acoes = ActionChains(driver)
            acoes.send_keys(texto_seguro_para_celula(celula))
            acoes.perform()
            time.sleep(0.3)

            coluna_atual += 1
            acoes = ActionChains(driver)
            if coluna_atual >= colunas_por_linha:
                acoes.send_keys(Keys.ENTER).send_keys(Keys.HOME)
                coluna_atual = 0
            else:
                acoes.send_keys(Keys.TAB)
            acoes.perform()
            time.sleep(0.3)
        total_processados += 1

    return total_processados
