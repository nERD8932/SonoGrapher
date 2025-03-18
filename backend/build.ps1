#!/usr/bin/env pwsh
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host 'Installing...'

try{
    . "../.venv/Scripts/activate.ps1"

    pyinstaller --paths="../.venv/Lib/site-packages/" --icon="../gui/icons/favicon.ico" app.py -n "SonoGrapher_Backend" -D --noconfirm

    if (Test-Path "../SonoGrapher_Backend/") {
        Remove-Item "../SonoGrapher_Backend/" -Recurse
    }
    Move-Item -Path "./dist/SonoGrapher_Backend" -Destination "../" -Force

    New-Item -ItemType Directory -Force -Path "../SonoGrapher_Backend/backend/logs/"
    New-Item -ItemType Directory -Force -Path "../SonoGrapher_Backend/backend/uploaded/"

    Copy-Item -Path "./app.py" -Destination "../SonoGrapher_Backend/" -Force
    Copy-Item -Path "./database.py" -Destination "../SonoGrapher_Backend/" -Force
    Copy-Item -Path "./SonoGrapherTemplate.docx" -Destination "../SonoGrapher_Backend/backend/" -Force
    Copy-Item -Path "./system_prompt.txt" -Destination "../SonoGrapher_Backend/backend/" -Force

    Set-Content -Path "../SonoGrapher_Backend/backend/rootUserToken.txt" -Value 'Brhyd7MpfC'

    Write-Host 'Done!'

}
catch {
    Write-Host "An error occurred: $_" -ForegroundColor Red
    Read-Host 'Press a key to continue...'
    exit 1
}

Read-Host 'Press a key to continue...'
exit 1