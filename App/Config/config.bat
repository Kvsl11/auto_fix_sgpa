@echo off
title Configurador AUTO-FICHA-OPE

setlocal

REM =====================================
REM IR PARA A PASTA DO BAT
REM =====================================

cd /d "%~dp0"

REM =====================================
REM DEFINIR PASTA RAIZ
REM =====================================

set "ROOT=%~dp0.."
set "PYTHON=%ROOT%\Python313\python.exe"
set "REQ=%ROOT%\requirements.txt"
set "LOG=%ROOT%\instalacao.log"

echo.
echo =====================================
echo CONFIGURADOR AUTO-FICHA-OPE
echo =====================================
echo.

REM =====================================
REM VERIFICAR PYTHON
REM =====================================

if not exist "%PYTHON%" (
  echo [ERRO] Python nao encontrado.
  echo.
  echo Caminho esperado:
  echo %PYTHON%
  echo.
  pause
  exit /b 1
)

echo [OK] Python encontrado.
echo.

REM =====================================
REM VERIFICAR PIP
REM =====================================

echo Verificando pip...

"%PYTHON%" -m pip --version >nul 2>&1

if errorlevel 1 (
  echo Instalando pip...
  "%PYTHON%" -m ensurepip --upgrade
)

echo.
echo Atualizando ferramentas...
echo.

"%PYTHON%" -m pip install --upgrade pip setuptools wheel

if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao atualizar ferramentas.
  pause
  exit /b 1
)

REM =====================================
REM GERAR REQUIREMENTS
REM =====================================

echo.
echo =====================================
echo GERANDO REQUIREMENTS
echo =====================================
echo.

"%PYTHON%" "%ROOT%\Config\gerar_requirements.py"

if errorlevel 1 (
  echo.
  echo [ERRO] Falha ao gerar requirements.
  pause
  exit /b 1
)

echo.
echo =====================================
echo REQUIREMENTS GERADO
echo =====================================
echo.

type "%REQ%"

echo.
echo =====================================
echo INSTALANDO DEPENDENCIAS
echo =====================================
echo.

"%PYTHON%" -m pip install -r "%REQ%" > "%LOG%" 2>&1

if errorlevel 1 (
  echo.
  echo [ERRO] Falha na instalacao.
  echo.
  echo Consulte:
  echo %LOG%
  echo.
  pause
  exit /b 1
)

echo.
echo =====================================
echo VALIDANDO AMBIENTE
echo =====================================
echo.

"%PYTHON%" -c "import requests"
if errorlevel 1 goto erro

"%PYTHON%" -c "import selenium"
if errorlevel 1 goto erro

"%PYTHON%" -c "import customtkinter"
if errorlevel 1 goto erro

"%PYTHON%" -c "import undetected_chromedriver"
if errorlevel 1 goto erro

echo.
echo =====================================
echo SUCESSO
echo =====================================
echo.

echo Dependencias instaladas com sucesso.
echo.

"%PYTHON%" --version

echo.
pause
exit /b 0

:erro

echo.
echo =====================================
echo ERRO
echo =====================================
echo.

echo Alguma dependencia nao foi instalada corretamente.
echo.

echo Consulte:
echo %LOG%

echo.
pause
exit /b 1
