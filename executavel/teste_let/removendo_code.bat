@echo off
title Desinstalacao do Visual Studio Code

winget uninstall --id Microsoft.VisualStudioCode -e --silent

if %errorlevel% equ 0 (
    echo.
    echo [SUCESSO] Visual Studio Code desinstalado com sucesso!
) else (
    echo.
    echo [ERRO] Falha na desinstalacao via Winget.
)

pause