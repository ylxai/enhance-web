# Manual Testing Scripts

Dua script terpisah untuk testing dan debugging sistem tethered shooting tanpa menjalankan full automation.

## 📸 Script 1: Manual Trigger (`manual_trigger.py`)

Script untuk kontrol manual shutter kamera menggunakan gPhoto2.

### 🚀 Cara Penggunaan

#### **Interactive Mode (Recommended)**
```bash
python3 manual_trigger.py
```

Menu interaktif:
- `c` atau `capture` - Ambil foto
- `s` atau `summary` - Tampilkan info kamera  
- `r` atau `reconfig` - Konfigurasi ulang kamera
- `q` atau `quit` - Keluar

#### **Single Capture Mode**
```bash
python3 manual_trigger.py --capture
```

#### **Burst Mode**
```bash
# 10 foto dengan interval 2 detik
python3 manual_trigger.py --burst 10

# 5 foto dengan interval 3 detik
python3 manual_trigger.py --burst 5 --interval 3
```

### ✅ Fitur

- ✅ Deteksi kamera otomatis
- ✅ Konfigurasi basic kamera (RAW+JPEG, capture target)
- ✅ Single capture dengan konfirmasi
- ✅ Burst mode dengan interval custom
- ✅ Auto backup ke folder `backup/`
- ✅ Monitoring waktu capture
- ✅ Error handling yang robust

### 📁 Output

```
captured/              # File hasil download dari kamera
├── manual_1703123456_001.CR2
├── manual_1703123456_001.JPG
├── manual_1703123467_002.CR2
└── manual_1703123467_002.JPG

backup/
├── raw/              # Backup file RAW
└── jpg/              # Backup file JPG
```

---

## 👁️ Script 2: Folder Watcher (`folder_watcher.py`)

Script untuk watch folder dan otomatis memproses foto yang disalin ke folder watch.

### 🚀 Cara Penggunaan

#### **Basic Mode**
```bash
python3 folder_watcher.py
```

#### **Dengan Event ID Spesifik**
```bash
python3 folder_watcher.py --event-id cm123abc456def
```

#### **Custom Scan Interval**
```bash
python3 folder_watcher.py --interval 5  # Scan setiap 5 detik
```

#### **Disable AI Enhancement**
```bash
python3 folder_watcher.py --no-ai
```

#### **Custom AI Mode**
```bash
python3 folder_watcher.py --ai-mode opencv    # OpenCV only
python3 folder_watcher.py --ai-mode gemini    # Gemini AI only
python3 folder_watcher.py --ai-mode disabled  # No enhancement
```

### 🔄 Workflow

1. **Start folder watcher**
2. **Copy foto ke folder `watch_folder/`**
3. **Sistem otomatis detect dan proses**
4. **Hasil disimpan di `processed/`**
5. **Auto upload ke web project**

### ✅ Fitur

- ✅ Real-time folder monitoring
- ✅ Full processing pipeline (AI + LUT + Crop + Watermark)
- ✅ Parallel processing dengan ThreadPoolExecutor
- ✅ Auto backup file original
- ✅ Web upload ke tab "Official"
- ✅ Real-time statistics
- ✅ Graceful shutdown dengan Ctrl+C

### 📁 Struktur Folder

```
watch_folder/          # DROP FOTO DI SINI
├── test_photo1.jpg    # Copy foto ke sini
├── test_photo2.jpg
└── test_photo3.jpg

processed/             # Hasil akhir
├── processed_test_photo1_1703123456.jpg
├── processed_test_photo2_1703123467.jpg
└── processed_test_photo3_1703123478.jpg

backup/jpg/            # Backup original
temp/                  # File temporary (auto cleanup)
```

### 📊 Real-time Stats

```
📊 Stats: Detected=5, Processed=4, Uploaded=4, Errors=0, Runtime=2.3min

📊 FINAL STATISTICS
----------------------------------------
⏱️ Total Runtime: 5.2 minutes
📁 Files Detected: 10
✅ Files Processed: 9
🌐 Files Uploaded: 8
❌ Errors: 1
⚡ Average Processing Time: 12.3s per file
📈 Success Rate: 90.0%
```

---

## 🧪 Testing Workflow

### **Scenario 1: Manual Camera Testing**
```bash
# 1. Test koneksi kamera
python3 manual_trigger.py

# 2. Ambil beberapa foto manual
# Gunakan command 'c' di interactive mode

# 3. Verify files di captured/ dan backup/
ls -la captured/
ls -la backup/raw/
ls -la backup/jpg/
```

### **Scenario 2: Processing Pipeline Testing**
```bash
# 1. Start folder watcher
python3 folder_watcher.py --ai-mode auto

# 2. Copy foto ke watch folder (terminal lain)
cp /path/to/test/photos/*.jpg watch_folder/

# 3. Monitor processing real-time
# Lihat output di terminal folder watcher

# 4. Check hasil
ls -la processed/
```

### **Scenario 3: Performance Testing**
```bash
# Test dengan banyak file
python3 folder_watcher.py --interval 1

# Copy batch photos
cp /path/to/many/photos/*.jpg watch_folder/

# Monitor stats dan performance
```

### **Scenario 4: AI Mode Comparison**
```bash
# Test OpenCV only (cepat)
python3 folder_watcher.py --ai-mode opencv

# Test Gemini AI only (kualitas)
python3 folder_watcher.py --ai-mode gemini

# Test disabled (tercepat)
python3 folder_watcher.py --no-ai
```

---

## 🔧 Troubleshooting

### **Manual Trigger Issues**

#### Camera Not Detected
```bash
# Check USB connection
lsusb | grep -i canon  # atau nikon, sony

# Check gPhoto2
gphoto2 --auto-detect
gphoto2 --summary

# Kill conflicting processes
sudo pkill -f gphoto2
sudo pkill -f gvfs-gphoto2
```

#### Permission Issues
```bash
# Add user to camera group
sudo gpasswd -a $USER plugdev
sudo udevadm control --reload-rules

# Logout dan login lagi
```

### **Folder Watcher Issues**

#### No Files Detected
```bash
# Check folder exists
ls -la watch_folder/

# Check file permissions
chmod 644 watch_folder/*.jpg

# Check scan interval
python3 folder_watcher.py --interval 1  # Faster scan
```

#### Processing Errors
```bash
# Check logs
tail -f logs/autocapture.log

# Test individual components
python3 test/test-ai-enhancement.py
python3 test/test-upload.py
```

#### Upload Failures
```bash
# Test web connection
curl http://74.63.10.103:3000/api/ping

# Check event ID
python3 -c "from event_selector import EventSelector; es = EventSelector(); print(es.get_active_event())"
```

---

## 📋 Tips & Best Practices

### **Untuk Manual Trigger**
- Gunakan burst mode untuk test performa kamera
- Monitor waktu capture untuk optimasi settings
- Test dengan berbagai format (RAW+JPEG, JPEG only)

### **Untuk Folder Watcher**
- Start dengan 1-2 foto dulu untuk test pipeline
- Monitor memory usage saat processing banyak file
- Gunakan `--no-ai` untuk test cepat tanpa AI
- Copy file bertahap, jangan sekaligus banyak

### **General Testing**
- Selalu backup foto penting sebelum test
- Monitor disk space (SSD 128GB terbatas)
- Test dengan berbagai ukuran dan format foto
- Cleanup folder `temp/` secara berkala

---

## 🎯 Integration dengan Main System

Kedua script ini menggunakan komponen yang sama dengan `auto_capture_ai_enhanced.py`:

- ✅ **Config** - Konfigurasi dan environment variables
- ✅ **Face Detection** - Proteksi wajah saat AI enhancement  
- ✅ **AI Enhancer** - Google Gemini dan OpenCV fallback
- ✅ **Image Processor** - LUT, crop, watermark
- ✅ **Web Integrator** - Upload ke tab "Official"
- ✅ **Event Selector** - Auto-detect atau pilih event

**Hasil testing dengan script manual ini akan 100% representatif dengan sistem full automation!**