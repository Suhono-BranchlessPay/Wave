$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
. (Join-Path $PSScriptRoot "load_dotenv.ps1")
$env:PYTHONPATH = "src"
& (Join-Path $root ".venv\Scripts\python.exe") -m wave_bp_collector.app
