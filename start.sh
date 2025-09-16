#!/bin/bash

# Startup script untuk Tethered Shooting System
# =============================================

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${GREEN}🚀 Starting Tethered Shooting AI Enhanced System${NC}"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment tidak ditemukan. Jalankan setup.sh dulu."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if camera connected
echo "🔍 Checking camera connection..."
if ! gphoto2 --auto-detect | grep -q "usb:"; then
    echo "⚠️  Warning: Tidak ada kamera terdeteksi."
    echo "   Pastikan kamera terhubung dan dalam mode yang tepat."
    echo
fi

# Start the main application
echo "🎯 Starting main application..."
python3 auto_capture_ai_enhanced.py

echo "👋 Application stopped."
