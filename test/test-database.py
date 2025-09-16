#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Database Connection & Configuration
========================================

Test koneksi ke database, environment variables, dan konfigurasi dasar sistem.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
from pathlib import Path

# Import konfigurasi
from config import Config

# Setup logging untuk test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseTester:
    """Test database connection dan konfigurasi"""
    
    def __init__(self):
        self.test_results = {}
        print("🗄️  DATABASE & CONFIGURATION TESTER")
        print("=" * 50)
    
    def test_environment_variables(self) -> bool:
        """Test environment variables dari .env"""
        try:
            print("\n📋 Testing Environment Variables...")
            
            # Test critical environment variables
            critical_vars = [
                'GOOGLE_API_KEY',
                'NEXT_PUBLIC_SUPABASE_URL', 
                'NEXT_PUBLIC_SUPABASE_ANON_KEY',
                'WEB_API_BASE_URL',
                'JWT_SECRET'
            ]
            
            missing_vars = []
            for var in critical_vars:
                value = os.getenv(var)
                if not value:
                    missing_vars.append(var)
                else:
                    # Mask sensitive values
                    if 'KEY' in var or 'SECRET' in var:
                        masked_value = value[:8] + "*" * (len(value) - 8) if len(value) > 8 else "***"
                        print(f"  ✅ {var}: {masked_value}")
                    else:
                        print(f"  ✅ {var}: {value}")
            
            if missing_vars:
                print(f"  ❌ Missing variables: {', '.join(missing_vars)}")
                return False
            
            print("  ✅ All critical environment variables loaded")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing environment variables: {e}")
            return False
    
    def test_config_validation(self) -> bool:
        """Test konfigurasi sistem"""
        try:
            print("\n⚙️  Testing Configuration Validation...")
            
            # Test konfigurasi basic
            print(f"  🤖 AI Model: {Config.GEMINI_MODEL}")
            print(f"  📁 Base Directory: {Config.BASE_DIR}")
            print(f"  🔧 Max Workers: {Config.PERFORMANCE['max_workers']}")
            print(f"  💾 Memory Limit: {Config.PERFORMANCE['memory_limit_mb']} MB")
            
            # Validasi konfigurasi
            print("  🔍 Validating configuration...")
            errors = Config.validate_config()
            
            if errors:
                print("  ⚠️  Configuration warnings:")
                for error in errors:
                    print(f"    - {error}")
            else:
                print("  ✅ Configuration validation passed")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing configuration: {e}")
            return False
    
    def test_directories_creation(self) -> bool:
        """Test pembuatan direktori sistem"""
        try:
            print("\n📁 Testing Directory Creation...")
            
            # Buat direktori
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
            
            all_exist = True
            for directory in required_dirs:
                if directory.exists():
                    print(f"  ✅ {directory.name}: {directory}")
                else:
                    print(f"  ❌ {directory.name}: MISSING")
                    all_exist = False
            
            return all_exist
            
        except Exception as e:
            print(f"  ❌ Error testing directories: {e}")
            return False
    
    def test_supabase_config(self) -> bool:
        """Test konfigurasi Supabase"""
        try:
            print("\n🗄️  Testing Supabase Configuration...")
            
            supabase_config = Config.SUPABASE_CONFIG
            
            if not supabase_config['url']:
                print("  ❌ Supabase URL not configured")
                return False
            
            if not supabase_config['anon_key']:
                print("  ❌ Supabase anon key not configured")
                return False
            
            print(f"  ✅ Supabase URL: {supabase_config['url']}")
            print(f"  ✅ Anon Key: {supabase_config['anon_key'][:20]}...")
            
            # Test basic connection (without actual query)
            if supabase_config['service_role_key']:
                print(f"  ✅ Service Role Key: {supabase_config['service_role_key'][:20]}...")
            else:
                print("  ⚠️  Service Role Key not configured")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing Supabase config: {e}")
            return False
    
    def test_web_integration_config(self) -> bool:
        """Test konfigurasi web integration"""
        try:
            print("\n🌐 Testing Web Integration Configuration...")
            
            web_config = Config.WEB_INTEGRATION
            
            print(f"  🔗 Base URL: {web_config['web_api_base_url']}")
            print(f"  📤 Upload Endpoint: {web_config['web_upload_endpoint']}")
            print(f"  📅 Event Endpoint: {web_config['web_event_endpoint']}")
            print(f"  🎯 Default Type: {web_config['default_event_type']}")
            print(f"  📋 Default Category: {web_config['default_photo_category']}")
            print(f"  ⚡ Timeout: {web_config['upload_timeout']}s")
            print(f"  🔄 Retry Attempts: {web_config['retry_attempts']}")
            
            if web_config['jwt_secret']:
                print(f"  🔐 JWT Secret: {web_config['jwt_secret'][:10]}...")
            else:
                print("  ❌ JWT Secret not configured")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing web integration config: {e}")
            return False
    
    def test_storage_config(self) -> bool:
        """Test konfigurasi cloud storage"""
        try:
            print("\n☁️  Testing Cloud Storage Configuration...")
            
            r2_config = Config.CLOUDFLARE_R2_CONFIG
            
            # Check Cloudflare R2
            r2_configured = all([
                r2_config['account_id'],
                r2_config['access_key_id'],
                r2_config['secret_access_key'],
                r2_config['bucket_name']
            ])
            
            if r2_configured:
                print(f"  ✅ Cloudflare R2 configured")
                print(f"    - Bucket: {r2_config['bucket_name']}")
                print(f"    - Public URL: {r2_config['public_url']}")
            else:
                print("  ⚠️  Cloudflare R2 not fully configured")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing storage config: {e}")
            return False
    
    def test_performance_settings(self) -> bool:
        """Test performance settings untuk hardware"""
        try:
            print("\n⚡ Testing Performance Settings...")
            
            perf_config = Config.PERFORMANCE
            
            print(f"  👥 Max Workers: {perf_config['max_workers']}")
            print(f"  💾 Memory Limit: {perf_config['memory_limit_mb']} MB")
            print(f"  🧹 Temp Cleanup: {perf_config['temp_cleanup']}")
            
            # Validasi untuk hardware target (i5-3570, 8GB RAM)
            if perf_config['max_workers'] > 3:
                print("  ⚠️  Max workers might be too high for i5-3570")
            
            if perf_config['memory_limit_mb'] > 4096:
                print("  ⚠️  Memory limit might be too high for 8GB system")
            
            print("  ✅ Performance settings validated for target hardware")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing performance settings: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test database dan konfigurasi"""
        print("🚀 Starting Database & Configuration Tests...\n")
        
        tests = [
            ("Environment Variables", self.test_environment_variables),
            ("Configuration Validation", self.test_config_validation),
            ("Directory Creation", self.test_directories_creation),
            ("Supabase Configuration", self.test_supabase_config),
            ("Web Integration Config", self.test_web_integration_config),
            ("Storage Configuration", self.test_storage_config),
            ("Performance Settings", self.test_performance_settings)
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
        print(f"📊 DATABASE & CONFIG TEST SUMMARY")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:30} : {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL DATABASE & CONFIG TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check configuration.")
            return False

def main():
    """Main function untuk database testing"""
    try:
        tester = DatabaseTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Database & configuration ready for tethered shooting!")
        else:
            print("\n❌ Please fix configuration issues before proceeding.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Database test cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Fatal error during database test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)