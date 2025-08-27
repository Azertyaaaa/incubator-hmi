#!/bin/bash

# Climate Chamber HMI - Raspberry Pi Setup Script
# Run this script on your Raspberry Pi to set up the environment

echo "🔧 Setting up Climate Chamber HMI on Raspberry Pi..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and system dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3 python3-pip python3-venv git

# Install system packages for GUI and serial
sudo apt install -y python3-tk python3-dev build-essential
sudo apt install -y libatlas-base-dev libopenjp2-7-dev libtiff5-dev
sudo apt install -y python3-matplotlib python3-pandas

# Install CustomTkinter system dependencies
sudo apt install -y python3-pil python3-pil.imagetk

# Create project directory
PROJECT_DIR="/home/pi/climate-hmi"
echo "📁 Creating project directory at $PROJECT_DIR..."
mkdir -p $PROJECT_DIR
cd $PROJECT_DIR

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
echo "📚 Installing Python packages..."
pip install customtkinter==5.2.0
pip install pyserial==3.5
pip install matplotlib==3.7.2
pip install pandas==2.0.3
pip install Pillow

# Add user to dialout group for serial access
echo "🔌 Adding user to dialout group for serial port access..."
sudo usermod -a -G dialout pi

echo "✅ Base setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your project files to $PROJECT_DIR"
echo "2. Run the display configuration script: ./deploy/pi_display_config.sh"
echo "3. Set up auto-start service: ./deploy/pi_service_setup.sh"
echo ""
echo "🔄 Please reboot your Pi after setup: sudo reboot"