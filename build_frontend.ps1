#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host @"
  ____                     ____                 _
 / ___|  ___  _ __   ___  / ___|_ __ __ _ _ __ | |__   ___ _ __
 \___ \ / _ \| '_ \ / _ \| |  _| '__/ _` | '_ \| '_ \ / _ \ '__|
  ___) | (_) | | | | (_) | |_| | | | (_| | |_) | | | |  __/ |
 |____/ \___/|_| |_|\___/ \____|_|  \__,_| .__/|_| |_|\___|_|
                                         |_|
"@

Write-Host ""
Write-Host ""
Write-Host "Installing..."
Write-Host ""
Write-Host ""
try
{
    # Activate virtual environment
    . "./.venv/Scripts/Activate.ps1"

    # Run PyInstaller
    pyinstaller -F --paths="./.venv/Lib/site-packages/" --icon="./gui/icons/favicon.ico" UI.py -n "SonoGrapher_Frontend" --noconsole

    # Remove old executable if it exists
    if (Test-Path "./SonoGrapher_Frontend.exe")
    {
        Remove-Item "./SonoGrapher_Frontend.exe" -Force
    }

    # Move the new executable
    Move-Item "./dist/SonoGrapher_Frontend.exe" "./" -Force

    Write-Host ""
    Write-Host ""
    Write-Host 'Done!'
    Write-Host ""
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host ""
    Write-Host "An error occurred: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host ""
    Read-Host 'Press a key to continue...'
    exit 1
}

Read-Host 'Press a key to continue...'
exit 1