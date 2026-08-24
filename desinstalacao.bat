@echo off
title Remocao - Automacao de Atendimento
echo ========================================
echo Iniciando processo de remocao...
echo ========================================
echo.

set "PASTA_ALVO=%userprofile%\Downloads\automacao-atendimento\automacao-atendimento"

if "%PASTA_ALVO%"=="%userprofile%" goto :fim
if "%PASTA_ALVO%"=="%userprofile%\Desktop" goto :fim

set /p CONFIRMA_PY="Deseja desinstalar o Python do computador? (S/N): "
if /i "%CONFIRMA_PY%"=="S" (
    winget uninstall --id Python.Python.3 --silent >nul 2>&1
    echo Python desinstalado.
) else (
    echo Python mantido no sistema.
)

echo.
echo Isto vai apagar a pasta:
echo %PASTA_ALVO%
set /p CONFIRMA="Confirma? (S/N): "
if /i not "%CONFIRMA%"=="S" goto :fim

rmdir /s /q "%PASTA_ALVO%"
echo Pasta removida.

:fim
pause