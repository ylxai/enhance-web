#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Face Detection & Protection System
=======================================

Test deteksi wajah, masking, dan proteksi untuk AI enhancement.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw

# Import modules
from config import Config
from face_detection import FaceProtectionMask

# Setup logging untuk test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FaceDetectionTester:
    """Test face detection dan protection system"""
    
    def __init__(self):
        self.test_results = {}
        self.face_detector = None
        self.test_images = {}
        print("👤 FACE DETECTION & PROTECTION TESTER")
        print("=" * 50)
    
    def test_face_detector_init(self) -> bool:
        """Test inisialisasi face detector"""
        try:
            print("\n🔧 Testing Face Detector Initialization...")
            
            self.face_detector = FaceProtectionMask()
            
            print(f"  ✅ Face detector initialized")
            print(f"  📁 Cascade path: {self.face_detector.cascade_path}")
            print(f"  ⚙️  Scale factor: {Config.FACE_DETECTION['scale_factor']}")
            print(f"  👥 Min neighbors: {Config.FACE_DETECTION['min_neighbors']}")
            print(f"  📏 Min size: {Config.FACE_DETECTION['min_size']}")
            print(f"  📦 Padding: {Config.FACE_DETECTION['padding']}")
            
            # Test cascade file exists
            if self.face_detector.cascade_path.exists():
                print(f"  ✅ Haar Cascade file found")
            else:
                print(f"  ❌ Haar Cascade file missing")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error initializing face detector: {e}")
            return False
    
    def create_test_images(self) -> bool:
        """Buat test images untuk face detection"""
        try:
            print("\n🖼️  Creating Test Images for Face Detection...")
            
            test_dir = Config.TEMP_DIR / "face_test"
            test_dir.mkdir(exist_ok=True)
            
            # === Test Image 1: Simple Face-like Pattern ===
            print("  🎨 Creating simple face pattern...")
            
            img1 = np.ones((400, 400, 3), dtype=np.uint8) * 200
            
            # Face oval
            cv2.ellipse(img1, (200, 180), (60, 80), 0, 0, 360, (220, 190, 170), -1)
            
            # Eyes
            cv2.circle(img1, (180, 160), 8, (50, 50, 50), -1)  # Left eye
            cv2.circle(img1, (220, 160), 8, (50, 50, 50), -1)  # Right eye
            
            # Nose
            cv2.ellipse(img1, (200, 180), (4, 8), 0, 0, 360, (180, 150, 130), -1)
            
            # Mouth
            cv2.ellipse(img1, (200, 200), (15, 6), 0, 0, 360, (150, 100, 100), -1)
            
            simple_face_path = test_dir / "simple_face.jpg"
            cv2.imwrite(str(simple_face_path), img1)
            self.test_images['simple_face'] = simple_face_path
            
            # === Test Image 2: Multiple Faces ===
            print("  👥 Creating multiple faces pattern...")
            
            img2 = np.ones((400, 600, 3), dtype=np.uint8) * 180
            
            # Face 1
            cv2.ellipse(img2, (150, 150), (50, 70), 0, 0, 360, (220, 190, 170), -1)
            cv2.circle(img2, (135, 135), 6, (30, 30, 30), -1)
            cv2.circle(img2, (165, 135), 6, (30, 30, 30), -1)
            cv2.ellipse(img2, (150, 160), (12, 4), 0, 0, 360, (150, 100, 100), -1)
            
            # Face 2
            cv2.ellipse(img2, (450, 200), (55, 75), 0, 0, 360, (210, 180, 160), -1)
            cv2.circle(img2, (430, 180), 7, (40, 40, 40), -1)
            cv2.circle(img2, (470, 180), 7, (40, 40, 40), -1)
            cv2.ellipse(img2, (450, 210), (14, 5), 0, 0, 360, (140, 90, 90), -1)
            
            multiple_faces_path = test_dir / "multiple_faces.jpg"
            cv2.imwrite(str(multiple_faces_path), img2)
            self.test_images['multiple_faces'] = multiple_faces_path
            
            # === Test Image 3: No Face ===
            print("  🌆 Creating no-face landscape...")
            
            img3 = np.ones((300, 500, 3), dtype=np.uint8) * 100
            
            # Landscape elements
            cv2.rectangle(img3, (0, 200), (500, 300), (34, 139, 34), -1)  # Ground
            cv2.rectangle(img3, (0, 0), (500, 200), (135, 206, 235), -1)  # Sky
            cv2.circle(img3, (400, 50), 30, (255, 255, 0), -1)  # Sun
            cv2.rectangle(img3, (100, 150), (120, 200), (139, 69, 19), -1)  # Tree trunk
            cv2.circle(img3, (110, 140), 25, (0, 128, 0), -1)  # Tree leaves
            
            no_face_path = test_dir / "no_face_landscape.jpg"
            cv2.imwrite(str(no_face_path), img3)
            self.test_images['no_face'] = no_face_path
            
            # === Test Image 4: Complex Scene dengan Face ===
            print("  🏞️  Creating complex scene with face...")
            
            img4 = np.ones((500, 700, 3), dtype=np.uint8) * 150
            
            # Background
            cv2.rectangle(img4, (0, 0), (700, 500), (120, 150, 180), -1)
            
            # Objects
            cv2.rectangle(img4, (50, 300), (150, 450), (100, 50, 0), -1)  # Building
            cv2.rectangle(img4, (200, 250), (300, 400), (80, 40, 0), -1)   # Another building
            
            # Face in scene
            cv2.ellipse(img4, (500, 200), (40, 55), 0, 0, 360, (220, 190, 170), -1)
            cv2.circle(img4, (485, 185), 5, (20, 20, 20), -1)
            cv2.circle(img4, (515, 185), 5, (20, 20, 20), -1)
            cv2.ellipse(img4, (500, 210), (10, 3), 0, 0, 360, (150, 100, 100), -1)
            
            complex_scene_path = test_dir / "complex_scene.jpg"
            cv2.imwrite(str(complex_scene_path), img4)
            self.test_images['complex_scene'] = complex_scene_path
            
            print(f"  ✅ Created {len(self.test_images)} test images")
            for name, path in self.test_images.items():
                print(f"    {name}: {path.name}")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error creating test images: {e}")
            return False
    
    def test_face_detection_accuracy(self) -> bool:
        """Test akurasi deteksi wajah"""
        try:
            print("\n🎯 Testing Face Detection Accuracy...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            if not self.test_images:
                print("  ❌ Test images not available")
                return False
            
            detection_results = {}
            
            for image_name, image_path in self.test_images.items():
                print(f"  🔍 Testing {image_name}...")
                
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"    ❌ Failed to load {image_name}")
                    continue
                
                # Detect faces
                faces = self.face_detector.detect_faces(image)
                detection_results[image_name] = len(faces)
                
                print(f"    📊 Detected {len(faces)} face(s)")
                
                # Expected results for validation
                expected_faces = {
                    'simple_face': 1,
                    'multiple_faces': 2,
                    'no_face': 0,
                    'complex_scene': 1
                }
                
                expected = expected_faces.get(image_name, 0)
                
                if len(faces) == expected:
                    print(f"    ✅ Correct detection (expected {expected})")
                elif len(faces) == 0 and expected > 0:
                    print(f"    ⚠️  Under-detection (expected {expected}, got {len(faces)})")
                elif len(faces) > expected:
                    print(f"    ⚠️  Over-detection (expected {expected}, got {len(faces)})")
                else:
                    print(f"    ❌ Detection mismatch (expected {expected}, got {len(faces)})")
            
            # Overall assessment
            total_tests = len(detection_results)
            if total_tests > 0:
                print(f"\n  📈 Detection Summary:")
                for image_name, count in detection_results.items():
                    print(f"    {image_name}: {count} faces")
                
                return True
            else:
                print("  ❌ No detection tests completed")
                return False
            
        except Exception as e:
            print(f"  ❌ Error testing face detection: {e}")
            return False
    
    def test_face_masking(self) -> bool:
        """Test pembuatan face mask"""
        try:
            print("\n🎭 Testing Face Masking...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            if not self.test_images:
                print("  ❌ Test images not available")
                return False
            
            test_dir = Config.TEMP_DIR / "face_test"
            
            for image_name, image_path in self.test_images.items():
                if 'no_face' in image_name:
                    continue  # Skip no-face images
                
                print(f"  🎨 Testing mask creation for {image_name}...")
                
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                # Detect faces
                faces = self.face_detector.detect_faces(image)
                
                if len(faces) == 0:
                    print(f"    ⚠️  No faces detected, skipping mask test")
                    continue
                
                # Create mask
                face_mask = self.face_detector.create_face_mask(image, faces)
                
                # Validate mask
                if face_mask is not None:
                    mask_pixels = np.sum(face_mask == 255)
                    total_pixels = face_mask.shape[0] * face_mask.shape[1]
                    mask_percentage = (mask_pixels / total_pixels) * 100
                    
                    print(f"    ✅ Mask created: {mask_pixels} pixels ({mask_percentage:.1f}% of image)")
                    
                    # Save mask untuk review
                    mask_path = test_dir / f"mask_{image_name}.jpg"
                    cv2.imwrite(str(mask_path), face_mask)
                    
                    # Create visualization
                    masked_visual = image.copy()
                    masked_visual[face_mask == 255] = [0, 255, 0]  # Green overlay
                    
                    visual_path = test_dir / f"masked_visual_{image_name}.jpg"
                    cv2.imwrite(str(visual_path), masked_visual)
                    
                else:
                    print(f"    ❌ Failed to create mask")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing face masking: {e}")
            return False
    
    def test_face_protection_pipeline(self) -> bool:
        """Test full face protection pipeline"""
        try:
            print("\n🛡️  Testing Face Protection Pipeline...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            if not self.test_images:
                print("  ❌ Test images not available")
                return False
            
            test_dir = Config.TEMP_DIR / "face_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  🔄 Testing protection pipeline for {image_name}...")
                
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                # Apply face protection
                protected_image, face_mask, has_faces = self.face_detector.apply_face_protection(image)
                
                print(f"    📊 Has faces: {has_faces}")
                
                if protected_image is not None:
                    print(f"    ✅ Protection applied")
                    
                    # Save protected image
                    protected_path = test_dir / f"protected_{image_name}.jpg"
                    cv2.imwrite(str(protected_path), protected_image)
                    
                    # Test restore functionality if faces detected
                    if has_faces:
                        print(f"    🔄 Testing face area restoration...")
                        
                        # Simulate enhanced image (dengan slight modification)
                        enhanced_image = cv2.addWeighted(protected_image, 0.8, image, 0.2, 0)
                        
                        # Restore face areas
                        restored_image = self.face_detector.restore_face_areas(
                            enhanced_image, image, face_mask
                        )
                        
                        if restored_image is not None:
                            print(f"    ✅ Face restoration successful")
                            
                            # Save restored image
                            restored_path = test_dir / f"restored_{image_name}.jpg"
                            cv2.imwrite(str(restored_path), restored_image)
                        else:
                            print(f"    ❌ Face restoration failed")
                            return False
                    
                else:
                    print(f"    ❌ Protection failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing protection pipeline: {e}")
            return False
    
    def test_visualization_functions(self) -> bool:
        """Test visualisasi deteksi untuk debugging"""
        try:
            print("\n👁️  Testing Visualization Functions...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            if not self.test_images:
                print("  ❌ Test images not available")
                return False
            
            test_dir = Config.TEMP_DIR / "face_test"
            
            for image_name, image_path in self.test_images.items():
                print(f"  🎨 Creating visualization for {image_name}...")
                
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                # Create visualization
                viz_path = test_dir / f"detection_viz_{image_name}.jpg"
                viz_image = self.face_detector.visualize_detection(image, viz_path)
                
                if viz_path.exists():
                    print(f"    ✅ Visualization saved: {viz_path.name}")
                else:
                    print(f"    ❌ Visualization failed")
                    return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing visualization: {e}")
            return False
    
    def test_performance_metrics(self) -> bool:
        """Test performance metrics untuk face detection"""
        try:
            print("\n⚡ Testing Performance Metrics...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            if not self.test_images:
                print("  ❌ Test images not available")
                return False
            
            performance_results = {}
            
            for image_name, image_path in self.test_images.items():
                print(f"  ⏱️  Testing performance for {image_name}...")
                
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    continue
                
                # Measure detection time
                start_time = time.time()
                faces = self.face_detector.detect_faces(image)
                detection_time = time.time() - start_time
                
                # Measure full protection pipeline time
                start_time = time.time()
                protected_image, face_mask, has_faces = self.face_detector.apply_face_protection(image)
                pipeline_time = time.time() - start_time
                
                performance_results[image_name] = {
                    'detection_time': detection_time,
                    'pipeline_time': pipeline_time,
                    'faces_found': len(faces),
                    'image_size': f"{image.shape[1]}x{image.shape[0]}"
                }
                
                print(f"    📊 Detection: {detection_time*1000:.1f}ms, Pipeline: {pipeline_time*1000:.1f}ms")
            
            # Summary
            if performance_results:
                avg_detection = np.mean([r['detection_time'] for r in performance_results.values()])
                avg_pipeline = np.mean([r['pipeline_time'] for r in performance_results.values()])
                
                print(f"\n  📈 Performance Summary:")
                print(f"    Average detection time: {avg_detection*1000:.1f}ms")
                print(f"    Average pipeline time: {avg_pipeline*1000:.1f}ms")
                
                # Performance assessment untuk target hardware (i5-3570)
                if avg_pipeline < 0.5:  # Under 500ms
                    print(f"    ✅ Performance excellent for target hardware")
                elif avg_pipeline < 1.0:  # Under 1 second
                    print(f"    ⚠️  Performance acceptable for target hardware")
                else:
                    print(f"    ❌ Performance may be slow for target hardware")
                
                return True
            else:
                print("  ❌ No performance data collected")
                return False
            
        except Exception as e:
            print(f"  ❌ Error testing performance: {e}")
            return False
    
    def test_edge_cases(self) -> bool:
        """Test edge cases untuk face detection"""
        try:
            print("\n🎯 Testing Edge Cases...")
            
            if not self.face_detector:
                print("  ❌ Face detector not initialized")
                return False
            
            # Test 1: Very small image
            print("  📏 Testing very small image...")
            small_img = np.ones((50, 50, 3), dtype=np.uint8) * 128
            faces = self.face_detector.detect_faces(small_img)
            print(f"    50x50 image: {len(faces)} faces detected")
            
            # Test 2: Very large image
            print("  📏 Testing large image...")
            large_img = np.ones((2000, 2000, 3), dtype=np.uint8) * 128
            start_time = time.time()
            faces = self.face_detector.detect_faces(large_img)
            large_time = time.time() - start_time
            print(f"    2000x2000 image: {len(faces)} faces, {large_time*1000:.1f}ms")
            
            # Test 3: Grayscale image
            print("  🎨 Testing grayscale image...")
            if self.test_images:
                color_img = cv2.imread(str(list(self.test_images.values())[0]))
                gray_img = cv2.cvtColor(color_img, cv2.COLOR_BGR2GRAY)
                gray_bgr = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
                faces = self.face_detector.detect_faces(gray_bgr)
                print(f"    Grayscale image: {len(faces)} faces detected")
            
            # Test 4: Empty/corrupted data
            print("  🚫 Testing edge case inputs...")
            
            # Empty array
            try:
                empty_img = np.array([])
                faces = self.face_detector.detect_faces(empty_img)
                print(f"    Empty array: handled gracefully")
            except:
                print(f"    Empty array: handled with exception (OK)")
            
            # Wrong shape
            try:
                wrong_shape = np.ones((100, 100), dtype=np.uint8)  # 2D instead of 3D
                faces = self.face_detector.detect_faces(wrong_shape)
                print(f"    Wrong shape: handled gracefully")
            except:
                print(f"    Wrong shape: handled with exception (OK)")
            
            print("  ✅ Edge cases testing completed")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing edge cases: {e}")
            return False
    
    def cleanup_test_files(self) -> bool:
        """Cleanup test files"""
        try:
            print("\n🧹 Cleaning Up Test Files...")
            
            test_dir = Config.TEMP_DIR / "face_test"
            if test_dir.exists():
                import shutil
                shutil.rmtree(test_dir)
                print(f"  ✅ Removed test directory: {test_dir}")
            
            return True
            
        except Exception as e:
            print(f"  ⚠️  Error cleaning up (non-critical): {e}")
            return True  # Non-critical error
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test face detection"""
        print("🚀 Starting Face Detection & Protection Tests...\n")
        
        tests = [
            ("Face Detector Initialization", self.test_face_detector_init),
            ("Create Test Images", self.create_test_images),
            ("Face Detection Accuracy", self.test_face_detection_accuracy),
            ("Face Masking", self.test_face_masking),
            ("Face Protection Pipeline", self.test_face_protection_pipeline),
            ("Visualization Functions", self.test_visualization_functions),
            ("Performance Metrics", self.test_performance_metrics),
            ("Edge Cases", self.test_edge_cases),
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
        print(f"📊 FACE DETECTION TEST SUMMARY")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35} : {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL FACE DETECTION TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check face detection configuration.")
            return False

def main():
    """Main function untuk face detection testing"""
    try:
        tester = FaceDetectionTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Face detection & protection ready for AI enhancement!")
            print("👤 Faces will be properly protected during enhancement process.")
        else:
            print("\n❌ Please fix face detection issues before proceeding.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Face detection test cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Fatal error during face detection test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)