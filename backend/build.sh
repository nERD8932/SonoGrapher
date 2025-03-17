#!/bin/bash
set -e
echo "Installing..."
source "../.venv/bin/activate"
pyinstaller --paths="../.venv/lib/site-packages/" --icon="../gui/icons/favicon.ico" app.py -n "SonoGrapher Backend v1.0" -D --noconfirm
if [ -d "../SonoGrapher Backend v1.0/" ]; then
    rm -rf "../SonoGrapher Backend v1.0/"
fi
mv "./dist/SonoGrapher Backend v1.0/" "../"
mkdir -p "../SonoGrapher Backend v1.0/backend/logs/"
mkdir -p "../SonoGrapher Backend v1.0/backend/uploaded/"
cp "./app.py" "../SonoGrapher Backend v1.0/"
cp "./database.py" "../SonoGrapher Backend v1.0/"
cp "./SonoGrapherTemplate.docx" "../SonoGrapher Backend v1.0/backend/"
cp "./system_prompt.txt" "../SonoGrapher Backend v1.0/backend/"
echo 'Brhyd7MpfC' > "../SonoGrapher Backend v1.0/backend/rootUserToken.txt"
echo "Done!"
read -p "Press any key to continue..."
