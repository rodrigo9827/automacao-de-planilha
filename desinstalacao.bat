@echo off
title Remocao do Python e Pasta de Automacao
echo ========================================
echo Iniciando processo de remocao...
echo ========================================
echo.

REM Remove a propria pasta do programa (onde este .bat esta salvo),
REM em vez de um caminho fixo — assim funciona independente de onde
REM a pasta foi extraida.
set "FOLDER_PATH=%~dp0"

echo [AVISO] Isto vai apagar a pasta do programa:
echo %FOLDER_PATH%
echo.
set /p CONFIRMA="Confirma a remocao? (S/N): "
if /i not "%CONFIRMA%"=="S" (
    echo Operacao cancelada.
    goto :fim
)

echo [1/2] Removendo a pasta do programa...
cd /d "%~dp0.."
rmdir /s /q "%FOLDER_PATH%"
if %errorlevel% equ 0 (
    echo [SUCESSO] Pasta removida com sucesso.
) else (
    echo [ERRO] Nao foi possivel remover a pasta. Verifique as permissoes.
)

echo.
echo ========================================
echo Desinstalando o Python (opcional)...
echo ========================================
set /p CONFIRMA_PY="Deseja tambem desinstalar o Python do computador? (S/N): "
if /i "%CONFIRMA_PY%"=="S" (
    winget uninstall --id Python.Python.3 --silent >nul 2>&1
    echo [OK] Comando de desinstalacao do Python executado.
) else (
    echo [INFO] Python mantido no sistema.
)

echo.
echo ========================================
echo Concluido!
echo ========================================

:fim
echo.
pause
