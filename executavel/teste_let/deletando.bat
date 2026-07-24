@echo off

echo ===============================
echo [-] - Deletando arquivos .txt  
echo ===============================
echo.
del /q /f "%~dp0*.txt"

echo =========================================
echo [+] - Arquivos .txt deletados com sucesso
echo =========================================
echo.

pause