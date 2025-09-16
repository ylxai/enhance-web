# Test Suite - Sistem Tethered Shooting AI Enhanced

Folder ini berisi test scripts untuk validasi semua komponen sistem tethered shooting sebelum digunakan untuk event production.

## 📋 Daftar Test Scripts

### 1. **test-database.py** - Database & Configuration
- ✅ Environment variables (.env)
- ✅ Konfigurasi sistem
- ✅ Pembuatan direktori
- ✅ Koneksi Supabase
- ✅ Web integration config
- ✅ Cloud storage config
- ✅ Performance settings

### 2. **test-event.py** - Event Selection & Management
- ✅ Event selector initialization
- ✅ JWT authentication token
- ✅ Fetch events dari database real
- ✅ Event display formatting
- ✅ Interactive menu display
- ✅ Event creation data
- ✅ Event ID validation
- ✅ API error handling

### 3. **test-face-detection.py** - Face Detection & Protection
- ✅ Face detector initialization
- ✅ Test images creation
- ✅ Face detection accuracy
- ✅ Face masking
- ✅ Protection pipeline
- ✅ Visualization functions
- ✅ Performance metrics
- ✅ Edge cases

### 4. **test-ai-enhancement.py** - AI Enhancement & Processing
- ✅ AI enhancer initialization
- ✅ Image processor initialization
- ✅ Test images dengan issues
- ✅ AI enhancement dengan fallback
- ✅ LUT application
- ✅ Auto crop
- ✅ Watermark application

### 5. **test-upload.py** - Web Upload Functionality
- ✅ Web integrator initialization
- ✅ Web API connection
- ✅ JWT token creation
- ✅ Test image creation
- ✅ Image preparation
- ✅ Event retrieval untuk upload
- ✅ Photo upload (dry run & actual)
- ✅ Upload error handling
- ✅ Upload stats retrieval

## 🚀 Cara Menjalankan Test

### Jalankan Semua Test
```bash
# Dari direktori tethered-shooting-system
cd test/
python3 run-all-tests.py
```

### Jalankan Test Individual
```bash
# Test database dan konfigurasi
python3 test-database.py

# Test event selection
python3 test-event.py

# Test face detection
python3 test-face-detection.py

# Test AI enhancement
python3 test-ai-enhancement.py

# Test web upload
python3 test-upload.py
```

### Master Test Runner Options
```bash
# Jalankan semua test
python3 run-all-tests.py

# Stop pada test pertama yang gagal
python3 run-all-tests.py --stop-on-failure

# Lihat daftar test available
python3 run-all-tests.py --list

# Jalankan test spesifik
python3 run-all-tests.py --tests "Database & Configuration" "Event Selection"
```

## 📊 Interpretasi Hasil Test

### ✅ ALL TESTS PASSED
- Sistem siap untuk production
- Semua komponen berfungsi dengan baik
- Bisa langsung mulai tethered shooting

### ⚠️ SOME TESTS FAILED
Periksa komponen yang gagal:

#### Database & Configuration Failed
```bash
# Periksa file .env
ls -la .env

# Periksa environment variables
python3 -c "from config import Config; print('API Key:', Config.GOOGLE_API_KEY[:10])"
```

#### Event Selection Failed
```bash
# Test koneksi API manual
curl -X GET "http://74.63.10.103:3000/api/ping"

# Periksa JWT secret
python3 -c "from config import Config; print('JWT:', Config.WEB_INTEGRATION['jwt_secret'][:10])"
```

#### Face Detection Failed
```bash
# Periksa OpenCV
python3 -c "import cv2; print('OpenCV:', cv2.__version__)"

# Periksa Haar Cascade
ls -la models/
```

#### AI Enhancement Failed
```bash
# Test Google API Key
python3 -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('API OK')"

# Periksa LUT dan watermark
ls -la presets/
ls -la watermarks/
```

#### Web Upload Failed
```bash
# Test koneksi web project
curl -X GET "http://74.63.10.103:3000/api/events"

# Periksa authentication
python3 -c "from web_integrator import WebIntegrator; w = WebIntegrator(); print(w.test_connection())"
```

## 📁 Test Output Files

Test akan menghasilkan file output di folder `temp/`:

### Database Test
- Tidak ada file output khusus

### Event Test
- Log authentication dan API calls

### Face Detection Test
```
temp/face_test/
├── simple_face.jpg           # Test image sederhana
├── multiple_faces.jpg        # Test image multiple faces
├── no_face_landscape.jpg     # Test image tanpa wajah
├── complex_scene.jpg         # Test scene kompleks
├── mask_*.jpg               # Face masks yang dibuat
├── masked_visual_*.jpg      # Visualisasi mask
├── protected_*.jpg          # Hasil face protection
├── restored_*.jpg           # Hasil face restoration
└── detection_viz_*.jpg      # Visualisasi deteksi
```

### AI Enhancement Test
```
temp/ai_test/
├── blurry_test.jpg          # Test image blur
├── noisy_test.jpg           # Test image noise
├── low_contrast_test.jpg    # Test image low contrast
├── enhanced_*.jpg           # Hasil AI enhancement
├── lut_*.jpg               # Hasil LUT application
├── cropped_*.jpg           # Hasil auto crop
└── watermarked_*.jpg       # Hasil watermark
```

### Upload Test
```
temp/
├── test_upload_image.jpg    # Test image untuk upload
└── upload_logs.json        # Log upload attempts
```

## 🔧 Troubleshooting

### Permission Errors
```bash
# Fix permission untuk script
chmod +x test/*.py
chmod +x run-all-tests.py
```

### Missing Dependencies
```bash
# Install missing packages
pip install -r ../requirements.txt

# Install system packages
sudo apt-get install gphoto2 libgphoto2-dev python3-opencv
```

### API Connection Issues
```bash
# Check network connectivity
ping 74.63.10.103

# Check web project status
curl -I http://74.63.10.103:3000

# Check firewall
sudo ufw status
```

### File Permission Issues
```bash
# Fix directory permissions
chmod 755 ../captured ../backup ../processed ../temp ../logs

# Fix file permissions
chmod 644 ../.env ../presets/* ../watermarks/*
```

## 💡 Tips untuk Development

### Menambah Test Baru
1. Buat file `test-nama-fitur.py`
2. Follow pattern dari test existing
3. Tambahkan ke `test_scripts` di `run-all-tests.py`

### Debug Test Spesifik
```bash
# Jalankan dengan verbose output
python3 test-database.py -v

# Debug dengan Python debugger
python3 -m pdb test-upload.py
```

### Performance Testing
```bash
# Ukur waktu eksekusi
time python3 test-ai-enhancement.py

# Monitor resource usage
htop & python3 test-face-detection.py
```

## 📈 Expected Test Times

Berdasarkan hardware target (Intel i5-3570, 8GB RAM):

- **Database Test**: ~10 seconds
- **Event Test**: ~15 seconds
- **Face Detection Test**: ~30 seconds
- **AI Enhancement Test**: ~60 seconds
- **Upload Test**: ~45 seconds

**Total waktu semua test**: ~2.5 menit

## ⚡ Quick Start

Untuk test cepat sebelum event:

```bash
# Test critical components saja
python3 run-all-tests.py --tests "Database & Configuration" "Web Upload"

# Test tanpa AI (untuk speed)
python3 test-database.py && python3 test-event.py && python3 test-upload.py
```

---

**Catatan**: Semua test dirancang untuk berjalan independent dan tidak memerlukan hardware kamera untuk sebagian besar functionality. Test akan menggunakan mock data dan fallback mechanisms untuk komponen yang memerlukan hardware external.