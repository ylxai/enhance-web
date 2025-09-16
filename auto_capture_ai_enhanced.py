#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistem Tethered Shooting Otomatis dengan AI Enhancement
======================================================

Sistem otomatis untuk fotografi event yang mengintegrasikan:
1. Tethered shooting menggunakan gPhoto2
2. AI enhancement menggunakan Google Gemini dengan proteksi wajah
3. Aplikasi LUT untuk color grading
4. Auto-crop berdasarkan orientasi
5. Watermarking otomatis
6. Processing paralel untuk performa optimal

Author: HafiPortrait Photography System
Compatible dengan: Intel i5-3570, 8GB RAM, SSD 128GB
"""

import cv2
import numpy as np
import logging
import time
import threading
import signal
import sys
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List
import json

# Import modules lokal
from config import Config
from camera_controller import CameraController
from gemini_enhancer import GeminiImageEnhancer
from image_processor import ImageProcessor
from face_detection import FaceProtectionMask
from web_integrator import WebIntegrator
from event_selector import EventSelector
from interactive_setup import InteractiveSetup

# Setup logging
logging.basicConfig(
    level=getattr(logging, Config.LOGGING["level"]),
    format=Config.LOGGING["format"],
    handlers=[
        logging.FileHandler(Config.LOGS_DIR / Config.LOGGING["file"]),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AutoCaptureSystem:
    """Main system untuk automated tethered shooting dengan AI enhancement"""
    
    def __init__(self, event_id: Optional[str] = None):
        """Inisialisasi sistem"""
        self.is_running = False
        self.selected_event_id = event_id  # Event ID yang dipilih user
        self.stats = {
            "total_captured": 0,
            "total_processed": 0,
            "total_errors": 0,
            "start_time": None,
            "last_capture_time": None
        }
        
        # Inisialisasi komponen
        self._init_components()
        
        # Setup signal handlers untuk graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("🚀 AutoCaptureSystem berhasil diinisialisasi")
    
    def _init_components(self):
        """Inisialisasi semua komponen sistem"""
        try:
            logger.info("Menginisialisasi komponen sistem...")
            
            # Buat direktori yang diperlukan
            Config.create_directories()
            
            # Validasi konfigurasi
            config_errors = Config.validate_config()
            if config_errors:
                logger.warning("⚠️ Beberapa konfigurasi bermasalah:")
                for error in config_errors:
                    logger.warning(f"  - {error}")
            
            # Inisialisasi face detection
            logger.info("Inisialisasi face detection...")
            self.face_detector = FaceProtectionMask()
            
            # Inisialisasi AI enhancer
            logger.info("Inisialisasi AI enhancer...")
            self.ai_enhancer = GeminiImageEnhancer()
            
            # Inisialisasi image processor
            logger.info("Inisialisasi image processor...")
            self.image_processor = ImageProcessor()
            
            # Inisialisasi web integrator
            logger.info("Inisialisasi web integrator...")
            self.web_integrator = WebIntegrator()
            
            # Test koneksi web API
            if Config.WEB_INTEGRATION["enabled"]:
                if self.web_integrator.test_connection():
                    logger.info("✅ Web API connection established")
                else:
                    logger.warning("⚠️ Web API connection failed, will retry during upload")
            
            # Inisialisasi camera controller
            logger.info("Inisialisasi camera controller...")
            self.camera = CameraController(callback_func=self._on_new_capture)
            self.camera.configure_camera()
            
            # Thread pool untuk parallel processing
            max_workers = Config.PERFORMANCE["max_workers"]
            self.executor = ThreadPoolExecutor(max_workers=max_workers)
            logger.info(f"Thread pool dibuat dengan {max_workers} workers")
            
            logger.info("✅ Semua komponen berhasil diinisialisasi")
            
        except Exception as e:
            logger.error(f"❌ Gagal inisialisasi komponen: {e}")
            raise
    
    def _signal_handler(self, signum, frame):
        """Handle sistem signals untuk graceful shutdown"""
        logger.info(f"Signal {signum} diterima, melakukan graceful shutdown...")
        self.stop()
    
    def _on_new_capture(self, file_path: Path):
        """
        Callback yang dipanggil ketika ada foto baru dari kamera
        
        Args:
            file_path: Path ke file yang baru di-capture
        """
        try:
            self.stats["total_captured"] += 1
            self.stats["last_capture_time"] = time.time()
            
            logger.info(f"📸 File baru diterima: {file_path}")
            
            # Submit untuk processing asynchronous
            future = self.executor.submit(self._process_image, file_path)
            
            # Tambahkan callback untuk handle hasil
            future.add_done_callback(lambda f: self._on_processing_complete(f, file_path))
            
        except Exception as e:
            logger.error(f"Error dalam callback capture: {e}")
            self.stats["total_errors"] += 1
    
    def _process_image(self, file_path: Path) -> Optional[Path]:
        """
        Process image dengan full pipeline
        
        Args:
            file_path: Path ke file input
            
        Returns:
            Path ke file hasil akhir atau None jika gagal
        """
        processing_start = time.time()
        
        try:
            logger.info(f"🔄 Memulai processing: {file_path.name}")
            
            # Hanya proses file JPG (skip RAW untuk kecepatan)
            if file_path.suffix.lower() not in ['.jpg', '.jpeg']:
                logger.info(f"Skip processing {file_path.name} (bukan JPG)")
                return None
            
            # === STEP 1: AI Enhancement ===
            logger.info("Step 1: AI Enhancement...")
            temp_enhanced = Config.TEMP_DIR / f"enhanced_{file_path.stem}.jpg"
            
            success, enhanced_path = self.ai_enhancer.enhance_image(file_path, temp_enhanced)
            if not success or not enhanced_path:
                logger.error(f"AI Enhancement gagal untuk {file_path.name}")
                enhanced_path = file_path  # Fallback ke original
            
            # === STEP 2: Load enhanced image ===
            enhanced_image = cv2.imread(str(enhanced_path))
            if enhanced_image is None:
                logger.error(f"Gagal load enhanced image: {enhanced_path}")
                return None
            
            # === STEP 3: Full Processing Pipeline (LUT + Crop + Watermark) ===
            logger.info("Step 2: Full Processing Pipeline...")
            final_filename = f"final_{file_path.stem}_{int(time.time())}.jpg"
            final_path = Config.PROCESSED_DIR / final_filename
            
            success, result_path = self.image_processor.process_full_pipeline(enhanced_image, final_path)
            
            if not success:
                logger.error(f"Processing pipeline gagal untuk {file_path.name}")
                return None
            
            # === STEP 4: Cleanup temporary files ===
            if Config.PERFORMANCE["temp_cleanup"]:
                try:
                    if temp_enhanced.exists() and temp_enhanced != file_path:
                        temp_enhanced.unlink()
                        logger.debug(f"Cleanup temp file: {temp_enhanced}")
                except Exception as e:
                    logger.warning(f"Gagal cleanup temp file: {e}")
            
            # === STEP 5: Web Integration (optional) ===
            if Config.WEB_INTEGRATION["enabled"] and Config.WEB_INTEGRATION["upload_to_web"]:
                self._upload_to_web(result_path, file_path)
            
            processing_time = time.time() - processing_start
            logger.info(f"✅ Processing selesai dalam {processing_time:.2f}s: {result_path}")
            
            return result_path
            
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            self.stats["total_errors"] += 1
            return None
    
    def _on_processing_complete(self, future, original_path: Path):
        """
        Callback ketika processing selesai
        
        Args:
            future: Future object dari processing
            original_path: Path file original
        """
        try:
            result_path = future.result()
            
            if result_path:
                self.stats["total_processed"] += 1
                logger.info(f"🎉 Processing berhasil: {original_path.name} -> {result_path.name}")
                
                # Log statistik
                self._log_statistics()
                
            else:
                logger.error(f"💥 Processing gagal: {original_path.name}")
                self.stats["total_errors"] += 1
                
        except Exception as e:
            logger.error(f"Error dalam processing callback: {e}")
            self.stats["total_errors"] += 1
    
    def _upload_to_web(self, processed_file_path: Path, original_file_path: Path):
        """
        Upload hasil ke web project dengan integrasi ke tab official
        
        Args:
            processed_file_path: Path ke file hasil processing
            original_file_path: Path ke file original
        """
        try:
            logger.info(f"🌐 Uploading to web: {processed_file_path.name}")
            
            # Upload menggunakan web integrator dengan event ID yang dipilih
            success = self.web_integrator.upload_photo(processed_file_path, self.selected_event_id)
            
            if success:
                logger.info(f"✅ Upload ke web berhasil: {processed_file_path.name}")
                logger.info("   📋 Foto akan tampil di tab 'Official' pada halaman event")
                
                # Log upload stats
                try:
                    stats = self.web_integrator.get_upload_stats()
                    logger.info(f"   📊 Upload stats: {stats}")
                except Exception as e:
                    logger.debug(f"Failed to get upload stats: {e}")
                    
            else:
                logger.warning(f"⚠️ Upload ke web gagal: {processed_file_path.name}")
                
                # Retry dengan file original jika processed gagal
                logger.info("   🔄 Mencoba upload file original sebagai fallback...")
                fallback_success = self.web_integrator.upload_photo(original_file_path)
                
                if fallback_success:
                    logger.info(f"✅ Fallback upload berhasil: {original_file_path.name}")
                else:
                    logger.error(f"❌ Semua upload gagal untuk: {original_file_path.name}")
                    
        except Exception as e:
            logger.error(f"❌ Error upload ke web: {e}")
            # Simpan info untuk retry nanti
            self._save_failed_upload_info(processed_file_path, original_file_path)
    
    def _save_failed_upload_info(self, processed_file: Path, original_file: Path):
        """Simpan info upload yang gagal untuk retry nanti"""
        try:
            failed_uploads_file = Config.LOGS_DIR / "failed_uploads.json"
            
            failed_info = {
                "timestamp": time.time(),
                "processed_file": str(processed_file),
                "original_file": str(original_file),
                "retry_count": 0
            }
            
            # Load existing failed uploads
            failed_uploads = []
            if failed_uploads_file.exists():
                with open(failed_uploads_file, 'r') as f:
                    failed_uploads = json.load(f)
            
            # Add new failed upload
            failed_uploads.append(failed_info)
            
            # Save back
            with open(failed_uploads_file, 'w') as f:
                json.dump(failed_uploads, f, indent=2)
                
            logger.info(f"📝 Failed upload info saved for retry: {original_file.name}")
            
        except Exception as e:
            logger.error(f"Error saving failed upload info: {e}")
    
    def _log_statistics(self):
        """Log statistik sistem"""
        if self.stats["start_time"]:
            runtime = time.time() - self.stats["start_time"]
            runtime_hours = runtime / 3600
            
            success_rate = (self.stats["total_processed"] / max(1, self.stats["total_captured"])) * 100
            
            logger.info(
                f"📊 Stats: Captured={self.stats['total_captured']}, "
                f"Processed={self.stats['total_processed']}, "
                f"Errors={self.stats['total_errors']}, "
                f"Success Rate={success_rate:.1f}%, "
                f"Runtime={runtime_hours:.1f}h"
            )
    
    def start(self):
        """Mulai sistem tethered capture"""
        try:
            if self.is_running:
                logger.warning("Sistem sudah berjalan")
                return
            
            logger.info("🚀 Memulai sistem tethered shooting...")
            
            self.is_running = True
            self.stats["start_time"] = time.time()
            
            # Mulai tethered capture
            self.camera.start_tethered_capture()
            
            logger.info("✅ Sistem aktif! Menunggu trigger dari kamera...")
            logger.info("📋 Tekan Ctrl+C untuk menghentikan sistem")
            
            # Main monitoring loop
            self._monitoring_loop()
            
        except Exception as e:
            logger.error(f"❌ Error starting sistem: {e}")
            self.stop()
    
    def _monitoring_loop(self):
        """Main monitoring loop untuk sistem"""
        last_stats_time = time.time()
        stats_interval = 60  # Log stats setiap 60 detik
        
        try:
            while self.is_running:
                # Monitor camera status
                camera_status = self.camera.get_camera_status()
                
                if not camera_status["connected"]:
                    logger.error("❌ Kamera tidak terhubung, mencoba reconnect...")
                    # Implementasi reconnect logic bisa ditambahkan di sini
                
                # Log stats secara berkala
                current_time = time.time()
                if current_time - last_stats_time >= stats_interval:
                    self._log_statistics()
                    last_stats_time = current_time
                
                # Monitor memory usage
                self._check_memory_usage()
                
                # Sleep untuk mengurangi CPU usage
                time.sleep(5)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt diterima")
        except Exception as e:
            logger.error(f"Error dalam monitoring loop: {e}")
        finally:
            self.stop()
    
    def _check_memory_usage(self):
        """Monitor penggunaan memory"""
        try:
            import psutil
            
            memory_mb = psutil.virtual_memory().used / 1024 / 1024
            memory_limit = Config.PERFORMANCE["memory_limit_mb"]
            
            if memory_mb > memory_limit:
                logger.warning(f"⚠️ Memory usage tinggi: {memory_mb:.1f}MB / {memory_limit}MB")
                
                # Trigger cleanup jika memory tinggi
                self._cleanup_temp_files()
                
        except ImportError:
            pass  # psutil tidak tersedia
        except Exception as e:
            logger.debug(f"Error checking memory: {e}")
    
    def _cleanup_temp_files(self):
        """Cleanup temporary files untuk menghemat space"""
        try:
            temp_files = list(Config.TEMP_DIR.glob("*"))
            cleaned_count = 0
            
            for temp_file in temp_files:
                if temp_file.is_file():
                    # Hapus file temp yang lebih dari 1 jam
                    file_age = time.time() - temp_file.stat().st_mtime
                    if file_age > 3600:  # 1 hour
                        temp_file.unlink()
                        cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"🧹 Cleanup {cleaned_count} temp files")
                
        except Exception as e:
            logger.error(f"Error cleanup temp files: {e}")
    
    def stop(self):
        """Stop sistem dengan graceful shutdown"""
        try:
            logger.info("🛑 Menghentikan sistem...")
            
            self.is_running = False
            
            # Stop camera
            if hasattr(self, 'camera'):
                self.camera.stop_tethered_capture()
                self.camera.disconnect()
            
            # Shutdown thread pool
            if hasattr(self, 'executor'):
                logger.info("Menunggu processing yang sedang berjalan selesai...")
                self.executor.shutdown(wait=True, timeout=30)
            
            # Final statistics
            self._log_statistics()
            
            # Final cleanup
            if Config.PERFORMANCE["temp_cleanup"]:
                self._cleanup_temp_files()
            
            logger.info("✅ Sistem berhasil dihentikan")
            
        except Exception as e:
            logger.error(f"Error saat shutdown: {e}")
    
    def get_status(self) -> dict:
        """Dapatkan status lengkap sistem"""
        camera_status = self.camera.get_camera_status() if hasattr(self, 'camera') else {}
        
        return {
            "system_running": self.is_running,
            "camera": camera_status,
            "statistics": self.stats.copy(),
            "config": {
                "ai_model": Config.GEMINI_MODEL,
                "max_workers": Config.PERFORMANCE["max_workers"],
                "memory_limit": Config.PERFORMANCE["memory_limit_mb"]
            }
        }

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Sistem Tethered Shooting AI Enhanced",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  # Basic usage
  python3 auto_capture_ai_enhanced.py                    # Interactive mode
  python3 auto_capture_ai_enhanced.py --event-id cm123   # Langsung dengan event ID
  
  # Event management
  python3 auto_capture_ai_enhanced.py --list-events      # Tampilkan daftar event
  python3 auto_capture_ai_enhanced.py --test-events      # Test event selection saja
  python3 auto_capture_ai_enhanced.py --auto-create      # Auto-create event baru
  
  # AI Enhancement options
  python3 auto_capture_ai_enhanced.py --no-ai            # Disable AI enhancement
  python3 auto_capture_ai_enhanced.py --ai-mode opencv   # Use OpenCV only
  python3 auto_capture_ai_enhanced.py --ai-mode gemini   # Use Gemini AI only
  python3 auto_capture_ai_enhanced.py --ai-mode auto     # Auto (Gemini + fallback)
  python3 auto_capture_ai_enhanced.py --ai-fallback      # Enable OpenCV fallback
  python3 auto_capture_ai_enhanced.py --ai-skip-on-failure  # Skip if AI fails
  
  # Combined examples
  python3 auto_capture_ai_enhanced.py --event-id cm123 --no-ai
  python3 auto_capture_ai_enhanced.py --ai-mode opencv --ai-fallback
        """
    )
    
    parser.add_argument(
        '--event-id', 
        type=str, 
        help='Event ID yang akan digunakan (skip interactive selection)'
    )
    
    parser.add_argument(
        '--test-events', 
        action='store_true',
        help='Test event selection dan keluar'
    )
    
    parser.add_argument(
        '--list-events', 
        action='store_true',
        help='Tampilkan daftar event dan keluar'
    )
    
    parser.add_argument(
        '--interactive', 
        action='store_true',
        help='Jalankan interactive setup lengkap (event, AI, watermark, dll)'
    )
    
    parser.add_argument(
        '--auto-create', 
        action='store_true',
        help='Auto-create event baru jika tidak ada yang aktif'
    )
    
    # AI Enhancement Options
    parser.add_argument(
        '--ai-mode',
        type=str,
        choices=['auto', 'gemini', 'opencv', 'disabled'],
        help='Mode AI enhancement (auto=Gemini+fallback, gemini=AI only, opencv=traditional only, disabled=no enhancement)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI enhancement completely (shortcut untuk --ai-mode disabled)'
    )
    
    parser.add_argument(
        '--ai-fallback',
        action='store_true',
        help='Enable fallback ke OpenCV jika Gemini AI gagal'
    )
    
    parser.add_argument(
        '--ai-skip-on-failure',
        action='store_true', 
        help='Skip enhancement jika AI gagal (lanjut tanpa enhancement)'
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        print("=" * 60)
        print("🎯 SISTEM TETHERED SHOOTING AI ENHANCED")
        print("   HafiPortrait Photography System")
        print("=" * 60)
        print()
        
        # Handle different modes
        event_selector = EventSelector()
        
        if args.list_events:
            print("📋 DAFTAR EVENT TERSEDIA")
            print("-" * 40)
            events = event_selector.fetch_all_events()
            event_selector.display_events_menu(events)
            return
        
        if args.test_events:
            print("🧪 TESTING EVENT SELECTION")
            print("-" * 40)
            selected_event_id = event_selector.select_event_interactive()
            if selected_event_id:
                print(f"✅ Test berhasil - Event terpilih: {selected_event_id}")
            else:
                print("❌ Test gagal - Tidak ada event terpilih")
            return
        
        if args.interactive:
            print("🎛️ INTERACTIVE SETUP MODE")
            print("-" * 40)
            
            interactive_setup = InteractiveSetup()
            config = interactive_setup.run_interactive_setup()
            
            if not config:
                print("❌ Interactive setup dibatalkan atau gagal")
                return
            
            # Apply configuration
            interactive_setup.apply_configuration()
            
            # Use event ID from interactive setup
            selected_event_id = config["event_id"]
            print(f"\n✅ Interactive setup completed!")
            print(f"🎯 Event terpilih: {selected_event_id}")
            
            # Skip manual AI configuration (already set in interactive)
            ai_mode_changed = True
            
        else:
            # === STEP 1: Determine Event ID ===
            selected_event_id = None
            
            if args.event_id:
                # Gunakan event ID dari command line
                selected_event_id = args.event_id
                print(f"🆔 Menggunakan Event ID dari command line: {selected_event_id}")
                
                # Validasi event ID exists
                events = event_selector.fetch_all_events()
                event_exists = any(event.get('id') == selected_event_id for event in events)
                
                if not event_exists:
                    print(f"❌ Event ID '{selected_event_id}' tidak ditemukan di database")
                    print("📋 Event yang tersedia:")
                    event_selector.display_events_menu(events[:5])
                    return
                
            elif args.auto_create:
                # Auto-create event baru
                print("🆕 Mode auto-create event...")
                selected_event_id = event_selector._create_new_event_interactive()
                
            else:
                # Interactive selection
                print("🎬 PILIH EVENT UNTUK TETHERED SHOOTING")
                print("-" * 40)
                selected_event_id = event_selector.select_event_interactive()
            
            if not selected_event_id:
                print("❌ Tidak ada event yang dipilih. Sistem dihentikan.")
                return
        
        print(f"\n✅ Event terpilih: {selected_event_id}")
        print(f"📋 Foto akan masuk ke tab 'Official' pada event ini")
        
        # === STEP 2: Apply AI Enhancement Options (only for non-interactive mode) ===
        if not args.interactive:
            ai_mode_changed = False
            
            if args.no_ai:
                Config.AI_ENHANCEMENT["enabled"] = False
                Config.AI_ENHANCEMENT["mode"] = "disabled"
                ai_mode_changed = True
                print(f"\n🚫 AI Enhancement disabled via --no-ai")
                
            elif args.ai_mode:
                Config.AI_ENHANCEMENT["mode"] = args.ai_mode
                if args.ai_mode == "disabled":
                    Config.AI_ENHANCEMENT["enabled"] = False
                else:
                    Config.AI_ENHANCEMENT["enabled"] = True
                ai_mode_changed = True
                print(f"\n🤖 AI Enhancement mode set to: {args.ai_mode}")
                
            if args.ai_fallback:
                Config.AI_ENHANCEMENT["fallback_to_opencv"] = True
                ai_mode_changed = True
                print(f"🔄 AI fallback to OpenCV enabled")
                
            if args.ai_skip_on_failure:
                Config.AI_ENHANCEMENT["skip_on_failure"] = True
                ai_mode_changed = True
                print(f"⏭️ AI skip on failure enabled")
        
        # Konfirmasi final
        print("\n" + "="*60)
        print("⚠️  KONFIRMASI AKHIR")
        print("="*60)
        print("Sistem akan mulai tethered shooting dengan konfigurasi:")
        print(f"🆔 Event ID: {selected_event_id}")
        print(f"🎯 Target: Tab 'Official' di halaman event")
        
        # AI Enhancement status
        ai_enabled = Config.AI_ENHANCEMENT["enabled"]
        ai_mode = Config.AI_ENHANCEMENT["mode"]
        ai_fallback = Config.AI_ENHANCEMENT["fallback_to_opencv"]
        ai_skip = Config.AI_ENHANCEMENT["skip_on_failure"]
        
        if not ai_enabled or ai_mode == "disabled":
            print(f"🚫 AI Enhancement: DISABLED")
        elif ai_mode == "opencv":
            print(f"🎨 AI Enhancement: OpenCV Traditional Only")
        elif ai_mode == "gemini":
            print(f"🤖 AI Enhancement: Google Gemini Only")
        else:  # auto
            print(f"🔄 AI Enhancement: Auto (Gemini + OpenCV fallback)")
        
        if ai_enabled and ai_mode != "disabled":
            print(f"   🛡️ Face Protection: Enabled")
            if ai_fallback:
                print(f"   🔄 OpenCV Fallback: Enabled")
            if ai_skip:
                print(f"   ⏭️ Skip on Failure: Enabled")
        
        print(f"🎨 Processing: LUT + Auto-crop + Watermark")
        print(f"🌐 Auto Upload: Aktif")
        print()
        
        confirm = input("❓ Lanjutkan dengan konfigurasi ini? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes', 'ya']:
            print("👋 Sistem dibatalkan oleh user")
            return
        
        # === STEP 2: Inisialisasi Sistem dengan Event ID ===
        print(f"\n🚀 Menginisialisasi sistem untuk event {selected_event_id}...")
        system = AutoCaptureSystem(event_id=selected_event_id)
        
        # Tampilkan status awal
        status = system.get_status()
        print("\n📋 Status Sistem:")
        print(f"  Selected Event: {selected_event_id}")
        print(f"  Camera Connected: {status['camera'].get('connected', False)}")
        print(f"  AI Model: {status['config']['ai_model']}")
        print(f"  Max Workers: {status['config']['max_workers']}")
        print(f"  Memory Limit: {status['config']['memory_limit']} MB")
        print()
        
        # === STEP 3: Mulai Sistem ===
        system.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistem dihentikan oleh pengguna")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
    finally:
        print("👋 Selamat tinggal!")

if __name__ == "__main__":
    main()