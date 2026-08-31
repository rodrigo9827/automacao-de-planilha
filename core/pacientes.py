import glob
import os
import shutil
from datetime import datetime


def listar_arquivos_txt(pasta: str) -> list[str]:
    #Retorna a lista de arquivos .txt da pasta, em ordem alfabética.
    padrao = os.path.join(pasta, "*.txt")
    return sorted(glob.glob(padrao))


def ler_paciente(caminho_arquivo: str) -> list[str]:
    #Lê um arquivo de paciente e devolve a lista de linhas
    #
    # Tenta UTF-8 primeiro (padrão do programa ao salvar). Se o arquivo
    # foi criado ou editado por outro programa que salva em ANSI/
    # Windows-1252 (comum em editores mais antigos), cai para essa
    # codificação em vez de travar com UnicodeDecodeError — sem isso,
    # um único arquivo com acentuação salvo "errado" travava a rodada
    # inteira, mesmo depois do login já ter sido feito no navegador.
    try:
        with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
            return [linha.rstrip("\n").rstrip("\r") for linha in arquivo]
    except UnicodeDecodeError:
        with open(caminho_arquivo, "r", encoding="cp1252") as arquivo:
            return [linha.rstrip("\n").rstrip("\r") for linha in arquivo]

def mover_processados(arquivos: list[str], pasta_origem: str) -> str:
    #Move os arquivos já usados para uma subpasta processados/AAAA-MM-DD/.
    hoje = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta_destino = os.path.join(pasta_origem, "processados", hoje)
    os.makedirs(pasta_destino, exist_ok=True)

    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        shutil.move(caminho, os.path.join(pasta_destino, nome_arquivo))

    return pasta_destino

def garantir_pasta(pasta: str) -> None:
    #Cria a pasta de atendimento se ela ainda não existir.
    os.makedirs(pasta, exist_ok=True)


def salvar_paciente(pasta: str, nome_arquivo_base: str, linhas: list[str]) -> str:
    #Salva as linhas de um paciente num novo arquivo .txt na pasta.
    garantir_pasta(pasta)
    caminho = os.path.join(pasta, f"{nome_arquivo_base}.txt")
    contador = 1
    while os.path.exists(caminho):
        contador += 1
        caminho = os.path.join(pasta, f"{nome_arquivo_base}_{contador}.txt")

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))

    return caminho
