#!/bin/sh
set -e

echo "  ____                     ____                 _"
echo " / ___|  ___  _ __   ___  / ___|_ __ __ _ _ __ | |__   ___ _ __"
echo " \___ \ / _ \| '_ \ / _ \| |  _| '__/ _  | '_ \| '_ \ / _ \ '__|"
echo "  ___) | (_) | | | | (_) | |_| | | | (_| | |_) | | | |  __/ |"
echo " |____/ \___/|_| |_|\___/ \____|_|  \__,_| .__/|_| |_|\___|_|"
echo "                                         |_|"

echo ""
echo ""
echo "Installing..."
echo ""
echo ""
. "./.venv/bin/activate"
pyinstaller -F --paths=./.venv/Lib/site-packages/ --icon=./gui/icons/favicon.ico UI.py -n "SonoGrapher_Frontend" --noconsole
if [ -d "./SonoGrapher_Frontend" ]; then
    rm -rf "./SonoGrapher_Frontend"
fi
mv "./dist/SonoGrapher_Frontend" "./"
echo ""
echo ""
echo "Done!"
echo ""
echo ""
read -r "Press a key to continue..."