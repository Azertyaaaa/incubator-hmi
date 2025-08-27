# Climate Chamber HMI - Build and Deploy

.PHONY: help build-package deploy-git deploy-package test clean

help:
	@echo "🏭 Climate Chamber HMI - Build & Deploy"
	@echo ""
	@echo "Build Options:"
	@echo "  build-package    Create standalone executable package"
	@echo "  test-local       Test the application locally"
	@echo ""
	@echo "Deploy Options:"
	@echo "  deploy-git       Git-based deployment (recommended for development)"
	@echo "  deploy-package   Package-based deployment (recommended for production)"
	@echo ""
	@echo "Utilities:"
	@echo "  clean           Clean build artifacts"
	@echo "  debug-service   Debug service issues on Pi"

# Build standalone package
build-package:
	@echo "🚀 Building standalone package..."
	python3 build_package.py

# Test application locally
test-local:
	@echo "🧪 Testing application locally..."
	python3 -m venv .test-venv
	.test-venv/bin/pip install -r requirements.txt
	.test-venv/bin/python main.py

# Git-based deployment instructions
deploy-git:
	@echo "📋 Git-based Deployment Instructions:"
	@echo ""
	@echo "1. Push your code to a Git repository"
	@echo "2. On your Pi, run:"
	@echo "   git clone <your-repo-url> climate-hmi"
	@echo "   cd climate-hmi"
	@echo "   chmod +x deploy/*.sh"
	@echo "   ./deploy/pi_setup.sh"
	@echo "   ./deploy/pi_display_config.sh"
	@echo "   ./deploy/pi_service_setup.sh"
	@echo "   sudo reboot"
	@echo ""
	@echo "✅ Advantages: Easy updates with 'git pull'"

# Package-based deployment instructions
deploy-package: build-package
	@echo "📋 Package-based Deployment Instructions:"
	@echo ""
	@echo "1. Transfer climate-hmi-package.tar.gz to your Pi"
	@echo "2. On your Pi, run:"
	@echo "   tar -xzf climate-hmi-package.tar.gz"
	@echo "   cd climate-hmi-package"
	@echo "   ./install.sh"
	@echo "   sudo reboot"
	@echo ""
	@echo "✅ Advantages: No Python dependencies needed on Pi"

# Debug service on Pi
debug-service:
	@echo "🔍 Run this on your Pi to debug service issues:"
	@echo "   ./deploy/debug_service.sh"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf dist/ build/ *.spec __pycache__/
	rm -rf climate-hmi-package/ climate-hmi-package.tar.gz
	rm -rf .test-venv/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} +