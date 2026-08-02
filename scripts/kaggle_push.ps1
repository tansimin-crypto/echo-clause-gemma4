# Push EchoClause Kaggle notebook kernel
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$NbDir = Join-Path $Root "notebooks"

if (-not (Test-Path "$env:USERPROFILE\.kaggle\kaggle.json")) {
    Write-Error "Missing ~/.kaggle/kaggle.json — configure Kaggle API credentials first."
}

Push-Location $NbDir
try {
    kaggle kernels push -p .
    Write-Host "Kernel pushed. Monitor with: kaggle kernels status mayn/echo-clause-gemma4-demo"
} finally {
    Pop-Location
}
