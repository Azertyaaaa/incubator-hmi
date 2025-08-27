#!/bin/bash

# Climate Chamber HMI - Service Setup for Auto-Start
# Creates systemd service to auto-start the HMI application

echo "🚀 Setting up auto-start service for Climate HMI..."

PROJECT_DIR="/home/pi/climate-hmi"

# Create systemd service file
echo "📝 Creating systemd service..."
sudo bash -c "cat > /etc/systemd/system/climate-hmi.service << EOF
[Unit]
Description=Climate Chamber HMI
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=$PROJECT_DIR
Environment=DISPLAY=:0
ExecStartPre=/bin/sleep 10
ExecStart=$PROJECT_DIR/start_hmi.sh
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF"

# Create start script
echo "📄 Creating startup script..."
cat > $PROJECT_DIR/start_hmi.sh << 'EOF'
#!/bin/bash

# Climate Chamber HMI Startup Script
cd /home/pi/climate-hmi

# Activate virtual environment
source .venv/bin/activate

# Set display
export DISPLAY=:0

# Start the HMI application
python3 main_new.py
EOF

chmod +x $PROJECT_DIR/start_hmi.sh

# Enable and start service
echo "⚡ Enabling service..."
sudo systemctl daemon-reload
sudo systemctl enable climate-hmi.service

echo "✅ Service setup complete!"
echo ""
echo "Service commands:"
echo "• Start: sudo systemctl start climate-hmi"
echo "• Stop: sudo systemctl stop climate-hmi"
echo "• Status: sudo systemctl status climate-hmi"
echo "• Logs: journalctl -u climate-hmi -f"
echo ""
echo "The HMI will now start automatically on boot!"