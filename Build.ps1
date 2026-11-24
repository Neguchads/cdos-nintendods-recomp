param(
    [ValidateSet("Fast","Dev","Test","Release","Rebuild")][string]$Profile = "Fast",
    [ValidateRange(1,128)][int]$Jobs = [Math]::Max(1,[Environment]::ProcessorCount - 2),
    [string]$Version
)
$ErrorActionPreference = "Stop"
Push-Location $PSScriptRoot
try {
    $python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (!(Test-Path $python)) {
        python -m venv .venv
        if ($LASTEXITCODE) { throw "venv creation failed" }
    }
    $env:Path = "$(Join-Path $PSScriptRoot '.venv\Scripts');$env:Path"
    & $python -c "import PIL,cmake,ninja"
    if ($LASTEXITCODE) {
        & $python -m pip install cmake ninja pillow
        if ($LASTEXITCODE) { throw "Python dependency setup failed" }
    }
    & $python tools/setup_toolchains.py
    if ($LASTEXITCODE) { throw "Toolchain setup failed" }
    $arguments = @("tools/rbs.py","--profile",$Profile.ToLowerInvariant(),"--jobs",$Jobs)
    if ($Version) { $arguments += @("--version",$Version) }
    & $python @arguments
    if ($LASTEXITCODE) { throw "RBS build failed ($LASTEXITCODE)" }
} finally { Pop-Location }
