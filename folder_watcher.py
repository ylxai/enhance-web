#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Folder Watcher - Auto Process Copied Photos
===========================================

Script untuk watch folder dan otomatis memproses foto yang disalin ke folder.
Untuk testing tanpa kamera dengan cara copy file ke folder watch.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
import logging
import shutil
from pathlib import Path
from typing import Set, Optional
from concurrent.futures import ThreadPoolExecutor
import argparse

# Import modules
from config import Config
from gemini_enhancer import GeminiImageEnhancer
from image_processor import ImageProcessor
from face_detection import FaceProtectionMask
from web_integrator import WebIntegrator
from event_selector import EventSelector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FolderWatcher:
    """Watch folder dan proses foto yang disalin"""
    
    def __init__(self, event_id: Optional[str] = None):
        self.watch_dir = Config.BASE_DIR / "watch_folder"
        self.processed_files: Set[str] = set()
        self.is_running = False
        self.event_id = event_id
        
        # Stats
        self.stats = {
            "total_detected": 0,
            "total_processed": 0,
            "total_uploaded": 0,
            "total_errors": 0,
            "start_time": None
        }
        
        print("👁️ FOLDER WATCHER - Auto Process Copied Photos")
        print("=" * 60)
        
        # Setup directories
        self._setup_directories()
        
        # Initialize components
        self._init_components()
    
    def _setup_directories(self):
        """Setup direktori yang diperlukan"""
        Config.create_directories()
        
        # Buat watch folder
        self.watch_dir.mkdir(exist_ok=True)
        
        print(f"📁 Watch folder: {self.watch_dir}")
        print(f"📁 Processed output: {Config.PROCESSED_DIR}")
        print(f"📁 Backup folder: {Config.BACKUP_JPG_DIR}")
    
    def _init_components(self):
        """Inisialisasi komponen processing"""
        try:
            print("\n🔧 Initializing processing components...")
            
            # Face detection
            self.face_detector = FaceProtectionMask()
            print("  ✅ Face detector ready")
            
            # AI enhancer
            self.ai_enhancer = GeminiImageEnhancer()
            print("  ✅ AI enhancer ready")
            
            # Image processor
            self.image_processor = ImageProcessor()
            print("  ✅ Image processor ready")
            
            # Web integrator
            self.web_integrator = WebIntegrator()
            if self.web_integrator.test_connection():
                print("  ✅ Web integrator ready")
            else:
                print("  ⚠️ Web integrator connection failed")
            
            # Thread pool for parallel processing
            self.executor = ThreadPoolExecutor(max_workers=Config.PERFORMANCE["max_workers"])
            print(f"  ✅ Thread pool ready ({Config.PERFORMANCE['max_workers']} workers)")
            
        except Exception as e:
            print(f"❌ Error initializing components: {e}")
            raise
    
    def scan_folder(self) -> Set[Path]:
        """Scan folder untuk file baru"""
        try:
            current_files = set()
            
            # Scan untuk file gambar
            image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
            
            for ext in image_extensions:
                current_files.update(self.watch_dir.glob(f"*{ext}"))
                current_files.update(self.watch_dir.glob(f"*{ext.upper()}"))
            
            # Filter file yang belum diproses
            new_files = set()
            for file_path in current_files:
                file_key = f"{file_path.name}_{file_path.stat().st_size}"
                if file_key not in self.processed_files:
                    new_files.add(file_path)
                    self.processed_files.add(file_key)
            
            return new_files
            
        except Exception as e:
            logger.error(f"Error scanning folder: {e}")
            return set()
    
    def process_image(self, image_path: Path) -> bool:
        """Process single image dengan full pipeline"""
        try:
            processing_start = time.time()
            logger.info(f"🔄 Processing: {image_path.name}")
            
            # Backup original
            self._backup_original(image_path)
            
            # === STEP 1: AI Enhancement ===
            logger.info("Step 1: AI Enhancement...")
            temp_enhanced = Config.TEMP_DIR / f"enhanced_{image_path.stem}.jpg"
            
            success, enhanced_path = self.ai_enhancer.enhance_image(image_path, temp_enhanced)
            if not success or not enhanced_path:
                logger.error(f"AI Enhancement failed for {image_path.name}")
                enhanced_path = image_path  # Fallback to original
            
            # === STEP 2: Load enhanced image ===
            import cv2
            enhanced_image = cv2.imread(str(enhanced_path))
            if enhanced_image is None:
                logger.error(f"Failed to load enhanced image: {enhanced_path}")
                return False
            
            # === STEP 3: Full Processing Pipeline ===
            logger.info("Step 2: Full Processing Pipeline...")
            final_filename = f"processed_{image_path.stem}_{int(time.time())}.jpg"
            final_path = Config.PROCESSED_DIR / final_filename
            
            success, result_path = self.image_processor.process_full_pipeline(enhanced_image, final_path)
            
            if not success:
                logger.error(f"Processing pipeline failed for {image_path.name}")
                return False
            
            # === STEP 4: Web Upload ===
            upload_success = False
            if Config.WEB_INTEGRATION["enabled"] and Config.WEB_INTEGRATION["upload_to_web"]:
                logger.info("Step 3: Web Upload...")
                upload_success = self.web_integrator.upload_photo(result_path, self.event_id)
                
                if upload_success:
                    logger.info(f"✅ Uploaded to web: {result_path.name}")
                    self.stats["total_uploaded"] += 1
                else:
                    logger.warning(f"⚠️ Upload failed: {result_path.name}")
            
            # === STEP 5: Cleanup ===
            if Config.PERFORMANCE["temp_cleanup"]:
                try:
                    if temp_enhanced.exists() and temp_enhanced != image_path:
                        temp_enhanced.unlink()
                except Exception as e:
                    logger.warning(f"Cleanup error: {e}")
            
            processing_time = time.time() - processing_start
            logger.info(f"✅ Processing completed in {processing_time:.2f}s: {result_path}")
            
            self.stats["total_processed"] += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {image_path.name}: {e}")
            self.stats["total_errors"] += 1
            return False
    
    def _backup_original(self, image_path: Path):
        """Backup file original"""
        try:
            backup_path = Config.BACKUP_JPG_DIR / image_path.name
            shutil.copy2(image_path, backup_path)
            logger.info(f"💾 Backup: {image_path.name}")
        except Exception as e:
            logger.warning(f"Backup failed: {e}")
    
    def watch_and_process(self, scan_interval: float = 2.0):
        """Main watch loop"""
        print(f"\n👁️ STARTING FOLDER WATCHER")
        print("-" * 40)
        print(f"📁 Watching: {self.watch_dir}")
        print(f"⏱️ Scan interval: {scan_interval}s")
        print(f"🎯 Event ID: {self.event_id or 'Auto-detect'}")
        print(f"📋 Copy photos to watch folder to start processing")
        print(f"🛑 Press Ctrl+C to stop")
        print("-" * 40)
        
        self.is_running = True
        self.stats["start_time"] = time.time()
        
        try:
            while self.is_running:
                # Scan for new files
                new_files = self.scan_folder()
                
                if new_files:
                    self.stats["total_detected"] += len(new_files)
                    logger.info(f"📁 Detected {len(new_files)} new files")
                    
                    # Process files
                    for file_path in new_files:
                        if self.is_running:
                            future = self.executor.submit(self.process_image, file_path)
                            # Bisa add callback di sini jika perlu
                
                # Show stats periodically
                if int(time.time()) % 30 == 0:  # Every 30 seconds
                    self._show_stats()
                
                time.sleep(scan_interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Folder watcher stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in watch loop: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop watcher dan cleanup"""
        self.is_running = False
        
        print(f"\n🛑 Stopping folder watcher...")
        
        # Shutdown thread pool
        if hasattr(self, 'executor'):
            logger.info("Waiting for processing to complete...")
            self.executor.shutdown(wait=True, timeout=30)
        
        # Final stats
        self._show_final_stats()
    
    def _show_stats(self):
        """Tampilkan statistik saat ini"""
        if self.stats["start_time"]:
            runtime = time.time() - self.stats["start_time"]
            runtime_min = runtime / 60
            
            print(f"\n📊 Stats: Detected={self.stats['total_detected']}, "
                  f"Processed={self.stats['total_processed']}, "
                  f"Uploaded={self.stats['total_uploaded']}, "
                  f"Errors={self.stats['total_errors']}, "
                  f"Runtime={runtime_min:.1f}min")
    
    def _show_final_stats(self):
        """Tampilkan statistik final"""
        if self.stats["start_time"]:
            total_runtime = time.time() - self.stats["start_time"]
            
            print(f"\n📊 FINAL STATISTICS")
            print("-" * 40)
            print(f"⏱️ Total Runtime: {total_runtime/60:.1f} minutes")
            print(f"📁 Files Detected: {self.stats['total_detected']}")
            print(f"✅ Files Processed: {self.stats['total_processed']}")
            print(f"🌐 Files Uploaded: {self.stats['total_uploaded']}")
            print(f"❌ Errors: {self.stats['total_errors']}")
            
            if self.stats["total_processed"] > 0:
                avg_time = total_runtime / self.stats["total_processed"]
                print(f"⚡ Average Processing Time: {avg_time:.1f}s per file")
            
            success_rate = (self.stats["total_processed"] / max(1, self.stats["total_detected"])) * 100
            print(f"📈 Success Rate: {success_rate:.1f}%")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Folder Watcher - Auto Process Copied Photos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python3 folder_watcher.py                           # Auto-detect event
  python3 folder_watcher.py --event-id cm123          # Specific event
  python3 folder_watcher.py --interval 5              # 5 second scan interval
  python3 folder_watcher.py --no-ai                   # Disable AI enhancement
  
Workflow:
  1. Start folder watcher
  2. Copy photos ke folder 'watch_folder/'
  3. Photos otomatis diproses dan diupload
  4. Hasil disimpan di 'processed/'
"""
    )
    
    parser.add_argument(
        '--event-id',
        type=str,
        help='Event ID untuk upload (akan auto-detect jika tidak disediakan)'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='Scan interval dalam detik (default: 2.0)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Disable AI enhancement'
    )
    
    parser.add_argument(
        '--ai-mode',
        type=str,
        choices=['auto', 'gemini', 'opencv', 'disabled'],
        help='AI enhancement mode'
    )
    
    args = parser.parse_args()
    
    try:
        # Apply AI settings
        if args.no_ai:
            Config.AI_ENHANCEMENT["enabled"] = False
            Config.AI_ENHANCEMENT["mode"] = "disabled"
            print("🚫 AI Enhancement disabled")
        elif args.ai_mode:
            Config.AI_ENHANCEMENT["mode"] = args.ai_mode
            if args.ai_mode == "disabled":
                Config.AI_ENHANCEMENT["enabled"] = False
            print(f"🤖 AI Enhancement mode: {args.ai_mode}")
        
        # Get event ID
        event_id = args.event_id
        if not event_id:
            print("📅 Auto-detecting active event...")
            event_selector = EventSelector()
            event_id = event_selector.get_active_event()
            
            if not event_id:
                print("⚠️ No active event found, will auto-create on first upload")
        
        # Initialize and start watcher
        watcher = FolderWatcher(event_id=event_id)
        watcher.watch_and_process(scan_interval=args.interval)
        
    except KeyboardInterrupt:
        print("\n👋 Folder watcher cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()