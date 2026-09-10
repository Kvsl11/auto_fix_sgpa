@echo off
setlocal

REM =====================================
REM AUTO-FICHA-OPE - INICIALIZADOR
REM =====================================

REM Vai para a pasta onde o BAT está
cd /d "%~dp0"

REM Caminhos principais
set "BASE_DIR=%~dp0"
set "PYTHON_EXE=%BASE_DIR%Python313\python.exe"
set "UPDATER=%BASE_DIR%updater.py"

REM =====================================
REM VERIFICACOES
REM =====================================

if not exist "%PYTHON_EXE%" (
    echo.
    echo [ERRO] Python interno nao encontrado:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

if not exist "%UPDATER%" (
    echo.
    echo [ERRO] updater.py nao encontrado:
    echo %UPDATER%
    pause
    exit /b 1
)

REM =====================================
REM EXECUCAO
REM =====================================

start "" "%PYTHON_EXE%" "%UPDATER%"

exit /b 0