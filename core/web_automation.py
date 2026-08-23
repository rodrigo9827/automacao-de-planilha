import time
from dataclasses import dataclass

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


def preencher_pacientes(
    driver: webdriver.Edge,
    linhas_por_paciente: list[list[str]],
    colunas_por_linha: int,
    ir_para_proxima_linha_livre: bool = True,
) -> int:
    # Digita os dados de todos os pacientes na planilha aberta.

    
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
