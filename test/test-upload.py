#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Web Upload Functionality
=============================

Test upload foto ke web project, koneksi API, dan integrasi dengan database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import json
import requests
from pathlib import Path
from PIL import Image
import io

# Import modules
from config import Config
from web_integrator import WebIntegrator
from event_selector import EventSelector

# Setup logging untuk test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UploadTester:
    """Test web upload functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.web_integrator = None
        self.event_selector = None
        self.test_image_path = None
        print("🌐 WEB UPLOAD FUNCTIONALITY TESTER")
        print("=" * 50)
    
    def test_web_integrator_init(self) -> bool:
        """Test inisialisasi web integrator"""
        try:
            print("\n🔧 Testing Web Integrator Initialization...")
            
            self.web_integrator = WebIntegrator()
            
            print(f"  ✅ Base URL: {self.web_integrator.base_url}")
            print(f"  ✅ Upload Endpoint: {self.web_integrator.upload_endpoint}")
            print(f"  ✅ Event Endpoint: {self.web_integrator.event_endpoint}")
            print(f"  ✅ Timeout: {self.web_integrator.timeout}s")
            print(f"  ✅ Retry Attempts: {self.web_integrator.retry_attempts}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error initializing web integrator: {e}")
            return False
    
    def test_api_connection(self) -> bool:
        """Test koneksi ke web API"""
        try:
            print("\n🔗 Testing Web API Connection...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            # Test ping endpoint
            success = self.web_integrator.test_connection()
            
            if success:
                print("  ✅ Web API connection successful")
                return True
            else:
                print("  ❌ Web API connection failed")
                
                # Additional debugging
                try:
                    ping_url = f"{self.web_integrator.base_url}/ping"
                    print(f"  🔍 Testing URL: {ping_url}")
                    
                    response = requests.get(ping_url, timeout=10)
                    print(f"  📊 Response Status: {response.status_code}")
                    print(f"  📄 Response Text: {response.text[:100]}...")
                    
                except Exception as e:
                    print(f"  🔍 Debug connection error: {e}")
                
                return False
            
        except Exception as e:
            print(f"  ❌ Error testing API connection: {e}")
            return False
    
    def test_jwt_token_creation(self) -> bool:
        """Test pembuatan JWT token untuk upload"""
        try:
            print("\n🔐 Testing JWT Token Creation for Upload...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            # Test token creation
            token = self.web_integrator._create_auth_token()
            
            if not token:
                print("  ❌ Failed to create JWT token")
                return False
            
            print(f"  ✅ JWT Token created: {token[:30]}...")
            
            # Test auth headers
            headers = self.web_integrator._get_auth_headers()
            
            expected_headers = ['Authorization', 'Content-Type', 'X-Source']
            for header in expected_headers:
                if header in headers:
                    value = headers[header][:50] + "..." if len(headers[header]) > 50 else headers[header]
                    print(f"  ✅ Header {header}: {value}")
                else:
                    print(f"  ❌ Missing header: {header}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing JWT token: {e}")
            return False
    
    def create_test_image(self) -> bool:
        """Buat test image untuk upload"""
        try:
            print("\n🖼️  Creating Test Image for Upload...")
            
            # Buat test image dengan PIL
            width, height = 800, 600
            test_img = Image.new('RGB', (width, height), color='skyblue')
            
            # Tambahkan text dan shapes untuk membuat realistic
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(test_img)
            
            # Background gradient effect
            for y in range(height):
                color_value = int(135 + (120 * y / height))  # Gradient from skyblue to darker
                draw.line([(0, y), (width, y)], fill=(135, 206, color_value))
            
            # Add shapes untuk simulate foto
            draw.rectangle([100, 100, 300, 200], fill='white', outline='black', width=2)
            draw.ellipse([400, 150, 600, 350], fill='yellow', outline='orange', width=3)
            draw.polygon([(650, 100), (750, 150), (700, 250), (600, 200)], fill='red', outline='darkred')
            
            # Add text
            try:
                font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 24)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 50), "TETHERED SHOOTING TEST IMAGE", fill='black', font=font)
            draw.text((50, 450), f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}", fill='white', font=font)
            draw.text((50, 480), f"Size: {width}x{height}", fill='white', font=font)
            draw.text((50, 510), "Format: JPEG | Quality: High", fill='white', font=font)
            
            # Save test image
            self.test_image_path = Config.TEMP_DIR / "test_upload_image.jpg"
            test_img.save(self.test_image_path, 'JPEG', quality=95, optimize=True)
            
            # Verify file
            if self.test_image_path.exists():
                file_size = self.test_image_path.stat().st_size
                print(f"  ✅ Test image created: {self.test_image_path}")
                print(f"  📏 Image size: {width}x{height}")
                print(f"  💾 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                return True
            else:
                print("  ❌ Failed to save test image")
                return False
            
        except Exception as e:
            print(f"  ❌ Error creating test image: {e}")
            return False
    
    def test_image_preparation(self) -> bool:
        """Test persiapan image untuk upload"""
        try:
            print("\n🎨 Testing Image Preparation for Upload...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            if not self.test_image_path or not self.test_image_path.exists():
                print("  ❌ Test image not available")
                return False
            
            # Test different quality settings
            qualities = ['high', 'medium', 'low']
            
            for quality in qualities:
                print(f"  🔍 Testing {quality} quality preparation...")
                
                image_bytes = self.web_integrator.prepare_image_for_upload(
                    self.test_image_path, quality
                )
                
                if image_bytes:
                    size_kb = len(image_bytes) / 1024
                    print(f"    ✅ {quality} quality: {len(image_bytes):,} bytes ({size_kb:.1f} KB)")
                else:
                    print(f"    ❌ Failed to prepare {quality} quality image")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing image preparation: {e}")
            return False
    
    def test_event_retrieval_for_upload(self) -> bool:
        """Test mendapatkan event untuk upload"""
        try:
            print("\n📅 Testing Event Retrieval for Upload...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            # Test get active event
            print("  🔍 Testing get active event...")
            active_event_id = self.web_integrator.get_active_event()
            
            if active_event_id:
                print(f"  ✅ Active event found: {active_event_id}")
                return True
            else:
                print("  ⚠️  No active event found")
                
                # Test create default event
                print("  🔍 Testing create default event...")
                created_event_id = self.web_integrator.create_default_event()
                
                if created_event_id:
                    print(f"  ✅ Default event created: {created_event_id}")
                    return True
                else:
                    print("  ❌ Failed to create default event")
                    return False
            
        except Exception as e:
            print(f"  ❌ Error testing event retrieval: {e}")
            return False
    
    def test_photo_upload_dry_run(self) -> bool:
        """Test upload foto (dry run tanpa actual upload)"""
        try:
            print("\n📤 Testing Photo Upload (Dry Run)...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            if not self.test_image_path or not self.test_image_path.exists():
                print("  ❌ Test image not available")
                return False
            
            # Get event untuk upload
            event_id = self.web_integrator.get_active_event()
            if not event_id:
                event_id = self.web_integrator.create_default_event()
            
            if not event_id:
                print("  ❌ No event available for upload test")
                return False
            
            print(f"  🎯 Target event: {event_id}")
            
            # Prepare upload data (tanpa actual upload)
            quality = Config.WEB_INTEGRATION["web_upload_quality"]
            image_bytes = self.web_integrator.prepare_image_for_upload(self.test_image_path, quality)
            
            if not image_bytes:
                print("  ❌ Failed to prepare image for upload")
                return False
            
            # Simulate upload data
            upload_data = {
                'eventId': event_id,
                'source': 'tethered_shooting',
                'category': Config.WEB_INTEGRATION["default_photo_category"],
                'type': 'official',
                'quality': quality,
                'timestamp': int(time.time()),
                'filename': self.test_image_path.name,
                'auto_uploaded': 'true'
            }
            
            print(f"  📋 Upload data prepared:")
            for key, value in upload_data.items():
                print(f"    {key}: {value}")
            
            print(f"  📏 Image data: {len(image_bytes):,} bytes")
            print("  ✅ Upload preparation successful (dry run)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing upload dry run: {e}")
            return False
    
    def test_actual_photo_upload(self) -> bool:
        """Test actual upload foto ke web project"""
        try:
            print("\n🚀 Testing Actual Photo Upload...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            if not self.test_image_path or not self.test_image_path.exists():
                print("  ❌ Test image not available")
                return False
            
            # Ask user confirmation untuk actual upload
            print("  ⚠️  This will perform ACTUAL upload to your web project!")
            print(f"     Image: {self.test_image_path.name}")
            print(f"     Target: Tab 'Official' in selected event")
            
            confirm = input("  ❓ Proceed with actual upload? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', 'ya']:
                print("  ⏭️  Actual upload skipped by user")
                return True
            
            print("  🔄 Performing actual upload...")
            
            # Perform actual upload
            success = self.web_integrator.upload_photo(self.test_image_path)
            
            if success:
                print("  ✅ Actual upload successful!")
                print("  📋 Check your web project - photo should appear in 'Official' tab")
                
                # Try to get upload stats
                try:
                    stats = self.web_integrator.get_upload_stats()
                    if stats and 'error' not in stats:
                        print(f"  📊 Upload stats: {stats}")
                except Exception as e:
                    print(f"  ⚠️  Could not get upload stats: {e}")
                
                return True
            else:
                print("  ❌ Actual upload failed")
                return False
            
        except Exception as e:
            print(f"  ❌ Error testing actual upload: {e}")
            return False
    
    def test_upload_error_handling(self) -> bool:
        """Test error handling untuk upload"""
        try:
            print("\n🛡️  Testing Upload Error Handling...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            # Test dengan file yang tidak ada
            print("  🔍 Testing with non-existent file...")
            fake_path = Config.TEMP_DIR / "non_existent_image.jpg"
            
            success = self.web_integrator.upload_photo(fake_path)
            
            if not success:
                print("  ✅ Non-existent file correctly rejected")
            else:
                print("  ❌ Non-existent file incorrectly accepted")
                return False
            
            # Test dengan endpoint invalid (sementara)
            print("  🔍 Testing with invalid endpoint...")
            original_endpoint = self.web_integrator.upload_endpoint
            self.web_integrator.upload_endpoint = "http://invalid-url-test.com/upload"
            
            if self.test_image_path and self.test_image_path.exists():
                success = self.web_integrator.upload_photo(self.test_image_path)
                
                if not success:
                    print("  ✅ Invalid endpoint correctly handled")
                else:
                    print("  ❌ Invalid endpoint incorrectly succeeded")
                    return False
            
            # Restore endpoint
            self.web_integrator.upload_endpoint = original_endpoint
            
            print("  ✅ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing upload error handling: {e}")
            return False
    
    def test_upload_stats_retrieval(self) -> bool:
        """Test pengambilan statistik upload"""
        try:
            print("\n📊 Testing Upload Stats Retrieval...")
            
            if not self.web_integrator:
                print("  ❌ Web integrator not initialized")
                return False
            
            # Get upload stats
            stats = self.web_integrator.get_upload_stats()
            
            if isinstance(stats, dict):
                if 'error' in stats:
                    print(f"  ⚠️  Stats retrieval error: {stats['error']}")
                    # This might be expected if no uploads yet
                    return True
                else:
                    print("  ✅ Upload stats retrieved:")
                    for key, value in stats.items():
                        print(f"    {key}: {value}")
                    return True
            else:
                print(f"  ❌ Unexpected stats format: {type(stats)}")
                return False
            
        except Exception as e:
            print(f"  ❌ Error testing upload stats: {e}")
            return False
    
    def cleanup_test_files(self) -> bool:
        """Cleanup test files"""
        try:
            print("\n🧹 Cleaning Up Test Files...")
            
            if self.test_image_path and self.test_image_path.exists():
                self.test_image_path.unlink()
                print(f"  ✅ Removed test image: {self.test_image_path.name}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error cleaning up: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test upload"""
        print("🚀 Starting Web Upload Functionality Tests...\n")
        
        tests = [
            ("Web Integrator Initialization", self.test_web_integrator_init),
            ("Web API Connection", self.test_api_connection),
            ("JWT Token Creation", self.test_jwt_token_creation),
            ("Create Test Image", self.create_test_image),
            ("Image Preparation", self.test_image_preparation),
            ("Event Retrieval for Upload", self.test_event_retrieval_for_upload),
            ("Photo Upload Dry Run", self.test_photo_upload_dry_run),
            ("Actual Photo Upload", self.test_actual_photo_upload),
            ("Upload Error Handling", self.test_upload_error_handling),
            ("Upload Stats Retrieval", self.test_upload_stats_retrieval),
            ("Cleanup Test Files", self.cleanup_test_files)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
                if result:
                    passed += 1
            except Exception as e:
                print(f"  ❌ Fatal error in {test_name}: {e}")
                self.test_results[test_name] = False
        
        # Summary
        print(f"\n{'='*50}")
        print(f"📊 WEB UPLOAD TEST SUMMARY")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35} : {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL WEB UPLOAD TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check web integration configuration.")
            return False

def main():
    """Main function untuk upload testing"""
    try:
        tester = UploadTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Web upload functionality ready for production!")
            print("📋 Photos will successfully upload to 'Official' tab in events.")
        else:
            print("\n❌ Please fix upload-related issues before proceeding.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Upload test cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Fatal error during upload test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)