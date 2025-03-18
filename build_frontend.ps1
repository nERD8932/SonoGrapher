#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Installing..."
try
{
    # Activate virtual environment
    . "./.venv/Scripts/Activate.ps1"

    # Run PyInstaller
    pyinstaller -F --paths="./.venv/Lib/site-packages/" --icon="./gui/icons/favicon.ico" UI.py -n "SonoGrapher_Frontend"

    # Remove old executable if it exists
    if (Test-Path "./SonoGrapher_Frontend.exe")
    {
        Remove-Item "./SonoGrapher_Frontend.exe" -Force
    }

    # Move the new executable
    Move-Item "./dist/SonoGrapher_Frontend.exe" "./" -Force

    Write-Host "Done!"
    Read-Host "Press any key to continue..."
}
catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
    Read-Host 'Press a key to continue...'
    exit 1
}

Read-Host 'Press a key to continue...'
exit 1