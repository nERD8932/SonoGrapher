#!/bin/sh
echo 'Installing...'
. ../.venv/bin/activate
pyinstaller --paths=..\.venv\Lib\site-packages\ --icon=..\gui\icons\favicon.ico app.py -n "SonoGrapher Backend v1.0" -D --optimize 2 --noconfirm
mv "./dist/SonoGrapher Backend v1.0/" "../"
mkdir "../SonoGrapher Backend v1.0/backend/logs/"
mkdir "../SonoGrapher Backend v1.0/backend/uploaded/"
cp "./app.py" "../SonoGrapher Backend v1.0/"
cp "./database.py" "../SonoGrapher Backend v1.0/"
cp "./SonoGrapherTemplate.docx" "../SonoGrapher Backend v1.0/backend/"
cp "./system_prompt.txt" "../SonoGrapher Backend v1.0/backend/"
echo 'Brhyd7MpfC' > "../SonoGrapher Backend v1.0/backend/rootUserToken.txt"
echo 'Done!'