# 🚀 Raspberry Pi Deployment Guide

Complete guide to deploy your Climate Chamber HMI on a Raspberry Pi with 1280x720 touchscreen.

## 📋 Prerequisites

- **Raspberry Pi 4** (recommended) or Pi 3B+
- **Touchscreen already configured and working**
- **MicroSD card** (32GB+ recommended)
- **Raspberry Pi OS** (Desktop version)
- **4 USB serial connections** for your Picos

## 🔧 Step 1: Initial Pi Setup

1. **Flash Raspberry Pi OS** to SD card using [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
2. **Enable SSH** (optional): Add empty `ssh` file to boot partition
3. **Boot your Pi** and complete initial setup
4. **Connect to internet** (WiFi or Ethernet)

## 📦 Step 2: Transfer Project Files

### Option A: Using Git (Recommended)
```bash
cd /home/pi
git clone <your-repository-url> climate-hmi
cd climate-hmi
```

### Option B: Manual Copy
```bash
# From your Windows machine, use SCP or USB drive
scp -r incubator-hmi/ pi@<pi-ip-address>:/home/pi/climate-hmi/
```

## 🛠️ Step 3: Run Setup Scripts

```bash
cd /home/pi/climate-hmi

# Make scripts executable
chmod +x deploy/*.sh

# 1. Install system dependencies and Python environment
./deploy/pi_setup.sh

# 2. Configure application settings (auto-login, screen blanking)
./deploy/pi_display_config.sh

# 3. Set up auto-start service
./deploy/pi_service_setup.sh

# 4. Reboot to apply all changes
sudo reboot
```

## 🔌 Step 4: Connect Hardware

1. **Connect USB cables** from your 4 Picos to Pi USB ports
2. **Identify serial ports**: Run `ls /dev/ttyACM*` or `ls /dev/ttyUSB*`
3. **Configure ports** in the HMI Settings tab:
   - Zone 1: /dev/ttyACM0 (or first available)
   - Zone 2: /dev/ttyACM1
   - Zone 3: /dev/ttyACM2 
   - Zone 4: /dev/ttyACM3

## ⚙️ Step 5: Configure Application

1. **Launch HMI**: The app should start automatically after reboot
2. **Open Settings tab** in the application
3. **Set serial ports** for each zone
4. **Configure calibration** values for mass sensors
5. **Test connections** using the "Apply Serial Settings" button

## 📱 Touch Optimization

The HMI is pre-configured for touch:
- **Large buttons** (50px+ height)
- **Clear fonts** (14-18px)
- **Fullscreen mode** by default
- **No keyboard required**

## 🔍 Troubleshooting

### Service Management
```bash
# Check service status
sudo systemctl status climate-hmi

# View logs
journalctl -u climate-hmi -f

# Restart service
sudo systemctl restart climate-hmi

# Stop service
sudo systemctl stop climate-hmi
```

### Serial Port Issues
```bash
# List available ports
ls /dev/tty*

# Check permissions
sudo usermod -a -G dialout pi
sudo reboot

# Test serial connection
sudo minicom -D /dev/ttyACM0 -b 115200
```

### Display Issues
```bash
# Test current resolution
xrandr

# If touchscreen needs recalibration
xinput_calibrator
```

### Python Issues
```bash
# Activate virtual environment
cd /home/pi/climate-hmi
source .venv/bin/activate

# Test import
python3 -c "import customtkinter; print('CustomTkinter OK')"

# Reinstall packages if needed
pip install --upgrade customtkinter matplotlib pandas pyserial
```

## 🔄 Updates

To update the application:
```bash
cd /home/pi/climate-hmi
git pull  # If using git
sudo systemctl restart climate-hmi
```

## 📊 Data Storage

- **Log files**: `/home/pi/climate-hmi/data/logs/`
- **Configuration**: `/home/pi/climate-hmi/config/hmi_config.json`
- **Backup important data** before updates!

## 🆘 Support

### Common Serial Device Names on Pi:
- **Pico/Arduino**: `/dev/ttyACM0`, `/dev/ttyACM1`, etc.
- **USB-Serial adapters**: `/dev/ttyUSB0`, `/dev/ttyUSB1`, etc.

### Performance Tips:
- **Close unused applications** for better performance
- **Use Class 10 SD card** for faster I/O
- **Monitor CPU temperature**: `vcgencmd measure_temp`

### Recovery:
If the HMI doesn't start:
```bash
# Stop auto-start
sudo systemctl disable climate-hmi

# Run manually to see errors
cd /home/pi/climate-hmi
source .venv/bin/activate
python3 main_new.py
```

## ✅ Success!

Your Climate Chamber HMI should now be running on your Pi with:
- ✅ 4-zone monitoring
- ✅ Touch-optimized interface
- ✅ Auto-start on boot
- ✅ Real-time charts
- ✅ Data logging
- ✅ USB export capability (when implemented)

The system will automatically reconnect to serial devices and recover from errors!