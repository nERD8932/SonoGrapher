#!/bin/sh
set -e
echo "  ____                     ____                 _"
echo " / ___|  ___  _ __   ___  / ___|_ __ __ _ _ __ | |__   ___ _ __"
echo " \___ \ / _ \| '_ \ / _ \| |  _| '__/ _  | '_ \| '_ \ / _ \ '__|"
echo "  ___) | (_) | | | | (_) | |_| | | | (_| | |_) | | | |  __/ |"
echo " |____/ \___/|_| |_|\___/ \____|_|  \__,_| .__/|_| |_|\___|_|"
echo "                                         |_|"

if ! ollama --version >/dev/null 2>&1; then
    echo "Ollama not found, installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi
echo ""
echo ""
echo "Installing..."
echo ""
echo ""
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
echo ""
echo ""
echo "Done!"
echo ""
echo ""
read -r "Press any key to continue..."
