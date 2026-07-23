@echo off
title Remocao do Python e Pasta de Automacao
echo ========================================
echo   Iniciando processo de remocao...
echo ========================================
echo.

:: 1. Apagar a pasta na pasta Downloads do usuario atual
set "FOLDER_PATH=%USERPROFILE%\Downloads\automacao-de-planilha-main"

if exist "%FOLDER_PATH%" (
    echo [1/2] Removendo a pasta "automacao-de-planilha-main"...
    rmdir /s /q "%FOLDER_PATH%"
    if %errorlevel% equ 0 (
        echo [SUCESSO] Pasta removida com sucesso.
    ) else (
        echo [ERRO] Nao foi possivel remover a pasta. Verifique as permissoes.
    )
) else (
    echo [INFO] A pasta "automacao-de-planilha-main" nao foi encontrada em Downloads.
)

echo.
echo ========================================
echo   Desinstalando o Python...
echo ========================================
echo.

:: 2. Tentar desinstalar via Winget (Mais eficiente se o Python foi instalado via Winget/Store)
winget uninstall --id Python.Python.3 --silent >nul 2>&1

:: Alternativa: tentar desinstalar executando o desinstalador do Python via MSICode/Registry (caso instalado via EXE padrão)
wmic product where "name like 'Python%%'" call uninstall /nointeractive >nul 2>&1

echo [2/2] Processo de desinstalacao do Python executado.
echo.
echo ========================================
echo   Concluded!
echo ========================================
echo.
pause