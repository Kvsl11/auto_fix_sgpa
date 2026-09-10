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
set "MAIN=%ROOT%\main.py"
set "REQ=%ROOT%\requirements.txt"
set "LOG=%ROOT%\instalacao.log"

echo.
echo =====================================
echo CONFIGURADOR AUTO-FICHA-OPE
echo =====================================
echo.

echo Pasta Raiz:
echo %ROOT%
echo.

echo Python:
echo %PYTHON%
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
REM GARANTIR PIP
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

REM =====================================
REM CRIAR REQUIREMENTS
REM =====================================

echo.
echo Criando requirements.txt...
echo.

(
echo requests
echo selenium
echo undetected-chromedriver
echo customtkinter
echo certifi
echo openpyxl
echo pillow
) > "%REQ%"

echo [OK] requirements.txt criado.
echo.

REM =====================================
REM INSTALAR PACOTES
REM =====================================

echo Instalando dependencias...
echo Aguarde...
echo.

"%PYTHON%" -m pip install -r "%REQ%" > "%LOG%" 2>&1

if errorlevel 1 (
    echo.
    echo [ERRO] Falha durante a instalacao.
    echo.
    echo Verifique:
    echo %LOG%
    echo.
    pause
    exit /b 1
)

REM =====================================
REM TESTAR MODULOS
REM =====================================

echo.
echo Testando modulos...
echo.

"%PYTHON%" -c "import requests"
if errorlevel 1 goto erro

"%PYTHON%" -c "import selenium"
if errorlevel 1 goto erro

"%PYTHON%" -c "import customtkinter"
if errorlevel 1 goto erro

"%PYTHON%" -c "import certifi"
if errorlevel 1 goto erro

"%PYTHON%" -c "import openpyxl"
if errorlevel 1 goto erro

"%PYTHON%" -c "import PIL"
if errorlevel 1 goto erro

"%PYTHON%" -c "import undetected_chromedriver"
if errorlevel 1 goto erro

echo.
echo =====================================
echo SUCESSO
echo =====================================
echo.
echo Todas as dependencias foram instaladas.
echo.

echo Python:
"%PYTHON%" --version

echo.
echo Teste final:
"%PYTHON%" -c "import undetected_chromedriver as uc; print('OK')"

echo.
pause
exit /b 0

:erro

echo.
echo =====================================
echo ERRO
echo =====================================
echo.
echo Alguma dependencia nao foi instalada.
echo.
echo Consulte:
echo %LOG%
echo.
pause
exit /b 1