@echo off

winget install --id Microsoft.VisualStudioCode -e --silent --accept-package-agreements --accept-source-agreements

if %errorlevel% equ 0 (
    echo.
    echo [SUCESSO] Visual Studio Code instalado com sucesso!
) else (
    echo.
    echo [ERRO] Falha na instalacao. Verifique se o Winget esta disponivel no seu sistema.
)

pause