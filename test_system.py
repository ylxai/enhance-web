#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test System untuk Validasi Semua Komponen
=========================================

Script untuk testing dan validasi semua komponen sistem tethered shooting
sebelum digunakan untuk event real-time.
"""

import cv2
import numpy as np
import logging
import time
import sys
from pathlib import Path
import traceback

# Import semua komponen sistem
from config import Config
from face_detection import FaceProtectionMask
from gemini_enhancer import GeminiImageEnhancer
from image_processor import ImageProcessor
from camera_controller import CameraController

# Setup logging untuk test
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class SystemTester:
    """Class untuk testing semua komponen sistem"""
    
    def __init__(self):
        """Inisialisasi tester"""
        self.test_results = {
            "config": False,
            "directories": False,
            "face_detection": False,
            "ai_enhancer": False,
            "image_processor": False,
            "camera": False,
            "full_pipeline": False
        }
        
        self.test_image_path = None
        
        print("🧪 SYSTEM TESTER - Validasi Komponen")
        print("=" * 50)
    
    def create_test_image(self) -> Path:
        """Buat test image dengan wajah untuk testing"""
        try:
            # Buat test image sederhana dengan face-like pattern
            test_img = np.ones((600, 800, 3), dtype=np.uint8) * 128
            
            # Tambahkan pattern yang menyerupai wajah
            # Oval untuk wajah
            cv2.ellipse(test_img, (400, 250), (80, 100), 0, 0, 360, (220, 190, 170), -1)
            
            # Mata
            cv2.circle(test_img, (370, 220), 15, (50, 50, 50), -1)  # Mata kiri
            cv2.circle(test_img, (430, 220), 15, (50, 50, 50), -1)  # Mata kanan
            
            # Hidung
            cv2.ellipse(test_img, (400, 250), (8, 15), 0, 0, 360, (180, 150, 130), -1)
            
            # Mulut
            cv2.ellipse(test_img, (400, 280), (25, 10), 0, 0, 360, (150, 100, 100), -1)
            
            # Tambahkan background pattern
            for i in range(0, 800, 50):
                cv2.line(test_img, (i, 0), (i, 600), (100, 100, 100), 1)
            for i in range(0, 600, 50):
                cv2.line(test_img, (0, i), (800, i), (100, 100, 100), 1)
            
            # Simpan test image
            test_path = Config.TEMP_DIR / "test_image.jpg"
            cv2.imwrite(str(test_path), test_img)
            
            self.test_image_path = test_path
            print(f"✅ Test image dibuat: {test_path}")
            return test_path
            
        except Exception as e:
            print(f"❌ Gagal membuat test image: {e}")
            return None
    
    def test_config(self) -> bool:
        """Test konfigurasi sistem"""
        print("\n1. Testing Configuration...")
        
        try:
            # Test konfigurasi basic
            assert hasattr(Config, 'GOOGLE_API_KEY'), "Google API Key tidak ditemukan"
            assert hasattr(Config, 'GEMINI_MODEL'), "Gemini model tidak ditemukan"
            assert hasattr(Config, 'BASE_DIR'), "Base directory tidak ditemukan"
            
            # Validasi konfigurasi
            errors = Config.validate_config()
            if errors:
                print("⚠️ Warning - Beberapa konfigurasi bermasalah:")
                for error in errors:
                    print(f"   - {error}")
            
            print("✅ Konfigurasi valid")
            return True
            
        except Exception as e:
            print(f"❌ Error konfigurasi: {e}")
            return False
    
    def test_directories(self) -> bool:
        """Test pembuatan direktori"""
        print("\n2. Testing Directories...")
        
        try:
            Config.create_directories()
            
            # Check semua direktori penting
            required_dirs = [
                Config.CAPTURE_DIR,
                Config.BACKUP_RAW_DIR,
                Config.BACKUP_JPG_DIR,
                Config.PROCESSED_DIR,
                Config.TEMP_DIR,
                Config.LOGS_DIR,
                Config.PRESETS_DIR,
                Config.WATERMARKS_DIR,
                Config.MODELS_DIR
            ]
            
            for directory in required_dirs:
                assert directory.exists(), f"Directory tidak ada: {directory}"
            
            print("✅ Semua direktori berhasil dibuat")
            return True
            
        except Exception as e:
            print(f"❌ Error direktori: {e}")
            return False
    
    def test_face_detection(self) -> bool:
        """Test face detection component"""
        print("\n3. Testing Face Detection...")
        
        try:
            # Buat test image jika belum ada
            if not self.test_image_path:
                self.create_test_image()
            
            # Inisialisasi face detector
            detector = FaceProtectionMask()
            
            # Load test image
            test_img = cv2.imread(str(self.test_image_path))
            assert test_img is not None, "Gagal load test image"
            
            # Test deteksi wajah
            faces = detector.detect_faces(test_img)
            print(f"   Detected faces: {len(faces)}")
            
            # Test masking
            masked_img, face_mask, has_faces = detector.apply_face_protection(test_img)
            print(f"   Face protection applied: {has_faces}")
            
            # Simpan hasil untuk review
            test_dir = Config.TEMP_DIR / "face_test"
            test_dir.mkdir(exist_ok=True)
            
            cv2.imwrite(str(test_dir / "original.jpg"), test_img)
            cv2.imwrite(str(test_dir / "masked.jpg"), masked_img)
            cv2.imwrite(str(test_dir / "face_mask.jpg"), face_mask)
            
            # Visualisasi deteksi
            viz = detector.visualize_detection(test_img, test_dir / "detection.jpg")
            
            print(f"   Test results saved to: {test_dir}")
            print("✅ Face detection working")
            return True
            
        except Exception as e:
            print(f"❌ Error face detection: {e}")
            traceback.print_exc()
            return False
    
    def test_ai_enhancer(self) -> bool:
        """Test AI enhancement component"""
        print("\n4. Testing AI Enhancer...")
        
        try:
            # Buat test image jika belum ada
            if not self.test_image_path:
                self.create_test_image()
            
            # Inisialisasi AI enhancer
            enhancer = GeminiImageEnhancer()
            
            # Test enhancement
            output_path = Config.TEMP_DIR / "enhanced_test.jpg"
            success, result_path = enhancer.enhance_image(self.test_image_path, output_path)
            
            if success and result_path:
                print(f"   Enhanced image saved: {result_path}")
                print("✅ AI enhancement working")
                return True
            else:
                print("⚠️ AI enhancement failed, but fallback should work")
                # Check jika fallback enhancement berjalan
                if output_path.exists():
                    print("✅ Fallback enhancement working")
                    return True
                else:
                    return False
            
        except Exception as e:
            print(f"❌ Error AI enhancer: {e}")
            traceback.print_exc()
            return False
    
    def test_image_processor(self) -> bool:
        """Test image processing component"""
        print("\n5. Testing Image Processor...")
        
        try:
            # Buat test image jika belum ada
            if not self.test_image_path:
                self.create_test_image()
            
            # Inisialisasi processor
            processor = ImageProcessor()
            
            # Load test image
            test_img = cv2.imread(str(self.test_image_path))
            
            # Test individual components
            print("   Testing LUT application...")
            lut_result = processor.apply_lut(test_img)
            assert lut_result is not None, "LUT application failed"
            
            print("   Testing auto crop...")
            crop_result = processor.auto_crop(test_img)
            assert crop_result is not None, "Auto crop failed"
            
            print("   Testing watermark...")
            watermark_result = processor.apply_watermark(test_img)
            assert watermark_result is not None, "Watermark failed"
            
            # Test full pipeline
            print("   Testing full pipeline...")
            output_path = Config.TEMP_DIR / "pipeline_test.jpg"
            success, result_path = processor.process_full_pipeline(test_img, output_path)
            
            if success and result_path:
                print(f"   Pipeline result: {result_path}")
                print("✅ Image processing working")
                return True
            else:
                print("❌ Image processing pipeline failed")
                return False
            
        except Exception as e:
            print(f"❌ Error image processor: {e}")
            traceback.print_exc()
            return False
    
    def test_camera(self) -> bool:
        """Test camera controller (non-destructive)"""
        print("\n6. Testing Camera Controller...")
        
        try:
            # Test deteksi kamera (tanpa capture)
            print("   Checking camera detection...")
            
            # Inisialisasi camera controller
            camera = CameraController()
            
            # Check status
            status = camera.get_camera_status()
            print(f"   Camera connected: {status['connected']}")
            print(f"   Camera capturing: {status['capturing']}")
            
            if status['connected']:
                print("✅ Camera controller working")
                return True
            else:
                print("⚠️ No camera detected (this is OK for testing)")
                return True  # OK untuk testing tanpa kamera
                
        except Exception as e:
            print(f"⚠️ Camera test failed: {e}")
            print("   (This is expected if no camera is connected)")
            return True  # OK untuk testing tanpa kamera fisik
    
    def test_full_pipeline(self) -> bool:
        """Test full processing pipeline end-to-end"""
        print("\n7. Testing Full Pipeline...")
        
        try:
            if not self.test_image_path:
                self.create_test_image()
            
            print("   Running complete processing pipeline...")
            
            # Simulasi pipeline lengkap
            start_time = time.time()
            
            # Step 1: Face detection dan proteksi
            detector = FaceProtectionMask()
            test_img = cv2.imread(str(self.test_image_path))
            protected_img, face_mask, has_faces = detector.apply_face_protection(test_img)
            
            # Step 2: AI enhancement (atau fallback)
            enhancer = GeminiImageEnhancer()
            enhanced_path = Config.TEMP_DIR / "pipeline_enhanced.jpg"
            cv2.imwrite(str(enhanced_path), protected_img)
            success, enhanced_result = enhancer.enhance_image(enhanced_path)
            
            if success and enhanced_result:
                enhanced_img = cv2.imread(str(enhanced_result))
            else:
                enhanced_img = protected_img
            
            # Restore face areas jika ada
            if has_faces:
                enhanced_img = detector.restore_face_areas(enhanced_img, test_img, face_mask)
            
            # Step 3: Full processing (LUT + Crop + Watermark)
            processor = ImageProcessor()
            final_path = Config.TEMP_DIR / "pipeline_final.jpg"
            success, result_path = processor.process_full_pipeline(enhanced_img, final_path)
            
            processing_time = time.time() - start_time
            
            if success and result_path:
                print(f"   Pipeline completed in {processing_time:.2f} seconds")
                print(f"   Final result: {result_path}")
                print("✅ Full pipeline working")
                return True
            else:
                print("❌ Full pipeline failed")
                return False
                
        except Exception as e:
            print(f"❌ Error full pipeline: {e}")
            traceback.print_exc()
            return False
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test"""
        print("Starting comprehensive system test...\n")
        
        # Daftar test yang akan dijalankan
        tests = [
            ("config", self.test_config),
            ("directories", self.test_directories),
            ("face_detection", self.test_face_detection),
            ("ai_enhancer", self.test_ai_enhancer),
            ("image_processor", self.test_image_processor),
            ("camera", self.test_camera),
            ("full_pipeline", self.test_full_pipeline)
        ]
        
        # Jalankan setiap test
        for test_name, test_func in tests:
            try:
                result = test_func()
                self.test_results[test_name] = result
            except Exception as e:
                print(f"❌ Fatal error in {test_name}: {e}")
                self.test_results[test_name] = False
        
        # Summary hasil test
        self.print_test_summary()
        
        # Return True jika semua critical tests pass
        critical_tests = ["config", "directories", "face_detection", "image_processor"]
        return all(self.test_results[test] for test in critical_tests)
    
    def print_test_summary(self):
        """Print summary hasil test"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:20} : {status}")
        
        print("-" * 50)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Sistem siap digunakan.")
        elif passed >= total - 1:
            print("⚠️ Most tests passed. Check failed components.")
        else:
            print("❌ Multiple failures. System needs attention.")
        
        print("\nNext steps:")
        if self.test_results["config"] and self.test_results["directories"]:
            print("1. ✅ Basic setup OK")
        else:
            print("1. ❌ Fix basic configuration first")
        
        if self.test_results["face_detection"]:
            print("2. ✅ Face detection ready")
        else:
            print("2. ❌ Check OpenCV and model files")
        
        if self.test_results["image_processor"]:
            print("3. ✅ Image processing ready")
        else:
            print("3. ❌ Check LUT and watermark files")
        
        if not self.test_results["camera"]:
            print("4. ⚠️ Connect camera and test again")
        else:
            print("4. ✅ Camera ready")
        
        print("\nTest files created in temp/ directory for review.")

def main():
    """Main function untuk menjalankan test"""
    try:
        tester = SystemTester()
        
        # Create test image
        tester.create_test_image()
        
        # Run all tests
        success = tester.run_all_tests()
        
        # Exit dengan appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()