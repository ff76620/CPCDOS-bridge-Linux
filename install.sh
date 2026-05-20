#!/bin/bash

echo "Installation CPCDOS Linux Layer..."

sudo apt update
while sudo fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1; do
    echo "Attente du verrou apt..."
    sleep 2
done
sudo apt install -y python3 python3-pip zenity vlc dos2unix libnotify-bin
sudo apt install -y build-essential

python3 -m pip install --break-system-packages psutil pyttsx3 notify2 watchdog pillow

mkdir -p ~/.cpc_bridge
mkdir -p ~/.cpc_engine
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/applications
mkdir -p ~/.cpc_outbox
mkdir -p ~/.cpc_inbox

cp bridge/cpcdos_bridge.py ~/.cpc_bridge/
cp engine/cpc_engine.py ~/.cpc_engine/
cp engine/cpcdos_helper.c ~/.cpc_engine/
cp engine/cpcdos_helper ~/.cpc_engine/
cp bin/cpc_engine_launcher.sh ~/.local/bin/
cp bin/launch_cpc_engine.sh ~/.local/bin/
cp bin/run-cpc ~/.local/bin/
cp desktop/run-cpc.desktop ~/.local/share/applications/
cp desktop/cpcdos-toggle.desktop ~/.local/share/applications/

gcc ~/.cpc_engine/cpcdos_helper.c -o ~/.cpc_engine/cpcdos_helper

chmod +x ~/.cpc_bridge/cpcdos_bridge.py
chmod +x ~/.cpc_engine/cpc_engine.py
chmod +x ~/.cpc_engine/cpcdos_helper.c
chmod +x ~/.cpc_engine/cpcdos_helper
chmod +x ~/.local/bin/run-cpc
chmod +x ~/.local/bin/cpc_engine_launcher.sh
chmod +x ~/.local/bin/launch_cpc_engine.sh

dos2unix ~/.cpc_bridge/cpcdos_bridge.py
dos2unix ~/.cpc_engine/cpc_engine.py
dos2unix ~/.cpc_engine/cpcdos_helper.c
dos2unix ~/.local/bin/run-cpc
dos2unix ~/.local/bin/cpc_engine_launcher.sh
dos2unix ~/.local/bin/launch_cpc_engine.sh

xdg-mime default run-cpc.desktop text/x-cpc
update-desktop-database ~/.local/share/applications

pkill -f cpcdos_bridge.py 2>/dev/null

nohup python3 ~/.cpc_engine/cpc_engine.py >/dev/null 2>&1 &
nohup python3 ~/.cpc_bridge/cpcdos_bridge.py >/dev/null 2>&1 &

echo "Installation terminée."
echo "CPCDOS Linux Layer actif."
