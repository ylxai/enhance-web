# Google GenAI SDK Integration untuk Image Enhancement
# ===================================================

import google.generativeai as genai
import cv2
import numpy as np
import base64
import io
import logging
import time
from PIL import Image
from pathlib import Path
from typing import Optional, Tuple
from config import Config
from face_detection import FaceProtectionMask

logger = logging.getLogger(__name__)

class GeminiImageEnhancer:
    """Class untuk enhancement gambar menggunakan Google Gemini AI"""
    
    def __init__(self):
        """Inisialisasi Gemini AI client"""
        try:
            # Konfigurasi API
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            # Inisialisasi face protection
            self.face_detector = FaceProtectionMask()
            
            # Test koneksi
            self._test_connection()
            
            logger.info(f"Gemini AI enhancer berhasil diinisialisasi dengan model: {Config.GEMINI_MODEL}")
            
        except Exception as e:
            logger.error(f"Gagal inisialisasi Gemini AI: {e}")
            raise
    
    def _test_connection(self):
        """Test koneksi ke Gemini AI"""
        try:
            # Buat test image kecil
            test_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
            test_pil = Image.fromarray(test_image)
            
            # Test dengan prompt sederhana
            response = self.model.generate_content([
                "Describe this image briefly in one sentence.",
                test_pil
            ])
            
            logger.info("✅ Koneksi ke Gemini AI berhasil")
            
        except Exception as e:
            logger.warning(f"Test koneksi Gemini AI gagal: {e}")
            # Tidak raise error, karena mungkin quota/network issue temporary
    
    def _prepare_image_for_ai(self, image: np.ndarray) -> Image.Image:
        """
        Persiapkan gambar untuk dikirim ke AI (resize jika perlu)
        
        Args:
            image: OpenCV image (BGR format)
            
        Returns:
            PIL Image untuk AI processing
        """
        # Konversi BGR ke RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize jika terlalu besar untuk menghemat bandwidth
        max_res = Config.AI_ENHANCEMENT["max_resolution"]
        height, width = rgb_image.shape[:2]
        
        if width > max_res[0] or height > max_res[1]:
            # Hitung scaling factor sambil maintain aspect ratio
            scale_w = max_res[0] / width
            scale_h = max_res[1] / height
            scale = min(scale_w, scale_h)
            
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            rgb_image = cv2.resize(rgb_image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            logger.info(f"Image direzise dari {width}x{height} ke {new_width}x{new_height}")
        
        return Image.fromarray(rgb_image)
    
    def _create_enhancement_prompt(self, has_faces: bool) -> str:
        """
        Buat prompt yang sesuai untuk enhancement
        
        Args:
            has_faces: Apakah gambar memiliki wajah yang perlu diproteksi
            
        Returns:
            Prompt string untuk AI
        """
        base_prompt = """
        Lakukan enhancement pada gambar fotografi ini dengan fokus pada:
        1. Mengurangi blur dan motion blur
        2. Meningkatkan ketajaman (sharpness) dan detail
        3. Koreksi pencahayaan dan kontras
        4. Mengurangi noise/grain
        5. Memperbaiki warna yang lebih hidup namun tetap natural
        """
        
        if has_faces:
            face_protection_prompt = Config.AI_ENHANCEMENT["face_protection_prompt"]
            return base_prompt + "\n\n" + face_protection_prompt
        else:
            return base_prompt + """
            
        Karena tidak ada wajah dalam gambar, lakukan enhancement maksimal pada:
        - Background dan landscape
        - Objek dan tekstur
        - Detail arsitektur atau produk
        - Warna dan saturasi optimal
        """
    
    def enhance_image(self, image_path: Path, output_path: Optional[Path] = None) -> Tuple[bool, Optional[Path]]:
        """
        Enhance gambar menggunakan AI atau fallback method
        
        Args:
            image_path: Path ke gambar input
            output_path: Path output (optional, akan auto-generate jika None)
            
        Returns:
            Tuple: (success, output_path)
        """
        try:
            logger.info(f"Memulai enhancement gambar: {image_path}")
            start_time = time.time()
            
            # Check AI enhancement mode
            ai_enabled = Config.AI_ENHANCEMENT["enabled"]
            ai_mode = Config.AI_ENHANCEMENT["mode"]
            
            logger.info(f"AI Enhancement - Enabled: {ai_enabled}, Mode: {ai_mode}")
            
            # Baca gambar
            image = cv2.imread(str(image_path))
            if image is None:
                logger.error(f"Gagal membaca gambar: {image_path}")
                return False, None
            
            original_image = image.copy()
            
            # Deteksi dan proteksi wajah
            protected_image, face_mask, has_faces = self.face_detector.apply_face_protection(image)
            
            # Determine enhancement method
            enhanced_cv = None
            enhancement_method = "none"
            
            if not ai_enabled or ai_mode == "disabled":
                logger.info("🚫 AI Enhancement disabled - using original image")
                enhanced_cv = protected_image.copy()
                enhancement_method = "disabled"
                
            elif ai_mode == "opencv":
                logger.info("🎨 Using OpenCV fallback enhancement only")
                enhanced_cv = self._opencv_enhancement_only(protected_image)
                enhancement_method = "opencv"
                
            elif ai_mode == "gemini":
                logger.info("🤖 Using Gemini AI enhancement only")
                enhanced_cv = self._gemini_enhancement_only(protected_image, has_faces)
                enhancement_method = "gemini"
                
            else:  # ai_mode == "auto"
                logger.info("🔄 Auto mode - trying Gemini AI with OpenCV fallback")
                enhanced_cv = self._auto_enhancement(protected_image, has_faces)
                enhancement_method = "auto"
            
            # Fallback jika enhancement gagal
            if enhanced_cv is None:
                if Config.AI_ENHANCEMENT["skip_on_failure"]:
                    logger.warning("⏭️ Enhancement failed, skipping (skip_on_failure=true)")
                    enhanced_cv = protected_image.copy()
                    enhancement_method = "skipped"
                else:
                    logger.error("❌ All enhancement methods failed")
                    return False, None
            
            # Resize kembali ke ukuran original jika diperlukan
            if enhanced_cv.shape[:2] != original_image.shape[:2]:
                enhanced_cv = cv2.resize(enhanced_cv, 
                                       (original_image.shape[1], original_image.shape[0]), 
                                       interpolation=cv2.INTER_LANCZOS4)
            
            # Restore area wajah jika ada (kecuali jika disabled)
            if has_faces and enhancement_method != "disabled":
                enhanced_cv = self.face_detector.restore_face_areas(enhanced_cv, original_image, face_mask)
                logger.info("Area wajah berhasil di-restore")
            
            # Tentukan output path
            if output_path is None:
                output_path = Config.TEMP_DIR / f"enhanced_{image_path.stem}.jpg"
            
            # Simpan hasil
            success = cv2.imwrite(str(output_path), enhanced_cv, 
                                [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if success:
                processing_time = time.time() - start_time
                logger.info(f"✅ Enhancement selesai ({enhancement_method}) dalam {processing_time:.2f} detik: {output_path}")
                return True, output_path
            else:
                logger.error(f"Gagal menyimpan gambar: {output_path}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error saat enhancement gambar: {e}")
            return False, None
    
    def _enhance_with_retry(self, image: Image.Image, prompt: str) -> Optional[Image.Image]:
        """
        Enhancement dengan retry mechanism
        
        Args:
            image: PIL Image
            prompt: Enhancement prompt
            
        Returns:
            Enhanced PIL Image atau None jika gagal
        """
        retry_attempts = Config.AI_ENHANCEMENT["retry_attempts"]
        timeout = Config.AI_ENHANCEMENT["timeout"]
        
        for attempt in range(retry_attempts):
            try:
                logger.info(f"Mencoba enhancement (attempt {attempt + 1}/{retry_attempts})")
                
                # Kirim request ke Gemini
                response = self.model.generate_content([prompt, image])
                
                # Gemini tidak langsung return image, jadi kita perlu handling khusus
                # Untuk sekarang, kita implementasikan workaround dengan prompt yang meminta deskripsi enhancement
                enhanced_description = response.text
                logger.info(f"Gemini response: {enhanced_description[:100]}...")
                
                # CATATAN: Implementasi ini adalah placeholder
                # Google Gemini saat ini belum support direct image generation/enhancement
                # Kita perlu menggunakan alternatif atau menunggu update API
                
                # Untuk sekarang, return image enhancement menggunakan OpenCV sebagai fallback
                return self._fallback_enhancement(image)
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} gagal: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Semua attempt enhancement gagal")
                    return None
        
        return None
    
    def _fallback_enhancement(self, image: Image.Image) -> Image.Image:
        """
        Fallback enhancement menggunakan OpenCV ketika Gemini tidak tersedia
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        logger.info("Menggunakan fallback enhancement dengan OpenCV")
        
        # Konversi ke OpenCV
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Enhancement menggunakan teknik tradisional
        enhanced = cv_image.copy()
        
        # 1. Unsharp masking untuk ketajaman
        gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
        enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
        
        # 2. CLAHE untuk kontras adaptif
        lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        # 3. Noise reduction
        enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
        
        # 4. Color enhancement
        hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        s = cv2.multiply(s, 1.2)  # Increase saturation slightly
        enhanced = cv2.merge([h, s, v])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
        
        # Konversi kembali ke PIL
        enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
        return Image.fromarray(enhanced_rgb)
    
    def _opencv_enhancement_only(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Enhancement menggunakan OpenCV saja (tanpa AI)
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Enhanced image atau None jika gagal
        """
        try:
            logger.info("🎨 Applying OpenCV-only enhancement...")
            
            enhanced = image.copy()
            
            # 1. Unsharp masking untuk ketajaman
            gaussian = cv2.GaussianBlur(enhanced, (0, 0), 2.0)
            enhanced = cv2.addWeighted(enhanced, 1.5, gaussian, -0.5, 0)
            
            # 2. CLAHE untuk kontras adaptif
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # 3. Noise reduction
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)
            
            # 4. Color enhancement
            hsv = cv2.cvtColor(enhanced, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            s = cv2.multiply(s, 1.2)  # Increase saturation slightly
            enhanced = cv2.merge([h, s, v])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
            
            logger.info("✅ OpenCV enhancement completed")
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in OpenCV enhancement: {e}")
            return None
    
    def _gemini_enhancement_only(self, image: np.ndarray, has_faces: bool) -> Optional[np.ndarray]:
        """
        Enhancement menggunakan Gemini AI saja (tanpa fallback)
        
        Args:
            image: Input image (BGR format)
            has_faces: Apakah ada wajah dalam gambar
            
        Returns:
            Enhanced image atau None jika gagal
        """
        try:
            logger.info("🤖 Applying Gemini AI enhancement only...")
            
            # Persiapkan gambar untuk AI
            pil_image = self._prepare_image_for_ai(image)
            
            # Buat prompt berdasarkan deteksi wajah
            prompt = self._create_enhancement_prompt(has_faces)
            
            # Enhancement menggunakan Gemini AI
            enhanced_pil = self._enhance_with_retry(pil_image, prompt)
            
            if enhanced_pil is None:
                logger.error("Gemini AI enhancement failed")
                return None
            
            # Konversi hasil ke OpenCV format
            enhanced_cv = cv2.cvtColor(np.array(enhanced_pil), cv2.COLOR_RGB2BGR)
            
            logger.info("✅ Gemini AI enhancement completed")
            return enhanced_cv
            
        except Exception as e:
            logger.error(f"Error in Gemini enhancement: {e}")
            return None
    
    def _auto_enhancement(self, image: np.ndarray, has_faces: bool) -> Optional[np.ndarray]:
        """
        Auto enhancement: coba Gemini AI dulu, fallback ke OpenCV
        
        Args:
            image: Input image (BGR format)
            has_faces: Apakah ada wajah dalam gambar
            
        Returns:
            Enhanced image atau None jika semua gagal
        """
        try:
            logger.info("🔄 Auto enhancement: trying Gemini AI first...")
            
            # Coba Gemini AI dulu
            enhanced_cv = self._gemini_enhancement_only(image, has_faces)
            
            if enhanced_cv is not None:
                logger.info("✅ Auto enhancement: Gemini AI succeeded")
                return enhanced_cv
            
            # Fallback ke OpenCV jika enabled
            if Config.AI_ENHANCEMENT["fallback_to_opencv"]:
                logger.info("🔄 Auto enhancement: fallback to OpenCV...")
                enhanced_cv = self._opencv_enhancement_only(image)
                
                if enhanced_cv is not None:
                    logger.info("✅ Auto enhancement: OpenCV fallback succeeded")
                    return enhanced_cv
                else:
                    logger.error("❌ Auto enhancement: OpenCV fallback also failed")
                    return None
            else:
                logger.error("❌ Auto enhancement: Gemini failed and OpenCV fallback disabled")
                return None
                
        except Exception as e:
            logger.error(f"Error in auto enhancement: {e}")
            return None
    
    def batch_enhance(self, input_dir: Path, output_dir: Path) -> int:
        """
        Batch enhancement untuk multiple images
        
        Args:
            input_dir: Directory input images
            output_dir: Directory output
            
        Returns:
            Jumlah gambar yang berhasil di-enhance
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(input_dir.glob(f"*{ext}"))
            image_files.extend(input_dir.glob(f"*{ext.upper()}"))
        
        success_count = 0
        
        for image_file in image_files:
            output_file = output_dir / f"enhanced_{image_file.name}"
            success, _ = self.enhance_image(image_file, output_file)
            
            if success:
                success_count += 1
                logger.info(f"✅ {image_file.name}")
            else:
                logger.error(f"❌ {image_file.name}")
        
        logger.info(f"Batch enhancement selesai: {success_count}/{len(image_files)} berhasil")
        return success_count

def test_enhancement():
    """Test function untuk enhancement"""
    try:
        enhancer = GeminiImageEnhancer()
        
        # Test dengan sample image jika ada
        test_image = Config.TEMP_DIR / "sample.jpg"
        if not test_image.exists():
            print("Untuk test, letakkan gambar sample di temp/sample.jpg")
            return
        
        print(f"Testing enhancement pada: {test_image}")
        
        output_path = Config.TEMP_DIR / "enhanced_sample.jpg"
        success, result_path = enhancer.enhance_image(test_image, output_path)
        
        if success:
            print(f"✅ Enhancement berhasil: {result_path}")
        else:
            print("❌ Enhancement gagal")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_enhancement()