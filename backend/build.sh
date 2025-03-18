#!/bin/sh
set -e
echo "Installing..."
. "../.venv/bin/activate"
pyinstaller --paths="../.venv/lib/site-packages/" --icon="../gui/icons/favicon.ico" app.py -n "SonoGrapher_Backend" -D --noconfirm
if [ -d "../SonoGrapher_Backend/" ]; then
    rm -rf "../SonoGrapher_Backend/"
fi
mv "./dist/SonoGrapher_Backend/" "../"
mkdir -p "../SonoGrapher_Backend/backend/logs/"
mkdir -p "../SonoGrapher_Backend/backend/uploaded/"
cp "./app.py" "../SonoGrapher_Backend/"
cp "./database.py" "../SonoGrapher_Backend/"
cp "./SonoGrapherTemplate.docx" "../SonoGrapher_Backend/backend/"
cp "./system_prompt.txt" "../SonoGrapher_Backend/backend/"
echo 'Brhyd7MpfC' > "../SonoGrapher_Backend/backend/rootUserToken.txt"
echo "Done!"
read -r "Press any key to continue..."
