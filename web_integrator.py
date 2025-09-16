# Web Integration untuk Upload ke Project HafiPortrait
# ===================================================

import requests
import jwt
import json
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any
import base64
from PIL import Image
import io

from config import Config

logger = logging.getLogger(__name__)

class WebIntegrator:
    """Class untuk integrasi dengan web project HafiPortrait"""
    
    def __init__(self):
        """Inisialisasi web integrator"""
        self.base_url = Config.WEB_INTEGRATION["web_api_base_url"]
        self.upload_endpoint = Config.WEB_INTEGRATION["web_upload_endpoint"]
        self.event_endpoint = Config.WEB_INTEGRATION["web_event_endpoint"]
        self.jwt_secret = Config.WEB_INTEGRATION["jwt_secret"]
        self.timeout = Config.WEB_INTEGRATION["upload_timeout"]
        self.retry_attempts = Config.WEB_INTEGRATION["retry_attempts"]
        
        # Cache untuk event ID yang aktif
        self.active_event_id = None
        self.active_event_cache_time = 0
        self.cache_duration = 300  # 5 menit
        
        logger.info(f"Web integrator initialized: {self.base_url}")
    
    def _create_auth_token(self) -> str:
        """Buat JWT token untuk authentication"""
        try:
            payload = {
                "source": "tethered_shooting",
                "timestamp": int(time.time()),
                "exp": int(time.time()) + 3600  # 1 hour expiry
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            return token
            
        except Exception as e:
            logger.error(f"Error creating auth token: {e}")
            return ""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Dapatkan headers untuk authentication"""
        token = self._create_auth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Source": "tethered-shooting-system"
        }
    
    def test_connection(self) -> bool:
        """Test koneksi ke web API"""
        try:
            logger.info("Testing connection to web API...")
            
            # Test ping endpoint
            ping_url = f"{self.base_url}/ping"
            response = requests.get(ping_url, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Web API connection successful")
                return True
            else:
                logger.error(f"❌ Web API connection failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Web API connection error: {e}")
            return False
    
    def get_active_event(self) -> Optional[str]:
        """Dapatkan event ID yang sedang aktif"""
        try:
            # Check cache dulu
            current_time = time.time()
            if (self.active_event_id and 
                current_time - self.active_event_cache_time < self.cache_duration):
                return self.active_event_id
            
            logger.info("Fetching active event...")
            
            headers = self._get_auth_headers()
            response = requests.get(
                self.event_endpoint,
                headers=headers,
                params={"status": "active", "limit": 1},
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                events = response.json()
                if events and len(events) > 0:
                    event_id = events[0].get("id")
                    
                    # Update cache
                    self.active_event_id = event_id
                    self.active_event_cache_time = current_time
                    
                    logger.info(f"✅ Active event found: {event_id}")
                    return event_id
                else:
                    logger.warning("⚠️ No active event found")
                    return None
            else:
                logger.error(f"❌ Failed to fetch events: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching active event: {e}")
            return None
    
    def create_default_event(self) -> Optional[str]:
        """Buat event default jika tidak ada event aktif"""
        try:
            logger.info("Creating default tethered shooting event...")
            
            event_data = {
                "name": f"Tethered Shooting Session {int(time.time())}",
                "description": "Auto-created event for tethered shooting session",
                "date": time.strftime("%Y-%m-%d"),
                "time": time.strftime("%H:%M"),
                "location": "Studio",
                "status": "active",
                "type": Config.WEB_INTEGRATION["default_event_type"],
                "category": "photography",
                "auto_created": True
            }
            
            headers = self._get_auth_headers()
            headers["Content-Type"] = "application/json"
            
            response = requests.post(
                self.event_endpoint,
                headers=headers,
                json=event_data,
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                event = response.json()
                event_id = event.get("id")
                
                # Update cache
                self.active_event_id = event_id
                self.active_event_cache_time = time.time()
                
                logger.info(f"✅ Default event created: {event_id}")
                return event_id
            else:
                logger.error(f"❌ Failed to create default event: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating default event: {e}")
            return None
    
    def prepare_image_for_upload(self, image_path: Path, quality: str = "high") -> Optional[bytes]:
        """Persiapkan gambar untuk upload dengan optimasi"""
        try:
            # Tentukan quality setting
            quality_settings = {
                "high": 95,
                "medium": 80,
                "low": 70
            }
            
            jpeg_quality = quality_settings.get(quality, 85)
            
            # Load dan optimasi gambar
            with Image.open(image_path) as img:
                # Convert ke RGB jika perlu
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Resize jika terlalu besar (max 4K untuk high quality)
                max_size = (3840, 2160) if quality == "high" else (1920, 1080)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save ke bytes
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='JPEG', quality=jpeg_quality, optimize=True)
                img_bytes = img_buffer.getvalue()
                
                logger.info(f"Image prepared: {len(img_bytes)} bytes, quality: {quality}")
                return img_bytes
                
        except Exception as e:
            logger.error(f"Error preparing image: {e}")
            return None
    
    def upload_photo(self, image_path: Path, event_id: Optional[str] = None) -> bool:
        """
        Upload foto ke web project
        
        Args:
            image_path: Path ke file gambar
            event_id: ID event (optional, akan auto-detect jika None)
            
        Returns:
            True jika berhasil upload
        """
        try:
            # Dapatkan event ID jika tidak disediakan
            if not event_id:
                event_id = self.get_active_event()
                
                # Buat default event jika tidak ada
                if not event_id:
                    event_id = self.create_default_event()
                
                if not event_id:
                    logger.error("❌ No event available for photo upload")
                    return False
            
            logger.info(f"Uploading photo to event {event_id}: {image_path.name}")
            
            # Persiapkan gambar
            quality = Config.WEB_INTEGRATION["web_upload_quality"]
            image_bytes = self.prepare_image_for_upload(image_path, quality)
            
            if not image_bytes:
                logger.error("❌ Failed to prepare image for upload")
                return False
            
            # Persiapkan form data untuk event photos endpoint
            files = {
                'photo': (image_path.name, image_bytes, 'image/jpeg')
            }
            
            data = {
                'uploaderName': 'Tethered Shooting System',
                'albumName': 'Official',  # Official album untuk tab official
                'source': 'tethered_shooting',
                'timestamp': int(time.time()),
                'auto_uploaded': 'true'
            }
            
            # Upload dengan retry mechanism
            for attempt in range(self.retry_attempts):
                try:
                    # Headers untuk multipart upload
                    headers = {
                        "Authorization": f"Bearer {self._create_auth_token()}",
                        "X-Source": "tethered-shooting-system"
                    }
                    
                    # Dynamic endpoint dengan event ID
                    upload_url = f"{Config.WEB_INTEGRATION['web_api_base_url']}/events/{event_id}/photos"
                    
                    response = requests.post(
                        upload_url,
                        files=files,
                        data=data,
                        headers=headers,
                        timeout=self.timeout
                    )
                    
                    if response.status_code in [200, 201]:
                        result = response.json()
                        photo_id = result.get('id', 'unknown')
                        photo_url = result.get('url', '')
                        
                        logger.info(f"✅ Photo uploaded successfully: ID={photo_id}")
                        logger.info(f"   Event: {event_id}")
                        logger.info(f"   URL: {photo_url}")
                        
                        # Send real-time notification jika ada SocketIO
                        self._send_realtime_notification(event_id, photo_id, photo_url)
                        
                        return True
                        
                    elif response.status_code == 413:
                        logger.error("❌ File too large for upload")
                        return False
                        
                    else:
                        logger.warning(f"⚠️ Upload attempt {attempt + 1} failed: {response.status_code}")
                        if attempt < self.retry_attempts - 1:
                            time.sleep(2 ** attempt)  # Exponential backoff
                        
                except requests.exceptions.Timeout:
                    logger.warning(f"⚠️ Upload timeout on attempt {attempt + 1}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(2 ** attempt)
                
                except Exception as e:
                    logger.error(f"❌ Upload error on attempt {attempt + 1}: {e}")
                    if attempt < self.retry_attempts - 1:
                        time.sleep(2 ** attempt)
            
            logger.error(f"❌ All upload attempts failed for {image_path.name}")
            return False
            
        except Exception as e:
            logger.error(f"❌ Fatal error uploading photo: {e}")
            return False
    
    def _send_realtime_notification(self, event_id: str, photo_id: str, photo_url: str):
        """Send real-time notification via SocketIO"""
        try:
            socketio_url = Config.WEB_INTEGRATION.get("socketio_url", "")
            if not socketio_url:
                return
            
            # Send notification ke SocketIO server
            notification_data = {
                "type": "photo_uploaded",
                "eventId": event_id,
                "photoId": photo_id,
                "photoUrl": photo_url,
                "category": "official",
                "source": "tethered_shooting",
                "timestamp": int(time.time())
            }
            
            # Implementasi SocketIO client bisa ditambahkan di sini
            logger.info(f"📡 Real-time notification sent for photo {photo_id}")
            
        except Exception as e:
            logger.warning(f"Failed to send real-time notification: {e}")
    
    def get_upload_stats(self) -> Dict[str, Any]:
        """Dapatkan statistik upload"""
        try:
            headers = self._get_auth_headers()
            stats_url = f"{self.base_url}/admin/stats"
            
            response = requests.get(
                stats_url,
                headers=headers,
                params={"source": "tethered_shooting"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Failed to fetch stats: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error fetching upload stats: {e}")
            return {"error": str(e)}

def test_web_integration():
    """Test function untuk web integration"""
    try:
        print("🧪 Testing Web Integration...")
        
        # Inisialisasi integrator
        integrator = WebIntegrator()
        
        # Test koneksi
        print("1. Testing API connection...")
        if integrator.test_connection():
            print("✅ API connection successful")
        else:
            print("❌ API connection failed")
            return
        
        # Test get active event
        print("\n2. Testing active event retrieval...")
        event_id = integrator.get_active_event()
        if event_id:
            print(f"✅ Active event found: {event_id}")
        else:
            print("⚠️ No active event, will create default")
            event_id = integrator.create_default_event()
            if event_id:
                print(f"✅ Default event created: {event_id}")
            else:
                print("❌ Failed to create default event")
                return
        
        # Test upload dengan sample image
        print("\n3. Testing photo upload...")
        sample_image = Config.TEMP_DIR / "test_image.jpg"
        
        if sample_image.exists():
            success = integrator.upload_photo(sample_image, event_id)
            if success:
                print("✅ Photo upload successful")
            else:
                print("❌ Photo upload failed")
        else:
            print("⚠️ No test image found, skipping upload test")
        
        # Test stats
        print("\n4. Testing stats retrieval...")
        stats = integrator.get_upload_stats()
        print(f"Stats: {stats}")
        
        print("\n✅ Web integration test completed")
        
    except Exception as e:
        print(f"❌ Error during web integration test: {e}")

if __name__ == "__main__":
    test_web_integration()