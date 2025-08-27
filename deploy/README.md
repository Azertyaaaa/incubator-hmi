# 🚀 Raspberry Pi Deployment Guide

Simple Git-based deployment for your Climate Chamber HMI on Raspberry Pi.

## 📋 Prerequisites

- **Raspberry Pi 4** (recommended) or Pi 3B+
- **Touchscreen already configured and working**
- **Raspberry Pi OS** (Desktop version)
- **Git repository** with your HMI project
- **User account** (script works with any username, including "admin")

## 🔧 Quick Deployment (3 Steps)

### **1. Clone Your Repository**
```bash
cd ~
git clone <your-repository-url> climate-hmi
cd climate-hmi
```

### **2. Run Setup Scripts**
```bash
# Make scripts executable
chmod +x deploy/*.sh

# Run all setup scripts
./deploy/pi_setup.sh
./deploy/pi_display_config.sh  
./deploy/pi_service_setup.sh

# Reboot to apply all changes
sudo reboot
```

### **3. Configure Hardware**
After reboot, the HMI should start automatically:
- Connect your 4 Picos via USB
- Use **Settings tab** to assign serial ports
- Configure mass calibration values
- Test connections

## 🔌 Typical Serial Port Assignments

```bash
# Check available ports
ls /dev/ttyACM*

# Usually:
Zone 1: /dev/ttyACM0
Zone 2: /dev/ttyACM1  
Zone 3: /dev/ttyACM2
Zone 4: /dev/ttyACM3
```

## ⚙️ What Gets Installed

### **System Packages**:
- Python 3 + pip + venv
- Serial communication libraries
- GUI dependencies (tkinter, PIL)
- Math libraries for matplotlib

### **Python Environment**:
- Virtual environment in `~/climate-hmi/.venv`
- CustomTkinter, PySerial, Matplotlib, Pandas
- All requirements from `requirements.txt`

### **Services**:
- Auto-start systemd service
- Screen blanking disabled
- Desktop shortcut created

## 🔄 Updates

To update your application:
```bash
cd ~/climate-hmi
git pull
sudo systemctl restart climate-hmi
```

## 🛠️ Service Management

```bash
# Check status
sudo systemctl status climate-hmi

# View logs
journalctl -u climate-hmi -f

# Restart
sudo systemctl restart climate-hmi

# Stop auto-start
sudo systemctl disable climate-hmi
```

## 🆘 Troubleshooting

### **Serial Issues**
```bash
# Check ports
ls /dev/tty*

# Test permissions
groups $USER  # Should include "dialout"

# If not in dialout group
sudo usermod -a -G dialout $USER
sudo reboot
```

### **App Won't Start**
```bash
# Run manually to see errors
cd ~/climate-hmi
source .venv/bin/activate
python3 main_new.py
```

### **Missing Dependencies**
```bash
cd ~/climate-hmi
source .venv/bin/activate
pip install -r requirements.txt
```

## 📁 File Structure

```
~/climate-hmi/
├── main_new.py              # Main application
├── requirements.txt         # Python dependencies
├── .venv/                   # Virtual environment
├── config/                  # Settings and calibration
├── core/                    # Serial and data management
├── ui/                      # Interface components
├── data/logs/              # Data logging
└── deploy/                 # Deployment scripts
```

## ✅ Success Indicators

After successful deployment:
- ✅ HMI starts automatically on boot
- ✅ Touch interface responds
- ✅ Serial ports detected in Settings
- ✅ Service shows "active (running)" status
- ✅ Desktop shortcut available

## 🔒 Security Note

The setup runs the HMI with the current user privileges (admin, pi, etc.). No root access needed for normal operation, only during setup.

Your Climate Chamber HMI is now ready for production use!