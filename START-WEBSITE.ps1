$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host 'Node.js 20 or newer is required. Install Node.js, then run this script again.' -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}
$nodeVersion = (node -p "process.versions.node").Split('.')[0]
if ([int]$nodeVersion -lt 20) {
    Write-Host 'Please upgrade to Node.js 20 or newer.' -ForegroundColor Red
    Read-Host 'Press Enter to exit'
    exit 1
}
if (-not (Test-Path 'node_modules/express')) {
    Write-Host 'Installing Express and EJS dependencies...' -ForegroundColor Cyan
    npm install
    if ($LASTEXITCODE -ne 0) { throw 'npm install failed. Check the connection and retry.' }
}
Write-Host 'Starting Fruit Atlas at http://localhost:3000 ...' -ForegroundColor Green
Start-Process 'http://localhost:3000'
npm start
