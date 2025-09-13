<#
Run Game Script (Windows PowerShell)
Launches the Snatchernauts framework using the RENPY_SDK environment variable.

Usage examples:
  powershell -ExecutionPolicy Bypass -File scripts/run-game.ps1 --lint
  powershell -ExecutionPolicy Bypass -File scripts/run-game.ps1 --debug
  powershell -ExecutionPolicy Bypass -File scripts/run-game.ps1 --compile

Environment:
  $env:RENPY_SDK  Path to Ren'Py SDK (defaults to $env:USERPROFILE\renpy-8.4.1-sdk)
#>

param()

$ErrorActionPreference = 'Stop'

function Show-Help {
    Write-Host "Run Game Script - Snatchernauts Framework"
    Write-Host ""
    Write-Host "Usage: scripts\\run-game.ps1 [--lint] [--debug] [--compile] [--help]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --lint       Run lint check only (does not start game)"
    Write-Host "  --debug      Enable debug output when launching the game"
    Write-Host "  --compile    Force recompilation before launching the game"
    Write-Host "  --help       Show this help message"
    Write-Host ""
    Write-Host "Environment Variables:"
    Write-Host "  RENPY_SDK   Path to Ren'Py SDK (default: %USERPROFILE%\\renpy-8.4.1-sdk)"
    Write-Host "               Current: $($env:RENPY_SDK)"
}

# Parse arguments (expect GNU-style switches like --lint)
$DebugFlag = $false
$LintOnly = $false
$CompileFirst = $false

foreach ($a in $args) {
    switch ($a) {
        '--debug'   { $DebugFlag = $true }
        '--lint'    { $LintOnly = $true }
        '--compile' { $CompileFirst = $true }
        '--help'    { Show-Help; exit 0 }
        default     { Write-Error "Unknown option: $a`nUse --help for usage." }
    }
}

# Resolve SDK path and Ren'Py executable
$sdk = if ([string]::IsNullOrWhiteSpace($env:RENPY_SDK)) { Join-Path $env:USERPROFILE 'renpy-8.4.1-sdk' } else { $env:RENPY_SDK }
$renpyExe = Join-Path $sdk 'renpy.exe'

if (-not (Test-Path -Path $sdk -PathType Container)) {
    Write-Error "ERROR: RENPY_SDK directory not found: $sdk`nSet RENPY_SDK to your Ren'Py 8.4.x SDK directory."
}
if (-not (Test-Path -Path $renpyExe -PathType Leaf)) {
    Write-Error "ERROR: renpy.exe not found in: $sdk`nEnsure you installed the Windows Ren'Py SDK and that RENPY_SDK points to it."
}

function Invoke-Renpy {
    param([string[]]$RenpyArgs)
    & $renpyExe '.' @RenpyArgs
    return $LASTEXITCODE
}

Write-Host "Starting Snatchernauts Framework..."
Write-Host "Using Ren'Py SDK: $sdk" 
Write-Host "Project directory: $(Get-Location)"

if ($LintOnly) {
    Write-Host "Running lint check..."
    $code = Invoke-Renpy @('lint')
    if ($code -ne 0) {
        # Fallback to --lint if the SDK expects option style
        $code = Invoke-Renpy @('--lint')
    }
    if ($code -ne 0) { exit $code }
    Write-Host "Lint check completed."
    exit 0
}

if ($CompileFirst) {
    Write-Host "Compiling game..."
    $code = Invoke-Renpy @('--compile')
    if ($code -ne 0) {
        # Fallback to subcommand style
        $code = Invoke-Renpy @('compile')
    }
    if ($code -ne 0) { exit $code }
    Write-Host "Compilation completed."
}

if ($DebugFlag) {
    Write-Host "Debug mode enabled"
    $code = Invoke-Renpy @('--debug')
} else {
    $code = Invoke-Renpy @()
}

exit $code

