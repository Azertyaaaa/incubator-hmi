#!/bin/bash

# Climate Chamber HMI - Service Debug Script
# Use this to troubleshoot service startup issues

echo "🔍 Debugging Climate HMI Service..."

USERNAME=$(whoami)
PROJECT_DIR="/home/$USERNAME/climate-hmi"

echo "📁 Checking project directory..."
if [ -d "$PROJECT_DIR" ]; then
    echo "✅ Project directory exists: $PROJECT_DIR"
else
    echo "❌ Project directory missing: $PROJECT_DIR"
    exit 1
fi

echo "🐍 Checking Python environment..."
if [ -d "$PROJECT_DIR/.venv" ]; then
    echo "✅ Virtual environment exists"
    cd $PROJECT_DIR
    source .venv/bin/activate
    echo "📦 Installed packages:"
    pip list | grep -E "(customtkinter|matplotlib|pandas|pyserial)"
else
    echo "❌ Virtual environment missing"
fi

echo "📄 Checking main application file..."
if [ -f "$PROJECT_DIR/main.py" ]; then
    echo "✅ main.py exists"
elif [ -f "$PROJECT_DIR/main_new.py" ]; then
    echo "⚠️  Found main_new.py but service expects main.py"
    echo "   Consider renaming: mv main_new.py main.py"
else
    echo "❌ No main application file found"
fi

echo "🔧 Checking startup script..."
if [ -f "$PROJECT_DIR/start_hmi.sh" ]; then
    echo "✅ Startup script exists"
    echo "📋 Script contents:"
    cat $PROJECT_DIR/start_hmi.sh
else
    echo "❌ Startup script missing"
fi

echo "⚙️ Checking systemd service..."
if [ -f "/etc/systemd/system/climate-hmi.service" ]; then
    echo "✅ Service file exists"
    echo "📊 Service status:"
    sudo systemctl status climate-hmi --no-pager
    
    echo "📋 Service logs (last 20 lines):"
    journalctl -u climate-hmi --no-pager -n 20
else
    echo "❌ Service file missing"
fi

echo "🖥️ Checking display environment..."
echo "DISPLAY variable: $DISPLAY"
echo "X11 processes:"
ps aux | grep -E "(X|Xorg|lightdm)" | grep -v grep

echo "🔌 Checking serial ports..."
echo "Available serial ports:"
ls /dev/ttyACM* /dev/ttyUSB* 2>/dev/null || echo "No serial ports found"

echo "👤 Checking user permissions..."
echo "User groups: $(groups)"
if groups | grep -q dialout; then
    echo "✅ User in dialout group"
else
    echo "❌ User not in dialout group"
    echo "   Fix with: sudo usermod -a -G dialout $USER && sudo reboot"
fi

echo ""
echo "🧪 Manual test commands:"
echo "1. Test app manually:"
echo "   cd $PROJECT_DIR && source .venv/bin/activate && python3 main.py"
echo ""
echo "2. Test with display:"
echo "   DISPLAY=:0 cd $PROJECT_DIR && source .venv/bin/activate && python3 main.py"
echo ""
echo "3. Restart service:"
echo "   sudo systemctl restart climate-hmi"