#!/bin/sh
echo 'Installing...'
pyinstaller --paths=..\.venv\Lib\site-packages\ --icon=..\gui\icons\favicon.ico app.py -n "SonoGrapher Backend v1.0" -D --optimize 2 --noconfirm
mkdir "../SonoGrapher Backend v1.0/backend/logs/"
mkdir "../SonoGrapher Backend v1.0/backend/uploaded/"
mv "./dist/SonoGrapher Backend v1.0/" "../SonoGrapher Backend v1.0/"
cp "./app.py" "../SonoGrapher Backend v1.0/"
cp "./database.py" "../SonoGrapher Backend v1.0/"
cp "./SonoGrapherTemplate.docx" "../SonoGrapher Backend v1.0/backend/"
cp "./system_prompt.txt" "../SonoGrapher Backend v1.0/backend/"
echo 'Brhyd7MpfC' > "../SonoGrapher Backend v1.0/backend/rootUserToken.txt"
echo 'Done!'