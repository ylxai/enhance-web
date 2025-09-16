#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Master Test Runner - Jalankan Semua Test
========================================

Script untuk menjalankan semua test sistem tethered shooting secara berurutan.
"""

import sys
import os
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MasterTestRunner:
    """Runner untuk semua test sistem"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.test_results = {}
        
        # Daftar test scripts dalam urutan yang logis
        self.test_scripts = [
            ("Database & Configuration", "test-database.py"),
            ("Event Selection", "test-event.py"),
            ("Face Detection", "test-face-detection.py"),
            ("AI Enhancement & Processing", "test-ai-enhancement.py"),
            ("Web Upload", "test-upload.py")
        ]
        
        print("🧪 MASTER TEST RUNNER")
        print("=" * 60)
        print("Menjalankan semua test sistem tethered shooting")
        print("=" * 60)
    
    def run_single_test(self, test_name: str, script_name: str) -> bool:
        """Jalankan single test script"""
        try:
            print(f"\n{'='*60}")
            print(f"🚀 RUNNING: {test_name}")
            print(f"📄 Script: {script_name}")
            print(f"{'='*60}")
            
            script_path = self.test_dir / script_name
            
            if not script_path.exists():
                print(f"❌ Test script tidak ditemukan: {script_path}")
                return False
            
            # Run test script
            start_time = time.time()
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=False,  # Show output in real time
                text=True,
                cwd=str(self.test_dir.parent)  # Run from parent directory
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            print(f"\n{'='*60}")
            if success:
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"{'='*60}")
            
            return success
            
        except Exception as e:
            print(f"❌ Error running {test_name}: {e}")
            return False
    
    def run_all_tests(self, stop_on_failure: bool = False) -> bool:
        """Jalankan semua test"""
        print(f"\n🎯 Starting comprehensive system testing...")
        print(f"📋 Total tests to run: {len(self.test_scripts)}")
        
        if stop_on_failure:
            print("⚠️  Mode: Stop on first failure")
        else:
            print("🔄 Mode: Run all tests regardless of failures")
        
        print()
        
        overall_start_time = time.time()
        passed = 0
        failed = 0
        
        for i, (test_name, script_name) in enumerate(self.test_scripts, 1):
            print(f"\n📍 TEST {i}/{len(self.test_scripts)}")
            
            success = self.run_single_test(test_name, script_name)
            self.test_results[test_name] = success
            
            if success:
                passed += 1
            else:
                failed += 1
                
                if stop_on_failure:
                    print(f"\n🛑 Stopping due to failure in: {test_name}")
                    break
            
            # Short pause between tests
            if i < len(self.test_scripts):
                print(f"\n⏳ Waiting 3 seconds before next test...")
                time.sleep(3)
        
        overall_duration = time.time() - overall_start_time
        
        # Final summary
        self.print_final_summary(passed, failed, overall_duration)
        
        return failed == 0
    
    def print_final_summary(self, passed: int, failed: int, duration: float):
        """Print final test summary"""
        total = passed + failed
        
        print(f"\n{'='*60}")
        print(f"🏁 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        # Individual test results
        for test_name, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:40} : {status}")
        
        print(f"\n{'='*60}")
        print(f"📊 OVERALL RESULTS")
        print(f"{'='*60}")
        print(f"✅ Tests Passed: {passed}")
        print(f"❌ Tests Failed: {failed}")
        print(f"📋 Total Tests: {total}")
        print(f"⏱️  Total Duration: {duration/60:.1f} minutes ({duration:.1f} seconds)")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n{'='*60}")
        
        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
            print("✅ Sistem tethered shooting siap untuk production!")
            print("\nNext steps:")
            print("1. Connect kamera DSLR")
            print("2. Jalankan: python3 auto_capture_ai_enhanced.py")
            print("3. Pilih event dan mulai shooting!")
        else:
            print("⚠️  SOME TESTS FAILED!")
            print("❌ Perbaiki issues sebelum menggunakan sistem.")
            print("\nRecommendations:")
            
            if not self.test_results.get("Database & Configuration", True):
                print("- Check file .env dan konfigurasi database")
            if not self.test_results.get("Event Selection", True):
                print("- Check koneksi API dan authentication")
            if not self.test_results.get("Face Detection", True):
                print("- Check OpenCV installation dan model files")
            if not self.test_results.get("AI Enhancement & Processing", True):
                print("- Check Google API key dan LUT/watermark files")
            if not self.test_results.get("Web Upload", True):
                print("- Check web project API dan network connection")
        
        print(f"{'='*60}")
    
    def run_specific_tests(self, test_names: list) -> bool:
        """Jalankan test spesifik saja"""
        print(f"\n🎯 Running specific tests: {', '.join(test_names)}")
        
        available_tests = {name: script for name, script in self.test_scripts}
        
        passed = 0
        failed = 0
        
        for test_name in test_names:
            if test_name in available_tests:
                success = self.run_single_test(test_name, available_tests[test_name])
                self.test_results[test_name] = success
                
                if success:
                    passed += 1
                else:
                    failed += 1
            else:
                print(f"❌ Test tidak ditemukan: {test_name}")
                print(f"Available tests: {list(available_tests.keys())}")
                failed += 1
        
        return failed == 0

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Master Test Runner untuk Sistem Tethered Shooting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Contoh penggunaan:
  python3 run-all-tests.py                           # Jalankan semua test
  python3 run-all-tests.py --stop-on-failure        # Stop pada test pertama yang gagal
  python3 run-all-tests.py --list                   # Tampilkan daftar test
  python3 run-all-tests.py --tests "Database" "Event"  # Jalankan test spesifik
        """
    )
    
    parser.add_argument(
        '--stop-on-failure',
        action='store_true',
        help='Stop pada test pertama yang gagal'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Tampilkan daftar test yang tersedia'
    )
    
    parser.add_argument(
        '--tests',
        nargs='+',
        help='Jalankan test spesifik (nama test)'
    )
    
    args = parser.parse_args()
    
    try:
        runner = MasterTestRunner()
        
        if args.list:
            print("\n📋 Available Tests:")
            for i, (name, script) in enumerate(runner.test_scripts, 1):
                print(f"  {i}. {name} ({script})")
            return
        
        if args.tests:
            success = runner.run_specific_tests(args.tests)
        else:
            success = runner.run_all_tests(stop_on_failure=args.stop_on_failure)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n🛑 Test suite cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error in test runner: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()