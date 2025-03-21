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
Write-Host 'Installing...'
Write-Host ""
Write-Host ""
try {
    ollama --version
}
catch {
    Write-Host "Ollama not found, installing..."
    winget install --id=Ollama.Ollama  -e
}

try{
    . "../.venv/Scripts/activate.ps1"

    pyinstaller --paths="../.venv/Lib/site-packages/" --icon="../gui/icons/favicon.ico" app.py -n "SonoGrapher_Backend" -D --noconfirm --recursive-copy-metadata "openai-whisper" --add-data "../.venv/Lib/site-packages/whisper;whisper/"

    if (Test-Path "../SonoGrapher_Backend/") {
        Remove-Item "../SonoGrapher_Backend/" -Recurse
    }
    Move-Item -Path "./dist/SonoGrapher_Backend" -Destination "../" -Force

    New-Item -ItemType Directory -Force -Path "../SonoGrapher_Backend/backend/logs/"
    New-Item -ItemType Directory -Force -Path "../SonoGrapher_Backend/backend/uploaded/"
    New-Item -ItemType Directory -Force -Path "../SonoGrapher_Backend/backend/generated/"

    Copy-Item -Path "./app.py" -Destination "../SonoGrapher_Backend/" -Force
    Copy-Item -Path "./database.py" -Destination "../SonoGrapher_Backend/" -Force
    Copy-Item -Path "./SonoGrapherTemplate.docx" -Destination "../SonoGrapher_Backend/backend/" -Force
    Copy-Item -Path "./system_prompt_json.txt" -Destination "../SonoGrapher_Backend/backend/" -Force
    Copy-Item -Path "./system_prompt_html.txt" -Destination "../SonoGrapher_Backend/backend/" -Force
    Copy-Item -Path "./system_prompt_markdown.txt" -Destination "../SonoGrapher_Backend/backend/" -Force
    Copy-Item -Path "../webpage" -Destination "../SonoGrapher_Backend/webpage/" -Force -Recurse
    Copy-Item -Path "../.venv/Lib/site-packages/pypandoc/files/" -Destination "../SonoGrapher_Backend/backend/pypandoc/" -Force -Recurse


    Set-Content -Path "../SonoGrapher_Backend/backend/rootUserToken.txt" -Value 'Brhyd7MpfC' -NoNewline

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