# Face Detection dan Masking untuk Proteksi Wajah
# ==============================================

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import List, Tuple, Optional
from config import Config

logger = logging.getLogger(__name__)

class FaceProtectionMask:
    """Class untuk deteksi wajah dan pembuatan mask proteksi"""
    
    def __init__(self):
        """Inisialisasi face detector"""
        self.cascade_path = self._get_cascade_path()
        self.face_cascade = cv2.CascadeClassifier(str(self.cascade_path))
        
        if self.face_cascade.empty():
            raise ValueError(f"Gagal memuat Haar Cascade dari {self.cascade_path}")
        
        logger.info(f"Face detector berhasil diinisialisasi: {self.cascade_path}")
    
    def _get_cascade_path(self) -> Path:
        """Dapatkan path ke file Haar Cascade"""
        # Cek di models directory dulu
        local_cascade = Config.MODELS_DIR / Config.FACE_DETECTION["cascade_file"]
        if local_cascade.exists():
            return local_cascade
        
        # Fallback ke OpenCV default
        import cv2
        opencv_data = cv2.data.haarcascades
        default_cascade = Path(opencv_data) / "haarcascade_frontalface_default.xml"
        
        if default_cascade.exists():
            logger.info("Menggunakan default OpenCV Haar Cascade")
            return default_cascade
        
        # Last resort - download atau error
        raise FileNotFoundError(
            f"Haar Cascade tidak ditemukan. "
            f"Silakan download {Config.FACE_DETECTION['cascade_file']} "
            f"ke {Config.MODELS_DIR}"
        )
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Deteksi wajah dalam gambar
        
        Args:
            image: Input gambar dalam format BGR (OpenCV)
            
        Returns:
            List koordinat wajah [(x, y, w, h), ...]
        """
        try:
            # Konversi ke grayscale untuk deteksi
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Equalizing histogram untuk deteksi yang lebih baik
            gray = cv2.equalizeHist(gray)
            
            # Deteksi wajah
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=Config.FACE_DETECTION["scale_factor"],
                minNeighbors=Config.FACE_DETECTION["min_neighbors"],
                minSize=Config.FACE_DETECTION["min_size"]
            )
            
            logger.info(f"Terdeteksi {len(faces)} wajah dalam gambar")
            return faces.tolist() if len(faces) > 0 else []
            
        except Exception as e:
            logger.error(f"Error saat deteksi wajah: {e}")
            return []
    
    def create_face_mask(self, image: np.ndarray, faces: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Buat mask untuk area wajah
        
        Args:
            image: Input gambar
            faces: List koordinat wajah [(x, y, w, h), ...]
            
        Returns:
            Binary mask (255 = area wajah, 0 = area lain)
        """
        height, width = image.shape[:2]
        mask = np.zeros((height, width), dtype=np.uint8)
        
        padding = Config.FACE_DETECTION["padding"]
        
        for (x, y, w, h) in faces:
            # Tambahkan padding untuk coverage yang lebih baik
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(width, x + w + padding)
            y2 = min(height, y + h + padding)
            
            # Buat mask berbentuk ellipse untuk hasil yang lebih natural
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            radius_x = (x2 - x1) // 2
            radius_y = (y2 - y1) // 2
            
            cv2.ellipse(mask, (center_x, center_y), (radius_x, radius_y), 0, 0, 360, 255, -1)
            
            logger.debug(f"Mask dibuat untuk wajah: ({x1}, {y1}) -> ({x2}, {y2})")
        
        return mask
    
    def apply_face_protection(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
        """
        Terapkan proteksi wajah pada gambar
        
        Args:
            image: Input gambar dalam format BGR
            
        Returns:
            Tuple: (masked_image, face_mask, has_faces)
            - masked_image: Gambar dengan area wajah di-blur/modify
            - face_mask: Binary mask area wajah
            - has_faces: Boolean apakah ada wajah terdeteksi
        """
        try:
            # Deteksi wajah
            faces = self.detect_faces(image)
            has_faces = len(faces) > 0
            
            if not has_faces:
                logger.info("Tidak ada wajah terdeteksi - akan proses normal tanpa proteksi")
                empty_mask = np.zeros(image.shape[:2], dtype=np.uint8)
                return image.copy(), empty_mask, False
            
            # Buat mask untuk area wajah
            face_mask = self.create_face_mask(image, faces)
            
            # Buat gambar dengan area wajah yang dimodifikasi untuk AI processing
            masked_image = image.copy()
            
            # Opsi 1: Blur area wajah sedikit untuk mengurangi detail yang akan di-enhance AI
            face_area = cv2.bitwise_and(image, image, mask=face_mask)
            blurred_face = cv2.GaussianBlur(face_area, (15, 15), 0)
            
            # Combine area wajah yang di-blur dengan area lain
            inverse_mask = cv2.bitwise_not(face_mask)
            non_face_area = cv2.bitwise_and(image, image, mask=inverse_mask)
            masked_image = cv2.add(non_face_area, blurred_face)
            
            logger.info(f"Proteksi wajah diterapkan untuk {len(faces)} wajah")
            
            return masked_image, face_mask, True
            
        except Exception as e:
            logger.error(f"Error saat menerapkan proteksi wajah: {e}")
            empty_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            return image.copy(), empty_mask, False
    
    def restore_face_areas(self, enhanced_image: np.ndarray, original_image: np.ndarray, 
                          face_mask: np.ndarray) -> np.ndarray:
        """
        Restore area wajah dari gambar asli ke gambar yang sudah di-enhance
        
        Args:
            enhanced_image: Gambar hasil enhancement AI
            original_image: Gambar asli
            face_mask: Mask area wajah
            
        Returns:
            Gambar final dengan area wajah di-restore dari original
        """
        try:
            if face_mask.sum() == 0:  # Tidak ada area wajah
                return enhanced_image
            
            # Smooth transition dengan gaussian blur pada mask
            blurred_mask = cv2.GaussianBlur(face_mask, (21, 21), 0)
            blurred_mask = blurred_mask.astype(np.float32) / 255.0
            
            # Resize mask ke 3 channel untuk operasi
            mask_3d = np.stack([blurred_mask] * 3, axis=2)
            
            # Blend area wajah dari original dengan enhanced background
            result = enhanced_image.astype(np.float32)
            original_float = original_image.astype(np.float32)
            
            # Area wajah dari original, area lain dari enhanced
            result = result * (1 - mask_3d) + original_float * mask_3d
            
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            logger.info("Area wajah berhasil di-restore dari gambar asli")
            return result
            
        except Exception as e:
            logger.error(f"Error saat restore area wajah: {e}")
            return enhanced_image
    
    def visualize_detection(self, image: np.ndarray, output_path: Optional[Path] = None) -> np.ndarray:
        """
        Visualisasi hasil deteksi wajah untuk debugging
        
        Args:
            image: Input gambar
            output_path: Path untuk save hasil (optional)
            
        Returns:
            Gambar dengan kotak deteksi wajah
        """
        faces = self.detect_faces(image)
        result = image.copy()
        
        for (x, y, w, h) in faces:
            # Gambar kotak hijau di sekitar wajah
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(result, 'Face', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        if output_path:
            cv2.imwrite(str(output_path), result)
            logger.info(f"Hasil deteksi disimpan ke: {output_path}")
        
        return result

# Utility functions
def test_face_detection(image_path: str):
    """Test function untuk deteksi wajah"""
    try:
        detector = FaceProtectionMask()
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Gagal membaca gambar: {image_path}")
            return
        
        print(f"Testing face detection pada: {image_path}")
        
        # Test deteksi
        faces = detector.detect_faces(image)
        print(f"Terdeteksi {len(faces)} wajah")
        
        # Test masking
        masked_img, face_mask, has_faces = detector.apply_face_protection(image)
        print(f"Has faces: {has_faces}")
        
        # Save hasil untuk review
        output_dir = Config.TEMP_DIR / "test_detection"
        output_dir.mkdir(exist_ok=True)
        
        cv2.imwrite(str(output_dir / "original.jpg"), image)
        cv2.imwrite(str(output_dir / "masked.jpg"), masked_img)
        cv2.imwrite(str(output_dir / "face_mask.jpg"), face_mask)
        
        # Visualisasi
        viz = detector.visualize_detection(image, output_dir / "detection_viz.jpg")
        
        print(f"Hasil test disimpan di: {output_dir}")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    # Test dengan gambar sample jika ada
    test_image = Config.TEMP_DIR / "sample.jpg"
    if test_image.exists():
        test_face_detection(str(test_image))
    else:
        print("Untuk test, letakkan gambar sample di temp/sample.jpg")