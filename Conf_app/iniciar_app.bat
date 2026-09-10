@echo off
setlocal

REM =====================================
REM AUTO-FICHA-OPE - INICIALIZADOR
REM =====================================

cd /d "%~dp0"

set "BASE_DIR=%~dp0"
set "PYTHON_EXE=%BASE_DIR%Python313\pythonw.exe"
set "UPDATER=%BASE_DIR%updater.py"

REM =====================================
REM VERIFICACOES
REM =====================================

if not exist "%PYTHON_EXE%" (
  powershell -Command ^
  "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') > $null; [System.Windows.Forms.MessageBox]::Show('Python interno nao encontrado.','Erro')"
  exit /b 1
)

if not exist "%UPDATER%" (
  powershell -Command ^
  "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') > $null; [System.Windows.Forms.MessageBox]::Show('updater.py nao encontrado.','Erro')"
  exit /b 1
)

REM =====================================
REM EXECUCAO SILENCIOSA
REM =====================================

start "" "%PYTHON_EXE%" "%UPDATER%"

exit
