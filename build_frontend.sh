#!/bin/sh
set -e
echo "Installing..."
. "./.venv/bin/activate"
pyinstaller -F --paths=./.venv/Lib/site-packages/ --icon=./gui/icons/favicon.ico UI.py -n "SonoGrapher_Frontend"
if [ -d "./SonoGrapher_Frontend" ]; then
    rm -rf "./SonoGrapher_Frontend"
fi
mv "./dist/SonoGrapher_Frontend" "./"
echo "Done!"
read -r "Press any key to continue..."