# Camera Controller untuk gPhoto2 Tethered Shooting
# =================================================

import subprocess
import time
import logging
import threading
import queue
from pathlib import Path
from typing import Optional, Tuple, List, Callable
import shutil
import re
from config import Config

logger = logging.getLogger(__name__)

class CameraController:
    """Class untuk kontrol kamera DSLR menggunakan gPhoto2"""
    
    def __init__(self, callback_func: Optional[Callable] = None):
        """
        Inisialisasi camera controller
        
        Args:
            callback_func: Function yang dipanggil ketika foto baru tersedia
        """
        self.callback_func = callback_func
        self.is_connected = False
        self.is_capturing = False
        self.capture_thread = None
        self.file_queue = queue.Queue()
        
        # Check gPhoto2 installation
        self._check_gphoto2()
        
        # Detect dan connect camera
        self._detect_camera()
        
        logger.info("Camera controller berhasil diinisialisasi")
    
    def _check_gphoto2(self):
        """Check apakah gPhoto2 terinstall"""
        try:
            result = subprocess.run(['gphoto2', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_info = result.stdout.split('\n')[0]
                logger.info(f"✅ gPhoto2 terdeteksi: {version_info}")
            else:
                raise Exception("gPhoto2 tidak ditemukan")
                
        except FileNotFoundError:
            raise Exception(
                "gPhoto2 tidak terinstall. Install dengan:\n"
                "Ubuntu/Debian: sudo apt-get install gphoto2 libgphoto2-dev\n"
                "CentOS/RHEL: sudo yum install gphoto2 libgphoto2-devel"
            )
        except Exception as e:
            raise Exception(f"Error checking gPhoto2: {e}")
    
    def _detect_camera(self):
        """Deteksi dan connect ke kamera"""
        try:
            logger.info("Mendeteksi kamera yang terhubung...")
            
            # Detect camera
            result = subprocess.run(['gphoto2', '--auto-detect'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                raise Exception(f"Gagal deteksi kamera: {result.stderr}")
            
            # Parse output untuk cari kamera
            lines = result.stdout.strip().split('\n')
            cameras = []
            
            for line in lines[2:]:  # Skip header lines
                if line.strip() and 'usb:' in line:
                    cameras.append(line.strip())
            
            if not cameras:
                raise Exception("Tidak ada kamera terdeteksi. Pastikan kamera terhubung dan dalam mode yang tepat.")
            
            logger.info(f"✅ Kamera terdeteksi: {cameras[0]}")
            
            # Test koneksi dengan get camera summary
            summary_result = subprocess.run(['gphoto2', '--summary'], 
                                          capture_output=True, text=True, timeout=15)
            
            if summary_result.returncode == 0:
                self.is_connected = True
                camera_info = summary_result.stdout.split('\n')[0:3]
                logger.info(f"✅ Koneksi kamera berhasil:\n" + '\n'.join(camera_info))
            else:
                raise Exception(f"Gagal connect ke kamera: {summary_result.stderr}")
                
        except Exception as e:
            logger.error(f"Error saat deteksi kamera: {e}")
            self.is_connected = False
            raise
    
    def configure_camera(self):
        """Konfigurasi kamera untuk tethered shooting"""
        try:
            logger.info("Mengkonfigurasi kamera untuk tethered shooting...")
            
            # Set capture target ke memory card dan PC
            config_commands = [
                ['gphoto2', '--set-config', 'capturetarget=1'],  # 0=Memory card, 1=Internal RAM
                ['gphoto2', '--set-config', 'imageformat=RAW+JPEG'],  # RAW + JPEG
                ['gphoto2', '--set-config', 'imageformatsd=RAW+JPEG'],  # For SD card
            ]
            
            for cmd in config_commands:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        logger.info(f"✅ Konfigurasi: {' '.join(cmd[2:])}")
                    else:
                        logger.warning(f"⚠️ Gagal konfigurasi {' '.join(cmd[2:])}: {result.stderr}")
                except Exception as e:
                    logger.warning(f"⚠️ Error konfigurasi {' '.join(cmd[2:])}: {e}")
            
            # Dapatkan informasi kamera current settings
            self._get_camera_settings()
            
        except Exception as e:
            logger.error(f"Error saat konfigurasi kamera: {e}")
    
    def _get_camera_settings(self):
        """Dapatkan current settings kamera"""
        try:
            settings_cmd = ['gphoto2', '--get-config', 'imageformat']
            result = subprocess.run(settings_cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info("Current camera settings:")
                for line in result.stdout.split('\n')[:10]:  # Tampilkan beberapa baris pertama
                    if line.strip():
                        logger.info(f"  {line}")
            
        except Exception as e:
            logger.warning(f"Gagal mendapatkan camera settings: {e}")
    
    def capture_single(self, filename_prefix: str = "capture") -> Tuple[bool, List[Path]]:
        """
        Capture single foto
        
        Args:
            filename_prefix: Prefix untuk nama file
            
        Returns:
            Tuple (success, list_of_downloaded_files)
        """
        try:
            if not self.is_connected:
                logger.error("Kamera tidak terhubung")
                return False, []
            
            logger.info("Mengambil foto...")
            
            # Buat timestamp untuk filename
            timestamp = int(time.time())
            
            # Capture dan download
            capture_cmd = [
                'gphoto2', 
                '--capture-image-and-download',
                '--filename', f"{filename_prefix}_{timestamp}_%n.%C"
            ]
            
            result = subprocess.run(capture_cmd, 
                                  capture_output=True, text=True, 
                                  timeout=30, cwd=Config.CAPTURE_DIR)
            
            if result.returncode != 0:
                logger.error(f"Gagal capture: {result.stderr}")
                return False, []
            
            # Parse output untuk dapatkan nama file yang didownload
            downloaded_files = self._parse_capture_output(result.stdout)
            
            if downloaded_files:
                logger.info(f"✅ Foto berhasil diambil: {len(downloaded_files)} file")
                for file_path in downloaded_files:
                    logger.info(f"  - {file_path}")
                
                # Backup files immediately
                self._backup_files(downloaded_files)
                
                return True, downloaded_files
            else:
                logger.error("Tidak ada file yang berhasil didownload")
                return False, []
                
        except subprocess.TimeoutExpired:
            logger.error("Timeout saat capture foto")
            return False, []
        except Exception as e:
            logger.error(f"Error saat capture: {e}")
            return False, []
    
    def _parse_capture_output(self, output: str) -> List[Path]:
        """Parse output gPhoto2 untuk dapatkan nama file yang didownload"""
        downloaded_files = []
        
        for line in output.split('\n'):
            # Look for download confirmation lines
            if 'Saving file as' in line:
                # Extract filename dari output seperti: "Saving file as capture_123456_001.CR2"
                match = re.search(r'Saving file as (.+)', line)
                if match:
                    filename = match.group(1).strip()
                    file_path = Config.CAPTURE_DIR / filename
                    if file_path.exists():
                        downloaded_files.append(file_path)
        
        return downloaded_files
    
    def _backup_files(self, files: List[Path]):
        """Backup files ke folder backup"""
        try:
            for file_path in files:
                # Tentukan backup directory berdasarkan extension
                if file_path.suffix.lower() in ['.cr2', '.nef', '.arw', '.raw']:
                    backup_dir = Config.BACKUP_RAW_DIR
                else:
                    backup_dir = Config.BACKUP_JPG_DIR
                
                # Copy file ke backup
                backup_path = backup_dir / file_path.name
                shutil.copy2(file_path, backup_path)
                
                logger.info(f"✅ Backup: {file_path.name} -> {backup_dir}")
                
        except Exception as e:
            logger.error(f"Error saat backup files: {e}")
    
    def start_tethered_capture(self):
        """Mulai tethered capture mode (menunggu trigger dari kamera)"""
        if self.is_capturing:
            logger.warning("Tethered capture sudah berjalan")
            return
        
        self.is_capturing = True
        self.capture_thread = threading.Thread(target=self._tethered_capture_loop, daemon=True)
        self.capture_thread.start()
        
        logger.info("🔄 Tethered capture mode dimulai - menunggu trigger dari kamera...")
    
    def stop_tethered_capture(self):
        """Stop tethered capture mode"""
        if self.is_capturing:
            self.is_capturing = False
            if self.capture_thread:
                self.capture_thread.join(timeout=5)
            logger.info("⏹️ Tethered capture mode dihentikan")
    
    def _tethered_capture_loop(self):
        """Main loop untuk tethered capture"""
        consecutive_errors = 0
        max_consecutive_errors = 5
        
        while self.is_capturing:
            try:
                logger.info("🎯 Menunggu trigger shutter dari kamera...")
                
                # Wait for camera trigger dengan timeout
                capture_cmd = [
                    'gphoto2',
                    '--capture-tethered',
                    '--hook-script=echo "CAPTURE_START"; echo "File: %f"',
                    '--filename', 'tethered_%n.%C'
                ]
                
                # Run dengan timeout untuk allow graceful shutdown
                process = subprocess.Popen(
                    capture_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=Config.CAPTURE_DIR
                )
                
                # Monitor process output
                while self.is_capturing and process.poll() is None:
                    try:
                        output = process.stdout.readline()
                        if output:
                            self._process_tethered_output(output.strip())
                        time.sleep(0.1)
                    except Exception as e:
                        logger.error(f"Error reading tethered output: {e}")
                        break
                
                # Clean up process
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)
                
                consecutive_errors = 0  # Reset error counter on successful operation
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Error dalam tethered capture loop: {e} (error #{consecutive_errors})")
                
                if consecutive_errors >= max_consecutive_errors:
                    logger.error("Terlalu banyak error berturut-turut, menghentikan tethered capture")
                    self.is_capturing = False
                    break
                
                # Wait sebelum retry
                time.sleep(5)
        
        logger.info("Tethered capture loop selesai")
    
    def _process_tethered_output(self, output: str):
        """Process output dari tethered capture"""
        try:
            if "CAPTURE_START" in output:
                logger.info("📸 Shutter trigger terdeteksi!")
            
            elif "File:" in output:
                # Extract filename
                filename = output.replace("File:", "").strip()
                file_path = Config.CAPTURE_DIR / filename
                
                if file_path.exists():
                    logger.info(f"📁 File berhasil didownload: {filename}")
                    
                    # Backup immediately
                    self._backup_files([file_path])
                    
                    # Tambahkan ke queue untuk processing
                    self.file_queue.put(file_path)
                    
                    # Call callback function jika ada
                    if self.callback_func:
                        try:
                            self.callback_func(file_path)
                        except Exception as e:
                            logger.error(f"Error dalam callback function: {e}")
            
        except Exception as e:
            logger.error(f"Error processing tethered output: {e}")
    
    def get_next_captured_file(self, timeout: Optional[float] = None) -> Optional[Path]:
        """
        Dapatkan file yang baru di-capture dari queue
        
        Args:
            timeout: Timeout dalam detik (None = blocking)
            
        Returns:
            Path ke file atau None jika timeout
        """
        try:
            return self.file_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_camera_status(self) -> dict:
        """Dapatkan status kamera"""
        return {
            "connected": self.is_connected,
            "capturing": self.is_capturing,
            "queue_size": self.file_queue.qsize()
        }
    
    def disconnect(self):
        """Disconnect dari kamera"""
        self.stop_tethered_capture()
        self.is_connected = False
        logger.info("Kamera disconnected")

def test_camera():
    """Test function untuk camera controller"""
    try:
        print("Testing camera controller...")
        
        # Test callback function
        def capture_callback(file_path):
            print(f"📸 Callback: File baru tersedia - {file_path}")
        
        # Inisialisasi camera
        camera = CameraController(callback_func=capture_callback)
        
        # Konfigurasi camera
        camera.configure_camera()
        
        # Test single capture
        print("\n1. Testing single capture...")
        success, files = camera.capture_single("test")
        if success:
            print(f"✅ Single capture berhasil: {len(files)} files")
        else:
            print("❌ Single capture gagal")
        
        # Test tethered mode (untuk demo, hanya 10 detik)
        print("\n2. Testing tethered mode selama 10 detik...")
        camera.start_tethered_capture()
        
        print("Silakan tekan shutter kamera dalam 10 detik...")
        start_time = time.time()
        
        while time.time() - start_time < 10:
            file_path = camera.get_next_captured_file(timeout=1)
            if file_path:
                print(f"📁 File baru dari tethered: {file_path}")
            
            status = camera.get_camera_status()
            print(f"Status: Connected={status['connected']}, Capturing={status['capturing']}, Queue={status['queue_size']}")
        
        camera.stop_tethered_capture()
        print("✅ Test tethered mode selesai")
        
        # Disconnect
        camera.disconnect()
        print("✅ Camera test selesai")
        
    except Exception as e:
        print(f"❌ Error during camera test: {e}")

if __name__ == "__main__":
    test_camera()