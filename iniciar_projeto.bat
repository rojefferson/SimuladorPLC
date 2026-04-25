@echo off
setlocal

:: ======================================================================
:: SCRIPT DE INICIALIZACAO COMPLETA - SIMULADOR PLC + INFRAESTRUTURA
:: ======================================================================

echo.
echo ==========================================================
echo   Iniciando ecossistema do Simulador PLC...
echo ==========================================================
echo.

:: 1. InfluxDB
echo [1/4] Iniciando InfluxDB...
start "InfluxDB" /min cmd /c "influxd"
if %errorlevel% neq 0 (
    echo [AVISO] Nao foi possivel iniciar o InfluxDB.
) else (
    echo [OK] InfluxDB iniciado.
)

:: 2. Node-RED
echo [2/4] Iniciando Node-RED...
:: Verifica se as dependencias estao instaladas
if not exist "%~dp0nodered\node_modules" (
    echo Instalando dependencias do Node-RED (isso pode demorar na primeira vez)...
    pushd "%~dp0nodered"
    call npm install --no-audit --no-fund
    popd
)
:: Inicia o Node-RED apontando para o arquivo de flows correto
start "Node-RED" /min cmd /c "node-red -u ./nodered ./nodered/flows/flows.json"
if %errorlevel% neq 0 (
    echo [AVISO] Nao foi possivel iniciar o Node-RED.
) else (
    echo [OK] Node-RED iniciado.
)

:: 3. Mosquitto (MQTT)
echo [3/4] Iniciando Mosquitto (MQTT)...
start "Mosquitto" /min cmd /c "mosquitto"
if %errorlevel% neq 0 (
    echo [AVISO] Nao foi possivel iniciar o Mosquitto.
) else (
    echo [OK] Mosquitto iniciado.
)

:: 4. Aplicacao Python (Simulador PLC)
echo [4/4] Iniciando Simulador PLC...
cd /d "%~dp0industrial-plc-simulator"
if exist .venv (
    start "Simulador PLC" .venv\Scripts\python.exe -m app.main
    echo [OK] Aplicacao Python iniciada.
) else (
    echo [ERRO] Ambiente virtual (.venv) nao encontrado.
)

echo.
echo ==========================================================
echo   Processos iniciados! Enderecos disponiveis:
echo ==========================================================
echo  -^> Simulador PLC (Modbus): 127.0.0.1:5020
echo  -^> Node-RED (Interface):   http://localhost:1880
echo  -^> InfluxDB (API/UI):     http://localhost:8086
echo  -^> Mosquitto (MQTT):      127.0.0.1:1883
echo ==========================================================
echo.
pause
