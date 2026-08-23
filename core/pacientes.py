"""
core/pacientes.py

Responsável só por lidar com os arquivos de pacientes (.txt):
- localizar os arquivos na pasta de atendimento
- mover para uma subpasta "processados" depois que a automação
  terminar com sucesso (isso resolve o problema do README antigo,
  que dizia que os arquivos precisavam ser apagados manualmente)

Mantido separado do resto para ficar fácil de testar e de entender:
cada função faz uma coisa só.
"""

from __future__ import annotations

import glob
import os
import shutil
from datetime import datetime


def listar_arquivos_txt(pasta: str) -> list[str]:
    """Retorna a lista de arquivos .txt da pasta, em ordem alfabética.

    Ordem alfabética é importante: garante que o programa sempre
    processa os pacientes na mesma sequência, o que facilita conferir
    depois se algo ficou faltando.
    """
    padrao = os.path.join(pasta, "*.txt")
    return sorted(glob.glob(padrao))


def ler_paciente(caminho_arquivo: str) -> list[str]:
    """Lê um arquivo de paciente e devolve a lista de linhas (sem \\n).

    Linhas em branco (parágrafo vazio) são mantidas de propósito:
    é assim que o sistema original deixa uma célula vazia quando
    necessário (conforme o README explicava).
    """
    with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
        return [linha.rstrip("\n").rstrip("\r") for linha in arquivo]


def mover_processados(arquivos: list[str], pasta_origem: str) -> str:
    """Move os arquivos já usados para uma subpasta 'processados/AAAA-MM-DD/'.

    Não apaga nada — só tira da frente, para não reprocessar o mesmo
    paciente duas vezes, mas mantendo o histórico caso precise conferir
    depois. Retorna o caminho da subpasta criada.
    """
    hoje = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta_destino = os.path.join(pasta_origem, "processados", hoje)
    os.makedirs(pasta_destino, exist_ok=True)

    for caminho in arquivos:
        nome_arquivo = os.path.basename(caminho)
        shutil.move(caminho, os.path.join(pasta_destino, nome_arquivo))

    return pasta_destino


def garantir_pasta(pasta: str) -> None:
    """Cria a pasta de atendimento se ela ainda não existir."""
    os.makedirs(pasta, exist_ok=True)


def salvar_paciente(pasta: str, nome_arquivo_base: str, linhas: list[str]) -> str:
    """Salva as linhas de um paciente num novo arquivo .txt na pasta.

    Se já existir um arquivo com o mesmo nome (ex: duas pacientes com
    nome parecido no mesmo dia), acrescenta um sufixo numérico em vez
    de sobrescrever o arquivo existente.
    """
    garantir_pasta(pasta)

    caminho = os.path.join(pasta, f"{nome_arquivo_base}.txt")
    contador = 1
    while os.path.exists(caminho):
        contador += 1
        caminho = os.path.join(pasta, f"{nome_arquivo_base}_{contador}.txt")

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas))

    return caminho
