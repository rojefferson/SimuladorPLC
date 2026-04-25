# Script de Inicializacao em PowerShell

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  Iniciando ecossistema do Simulador PLC..." -ForegroundColor Cyan
Write-Host "==========================================================`n"

# 1. InfluxDB
Write-Host "[1/3] Iniciando InfluxDB..." -ForegroundColor Yellow
try {
    Start-Process "influxd" -WindowStyle Minimized -ErrorAction Stop
    Write-Host "[OK] InfluxDB iniciado." -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Nao foi possivel iniciar o InfluxDB. Verifique se o binario esta no PATH." -ForegroundColor Red
}

# 2. Node-RED
Write-Host "[2/4] Iniciando Node-RED..." -ForegroundColor Yellow
$noderedPath = Join-Path $PSScriptRoot "nodered"
if (!(Test-Path (Join-Path $noderedPath "node_modules"))) {
    Write-Host "Instalando dependencias do Node-RED (isso pode demorar)..." -ForegroundColor Cyan
    Set-Location $noderedPath
    npm install --no-audit --no-fund
    Set-Location $PSScriptRoot
}
try {
    $flowPath = Join-Path $noderedPath "flows\flows.json"
    Start-Process "node-red" -ArgumentList "-u ./nodered $flowPath" -WindowStyle Minimized -ErrorAction Stop
    Write-Host "[OK] Node-RED iniciado." -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Nao foi possivel iniciar o Node-RED." -ForegroundColor Red
}

# 3. Mosquitto (MQTT)
Write-Host "[3/4] Iniciando Mosquitto (MQTT)..." -ForegroundColor Yellow
try {
    Start-Process "mosquitto" -WindowStyle Minimized -ErrorAction Stop
    Write-Host "[OK] Mosquitto iniciado." -ForegroundColor Green
} catch {
    Write-Host "[AVISO] Nao foi possivel iniciar o Mosquitto." -ForegroundColor Red
}

# 4. Aplicacao Python
Write-Host "[4/4] Iniciando Simulador PLC..." -ForegroundColor Yellow
$projectPath = Join-Path $PSScriptRoot "industrial-plc-simulator"
$venvPath = Join-Path $projectPath ".venv\Scripts\python.exe"

if (Test-Path $venvPath) {
    Set-Location $projectPath
    Start-Process ".\.venv\Scripts\python.exe" -ArgumentList "-m app.main"
    Write-Host "[OK] Aplicacao Python iniciada." -ForegroundColor Green
    Set-Location $PSScriptRoot
} else {
    Write-Host "[ERRO] Ambiente virtual nao encontrado em '$projectPath'." -ForegroundColor Red
}

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  Processos iniciados! Enderecos disponiveis:" -ForegroundColor Cyan
Write-Host "=========================================================="
Write-Host " -> Simulador PLC (Modbus): 127.0.0.1:5020" -ForegroundColor White
Write-Host " -> Node-RED (Interface):   http://localhost:1880" -ForegroundColor White
Write-Host " -> InfluxDB (API/UI):     http://localhost:8086" -ForegroundColor White
Write-Host " -> Mosquitto (MQTT):      127.0.0.1:1883" -ForegroundColor White
Write-Host "==========================================================`n"

Read-Host "Pressione Enter para sair..."
