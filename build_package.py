#!/usr/bin/env python3
"""
Climate Chamber HMI - Packaging Script
Creates a standalone executable for easier Pi deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('ui/*.py', 'ui'),
        ('core/*.py', 'core'), 
        ('config/*.py', 'config'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'matplotlib.backends.backend_tkagg',
        'PIL._tkinter_finder',
        'serial.tools.list_ports',
        'pandas',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='climate-hmi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
'''
    
    with open('climate-hmi.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def build_package():
    """Build the standalone package"""
    print("🚀 Building Climate Chamber HMI Package...")
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ Please run this script from the project root directory")
        return False
    
    # Install PyInstaller if not present
    print("📦 Installing PyInstaller...")
    if not run_command("pip install pyinstaller", "Installing PyInstaller"):
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build the package
    if not run_command("pyinstaller climate-hmi.spec --clean", "Building package"):
        return False
    
    # Create deployment package
    if os.path.exists('dist/climate-hmi'):
        print("📁 Creating deployment package...")
        
        # Create package directory
        package_dir = 'climate-hmi-package'
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        os.makedirs(package_dir)
        
        # Copy executable
        shutil.copytree('dist/climate-hmi', f'{package_dir}/bin')
        
        # Copy deployment scripts
        shutil.copytree('deploy', f'{package_dir}/deploy')
        
        # Create package-specific scripts
        create_package_scripts(package_dir)
        
        # Create archive
        if run_command(f"tar -czf climate-hmi-package.tar.gz {package_dir}", "Creating archive"):
            print(f"✅ Package created: climate-hmi-package.tar.gz")
            print(f"📋 Deploy on Pi with:")
            print(f"   tar -xzf climate-hmi-package.tar.gz")
            print(f"   cd climate-hmi-package")
            print(f"   ./install.sh")
        
        return True
    
    return False

def create_package_scripts(package_dir):
    """Create package-specific installation scripts"""
    
    # Install script
    install_script = f'''\
#!/bin/bash
# Climate Chamber HMI - Packaged Installation Script

echo "🚀 Installing Climate Chamber HMI (Packaged Version)..."

USERNAME=$(whoami)
INSTALL_DIR="/home/$USERNAME/climate-hmi"

# Create installation directory
mkdir -p $INSTALL_DIR
cd $INSTALL_DIR

# Copy executable
cp -r ../bin/* ./
chmod +x climate-hmi

# Install system dependencies only
sudo apt update
sudo apt install -y python3-tk libatlas-base-dev

# Add user to dialout group
sudo usermod -a -G dialout $USERNAME

# Create startup script
cat > start_hmi.sh << EOF
#!/bin/bash
cd /home/$USERNAME/climate-hmi
export DISPLAY=:0
./climate-hmi
EOF

chmod +x start_hmi.sh

# Create systemd service
sudo bash -c "cat > /etc/systemd/system/climate-hmi.service << EOF
[Unit]
Description=Climate Chamber HMI (Packaged)
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=$USERNAME
Group=$USERNAME
WorkingDirectory=$INSTALL_DIR
Environment=DISPLAY=:0
ExecStartPre=/bin/sleep 10
ExecStart=$INSTALL_DIR/start_hmi.sh
Restart=always
RestartSec=5

[Install]
WantedBy=graphical-session.target
EOF"

# Enable service
sudo systemctl daemon-reload
sudo systemctl enable climate-hmi.service

echo "✅ Installation complete!"
echo "🔄 Reboot and the HMI will start automatically"
echo ""
echo "Service commands:"
echo "• Status: sudo systemctl status climate-hmi"
echo "• Logs: journalctl -u climate-hmi -f"
echo "• Manual start: ./start_hmi.sh"
'''
    
    with open(f'{package_dir}/install.sh', 'w') as f:
        f.write(install_script)
    os.chmod(f'{package_dir}/install.sh', 0o755)
    
    # README for package
    readme = '''\
# Climate Chamber HMI - Packaged Deployment

This is a self-contained package with no Python dependencies needed on the Pi.

## Installation

1. Extract the package:
   ```bash
   tar -xzf climate-hmi-package.tar.gz
   cd climate-hmi-package
   ```

2. Run the installer:
   ```bash
   ./install.sh
   ```

3. Reboot:
   ```bash
   sudo reboot
   ```

## What's Included

- Pre-compiled executable (no Python virtual env needed)
- Automatic system service setup
- Minimal system dependencies
- Ready-to-run package

## Manual Testing

Before installation, you can test the app manually:
```bash
cd climate-hmi-package/bin
./climate-hmi
```

The packaged version includes all Python dependencies and should run without additional setup.
'''
    
    with open(f'{package_dir}/README.md', 'w') as f:
        f.write(readme)

if __name__ == "__main__":
    if build_package():
        print("\n🎉 Package build successful!")
    else:
        print("\n❌ Package build failed!")
        sys.exit(1)