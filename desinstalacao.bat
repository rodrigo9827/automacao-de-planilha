@echo off
title Remocao - Automacao de Atendimento
echo ========================================
echo Iniciando processo de remocao...
echo ========================================
echo.

set "PASTA_ALVO=%userprofile%\Downloads\automacao-de-planilha-main\automacao-de-planilha-main"

if "%PASTA_ALVO%"=="%userprofile%" goto :fim
if "%PASTA_ALVO%"=="%userprofile%\Desktop" goto :fim

set /p CONFIRMA_PY="Deseja desinstalar o Python do computador? (S/N): "
if /i "%CONFIRMA_PY%"=="S" (
    echo.
    echo Baixando assistente para remover o Python...
    curl -L -o "%temp%\python_installer.exe" "https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe" >nul 2>&1
    
    if exist "%temp%\python_installer.exe" (
        echo Desinstalando o Python em segundo plano...
        "%temp%\python_installer.exe" /uninstall /quiet
        del /f /q "%temp%\python_installer.exe" >nul 2>&1
        echo Python 3.13.2 desinstalado com sucesso.
    ) else (
        echo [ERRO] Falha ao baixar o assistente de desinstalacao.
    )
) else (
    echo Python mantido no sistema.
)

echo.
echo Isto vai apagar a pasta:
echo %PASTA_ALVO%
set /p CONFIRMA="Confirma? (S/N): "
if /i not "%CONFIRMA%"=="S" goto :fim

if exist "%PASTA_ALVO%" (
    rmdir /s /q "%PASTA_ALVO%"
    echo Pasta removida com sucesso.
) else (
    echo A pasta alvo nao foi encontrada para remocao.
)

:fim
echo.
pause