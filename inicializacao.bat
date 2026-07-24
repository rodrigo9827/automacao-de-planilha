@echo off
title Script de Automacao com Python

echo ============================================
echo   Verificando instalacao do Python...
echo ============================================

:: Tenta localizar o executavel do Python no sistema ou nos caminhos padroes de instalacao
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

:: Procura pelo executavel direto na pasta AppData (caso a variavel PATH ainda nao tenha atualizado)
for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD="%%D\python.exe""
        goto :python_encontrado
    )
)

:: Se nao encontrou, baixa e instala
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
echo ============================================
echo [OK] Instalacao do Python concluida
echo ============================================

:: Busca novamente o caminho do executavel instalado recente
for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON_CMD="%%D\python.exe""
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
echo [1/4] Instalando bibliotecas externas (pyautogui)...
%PYTHON_CMD% -m pip install pyautogui --quiet

echo.
echo [2/4] Definindo caminhos de diretorio...
set "ORIGEM=%userprofile%\Desktop\atendimento_rodada"

set "DESTINO1=%userprofile%\Downloads\automacao-de-planilha-main\automacao-de-planilha-main\executavel\teste_let"
set "DESTINO2=%userprofile%\Downloads\automacao-de-planilha-main\automacao-de-planilha-main\executavel\teste_let"

if exist "%DESTINO1%" (
    set "DESTINO=%DESTINO1%"
) else if exist "%DESTINO2%" (
    set "DESTINO=%DESTINO2%"
) else (
    echo [AVISO] Nao foi possivel localizar a pasta 'executavel' em Downloads.
    echo Verifique se a pasta foi descompactada corretamente.
    goto :fim
)

if not exist "%ORIGEM%" mkdir "%ORIGEM%"

echo.
echo [3/4] Movendo arquivos TXT...
move /y "%ORIGEM%\*.txt" "%DESTINO%\" >nul 2>&1

echo.
echo [4/4] Executando o script Python...
cd /d "%DESTINO%"

if exist "tratando_texto.py" (
    %PYTHON_CMD% tratando_texto.py
) else (
    echo [ERRO] O arquivo tratando_texto.py nao foi encontrado em:
    echo %DESTINO%
)

echo.
echo ============================================
echo   EXECUCAO FINALIZADA!
echo ============================================

:fim
echo.

pause