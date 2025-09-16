# Konfigurasi Sistem Tethered Shooting AI Enhanced
# ==============================================

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Konfigurasi utama untuk sistem tethered shooting"""
    
    # === GOOGLE GENAI CONFIGURATION ===
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDpyXdK_x2fagj7y0DrVrfpV7qZY34zxFY")
    GEMINI_MODEL = "gemini-2.5-flash"  # Model yang optimal untuk image enhancement
    
    # === DIREKTORI SYSTEM ===
    BASE_DIR = Path(__file__).parent.absolute()
    
    # Input/Output Directories
    CAPTURE_DIR = BASE_DIR / "captured"           # Foto hasil download dari kamera
    BACKUP_DIR = BASE_DIR / "backup"              # Backup file asli
    BACKUP_RAW_DIR = BACKUP_DIR / "raw"           # Backup file RAW
    BACKUP_JPG_DIR = BACKUP_DIR / "jpg"           # Backup file JPG
    PROCESSED_DIR = BASE_DIR / "processed"        # Hasil akhir siap pakai
    TEMP_DIR = BASE_DIR / "temp"                  # File temporary processing
    LOGS_DIR = BASE_DIR / "logs"                  # Log files
    
    # Assets Directories
    PRESETS_DIR = BASE_DIR / "presets"            # LUT files (.cube)
    WATERMARKS_DIR = BASE_DIR / "watermarks"      # Watermark files
    MODELS_DIR = BASE_DIR / "models"              # OpenCV models (haar cascades)
    
    # === CAMERA SETTINGS ===
    CAMERA_CONFIG = {
        "capture_format": "RAW+JPEG",             # Download both RAW and JPEG
        "tethered_mode": True,                    # Enable tethered shooting
        "auto_download": True,                    # Auto download after capture
        "delete_after_download": False,           # Keep files on camera
    }
    
    # === IMAGE PROCESSING SETTINGS ===
    
    # Face Detection Settings
    FACE_DETECTION = {
        "method": "disabled",                  # opencv_haar | dlib | mediapipe
        "cascade_file": "haarcascade_frontalface_alt.xml",
        "scale_factor": 1.1,                     # Deteksi scale factor
        "min_neighbors": 5,                      # Minimum neighbors untuk deteksi
        "min_size": (30, 30),                    # Minimum face size
        "padding": 20,                           # Padding around face untuk mask
    }
    
    # AI Enhancement Settings
    AI_ENHANCEMENT = {
        "enabled": os.getenv("AI_ENHANCEMENT_ENABLED", "true").lower() == "true",
        "mode": os.getenv("AI_ENHANCEMENT_MODE", "gemini"),  # auto | gemini | opencv | disabled
        "max_resolution": (2048, 2048),          # Max resolution untuk kirim ke AI (hemat bandwidth)
        "face_protection_prompt": """
        Lakukan enhancement pada gambar ini dengan instruksi khusus:
        1. Untuk area WAJAH : Hanya lakukan koreksi warna dan penajaman SANGAT HALUS
        2. Untuk area SELAIN WAJAH: Lakukan unblur, superfokus, koreksi goyangan, dan enhancement lengkap
        3. PRIORITAS UTAMA: TIDAK MENGUBAH STRUKTUR ASLI WAJAH sama sekali
        4. Pertahankan naturalness warna kulit
        5. Tingkatkan ketajaman dan detail pada background, pakaian, aksesoris
        """,
        "retry_attempts": 3,                     # Retry jika API gagal
        "timeout": 60,                           # Timeout dalam detik
        "fallback_to_opencv": os.getenv("AI_FALLBACK_OPENCV", "true").lower() == "true",
        "skip_on_failure": os.getenv("AI_SKIP_ON_FAILURE", "false").lower() == "true",
    }
    
    # Auto Crop Settings
    AUTO_CROP = {
        "portrait_ratio": (5, 7),                # Ratio untuk foto portrait
        "landscape_ratio": (7, 5),               # Ratio untuk foto landscape
        "target_dpi": 300,                       # DPI untuk cetak
        "min_resolution": (1500, 2100),         # Minimum resolution hasil crop
    }
    
    # Watermark Settings
    WATERMARK = {
        "file": "nama.png",                   # Nama file watermark
        "size_ratio": 0.15,                     # 15% dari lebar gambar
        "position": {
            "horizontal": "center",               # left | center | right
            "vertical": 0.85,                    # 85% dari atas (0.0 = top, 1.0 = bottom)
        },
        "opacity": 0.8,                         # Transparansi watermark
    }
    
    # LUT Settings
    LUT_SETTINGS = {
        "file": "",               # Nama file LUT
        "intensity": 1.0,                       # Intensitas aplikasi LUT (0.0-1.0)
    }
    
    # === PERFORMANCE SETTINGS ===
    PERFORMANCE = {
        "max_workers": 2,                       # Max parallel processing (sesuai CPU i5-3570)
        "temp_cleanup": True,                   # Auto cleanup temp files
        "compress_backup": False,               # Jangan compress backup (lebih cepat)
        "memory_limit_mb": 2048,               # Limit memory usage (2GB dari 8GB)
    }
    
    # === LOGGING SETTINGS ===
    LOGGING = {
        "level": "INFO",                        # DEBUG | INFO | WARNING | ERROR
        "file": "autocapture.log",              # Log filename
        "max_size_mb": 10,                      # Max log file size
        "backup_count": 5,                      # Number of backup log files
        "format": "%(asctime)s - %(levelname)s - %(message)s",
    }
    
    # === WEB INTEGRATION SETTINGS ===
    WEB_INTEGRATION = {
        "enabled": True,                        # Enable integrasi dengan web
        "upload_to_web": True,                  # Auto upload hasil ke web
        "web_api_base_url": os.getenv("WEB_API_BASE_URL", "http://74.63.10.103:3002/api"),
        "web_upload_endpoint": os.getenv("WEB_UPLOAD_ENDPOINT", "http://74.63.10.103:3002/api/photos"),
        "web_event_endpoint": os.getenv("WEB_EVENT_ENDPOINT", "http://74.63.10.103:3002/api/events"),
        "web_upload_quality": "high",           # low | medium | high
        "auto_assign_to_event": os.getenv("AUTO_ASSIGN_TO_EVENT", "true").lower() == "true",
        "default_event_type": os.getenv("DEFAULT_EVENT_TYPE", "official"),
        "default_photo_category": os.getenv("DEFAULT_PHOTO_CATEGORY", "professional"),
        "jwt_secret": os.getenv("JWT_SECRET", ""),
        "upload_timeout": int(os.getenv("UPLOAD_TIMEOUT", "300")),
        "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
    }
    
    # === SUPABASE CONFIGURATION ===
    SUPABASE_CONFIG = {
        "url": os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""),
        "anon_key": os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", ""),
        "service_role_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
    }
    
    # === CLOUD STORAGE CONFIGURATION ===
    CLOUDFLARE_R2_CONFIG = {
        "account_id": os.getenv("CLOUDFLARE_R2_ACCOUNT_ID", ""),
        "access_key_id": os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID", ""),
        "secret_access_key": os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY", ""),
        "bucket_name": os.getenv("CLOUDFLARE_R2_BUCKET_NAME", ""),
        "public_url": os.getenv("CLOUDFLARE_R2_PUBLIC_URL", ""),
        "endpoint": os.getenv("CLOUDFLARE_R2_ENDPOINT", ""),
    }
    
    @classmethod
    def create_directories(cls):
        """Buat semua direktori yang dibutuhkan"""
        directories = [
            cls.CAPTURE_DIR, cls.BACKUP_RAW_DIR, cls.BACKUP_JPG_DIR,
            cls.PROCESSED_DIR, cls.TEMP_DIR, cls.LOGS_DIR,
            cls.PRESETS_DIR, cls.WATERMARKS_DIR, cls.MODELS_DIR
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Direktori dibuat: {directory}")
    
    @classmethod
    def validate_config(cls):
        """Validasi konfigurasi dan file yang dibutuhkan"""
        errors = []
        
        # Check API Key
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY == "AIzaSyDpyXdK_x2fagj7y0DrVrfpV7qZY34zxFY":
            errors.append("Google API Key belum diset")
        
        # Check required files
        lut_file = cls.PRESETS_DIR / cls.LUT_SETTINGS["file"]
        if not lut_file.exists():
            errors.append(f"File LUT tidak ditemukan: {lut_file}")
        
        watermark_file = cls.WATERMARKS_DIR / cls.WATERMARK["file"]
        if not watermark_file.exists():
            errors.append(f"File watermark tidak ditemukan: {watermark_file}")
        
        return errors

if __name__ == "__main__":
    # Test konfigurasi
    print("Testing konfigurasi sistem...")
    Config.create_directories()
    
    errors = Config.validate_config()
    if errors:
        print("❌ Error dalam konfigurasi:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Konfigurasi valid!")
