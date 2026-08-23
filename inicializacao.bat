@echo off
title Automacao de Atendimento - Gestantes
echo ============================================
echo Verificando instalacao do Python...
echo ============================================

set "PYTHON_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :python_encontrado
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py"
    goto :python_encontrado
)

for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
        goto :python_encontrado
    )
)

echo [X] Python nao foi encontrado no sistema.
echo.
echo Baixando o instalador oficial do Python 3.13...

set "PYTHON_URL=https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe"
set "INSTALLER=%temp%\python_installer.exe"

curl -L -o "%INSTALLER%" "%PYTHON_URL%"

if not exist "%INSTALLER%" (
    echo [ERRO] Falha ao baixar o instalador. Verifique a conexao com a internet.
    goto :fim
)

echo.
echo Instalando o Python em segundo plano...
"%INSTALLER%" /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del /f /q "%INSTALLER%" >nul 2>&1

echo.
echo [OK] Instalacao do Python concluida!

for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD=%%D\python.exe"
    )
)

if not defined PYTHON_CMD (
    echo [AVISO] O Python foi instalado, mas e necessario reiniciar o computador ou o terminal.
    goto :fim
)

:python_encontrado
echo [OK] Utilizando o interpretador: %PYTHON_CMD%
%PYTHON_CMD% --version

echo.
echo [1/4] Instalando bibliotecas necessarias (selenium)...
%PYTHON_CMD% -m pip install -r requirements.txt --quiet

echo.
echo [2/4] Definindo caminhos de diretorio...
set "ORIGEM=%userprofile%\Desktop\atendimento_rodada"

REM Caminho unico: o instalador ja cuida de rodar a partir da pasta correta
set "DESTINO=%~dp0"

if not exist "%ORIGEM%" mkdir "%ORIGEM%"

echo.
echo [3/4] Verificando pacientes na pasta de atendimento...
dir /b "%ORIGEM%\*.txt" >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Nenhum arquivo .txt encontrado em "%ORIGEM%".
    echo Coloque os pacientes la antes de iniciar, se ainda nao colocou.
)

echo.
echo [4/4] Executando o programa...
cd /d "%DESTINO%"

if exist "main.py" (
    %PYTHON_CMD% main.py
) else (
    echo [ERRO] O arquivo main.py nao foi encontrado em:
    echo %DESTINO%
)

echo.
echo ============================================
echo EXECUCAO FINALIZADA!
echo ============================================

:fim
echo.
pause
