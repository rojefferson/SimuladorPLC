@echo off
cd /d "%~dp0"

echo [1/3] Verificando Ambiente Virtual...
if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
)

echo [2/3] Instalando/Verificando Dependencias...
echo (Isso pode demorar alguns minutos na primeira vez devido ao tamanho do PySide6)
.venv\Scripts\python.exe -m pip install PySide6 pymodbus

echo [3/3] Iniciando Simulador...
.venv\Scripts\python.exe -m app.main

if errorlevel 1 (
    echo.
    echo Ocorreu um erro ao iniciar a aplicacao.
    pause
)
