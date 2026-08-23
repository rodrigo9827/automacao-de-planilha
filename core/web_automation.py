"""
core/web_automation.py

Aqui mora a parte "navegador" da automação, usando Selenium no lugar
do pyautogui original. A diferença prática:

- pyautogui clica em coordenadas FIXAS da tela (x=500, y=500) e confia
  em time.sleep() para "esperar" a página carregar. Se a janela mover,
  a resolução mudar, ou a internet estiver mais lenta num dia, quebra.
- Selenium conversa direto com o navegador: sabemos exatamente quando
  um campo de login apareceu (WebDriverWait), conseguimos checar se o
  login deu erro, e o clique inicial na planilha é relativo ao elemento
  da página, não a um pixel fixo da tela.

Uma limitação que não muda: o Excel Online desenha a grade de células
num <canvas> (imagem), não em elementos HTML individuais. Por isso não
dá pra pedir "clique na célula B4" via seletor — depois do clique
inicial, a navegação entre células continua sendo por teclado
(Tab / Enter / Home), só que mandado pelo Selenium em vez do pyautogui.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# IDs padrão da página de login da Microsoft (login.microsoftonline.com).
# São estáveis há anos e usados em qualquer automação RPA de Office 365,
# mas se a Microsoft trocar o layout do login um dia, é AQUI que se ajusta.
ID_CAMPO_EMAIL = "i0116"
ID_BOTAO_AVANCAR = "idSIButton9"
ID_CAMPO_SENHA = "i0118"
ID_BOTAO_ENTRAR = "idSIButton9"  # mesmo id é reaproveitado na tela de senha
ID_BOTAO_MANTER_CONECTADO = "idSIButton9"  # e na tela "Continuar conectado?"

TEMPO_ESPERA_PADRAO = 20  # segundos máximos esperando cada elemento aparecer


class ErroDeLogin(Exception):
    """Erro específico para falha de autenticação (senha errada, etc.)."""


@dataclass
class ResultadoAutomacao:
    sucesso: bool
    mensagem: str
    pacientes_processados: int = 0


def iniciar_navegador() -> webdriver.Edge:
    """Abre uma janela do Edge controlada pelo Selenium.

    Não usa modo headless (invisível) de propósito: a enfermeira que
    está rodando o programa precisa ver a tela, tanto para confirmar
    visualmente que está tudo certo quanto para poder intervir na mão
    se algo sair do esperado (ex: um aviso extra de segurança).

    Como a empresa usa Edge por padrão, usamos webdriver.Edge().
    A partir do Selenium 4.6, o driver (msedgedriver) é baixado e
    gerenciado automaticamente — não precisa instalar nada à parte,
    só precisa de acesso à internet na primeira execução.
    """
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
    """Preenche e-mail e senha na tela de login da Microsoft.

    Levanta ErroDeLogin se, depois de tentar, a página ainda mostrar
    um campo de senha (sinal de que a senha foi rejeitada) — assim o
    programa avisa a enfermeira em vez de continuar digitando dados
    de paciente numa página de login que falhou.
    """
    espera = WebDriverWait(driver, TEMPO_ESPERA_PADRAO)

    campo_email = espera.until(
        EC.visibility_of_element_located((By.ID, ID_CAMPO_EMAIL))
    )
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

    # Depois do "Entrar", a Microsoft costuma perguntar
    # "Continuar conectado?". Se aparecer, clicamos "Sim".
    # Se não aparecer (ou já der erro de senha antes), seguimos.
    try:
        botao_manter = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((By.ID, ID_BOTAO_MANTER_CONECTADO))
        )
        botao_manter.click()
    except Exception:
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
    """Espera a interface do Excel Online terminar de carregar.

    Como a grade é um canvas, não dá pra esperar "a célula A1 existir".
    Em vez disso, esperamos o elemento de trabalho (workbook) da página
    aparecer, e ainda damos uma pausa extra de segurança — o Excel
    Online continua desenhando por alguns segundos depois disso.
    """
    espera = WebDriverWait(driver, timeout)
    espera.until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(4)  # margem de segurança para o canvas terminar de desenhar


def preencher_pacientes(
    driver: webdriver.Edge,
    linhas_por_paciente: list[list[str]],
    colunas_por_linha: int,
    ir_para_proxima_linha_livre: bool = True,
) -> int:
    """Digita os dados de todos os pacientes na planilha aberta.

    linhas_por_paciente: uma lista de pacientes, cada um já lido como
    lista de linhas (uma célula por linha do arquivo .txt).

    Antes de começar a digitar, verifica se já existe algum dado na
    planilha e, se existir, começa na primeira linha livre depois
    dele — nunca sobrescreve o que já foi preenchido.

    Como a grade é um canvas, não dá pra "ler" o conteúdo de uma
    célula diretamente. Por isso usamos o atalho Ctrl+End do próprio
    Excel: ele pula automaticamente para a última célula que tem
    algum dado (se a planilha estiver vazia, fica em A1/A2). Daí é só
    descer uma linha e voltar para a coluna A — garantindo uma linha
    livre tanto se já havia dado quanto se a planilha estava vazia.

    Retorna quantos pacientes foram escritos.
    """
    corpo = driver.find_element(By.TAG_NAME, "body")

    # Clica na área da planilha para garantir o foco do teclado nela
    corpo.click()
    time.sleep(1)

    if ir_para_proxima_linha_livre:
        acoes = ActionChains(driver)
        acoes.key_down(Keys.CONTROL).send_keys(Keys.END).key_up(Keys.CONTROL)
        acoes.perform()
        time.sleep(1)

        acoes = ActionChains(driver)
        acoes.send_keys(Keys.DOWN).send_keys(Keys.HOME)
        acoes.perform()
        time.sleep(0.5)

    total_processados = 0
    for linhas in linhas_por_paciente:
        coluna_atual = 0
        for celula in linhas:
            acoes = ActionChains(driver)
            acoes.send_keys(celula)
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
