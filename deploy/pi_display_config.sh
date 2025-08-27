#!/bin/bash

# Climate Chamber HMI - Display Configuration for Raspberry Pi
# Minimal configuration assuming display is already working

echo "🖥️ Configuring application display settings..."

# Configure auto-login to desktop (optional)
echo "👤 Setting up auto-login to desktop..."
sudo raspi-config nonint do_boot_behaviour B4

# Disable screen blanking
echo "💡 Disabling screen blanking..."
sudo bash -c 'cat >> /home/pi/.xsessionrc << EOF
xset s off
xset -dpms
xset s noblank
EOF'

# Create desktop entry
echo "🖥️ Creating desktop shortcut..."
mkdir -p /home/pi/Desktop
cat > /home/pi/Desktop/climate-hmi.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Climate Chamber HMI
Comment=Climate Chamber Monitoring System
Exec=/home/pi/climate-hmi/start_hmi.sh
Icon=/home/pi/climate-hmi/icon.png
Terminal=false
Categories=Application;
EOF

chmod +x /home/pi/Desktop/climate-hmi.desktop

echo "✅ Display configuration complete!"
echo "🔄 Reboot required for display changes to take effect."