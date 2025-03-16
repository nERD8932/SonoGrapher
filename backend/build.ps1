Write-Host 'Installing...'

pyinstaller --paths="..\.venv\Lib\site-packages\" --icon="..\gui\icons\favicon.ico" app.py -n "SonoGrapher Backend v1.0" -D --optimize 2 --noconfirm
Move-Item -Path "./dist/SonoGrapher Backend v1.0/" -Destination "../" -Force

New-Item -ItemType Directory -Force -Path "../SonoGrapher Backend v1.0/backend/logs/"
New-Item -ItemType Directory -Force -Path "../SonoGrapher Backend v1.0/backend/uploaded/"

Copy-Item -Path "./app.py" -Destination "../SonoGrapher Backend v1.0/" -Force
Copy-Item -Path "./database.py" -Destination "../SonoGrapher Backend v1.0/" -Force
Copy-Item -Path "./SonoGrapherTemplate.docx" -Destination "../SonoGrapher Backend v1.0/backend/" -Force
Copy-Item -Path "./system_prompt.txt" -Destination "../SonoGrapher Backend v1.0/backend/" -Force

Set-Content -Path "../SonoGrapher Backend v1.0/backend/rootUserToken.txt" -Value 'Brhyd7MpfC'

Write-Host 'Done!'