#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Manual Trigger - gPhoto2 Shutter Control
========================================

Script sederhana untuk trigger shutter kamera secara manual menggunakan gPhoto2.
Untuk testing dan debugging tanpa full automation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import subprocess
import time
import logging
from pathlib import Path

# Import modules
from config import Config

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ManualTrigger:
    """Manual camera trigger menggunakan gPhoto2"""
    
    def __init__(self):
        self.capture_count = 0
        print("📸 MANUAL TRIGGER - gPhoto2 Shutter Control")
        print("=" * 50)
        
        # Buat direktori jika belum ada
        Config.create_directories()
        
    def check_camera_connection(self) -> bool:
        """Check koneksi kamera"""
        try:
            print("🔍 Checking camera connection...")
            
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                cameras = []
                
                for line in lines[2:]:  # Skip header
                    if line.strip() and 'usb:' in line:
                        cameras.append(line.strip())
                
                if cameras:
                    print(f"✅ Camera detected: {cameras[0]}")
                    return True
                else:
                    print("❌ No camera detected")
                    return False
            else:
                print(f"❌ gPhoto2 error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ gPhoto2 not installed. Install with:")
            print("   Ubuntu/Debian: sudo apt-get install gphoto2")
            return False
        except Exception as e:
            print(f"❌ Error checking camera: {e}")
            return False
    
    def get_camera_summary(self):
        """Tampilkan summary kamera"""
        try:
            print("\n📋 Camera Summary:")
            print("-" * 30)
            
            result = subprocess.run(['gphoto2', '--summary'], 
                                  capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # Tampilkan beberapa baris pertama yang penting
                lines = result.stdout.split('\n')
                for line in lines[:10]:
                    if line.strip():
                        print(f"  {line}")
            else:
                print(f"  Error: {result.stderr}")
                
        except Exception as e:
            print(f"  Error: {e}")
    
    def configure_camera_basic(self):
        """Konfigurasi basic kamera untuk manual shooting"""
        try:
            print("\n⚙️ Configuring camera...")
            
            config_commands = [
                ['gphoto2', '--set-config', 'capturetarget=1'],  # Internal RAM
                ['gphoto2', '--set-config', 'imageformat=RAW+JPEG'],
            ]
            
            for cmd in config_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        print(f"  ✅ {' '.join(cmd[2:])}")
                    else:
                        print(f"  ⚠️ {' '.join(cmd[2:])}: {result.stderr}")
                except Exception as e:
                    print(f"  ⚠️ {' '.join(cmd[2:])}: {e}")
            
        except Exception as e:
            print(f"❌ Error configuring camera: {e}")
    
    def capture_single(self) -> bool:
        """Capture single foto"""
        try:
            self.capture_count += 1
            timestamp = int(time.time())
            
            print(f"\n📸 Capturing photo #{self.capture_count}...")
            
            # Capture dan download
            capture_cmd = [
                'gphoto2', 
                '--capture-image-and-download',
                '--filename', f'manual_{timestamp}_%n.%C'
            ]
            
            start_time = time.time()
            result = subprocess.run(capture_cmd, 
                                  capture_output=True, text=True, 
                                  timeout=30, cwd=Config.CAPTURE_DIR)
            
            capture_time = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ Capture successful in {capture_time:.2f}s")
                
                # Parse output untuk dapatkan file yang didownload
                downloaded_files = []
                for line in result.stdout.split('\n'):
                    if 'Saving file as' in line:
                        import re
                        match = re.search(r'Saving file as (.+)', line)
                        if match:
                            filename = match.group(1).strip()
                            file_path = Config.CAPTURE_DIR / filename
                            if file_path.exists():
                                downloaded_files.append(file_path)
                                print(f"  📁 Downloaded: {filename}")
                
                # Backup files
                if downloaded_files:
                    self._backup_files(downloaded_files)
                
                return True
            else:
                print(f"❌ Capture failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Capture timeout (30s)")
            return False
        except Exception as e:
            print(f"❌ Capture error: {e}")
            return False
    
    def _backup_files(self, files):
        """Backup files ke folder backup"""
        try:
            import shutil
            
            for file_path in files:
                if file_path.suffix.lower() in ['.cr2', '.nef', '.arw', '.raw']:
                    backup_dir = Config.BACKUP_RAW_DIR
                else:
                    backup_dir = Config.BACKUP_JPG_DIR
                
                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                print(f"  💾 Backup: {file_path.name} -> {backup_dir.name}/")
                
        except Exception as e:
            print(f"⚠️ Backup error: {e}")
    
    def interactive_mode(self):
        """Mode interaktif untuk manual trigger"""
        print(f"\n🎯 INTERACTIVE MANUAL TRIGGER MODE")
        print("-" * 40)
        print("Commands:")
        print("  c, capture - Take a photo")
        print("  s, summary - Show camera summary")
        print("  r, reconfig - Reconfigure camera")
        print("  q, quit - Exit")
        print("-" * 40)
        
        while True:
            try:
                command = input(f"\n📸 Command (capture #{self.capture_count + 1}): ").strip().lower()
                
                if command in ['c', 'capture', '']:
                    self.capture_single()
                    
                elif command in ['s', 'summary']:
                    self.get_camera_summary()
                    
                elif command in ['r', 'reconfig']:
                    self.configure_camera_basic()
                    
                elif command in ['q', 'quit', 'exit']:
                    print("👋 Exiting manual trigger mode")
                    break
                    
                else:
                    print("⚠️ Unknown command. Use: c/capture, s/summary, r/reconfig, q/quit")
                    
            except KeyboardInterrupt:
                print("\n👋 Manual trigger interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def burst_mode(self, count: int = 5, interval: float = 2.0):
        """Burst mode - multiple captures dengan interval"""
        print(f"\n📸 BURST MODE: {count} photos, {interval}s interval")
        print("-" * 40)
        
        success_count = 0
        
        for i in range(count):
            print(f"\n📸 Burst {i+1}/{count}")
            
            if self.capture_single():
                success_count += 1
            
            if i < count - 1:  # Tidak sleep setelah foto terakhir
                print(f"⏱️ Waiting {interval}s...")
                time.sleep(interval)
        
        print(f"\n📊 Burst completed: {success_count}/{count} successful")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manual Trigger - gPhoto2 Shutter Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python3 manual_trigger.py                    # Interactive mode
  python3 manual_trigger.py --capture          # Single capture
  python3 manual_trigger.py --burst 10         # Burst 10 photos
  python3 manual_trigger.py --burst 5 --interval 3  # 5 photos, 3s interval
        """
    )
    
    parser.add_argument(
        '--capture',
        action='store_true',
        help='Take single photo and exit'
    )
    
    parser.add_argument(
        '--burst',
        type=int,
        help='Burst mode - number of photos to take'
    )
    
    parser.add_argument(
        '--interval',
        type=float,
        default=2.0,
        help='Interval between burst photos (seconds, default: 2.0)'
    )
    
    args = parser.parse_args()
    
    try:
        trigger = ManualTrigger()
        
        # Check camera connection
        if not trigger.check_camera_connection():
            print("\n❌ Cannot proceed without camera connection")
            return
        
        # Get camera info
        trigger.get_camera_summary()
        
        # Configure camera
        trigger.configure_camera_basic()
        
        # Execute mode
        if args.capture:
            print(f"\n📸 SINGLE CAPTURE MODE")
            trigger.capture_single()
            
        elif args.burst:
            trigger.burst_mode(args.burst, args.interval)
            
        else:
            trigger.interactive_mode()
        
        print(f"\n📊 Session Summary:")
        print(f"  Total captures: {trigger.capture_count}")
        print(f"  Files saved to: {Config.CAPTURE_DIR}")
        print(f"  Backups saved to: {Config.BACKUP_RAW_DIR} & {Config.BACKUP_JPG_DIR}")
        
    except KeyboardInterrupt:
        print("\n👋 Manual trigger cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

if __name__ == "__main__":
    main()