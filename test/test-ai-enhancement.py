#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test AI Enhancement & Image Processing
=====================================

Test Google Gemini AI enhancement, image processing pipeline, dan fallback mechanisms.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Import modules
from config import Config
from gemini_enhancer import GeminiImageEnhancer
from image_processor import ImageProcessor
from face_detection import FaceProtectionMask

# Setup logging untuk test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AIEnhancementTester:
    """Test AI enhancement dan image processing"""
    
    def __init__(self):
        self.test_results = {}
        self.ai_enhancer = None
        self.image_processor = None
        self.face_detector = None
        self.test_images = {}
        print("🤖 AI ENHANCEMENT & IMAGE PROCESSING TESTER")
        print("=" * 50)
    
    def test_ai_enhancer_init(self) -> bool:
        """Test inisialisasi AI enhancer"""
        try:
            print("\n🔧 Testing AI Enhancer Initialization...")
            
            self.ai_enhancer = GeminiImageEnhancer()
            
            print(f"  ✅ AI enhancer initialized")
            print(f"  🤖 Model: {Config.GEMINI_MODEL}")
            print(f"  📏 Max resolution: {Config.AI_ENHANCEMENT['max_resolution']}")
            print(f"  🔄 Retry attempts: {Config.AI_ENHANCEMENT['retry_attempts']}")
            print(f"  ⏱️  Timeout: {Config.AI_ENHANCEMENT['timeout']}s")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error initializing AI enhancer: {e}")
            return False
    
    def test_image_processor_init(self) -> bool:
        """Test inisialisasi image processor"""
        try:
            print("\n🎨 Testing Image Processor Initialization...")
            
            self.image_processor = ImageProcessor()
            
            print(f"  ✅ Image processor initialized")
            print(f"  🎯 Portrait ratio: {Config.AUTO_CROP['portrait_ratio']}")
            print(f"  🎯 Landscape ratio: {Config.AUTO_CROP['landscape_ratio']}")
            print(f"  🖼️  Target DPI: {Config.AUTO_CROP['target_dpi']}")
            print(f"  💧 Watermark size: {Config.WATERMARK['size_ratio']*100}%")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error initializing image processor: {e}")
            return False
    
    def create_test_images_with_issues(self) -> bool:
        """Buat test images dengan berbagai issues untuk enhancement"""
        try:
            print("\n🖼️  Creating Test Images with Enhancement Issues...")
            
            test_dir = Config.TEMP_DIR / "ai_test"
            test_dir.mkdir(exist_ok=True)
            
            # === Blurry Image ===
            print("  📷 Creating blurry image...")
            blurry_img = np.ones((600, 800, 3), dtype=np.uint8) * 100
            
            # Add content
            cv2.rectangle(blurry_img, (100, 100), (300, 300), (200, 150, 100), -1)
            cv2.circle(blurry_img, (500, 200), 80, (150, 200, 250), -1)
            cv2.rectangle(blurry_img, (400, 350), (600, 500), (100, 200, 150), -1)
            
            # Apply blur
            blurry_img = cv2.GaussianBlur(blurry_img, (15, 15), 0)
            
            blurry_path = test_dir / "blurry_test.jpg"
            cv2.imwrite(str(blurry_path), blurry_img)
            self.test_images['blurry'] = blurry_path
            
            # === Noisy Image ===
            print("  📡 Creating noisy image...")
            clean_img = np.ones((500, 700, 3), dtype=np.uint8) * 120
            cv2.rectangle(clean_img, (50, 50), (250, 250), (180, 160, 140), -1)
            cv2.circle(clean_img, (450, 300), 100, (160, 180, 200), -1)
            
            # Add noise
            noise = np.random.randint(0, 50, clean_img.shape, dtype=np.uint8)
            noisy_img = cv2.add(clean_img, noise)
            
            noisy_path = test_dir / "noisy_test.jpg"
            cv2.imwrite(str(noisy_path), noisy_img)
            self.test_images['noisy'] = noisy_path
            
            # === Low Contrast Image ===
            print("  🌫️  Creating low contrast image...")
            low_contrast = np.ones((400, 600, 3), dtype=np.uint8) * 128
            
            # Very subtle differences
            cv2.rectangle(low_contrast, (100, 100), (300, 250), (138, 138, 138), -1)
            cv2.circle(low_contrast, (400, 200), 60, (118, 118, 118), -1)
            
            low_contrast_path = test_dir / "low_contrast_test.jpg"
            cv2.imwrite(str(low_contrast_path), low_contrast)
            self.test_images['low_contrast'] = low_contrast_path
            
            print(f"  ✅ Created {len(self.test_images)} test images for enhancement")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error creating test images: {e}")
            return False
    
    def test_ai_enhancement_fallback(self) -> bool:
        """Test AI enhancement dengan fallback ke OpenCV"""
        try:
            print("\n🤖 Testing AI Enhancement with Fallback...")
            
            if not self.ai_enhancer or not self.test_images:
                print("  ❌ Required components not initialized")
                return False
            
            test_dir = Config.TEMP_DIR / "ai_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  🔄 Testing enhancement for {image_name}...")
                
                output_path = test_dir / f"enhanced_{image_name}.jpg"
                
                start_time = time.time()
                success, result_path = self.ai_enhancer.enhance_image(image_path, output_path)
                enhancement_time = time.time() - start_time
                
                if success and result_path and result_path.exists():
                    print(f"    ✅ Enhancement successful in {enhancement_time:.2f}s")
                    
                    # Compare file sizes
                    original_size = image_path.stat().st_size
                    enhanced_size = result_path.stat().st_size
                    print(f"    📊 Size: {original_size} → {enhanced_size} bytes")
                    
                else:
                    print(f"    ❌ Enhancement failed for {image_name}")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing AI enhancement: {e}")
            return False
    
    def test_lut_application(self) -> bool:
        """Test aplikasi LUT untuk color grading"""
        try:
            print("\n🎨 Testing LUT Application...")
            
            if not self.image_processor or not self.test_images:
                print("  ❌ Required components not initialized")
                return False
            
            # Create sample LUT if not exists
            lut_file = Config.PRESETS_DIR / Config.LUT_SETTINGS["file"]
            if not lut_file.exists():
                print("  📁 Creating sample LUT file...")
                self._create_sample_lut()
            
            test_dir = Config.TEMP_DIR / "ai_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  🎯 Testing LUT for {image_name}...")
                
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                # Apply LUT
                lut_result = self.image_processor.apply_lut(image)
                
                if lut_result is not None:
                    lut_output = test_dir / f"lut_{image_name}.jpg"
                    cv2.imwrite(str(lut_output), lut_result)
                    print(f"    ✅ LUT applied successfully")
                else:
                    print(f"    ❌ LUT application failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing LUT application: {e}")
            return False
    
    def _create_sample_lut(self):
        """Create sample LUT file for testing"""
        lut_size = 33
        lut_data = []
        
        for b in range(lut_size):
            for g in range(lut_size):
                for r in range(lut_size):
                    r_val = r / (lut_size - 1)
                    g_val = g / (lut_size - 1)
                    b_val = b / (lut_size - 1)
                    lut_data.append(f'{r_val:.6f} {g_val:.6f} {b_val:.6f}')
        
        lut_file = Config.PRESETS_DIR / Config.LUT_SETTINGS["file"]
        with open(lut_file, 'w') as f:
            f.write('# Sample LUT for Testing\n')
            f.write('TITLE "Test LUT"\n')
            f.write('LUT_3D_SIZE 33\n')
            f.write('DOMAIN_MIN 0.0 0.0 0.0\n')
            f.write('DOMAIN_MAX 1.0 1.0 1.0\n\n')
            for line in lut_data:
                f.write(line + '\n')
    
    def test_auto_crop(self) -> bool:
        """Test auto crop functionality"""
        try:
            print("\n✂️  Testing Auto Crop...")
            
            if not self.image_processor or not self.test_images:
                print("  ❌ Required components not initialized")
                return False
            
            test_dir = Config.TEMP_DIR / "ai_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  📐 Testing crop for {image_name}...")
                
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                original_shape = image.shape[:2]
                orientation = self.image_processor.detect_orientation(image)
                
                cropped = self.image_processor.auto_crop(image)
                
                if cropped is not None:
                    cropped_shape = cropped.shape[:2]
                    crop_output = test_dir / f"cropped_{image_name}.jpg"
                    cv2.imwrite(str(crop_output), cropped)
                    
                    print(f"    ✅ {orientation}: {original_shape} → {cropped_shape}")
                else:
                    print(f"    ❌ Crop failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing auto crop: {e}")
            return False
    
    def test_watermark_application(self) -> bool:
        """Test watermark application"""
        try:
            print("\n💧 Testing Watermark Application...")
            
            if not self.image_processor or not self.test_images:
                print("  ❌ Required components not initialized")
                return False
            
            # Create sample watermark if not exists
            watermark_file = Config.WATERMARKS_DIR / Config.WATERMARK["file"]
            if not watermark_file.exists():
                print("  🖼️  Creating sample watermark...")
                self._create_sample_watermark()
            
            test_dir = Config.TEMP_DIR / "ai_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  🏷️  Testing watermark for {image_name}...")
                
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                watermarked = self.image_processor.apply_watermark(image)
                
                if watermarked is not None:
                    watermark_output = test_dir / f"watermarked_{image_name}.jpg"
                    cv2.imwrite(str(watermark_output), watermarked)
                    print(f"    ✅ Watermark applied successfully")
                else:
                    print(f"    ❌ Watermark application failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing watermark: {e}")
            return False
    
    def _create_sample_watermark(self):
        """Create sample watermark for testing"""
        from PIL import Image, ImageDraw, ImageFont
        
        width, height = 300, 80
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 24)
        except:
            font = ImageFont.load_default()
        
        text = 'Test Watermark'
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
        
        watermark_file = Config.WATERMARKS_DIR / Config.WATERMARK["file"]
        img.save(watermark_file)
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test AI enhancement dan processing"""
        print("🚀 Starting AI Enhancement & Image Processing Tests...\n")
        
        tests = [
            ("AI Enhancer Initialization", self.test_ai_enhancer_init),
            ("Image Processor Initialization", self.test_image_processor_init),
            ("Create Test Images", self.create_test_images_with_issues),
            ("AI Enhancement Fallback", self.test_ai_enhancement_fallback),
            ("LUT Application", self.test_lut_application),
            ("Auto Crop", self.test_auto_crop),
            ("Watermark Application", self.test_watermark_application)
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
        print(f"📊 AI ENHANCEMENT TEST SUMMARY")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35} : {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL AI ENHANCEMENT TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check AI/processing configuration.")
            return False

def main():
    """Main function untuk AI enhancement testing"""
    try:
        tester = AIEnhancementTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ AI enhancement & image processing ready!")
            print("🤖 System will enhance photos with face protection.")
        else:
            print("\n❌ Please fix AI enhancement issues before proceeding.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 AI enhancement test cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Fatal error during AI enhancement test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)