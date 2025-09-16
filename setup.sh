#!/bin/bash

# Setup Script untuk Sistem Tethered Shooting AI Enhanced
# =======================================================

set -e  # Exit on any error

echo "🎯 SETUP SISTEM TETHERED SHOOTING AI ENHANCED"
echo "=============================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function untuk print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "Jangan jalankan script ini sebagai root!"
   exit 1
fi

# Detect OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/debian_version ]; then
        OS="debian"
        print_info "Detected: Debian/Ubuntu Linux"
    elif [ -f /etc/redhat-release ]; then
        OS="redhat"
        print_info "Detected: RedHat/CentOS/Fedora Linux"
    else
        OS="linux"
        print_info "Detected: Generic Linux"
    fi
else
    print_error "OS tidak didukung. Script ini hanya untuk Linux."
    exit 1
fi

# Function untuk install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    if [[ "$OS" == "debian" ]]; then
        sudo apt-get update
        sudo apt-get install -y \
            python3 \
            python3-pip \
            python3-dev \
            python3-venv \
            gphoto2 \
            libgphoto2-dev \
            libgphoto2-port12 \
            build-essential \
            cmake \
            pkg-config \
            libjpeg-dev \
            libpng-dev \
            libtiff-dev \
            libopencv-dev \
            python3-opencv \
            git \
            curl \
            wget
            
    elif [[ "$OS" == "redhat" ]]; then
        sudo yum update -y
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y \
            python3 \
            python3-pip \
            python3-devel \
            gphoto2 \
            libgphoto2-devel \
            cmake \
            pkg-config \
            libjpeg-turbo-devel \
            libpng-devel \
            libtiff-devel \
            opencv-devel \
            python3-opencv \
            git \
            curl \
            wget
    fi
    
    print_status "System dependencies installed"
}

# Function untuk setup Python virtual environment
setup_python_env() {
    print_info "Setting up Python virtual environment..."
    
    # Create virtual environment
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    print_info "Installing Python packages..."
    pip install -r requirements.txt
    
    print_status "Python environment setup complete"
}

# Function untuk create directories
create_directories() {
    print_info "Creating necessary directories..."
    
    python3 -c "
from config import Config
Config.create_directories()
print('✅ All directories created')
"
    
    print_status "Directories created"
}

# Function untuk download OpenCV models
download_models() {
    print_info "Downloading OpenCV Haar Cascade models..."
    
    mkdir -p models
    
    # Download Haar Cascade untuk face detection
    CASCADE_URL="https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    
    if [ ! -f "models/haarcascade_frontalface_default.xml" ]; then
        wget -O models/haarcascade_frontalface_default.xml "$CASCADE_URL"
        print_status "Haar Cascade model downloaded"
    else
        print_info "Haar Cascade model already exists"
    fi
    
    # Create alternative cascade file name
    cp models/haarcascade_frontalface_default.xml models/haarcascade_frontalface_alt.xml
}

# Function untuk create sample assets
create_sample_assets() {
    print_info "Creating sample assets..."
    
    # Create sample LUT file (identity LUT)
    python3 -c "
import numpy as np
from pathlib import Path

# Create identity LUT (no color change)
lut_size = 33
lut_data = []

for b in range(lut_size):
    for g in range(lut_size):
        for r in range(lut_size):
            # Normalize to 0-1 range
            r_val = r / (lut_size - 1)
            g_val = g / (lut_size - 1)
            b_val = b / (lut_size - 1)
            lut_data.append(f'{r_val:.6f} {g_val:.6f} {b_val:.6f}')

# Write .cube file
with open('presets/my_preset.cube', 'w') as f:
    f.write('# Sample Identity LUT\\n')
    f.write('TITLE \"Identity LUT\"\\n')
    f.write('LUT_3D_SIZE 33\\n')
    f.write('DOMAIN_MIN 0.0 0.0 0.0\\n')
    f.write('DOMAIN_MAX 1.0 1.0 1.0\\n')
    f.write('\\n')
    for line in lut_data:
        f.write(line + '\\n')

print('✅ Sample LUT created: presets/my_preset.cube')
"
    
    # Create sample watermark (simple text)
    python3 -c "
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Create sample watermark
width, height = 400, 100
img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Try to use a font, fallback to default if not available
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 36)
except:
    font = ImageFont.load_default()

# Draw text
text = 'HafiPortrait'
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]

x = (width - text_width) // 2
y = (height - text_height) // 2

# White text with some transparency
draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)

# Add subtle shadow
draw.text((x+2, y+2), text, fill=(0, 0, 0, 100), font=font)
draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)

img.save('watermarks/my_logo.png')
print('✅ Sample watermark created: watermarks/my_logo.png')
"
    
    print_status "Sample assets created"
}

# Function untuk test kamera
test_camera() {
    print_info "Testing camera connection..."
    
    if command -v gphoto2 &> /dev/null; then
        echo "Detecting cameras..."
        gphoto2 --auto-detect || print_warning "Tidak ada kamera terdeteksi. Pastikan kamera terhubung."
        
        # Test gphoto2 version
        echo "gPhoto2 version:"
        gphoto2 --version | head -1
        
        print_info "Camera test complete. Connect your camera and run the main script."
    else
        print_error "gphoto2 tidak ditemukan!"
        exit 1
    fi
}

# Function untuk create startup script
create_startup_script() {
    print_info "Creating startup script..."
    
    cat > start.sh << 'EOF'
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
EOF
    
    chmod +x start.sh
    print_status "Startup script created (start.sh)"
}

# Function untuk create service file
create_service_file() {
    print_info "Creating systemd service file..."
    
    CURRENT_DIR=$(pwd)
    USER=$(whoami)
    
    cat > tethered-shooting.service << EOF
[Unit]
Description=Tethered Shooting AI Enhanced System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment=PATH=$CURRENT_DIR/venv/bin
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/auto_capture_ai_enhanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    print_info "Service file created: tethered-shooting.service"
    print_info "To install as system service:"
    print_info "  sudo cp tethered-shooting.service /etc/systemd/system/"
    print_info "  sudo systemctl enable tethered-shooting"
    print_info "  sudo systemctl start tethered-shooting"
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    
    # Convert version to comparable format (e.g., 3.12 -> 312, 3.7 -> 37)
    version_numeric=$(echo "$python_version" | sed 's/\.//g')
    required_numeric=37
    
    if [[ $version_numeric -ge $required_numeric ]]; then
        print_status "Python version: $python_version"
    else
        print_error "Python 3.7+ required. Current version: $python_version"
        exit 1
    fi
    
    # Run setup steps
    install_system_deps
    echo
    
    setup_python_env
    echo
    
    create_directories
    echo
    
    download_models
    echo
    
    create_sample_assets
    echo
    
    test_camera
    echo
    
    create_startup_script
    echo
    
    create_service_file
    echo
    
    print_status "Setup complete! 🎉"
    echo
    echo "Next steps:"
    echo "1. Edit config.py jika perlu adjust settings"
    echo "2. Replace sample assets dengan file asli Anda:"
    echo "   - presets/my_preset.cube (file LUT Anda)"
    echo "   - watermarks/my_logo.png (logo watermark Anda)"
    echo "3. Connect kamera DSLR ke USB"
    echo "4. Run: ./start.sh"
    echo
    print_info "Sistem siap digunakan!"
}

# Run main setup
main