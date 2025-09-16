#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interactive Setup untuk Sistem Tethered Shooting
===============================================

Interface interaktif untuk memilih semua konfigurasi sebelum mulai shooting.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from pathlib import Path
from typing import Dict, Any, Optional

# Import modules
from config import Config
from event_selector import EventSelector

class InteractiveSetup:
    """Interactive setup untuk konfigurasi lengkap sistem"""
    
    def __init__(self):
        self.selected_config = {
            "event_id": None,
            "ai_mode": "auto",
            "ai_enabled": True,
            "ai_fallback": True,
            "ai_skip_on_failure": False,
            "face_protection": True,
            "lut_file": "my_preset.cube",
            "lut_intensity": 1.0,
            "watermark_file": "my_logo.png",
            "watermark_enabled": True,
            "watermark_opacity": 0.8,
            "crop_mode": "auto",
            "upload_quality": "high",
            "performance_mode": "balanced"
        }
        
        print("🎛️  INTERACTIVE SETUP - SISTEM TETHERED SHOOTING")
        print("=" * 60)
        print("Konfigurasikan sistem sesuai kebutuhan event Anda")
        print("=" * 60)
    
    def run_interactive_setup(self) -> Dict[str, Any]:
        """Jalankan full interactive setup"""
        try:
            print("\n🚀 Memulai interactive setup...")
            print("Tekan Ctrl+C kapan saja untuk keluar")
            
            # Step 1: Event Selection
            if not self._select_event():
                return None
            
            # Step 2: AI Enhancement Setup
            if not self._setup_ai_enhancement():
                return None
            
            # Step 3: Image Processing Setup
            if not self._setup_image_processing():
                return None
            
            # Step 4: Performance & Upload Setup
            if not self._setup_performance_upload():
                return None
            
            # Step 5: Final Review & Confirmation
            if not self._final_confirmation():
                return None
            
            return self.selected_config
            
        except KeyboardInterrupt:
            print("\n👋 Setup dibatalkan oleh user")
            return None
        except Exception as e:
            print(f"\n❌ Error dalam interactive setup: {e}")
            return None
    
    def _select_event(self) -> bool:
        """Step 1: Event Selection"""
        try:
            print(f"\n{'='*60}")
            print("📅 STEP 1: PILIH EVENT")
            print(f"{'='*60}")
            
            event_selector = EventSelector()
            selected_event_id = event_selector.select_event_interactive()
            
            if not selected_event_id:
                print("❌ Event selection dibatalkan")
                return False
            
            self.selected_config["event_id"] = selected_event_id
            print(f"✅ Event terpilih: {selected_event_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error dalam event selection: {e}")
            return False
    
    def _setup_ai_enhancement(self) -> bool:
        """Step 2: AI Enhancement Setup"""
        try:
            print(f"\n{'='*60}")
            print("🤖 STEP 2: AI ENHANCEMENT SETUP")
            print(f"{'='*60}")
            
            print("Pilih mode AI enhancement untuk foto:")
            print("1. 🔄 Auto (Gemini AI + OpenCV fallback) - Recommended")
            print("2. 🤖 Gemini Only (AI saja, kualitas terbaik)")
            print("3. 🎨 OpenCV Only (Traditional, cepat & reliable)")
            print("4. 🚫 Disabled (Tidak ada enhancement, tercepat)")
            
            while True:
                choice = input("\n❓ Pilihan Anda (1-4): ").strip()
                
                if choice == "1":
                    self.selected_config["ai_mode"] = "auto"
                    self.selected_config["ai_enabled"] = True
                    self.selected_config["ai_fallback"] = True
                    print("✅ Mode: Auto (Gemini + OpenCV fallback)")
                    break
                elif choice == "2":
                    self.selected_config["ai_mode"] = "gemini"
                    self.selected_config["ai_enabled"] = True
                    self.selected_config["ai_fallback"] = False
                    print("✅ Mode: Gemini AI Only")
                    break
                elif choice == "3":
                    self.selected_config["ai_mode"] = "opencv"
                    self.selected_config["ai_enabled"] = True
                    self.selected_config["ai_fallback"] = False
                    print("✅ Mode: OpenCV Traditional Only")
                    break
                elif choice == "4":
                    self.selected_config["ai_mode"] = "disabled"
                    self.selected_config["ai_enabled"] = False
                    self.selected_config["face_protection"] = False
                    print("✅ Mode: Enhancement Disabled")
                    break
                else:
                    print("⚠️ Pilihan tidak valid, masukkan 1-4")
            
            # Advanced AI options (jika AI enabled)
            if self.selected_config["ai_enabled"]:
                print(f"\n🔧 Advanced AI Options:")
                
                # Face protection
                if self.selected_config["ai_mode"] != "disabled":
                    face_protection = input("🛡️ Enable face protection? (Y/n): ").strip().lower()
                    self.selected_config["face_protection"] = face_protection not in ['n', 'no', 'tidak']
                
                # Skip on failure
                if self.selected_config["ai_mode"] in ["gemini", "auto"]:
                    skip_failure = input("⏭️ Skip jika AI gagal? (y/N): ").strip().lower()
                    self.selected_config["ai_skip_on_failure"] = skip_failure in ['y', 'yes', 'ya']
                
                print(f"   Face Protection: {self.selected_config['face_protection']}")
                print(f"   Skip on Failure: {self.selected_config['ai_skip_on_failure']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error dalam AI setup: {e}")
            return False
    
    def _setup_image_processing(self) -> bool:
        """Step 3: Image Processing Setup"""
        try:
            print(f"\n{'='*60}")
            print("🎨 STEP 3: IMAGE PROCESSING SETUP")
            print(f"{'='*60}")
            
            # LUT Selection
            print("\n📁 LUT (Color Grading) Setup:")
            available_luts = list(Config.PRESETS_DIR.glob("*.cube"))
            
            if available_luts:
                print("Available LUT files:")
                for i, lut_file in enumerate(available_luts, 1):
                    print(f"  {i}. {lut_file.name}")
                print(f"  {len(available_luts) + 1}. Skip LUT (no color grading)")
                
                while True:
                    choice = input(f"\n❓ Pilih LUT (1-{len(available_luts) + 1}): ").strip()
                    try:
                        choice_int = int(choice)
                        if 1 <= choice_int <= len(available_luts):
                            self.selected_config["lut_file"] = available_luts[choice_int - 1].name
                            print(f"✅ LUT: {self.selected_config['lut_file']}")
                            
                            # LUT intensity
                            intensity = input("🎯 LUT intensity (0.0-1.0, default 1.0): ").strip()
                            try:
                                self.selected_config["lut_intensity"] = float(intensity) if intensity else 1.0
                                print(f"   Intensity: {self.selected_config['lut_intensity']}")
                            except:
                                self.selected_config["lut_intensity"] = 1.0
                                print("   Intensity: 1.0 (default)")
                            break
                        elif choice_int == len(available_luts) + 1:
                            self.selected_config["lut_file"] = None
                            print("✅ LUT: Disabled")
                            break
                        else:
                            print("⚠️ Pilihan tidak valid")
                    except ValueError:
                        print("⚠️ Masukkan angka yang valid")
            else:
                print("⚠️ Tidak ada LUT file ditemukan, LUT disabled")
                self.selected_config["lut_file"] = None
            
            # Watermark Selection
            print("\n💧 Watermark Setup:")
            available_watermarks = list(Config.WATERMARKS_DIR.glob("*.png"))
            
            if available_watermarks:
                print("Available watermark files:")
                for i, wm_file in enumerate(available_watermarks, 1):
                    print(f"  {i}. {wm_file.name}")
                print(f"  {len(available_watermarks) + 1}. No watermark")
                
                while True:
                    choice = input(f"\n❓ Pilih watermark (1-{len(available_watermarks) + 1}): ").strip()
                    try:
                        choice_int = int(choice)
                        if 1 <= choice_int <= len(available_watermarks):
                            self.selected_config["watermark_file"] = available_watermarks[choice_int - 1].name
                            self.selected_config["watermark_enabled"] = True
                            print(f"✅ Watermark: {self.selected_config['watermark_file']}")
                            
                            # Watermark opacity
                            opacity = input("👻 Watermark opacity (0.0-1.0, default 0.8): ").strip()
                            try:
                                self.selected_config["watermark_opacity"] = float(opacity) if opacity else 0.8
                                print(f"   Opacity: {self.selected_config['watermark_opacity']}")
                            except:
                                self.selected_config["watermark_opacity"] = 0.8
                                print("   Opacity: 0.8 (default)")
                            break
                        elif choice_int == len(available_watermarks) + 1:
                            self.selected_config["watermark_enabled"] = False
                            print("✅ Watermark: Disabled")
                            break
                        else:
                            print("⚠️ Pilihan tidak valid")
                    except ValueError:
                        print("⚠️ Masukkan angka yang valid")
            else:
                print("⚠️ Tidak ada watermark file ditemukan, watermark disabled")
                self.selected_config["watermark_enabled"] = False
            
            # Auto Crop Setup
            print("\n✂️ Auto Crop Setup:")
            print("1. 🔄 Auto (5x7 portrait, 7x5 landscape)")
            print("2. 📱 Force Portrait (5x7)")
            print("3. 🖥️ Force Landscape (7x5)")
            print("4. 🚫 No cropping")
            
            while True:
                choice = input("\n❓ Pilihan crop (1-4): ").strip()
                if choice == "1":
                    self.selected_config["crop_mode"] = "auto"
                    print("✅ Crop: Auto (berdasarkan orientasi)")
                    break
                elif choice == "2":
                    self.selected_config["crop_mode"] = "portrait"
                    print("✅ Crop: Force Portrait (5x7)")
                    break
                elif choice == "3":
                    self.selected_config["crop_mode"] = "landscape"
                    print("✅ Crop: Force Landscape (7x5)")
                    break
                elif choice == "4":
                    self.selected_config["crop_mode"] = "disabled"
                    print("✅ Crop: Disabled")
                    break
                else:
                    print("⚠️ Pilihan tidak valid, masukkan 1-4")
            
            return True
            
        except Exception as e:
            print(f"❌ Error dalam image processing setup: {e}")
            return False
    
    def _setup_performance_upload(self) -> bool:
        """Step 4: Performance & Upload Setup"""
        try:
            print(f"\n{'='*60}")
            print("⚡ STEP 4: PERFORMANCE & UPLOAD SETUP")
            print(f"{'='*60}")
            
            # Performance Mode
            print("\n🚀 Performance Mode (untuk Intel i5-3570, 8GB RAM):")
            print("1. 🏃 Speed (prioritas kecepatan, minimal processing)")
            print("2. ⚖️ Balanced (balance speed vs quality)")
            print("3. 🎯 Quality (prioritas kualitas, processing maksimal)")
            
            while True:
                choice = input("\n❓ Pilih performance mode (1-3): ").strip()
                if choice == "1":
                    self.selected_config["performance_mode"] = "speed"
                    print("✅ Performance: Speed Mode")
                    # Adjust settings for speed
                    self._apply_speed_optimizations()
                    break
                elif choice == "2":
                    self.selected_config["performance_mode"] = "balanced"
                    print("✅ Performance: Balanced Mode")
                    break
                elif choice == "3":
                    self.selected_config["performance_mode"] = "quality"
                    print("✅ Performance: Quality Mode")
                    # Adjust settings for quality
                    self._apply_quality_optimizations()
                    break
                else:
                    print("⚠️ Pilihan tidak valid, masukkan 1-3")
            
            # Upload Quality
            print("\n📤 Upload Quality ke Web Project:")
            print("1. 🔥 High (95% quality, file besar)")
            print("2. ⚖️ Medium (80% quality, balanced)")
            print("3. ⚡ Low (70% quality, file kecil, cepat upload)")
            
            while True:
                choice = input("\n❓ Pilih upload quality (1-3): ").strip()
                if choice == "1":
                    self.selected_config["upload_quality"] = "high"
                    print("✅ Upload Quality: High (95%)")
                    break
                elif choice == "2":
                    self.selected_config["upload_quality"] = "medium"
                    print("✅ Upload Quality: Medium (80%)")
                    break
                elif choice == "3":
                    self.selected_config["upload_quality"] = "low"
                    print("✅ Upload Quality: Low (70%)")
                    break
                else:
                    print("⚠️ Pilihan tidak valid, masukkan 1-3")
            
            return True
            
        except Exception as e:
            print(f"❌ Error dalam performance & upload setup: {e}")
            return False
    
    def _apply_speed_optimizations(self):
        """Apply optimizations for speed mode"""
        if self.selected_config["ai_mode"] == "auto":
            self.selected_config["ai_mode"] = "opencv"
            print("   🎨 AI mode changed to OpenCV for speed")
        
        self.selected_config["ai_skip_on_failure"] = True
        print("   ⏭️ Skip on failure enabled for speed")
    
    def _apply_quality_optimizations(self):
        """Apply optimizations for quality mode"""
        if self.selected_config["ai_mode"] == "opencv":
            self.selected_config["ai_mode"] = "auto"
            print("   🤖 AI mode changed to Auto for quality")
        
        self.selected_config["ai_fallback"] = True
        print("   🔄 AI fallback enabled for quality")
    
    def _final_confirmation(self) -> bool:
        """Step 5: Final Review & Confirmation"""
        try:
            print(f"\n{'='*60}")
            print("📋 STEP 5: FINAL CONFIGURATION REVIEW")
            print(f"{'='*60}")
            
            print("\n🎯 KONFIGURASI YANG DIPILIH:")
            print("-" * 40)
            
            # Event Info
            print(f"📅 Event ID: {self.selected_config['event_id']}")
            
            # AI Enhancement
            ai_mode_display = {
                "auto": "🔄 Auto (Gemini + OpenCV fallback)",
                "gemini": "🤖 Gemini AI Only",
                "opencv": "🎨 OpenCV Traditional Only",
                "disabled": "🚫 Disabled"
            }
            print(f"🤖 AI Enhancement: {ai_mode_display[self.selected_config['ai_mode']]}")
            
            if self.selected_config["ai_enabled"]:
                print(f"   🛡️ Face Protection: {'Enabled' if self.selected_config['face_protection'] else 'Disabled'}")
                if self.selected_config["ai_fallback"]:
                    print(f"   🔄 OpenCV Fallback: Enabled")
                if self.selected_config["ai_skip_on_failure"]:
                    print(f"   ⏭️ Skip on Failure: Enabled")
            
            # Image Processing
            if self.selected_config["lut_file"]:
                print(f"🎨 LUT: {self.selected_config['lut_file']} (intensity: {self.selected_config['lut_intensity']})")
            else:
                print(f"🎨 LUT: Disabled")
            
            crop_display = {
                "auto": "🔄 Auto (berdasarkan orientasi)",
                "portrait": "📱 Force Portrait (5x7)",
                "landscape": "🖥️ Force Landscape (7x5)",
                "disabled": "🚫 Disabled"
            }
            print(f"✂️ Auto Crop: {crop_display[self.selected_config['crop_mode']]}")
            
            if self.selected_config["watermark_enabled"]:
                print(f"💧 Watermark: {self.selected_config['watermark_file']} (opacity: {self.selected_config['watermark_opacity']})")
            else:
                print(f"💧 Watermark: Disabled")
            
            # Performance & Upload
            performance_display = {
                "speed": "🏃 Speed (prioritas kecepatan)",
                "balanced": "⚖️ Balanced",
                "quality": "🎯 Quality (prioritas kualitas)"
            }
            print(f"⚡ Performance: {performance_display[self.selected_config['performance_mode']]}")
            
            quality_display = {
                "high": "🔥 High (95%)",
                "medium": "⚖️ Medium (80%)",
                "low": "⚡ Low (70%)"
            }
            print(f"📤 Upload Quality: {quality_display[self.selected_config['upload_quality']]}")
            
            # Workflow Preview
            print(f"\n🔄 WORKFLOW YANG AKAN DIJALANKAN:")
            print("-" * 40)
            workflow_steps = []
            workflow_steps.append("📸 Camera Capture")
            workflow_steps.append("💾 Backup (RAW + JPG)")
            
            if self.selected_config["face_protection"]:
                workflow_steps.append("👤 Face Detection")
            
            if self.selected_config["ai_enabled"]:
                workflow_steps.append(f"🤖 AI Enhancement ({self.selected_config['ai_mode']})")
            
            if self.selected_config["lut_file"]:
                workflow_steps.append("🎨 LUT Color Grading")
            
            if self.selected_config["crop_mode"] != "disabled":
                workflow_steps.append("✂️ Auto Crop")
            
            if self.selected_config["watermark_enabled"]:
                workflow_steps.append("💧 Watermark")
            
            workflow_steps.append("🌐 Upload ke Web (Tab Official)")
            
            for i, step in enumerate(workflow_steps, 1):
                print(f"  {i}. {step}")
            
            # Estimated performance
            print(f"\n⏱️ ESTIMASI PERFORMANCE:")
            print("-" * 40)
            processing_time = self._estimate_processing_time()
            print(f"Processing per foto: ~{processing_time} detik")
            print(f"Throughput: ~{3600/processing_time:.0f} foto per jam")
            
            # Final confirmation
            print(f"\n{'='*60}")
            confirm = input("❓ Lanjutkan dengan konfigurasi ini? (Y/n): ").strip().lower()
            
            if confirm in ['', 'y', 'yes', 'ya']:
                print("✅ Konfigurasi dikonfirmasi!")
                return True
            else:
                print("❌ Setup dibatalkan")
                return False
            
        except Exception as e:
            print(f"❌ Error dalam final confirmation: {e}")
            return False
    
    def _estimate_processing_time(self) -> int:
        """Estimate processing time berdasarkan konfigurasi"""
        base_time = 2  # Base processing time
        
        # AI Enhancement time
        if self.selected_config["ai_mode"] == "gemini":
            base_time += 15  # Gemini AI time
        elif self.selected_config["ai_mode"] == "auto":
            base_time += 10  # Average (sometimes Gemini, sometimes OpenCV)
        elif self.selected_config["ai_mode"] == "opencv":
            base_time += 3   # OpenCV processing time
        
        # Face detection overhead
        if self.selected_config["face_protection"]:
            base_time += 1
        
        # Image processing
        if self.selected_config["lut_file"]:
            base_time += 2
        if self.selected_config["crop_mode"] != "disabled":
            base_time += 1
        if self.selected_config["watermark_enabled"]:
            base_time += 1
        
        # Upload time (depends on quality)
        upload_times = {"high": 5, "medium": 3, "low": 2}
        base_time += upload_times[self.selected_config["upload_quality"]]
        
        # Performance mode adjustments
        if self.selected_config["performance_mode"] == "speed":
            base_time = int(base_time * 0.7)  # 30% faster
        elif self.selected_config["performance_mode"] == "quality":
            base_time = int(base_time * 1.3)  # 30% slower but better quality
        
        return max(base_time, 3)  # Minimum 3 seconds
    
    def apply_configuration(self):
        """Apply selected configuration to Config object"""
        try:
            # AI Enhancement settings
            Config.AI_ENHANCEMENT["enabled"] = self.selected_config["ai_enabled"]
            Config.AI_ENHANCEMENT["mode"] = self.selected_config["ai_mode"]
            Config.AI_ENHANCEMENT["fallback_to_opencv"] = self.selected_config["ai_fallback"]
            Config.AI_ENHANCEMENT["skip_on_failure"] = self.selected_config["ai_skip_on_failure"]
            
            # LUT settings
            if self.selected_config["lut_file"]:
                Config.LUT_SETTINGS["file"] = self.selected_config["lut_file"]
                Config.LUT_SETTINGS["intensity"] = self.selected_config["lut_intensity"]
            
            # Watermark settings
            if self.selected_config["watermark_enabled"]:
                Config.WATERMARK["file"] = self.selected_config["watermark_file"]
                Config.WATERMARK["opacity"] = self.selected_config["watermark_opacity"]
            
            # Upload quality
            Config.WEB_INTEGRATION["web_upload_quality"] = self.selected_config["upload_quality"]
            
            print("✅ Configuration applied to system")
            
        except Exception as e:
            print(f"❌ Error applying configuration: {e}")

def main():
    """Main function untuk interactive setup"""
    try:
        setup = InteractiveSetup()
        config = setup.run_interactive_setup()
        
        if config:
            print(f"\n🎉 Interactive setup completed successfully!")
            print(f"🚀 Configuration ready untuk tethered shooting")
            
            # Apply configuration
            setup.apply_configuration()
            
            return config
        else:
            print(f"\n❌ Interactive setup cancelled or failed")
            return None
            
    except KeyboardInterrupt:
        print("\n👋 Interactive setup cancelled by user")
        return None
    except Exception as e:
        print(f"\n❌ Fatal error in interactive setup: {e}")
        return None

if __name__ == "__main__":
    config = main()
    if config:
        print(f"\n✨ Ready to start tethered shooting with your configuration!")
    else:
        print(f"\n🔄 Run setup again when ready")