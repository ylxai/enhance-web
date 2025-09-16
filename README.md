# Sistem Tethered Shooting AI Enhanced

Sistem otomatis untuk fotografi event yang mengintegrasikan tethered shooting, AI enhancement dengan proteksi wajah, dan processing gambar profesional.

## 🎯 Fitur Utama

### 📸 Tethered Shooting Otomatis
- Kontrol kamera DSLR menggunakan gPhoto2
- Auto-download file RAW dan JPG setelah capture
- Backup otomatis ke folder terpisah
- Monitoring real-time status kamera

### 🤖 AI Enhancement dengan Proteksi Wajah
- Enhancement menggunakan Google Gemini AI
- Deteksi wajah otomatis dengan OpenCV
- Masking area wajah untuk proteksi struktur asli
- Enhancement maksimal untuk background dan objek

### 🎨 Processing Profesional
- Aplikasi LUT (.cube format) untuk color grading
- Auto-crop berdasarkan orientasi (5x7 portrait, 7x5 landscape)
- Watermarking otomatis dengan transparansi
- Output siap cetak (300 DPI)

### ⚡ Performance Optimal
- Processing paralel dengan ThreadPoolExecutor
- Optimasi untuk spek Intel i5-3570, 8GB RAM
- Auto-cleanup file temporary
- Monitoring memory usage

## 📋 Persyaratan Sistem

### Hardware
- **CPU**: Intel i5-3570 (atau equivalent)
- **RAM**: 8GB minimum
- **Storage**: SSD 128GB (untuk ~300 foto per event)
- **Camera**: DSLR dengan USB tethering support

### Software
- **OS**: Linux (Ubuntu 18.04+, CentOS 7+, atau compatible)
- **Python**: 3.7+
- **gPhoto2**: 2.5+
- **OpenCV**: 4.0+

## 🚀 Instalasi

### 1. Clone Repository
```bash
cd gemini/tethered-shooting-system
```

### 2. Jalankan Setup Otomatis
```bash
chmod +x setup.sh
./setup.sh
```

Setup script akan otomatis:
- Install system dependencies (gPhoto2, OpenCV, etc.)
- Create Python virtual environment
- Install Python packages
- Download OpenCV models
- Create sample LUT dan watermark
- Test koneksi kamera

### 3. Konfigurasi

#### Edit API Key (Sudah diset)
File `config.py` sudah berisi API key Google Gemini Anda.

#### Replace Sample Assets
```bash
# Ganti dengan LUT file Anda
cp /path/to/your/preset.cube presets/my_preset.cube

# Ganti dengan logo watermark Anda  
cp /path/to/your/logo.png watermarks/my_logo.png
```

## 🎮 Penggunaan

### Menjalankan Sistem

#### Mode Interaktif
```bash
# Default (interactive event selection + auto AI)
./start.sh

# Custom dengan options
python3 auto_capture_ai_enhanced.py --event-id cm123abc456def
python3 auto_capture_ai_enhanced.py --no-ai
python3 auto_capture_ai_enhanced.py --ai-mode opencv
```

#### Mode Background/Service
```bash
# Install sebagai system service
sudo cp tethered-shooting.service /etc/systemd/system/
sudo systemctl enable tethered-shooting
sudo systemctl start tethered-shooting

# Monitor logs
sudo journalctl -u tethered-shooting -f
```

### 🤖 AI Enhancement Options

Sistem mendukung berbagai mode AI enhancement:

#### **Mode Auto (Default)**
```bash
python3 auto_capture_ai_enhanced.py --ai-mode auto
```
- Coba Google Gemini AI dulu
- Fallback ke OpenCV jika AI gagal
- Optimal untuk most cases

#### **Mode Gemini Only**
```bash
python3 auto_capture_ai_enhanced.py --ai-mode gemini
```
- Hanya gunakan Google Gemini AI
- Gagal jika API tidak available
- Kualitas terbaik (jika berhasil)

#### **Mode OpenCV Only**
```bash
python3 auto_capture_ai_enhanced.py --ai-mode opencv
```
- Hanya gunakan traditional OpenCV enhancement
- Tidak perlu internet/API
- Cepat dan reliable

#### **Mode Disabled**
```bash
python3 auto_capture_ai_enhanced.py --no-ai
# atau
python3 auto_capture_ai_enhanced.py --ai-mode disabled
```
- Skip enhancement completely
- Paling cepat untuk high-volume shooting
- Langsung ke LUT + crop + watermark

#### **Advanced Options**
```bash
# Enable fallback ke OpenCV
python3 auto_capture_ai_enhanced.py --ai-fallback

# Skip enhancement jika gagal (lanjut tanpa enhancement)
python3 auto_capture_ai_enhanced.py --ai-skip-on-failure

# Kombinasi
python3 auto_capture_ai_enhanced.py --ai-mode gemini --ai-skip-on-failure
```

### Workflow Otomatis

1. **Connect Kamera**: Hubungkan DSLR via USB, set ke mode tethering
2. **Start Sistem**: Jalankan `./start.sh` 
3. **Auto Processing**: Setiap kali shutter ditekan:
   - File RAW+JPG didownload otomatis
   - Backup dibuat ke folder `backup/`
   - JPG diproses dengan AI enhancement (proteksi wajah)
   - Aplikasi LUT untuk color grading
   - Auto-crop sesuai orientasi
   - Watermark ditambahkan
   - Hasil final disimpan di `processed/`

### Struktur Folder
```
tethered-shooting-system/
├── captured/           # File dari kamera
├── backup/
│   ├── raw/           # Backup file RAW
│   └── jpg/           # Backup file JPG
├── processed/         # Hasil final siap pakai
├── temp/              # File temporary
├── logs/              # Log files
├── presets/           # LUT files (.cube)
├── watermarks/        # Logo/watermark files
└── models/            # OpenCV models
```

## ⚙️ Konfigurasi Advanced

### Camera Settings
```python
CAMERA_CONFIG = {
    "capture_format": "RAW+JPEG",
    "tethered_mode": True,
    "auto_download": True,
}
```

### AI Enhancement
```python
AI_ENHANCEMENT = {
    "max_resolution": (2048, 2048),  # Max untuk kirim ke AI
    "retry_attempts": 3,             # Retry jika gagal
    "timeout": 60,                   # Timeout detik
}
```

### Face Detection
```python
FACE_DETECTION = {
    "method": "opencv_haar",         # opencv_haar | dlib | mediapipe
    "scale_factor": 1.1,
    "min_neighbors": 5,
    "padding": 20,                   # Padding around face
}
```

### Auto Crop
```python
AUTO_CROP = {
    "portrait_ratio": (5, 7),        # Ratio untuk portrait
    "landscape_ratio": (7, 5),       # Ratio untuk landscape
    "target_dpi": 300,               # DPI untuk cetak
}
```

### Watermark
```python
WATERMARK = {
    "size_ratio": 0.15,              # 15% dari lebar gambar
    "position": {
        "horizontal": "center",       # left | center | right
        "vertical": 0.85,            # 85% dari atas
    },
    "opacity": 0.8,                  # Transparansi
}
```

## 🛠️ Troubleshooting

### Camera Issues

#### Kamera Tidak Terdeteksi
```bash
# Check USB connection
lsusb | grep -i canon  # atau nikon, sony, dll

# Test gPhoto2
gphoto2 --auto-detect
gphoto2 --summary
```

#### Permission Error
```bash
# Add user ke camera group
sudo gpasswd -a $USER plugdev
sudo udevadm control --reload-rules
```

#### Kamera Busy
```bash
# Kill proses yang menggunakan kamera
sudo pkill -f gphoto2
sudo pkill -f gvfs-gphoto2

# Restart udev
sudo systemctl restart udev
```

### AI Enhancement Issues

#### Google API Error
- Check API key di `config.py`
- Verify quota di Google Cloud Console
- Check internet connection

#### Memory Issues
```bash
# Monitor memory usage
htop
free -h

# Adjust memory limit di config.py
PERFORMANCE = {
    "memory_limit_mb": 1536,  # Reduce jika perlu
}
```

### Processing Issues

#### LUT File Error
```bash
# Validate LUT file format
head -20 presets/my_preset.cube
```

#### Watermark Error
```bash
# Check watermark file
file watermarks/my_logo.png
```

## 📊 Monitoring

### Real-time Status
```bash
# Monitor logs
tail -f logs/autocapture.log

# Check system status
./start.sh --status
```

### Performance Metrics
- **Processing Speed**: ~10-30 detik per foto (tergantung AI response)
- **Memory Usage**: ~1-2GB peak saat processing
- **Storage**: ~30MB per foto (RAW+JPG+processed)

## 🔧 Development

### Testing Components

#### Test Face Detection
```python
python3 face_detection.py
```

#### Test AI Enhancement
```python
python3 gemini_enhancer.py
```

#### Test Image Processing
```python
python3 image_processor.py
```

#### Test Camera
```python
python3 camera_controller.py
```

### Custom Modifications

#### Tambah LUT Processing
```python
# Edit image_processor.py
def apply_custom_lut(self, image):
    # Your custom LUT logic
    pass
```

#### Tambah Filter AI
```python
# Edit gemini_enhancer.py
def custom_enhancement_prompt(self):
    return "Your custom AI prompt"
```

## 🌐 Web Integration

Sistem ini terintegrasi dengan web project utama:

### Auto Upload
```python
WEB_INTEGRATION = {
    "enabled": True,
    "upload_to_web": True,
    "web_api_endpoint": "http://localhost:3000/api/photos",
}
```

### Real-time Updates
- Foto otomatis diupload ke web gallery
- Status update via WebSocket
- Mobile notification support

## 📝 License

© 2024 HafiPortrait Photography System

## 👥 Support

Untuk bantuan:
1. Check troubleshooting section
2. Review logs di `logs/autocapture.log`
3. Test individual components
4. Check hardware connections

---

**Sistem ini dirancang khusus untuk fotografi event real-time dengan kualitas profesional. Kecepatan, keandalan, dan proteksi wajah adalah prioritas utama.**