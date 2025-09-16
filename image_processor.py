# Image Processing untuk LUT, Auto-Crop, dan Watermark
# ====================================================

import cv2
import numpy as np
import logging
from PIL import Image, ImageDraw
from pathlib import Path
from typing import Tuple, Optional
import colour
from config import Config

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Class untuk processing gambar: LUT, cropping, watermarking"""
    
    def __init__(self):
        """Inisialisasi image processor"""
        self.lut_cache = {}  # Cache untuk LUT yang sudah dimuat
        self.watermark_cache = {}  # Cache untuk watermark
        logger.info("Image processor berhasil diinisialisasi")
    
    def load_lut(self, lut_path: Optional[Path] = None) -> Optional[np.ndarray]:
        """
        Load LUT file (.cube format)
        
        Args:
            lut_path: Path ke file LUT (optional, akan pakai default dari config)
            
        Returns:
            LUT array atau None jika gagal
        """
        if lut_path is None:
            lut_path = Config.PRESETS_DIR / Config.LUT_SETTINGS["file"]
        
        # Check cache
        cache_key = str(lut_path)
        if cache_key in self.lut_cache:
            return self.lut_cache[cache_key]
        
        try:
            if not lut_path.exists():
                logger.warning(f"File LUT tidak ditemukan: {lut_path}")
                return None
            
            # Load .cube LUT file
            with open(lut_path, 'r') as f:
                lines = f.readlines()
            
            # Parse .cube file
            lut_size = 33  # Default size untuk .cube
            lut_data = []
            
            for line in lines:
                line = line.strip()
                
                # Skip comments dan metadata
                if line.startswith('#') or line.startswith('TITLE') or line.startswith('DOMAIN_MIN') or line.startswith('DOMAIN_MAX'):
                    continue
                    
                # Check LUT size
                if line.startswith('LUT_3D_SIZE'):
                    lut_size = int(line.split()[1])
                    continue
                
                # Parse RGB values
                if line and not line.startswith('LUT_1D_SIZE'):
                    try:
                        r, g, b = map(float, line.split()[:3])
                        lut_data.append([r, g, b])
                    except ValueError:
                        continue
            
            if len(lut_data) != lut_size ** 3:
                logger.error(f"LUT size mismatch: expected {lut_size**3}, got {len(lut_data)}")
                return None
            
            # Convert ke numpy array dan reshape
            lut_array = np.array(lut_data, dtype=np.float32)
            lut_array = lut_array.reshape(lut_size, lut_size, lut_size, 3)
            
            # Convert dari range 0-1 ke 0-255 jika diperlukan
            if lut_array.max() <= 1.0:
                lut_array = lut_array * 255
            
            # Cache LUT
            self.lut_cache[cache_key] = lut_array
            
            logger.info(f"✅ LUT berhasil dimuat: {lut_path} (size: {lut_size}x{lut_size}x{lut_size})")
            return lut_array
            
        except Exception as e:
            logger.error(f"Gagal memuat LUT {lut_path}: {e}")
            return None
    
    def apply_lut(self, image: np.ndarray, lut_path: Optional[Path] = None, intensity: float = 1.0) -> np.ndarray:
        """
        Aplikasikan LUT ke gambar
        
        Args:
            image: Input image (BGR format)
            lut_path: Path ke LUT file (optional)
            intensity: Intensitas aplikasi LUT (0.0-1.0)
            
        Returns:
            Gambar dengan LUT applied
        """
        try:
            # Load LUT
            lut = self.load_lut(lut_path)
            if lut is None:
                logger.warning("LUT tidak tersedia, skip aplikasi LUT")
                return image
            
            # Convert BGR ke RGB untuk processing
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            original_image = rgb_image.copy()
            
            # Normalisasi input ke range 0-1
            normalized_img = rgb_image.astype(np.float32) / 255.0
            
            # Apply LUT menggunakan interpolasi trilinear
            lut_size = lut.shape[0]
            
            # Scale coordinates ke LUT space
            coords = normalized_img * (lut_size - 1)
            
            # Floor coordinates untuk interpolasi
            coords_floor = np.floor(coords).astype(np.int32)
            coords_floor = np.clip(coords_floor, 0, lut_size - 2)
            
            # Fractional parts untuk interpolasi
            fractions = coords - coords_floor
            
            # Trilinear interpolation
            # Get 8 corner values
            c000 = lut[coords_floor[:,:,0], coords_floor[:,:,1], coords_floor[:,:,2]]
            c001 = lut[coords_floor[:,:,0], coords_floor[:,:,1], coords_floor[:,:,2] + 1]
            c010 = lut[coords_floor[:,:,0], coords_floor[:,:,1] + 1, coords_floor[:,:,2]]
            c011 = lut[coords_floor[:,:,0], coords_floor[:,:,1] + 1, coords_floor[:,:,2] + 1]
            c100 = lut[coords_floor[:,:,0] + 1, coords_floor[:,:,1], coords_floor[:,:,2]]
            c101 = lut[coords_floor[:,:,0] + 1, coords_floor[:,:,1], coords_floor[:,:,2] + 1]
            c110 = lut[coords_floor[:,:,0] + 1, coords_floor[:,:,1] + 1, coords_floor[:,:,2]]
            c111 = lut[coords_floor[:,:,0] + 1, coords_floor[:,:,1] + 1, coords_floor[:,:,2] + 1]
            
            # Interpolate along x
            xf = fractions[:,:,0:1]
            c00 = c000 * (1 - xf) + c100 * xf
            c01 = c001 * (1 - xf) + c101 * xf
            c10 = c010 * (1 - xf) + c110 * xf
            c11 = c011 * (1 - xf) + c111 * xf
            
            # Interpolate along y
            yf = fractions[:,:,1:2]
            c0 = c00 * (1 - yf) + c10 * yf
            c1 = c01 * (1 - yf) + c11 * yf
            
            # Interpolate along z
            zf = fractions[:,:,2:3]
            result = c0 * (1 - zf) + c1 * zf
            
            # Convert kembali ke 0-255 range
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            # Blend dengan original berdasarkan intensity
            if intensity < 1.0:
                result = original_image * (1 - intensity) + result * intensity
                result = result.astype(np.uint8)
            
            # Convert kembali ke BGR
            result_bgr = cv2.cvtColor(result, cv2.COLOR_RGB2BGR)
            
            logger.info(f"✅ LUT applied dengan intensity {intensity}")
            return result_bgr
            
        except Exception as e:
            logger.error(f"Error saat aplikasi LUT: {e}")
            return image
    
    def detect_orientation(self, image: np.ndarray) -> str:
        """
        Deteksi orientasi gambar (portrait atau landscape)
        
        Args:
            image: Input image
            
        Returns:
            "portrait" atau "landscape"
        """
        height, width = image.shape[:2]
        return "portrait" if height > width else "landscape"
    
    def calculate_crop_dimensions(self, image: np.ndarray, target_ratio: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Hitung dimensi crop untuk mendapatkan ratio yang diinginkan
        
        Args:
            image: Input image
            target_ratio: Target ratio (w, h)
            
        Returns:
            Tuple (x, y, width, height) untuk crop
        """
        height, width = image.shape[:2]
        target_w, target_h = target_ratio
        
        # Hitung ratio
        current_ratio = width / height
        target_ratio_value = target_w / target_h
        
        if current_ratio > target_ratio_value:
            # Image terlalu lebar, crop dari kiri-kanan
            new_width = int(height * target_ratio_value)
            new_height = height
            x = (width - new_width) // 2
            y = 0
        else:
            # Image terlalu tinggi, crop dari atas-bawah
            new_width = width
            new_height = int(width / target_ratio_value)
            x = 0
            y = (height - new_height) // 2
        
        return x, y, new_width, new_height
    
    def auto_crop(self, image: np.ndarray) -> np.ndarray:
        """
        Auto crop gambar berdasarkan orientasi
        
        Args:
            image: Input image
            
        Returns:
            Cropped image
        """
        try:
            orientation = self.detect_orientation(image)
            
            if orientation == "portrait":
                target_ratio = Config.AUTO_CROP["portrait_ratio"]
            else:
                target_ratio = Config.AUTO_CROP["landscape_ratio"]
            
            # Hitung crop dimensions
            x, y, width, height = self.calculate_crop_dimensions(image, target_ratio)
            
            # Crop image
            cropped = image[y:y+height, x:x+width]
            
            # Check minimum resolution
            min_res = Config.AUTO_CROP["min_resolution"]
            if cropped.shape[1] < min_res[0] or cropped.shape[0] < min_res[1]:
                logger.warning(f"Hasil crop terlalu kecil ({cropped.shape[1]}x{cropped.shape[0]}), skip cropping")
                return image
            
            logger.info(f"✅ Auto crop {orientation}: {image.shape[1]}x{image.shape[0]} -> {width}x{height}")
            return cropped
            
        except Exception as e:
            logger.error(f"Error saat auto crop: {e}")
            return image
    
    def load_watermark(self, watermark_path: Optional[Path] = None) -> Optional[np.ndarray]:
        """
        Load watermark image dengan transparency
        
        Args:
            watermark_path: Path ke watermark (optional)
            
        Returns:
            Watermark image dengan alpha channel atau None
        """
        if watermark_path is None:
            watermark_path = Config.WATERMARKS_DIR / Config.WATERMARK["file"]
        
        # Check cache
        cache_key = str(watermark_path)
        if cache_key in self.watermark_cache:
            return self.watermark_cache[cache_key]
        
        try:
            if not watermark_path.exists():
                logger.warning(f"File watermark tidak ditemukan: {watermark_path}")
                return None
            
            # Load dengan PIL untuk preserve alpha channel
            watermark_pil = Image.open(watermark_path).convert("RGBA")
            watermark_array = np.array(watermark_pil)
            
            # Cache watermark
            self.watermark_cache[cache_key] = watermark_array
            
            logger.info(f"✅ Watermark berhasil dimuat: {watermark_path}")
            return watermark_array
            
        except Exception as e:
            logger.error(f"Gagal memuat watermark {watermark_path}: {e}")
            return None
    
    def apply_watermark(self, image: np.ndarray, watermark_path: Optional[Path] = None) -> np.ndarray:
        """
        Aplikasikan watermark ke gambar
        
        Args:
            image: Input image (BGR format)
            watermark_path: Path ke watermark (optional)
            
        Returns:
            Image dengan watermark
        """
        try:
            # Load watermark
            watermark = self.load_watermark(watermark_path)
            if watermark is None:
                logger.warning("Watermark tidak tersedia, skip watermark")
                return image
            
            # Convert image ke RGBA untuk blending
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_rgba = np.dstack([image_rgb, np.ones((image_rgb.shape[0], image_rgb.shape[1]), dtype=np.uint8) * 255])
            
            # Hitung ukuran watermark
            img_height, img_width = image.shape[:2]
            size_ratio = Config.WATERMARK["size_ratio"]
            watermark_width = int(img_width * size_ratio)
            
            # Resize watermark sambil maintain aspect ratio
            wm_height, wm_width = watermark.shape[:2]
            aspect_ratio = wm_height / wm_width
            watermark_height = int(watermark_width * aspect_ratio)
            
            watermark_resized = cv2.resize(watermark, (watermark_width, watermark_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Hitung posisi watermark
            position = Config.WATERMARK["position"]
            
            if position["horizontal"] == "center":
                x = (img_width - watermark_width) // 2
            elif position["horizontal"] == "left":
                x = 50  # Padding dari kiri
            else:  # right
                x = img_width - watermark_width - 50  # Padding dari kanan
            
            y = int(img_height * position["vertical"]) - watermark_height // 2
            
            # Pastikan watermark tidak keluar dari frame
            x = max(0, min(x, img_width - watermark_width))
            y = max(0, min(y, img_height - watermark_height))
            
            # Apply watermark dengan alpha blending
            overlay = image_rgba.copy()
            
            # Extract alpha channel dari watermark
            watermark_rgb = watermark_resized[:, :, :3]
            watermark_alpha = watermark_resized[:, :, 3] / 255.0
            
            # Apply opacity setting
            opacity = Config.WATERMARK["opacity"]
            watermark_alpha = watermark_alpha * opacity
            
            # Alpha blending
            for c in range(3):  # RGB channels
                overlay[y:y+watermark_height, x:x+watermark_width, c] = (
                    overlay[y:y+watermark_height, x:x+watermark_width, c] * (1 - watermark_alpha) +
                    watermark_rgb[:, :, c] * watermark_alpha
                )
            
            # Convert kembali ke BGR
            result_rgb = overlay[:, :, :3]
            result_bgr = cv2.cvtColor(result_rgb.astype(np.uint8), cv2.COLOR_RGB2BGR)
            
            logger.info(f"✅ Watermark applied di posisi ({x}, {y}) dengan ukuran {watermark_width}x{watermark_height}")
            return result_bgr
            
        except Exception as e:
            logger.error(f"Error saat aplikasi watermark: {e}")
            return image
    
    def process_full_pipeline(self, image: np.ndarray, output_path: Optional[Path] = None) -> Tuple[bool, Optional[Path]]:
        """
        Jalankan full pipeline: LUT -> Auto Crop -> Watermark
        
        Args:
            image: Input image
            output_path: Output path (optional)
            
        Returns:
            Tuple (success, output_path)
        """
        try:
            logger.info("Memulai full processing pipeline...")
            
            # Step 1: Apply LUT
            processed = self.apply_lut(image, intensity=Config.LUT_SETTINGS["intensity"])
            
            # Step 2: Auto Crop
            processed = self.auto_crop(processed)
            
            # Step 3: Apply Watermark
            processed = self.apply_watermark(processed)
            
            # Save hasil
            if output_path is None:
                output_path = Config.PROCESSED_DIR / f"final_{int(time.time())}.jpg"
            
            success = cv2.imwrite(str(output_path), processed, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            if success:
                logger.info(f"✅ Full pipeline selesai: {output_path}")
                return True, output_path
            else:
                logger.error(f"Gagal menyimpan hasil: {output_path}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error dalam full pipeline: {e}")
            return False, None

def test_processing():
    """Test function untuk image processing"""
    try:
        processor = ImageProcessor()
        
        # Test dengan sample image
        test_image_path = Config.TEMP_DIR / "sample.jpg"
        if not test_image_path.exists():
            print("Untuk test, letakkan gambar sample di temp/sample.jpg")
            return
        
        image = cv2.imread(str(test_image_path))
        if image is None:
            print(f"Gagal membaca gambar: {test_image_path}")
            return
        
        print("Testing image processing pipeline...")
        
        # Test individual components
        print("1. Testing LUT application...")
        lut_result = processor.apply_lut(image)
        cv2.imwrite(str(Config.TEMP_DIR / "test_lut.jpg"), lut_result)
        
        print("2. Testing auto crop...")
        crop_result = processor.auto_crop(image)
        cv2.imwrite(str(Config.TEMP_DIR / "test_crop.jpg"), crop_result)
        
        print("3. Testing watermark...")
        watermark_result = processor.apply_watermark(image)
        cv2.imwrite(str(Config.TEMP_DIR / "test_watermark.jpg"), watermark_result)
        
        print("4. Testing full pipeline...")
        success, output_path = processor.process_full_pipeline(image, Config.TEMP_DIR / "test_full_pipeline.jpg")
        
        if success:
            print(f"✅ Full pipeline test berhasil: {output_path}")
        else:
            print("❌ Full pipeline test gagal")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_processing()