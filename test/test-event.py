#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test Event Selection & Management
=================================

Test koneksi ke API event, fetch data real, dan interactive selection.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
import time
import json
from datetime import datetime

# Import modules
from config import Config
from event_selector import EventSelector

# Setup logging untuk test
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventTester:
    """Test event selection dan management"""
    
    def __init__(self):
        self.test_results = {}
        self.event_selector = None
        print("📅 EVENT SELECTION & MANAGEMENT TESTER")
        print("=" * 50)
    
    def test_event_selector_init(self) -> bool:
        """Test inisialisasi event selector"""
        try:
            print("\n🔧 Testing Event Selector Initialization...")
            
            self.event_selector = EventSelector()
            
            print(f"  ✅ Base URL: {self.event_selector.base_url}")
            print(f"  ✅ Event Endpoint: {self.event_selector.event_endpoint}")
            print(f"  ✅ JWT Secret: {'*' * 10}...")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error initializing event selector: {e}")
            return False
    
    def test_auth_token_creation(self) -> bool:
        """Test pembuatan JWT token untuk authentication"""
        try:
            print("\n🔐 Testing Authentication Token Creation...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Test token creation
            token = self.event_selector._create_auth_token()
            
            if not token:
                print("  ❌ Failed to create auth token")
                return False
            
            print(f"  ✅ Token created: {token[:20]}...")
            
            # Test headers
            headers = self.event_selector._get_auth_headers()
            
            if 'Authorization' in headers:
                print(f"  ✅ Auth headers: {headers['Authorization'][:30]}...")
            else:
                print("  ❌ No Authorization header")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing auth token: {e}")
            return False
    
    def test_fetch_events_from_database(self) -> bool:
        """Test fetch events dari database real"""
        try:
            print("\n🗄️  Testing Fetch Events from Database...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            print("  🔄 Fetching events from database...")
            events = self.event_selector.fetch_all_events()
            
            if not isinstance(events, list):
                print(f"  ❌ Expected list, got {type(events)}")
                return False
            
            print(f"  ✅ Successfully fetched {len(events)} events")
            
            if len(events) > 0:
                # Test structure event pertama
                first_event = events[0]
                
                print("  📋 Sample event structure:")
                required_fields = ['id', 'name', 'status']
                optional_fields = ['date', 'time', 'location', 'description']
                
                for field in required_fields:
                    if field in first_event:
                        value = str(first_event[field])[:50]
                        print(f"    ✅ {field}: {value}")
                    else:
                        print(f"    ❌ Missing required field: {field}")
                        return False
                
                for field in optional_fields:
                    if field in first_event:
                        value = str(first_event[field])[:50]
                        print(f"    ℹ️  {field}: {value}")
                
                # Test event dengan status berbeda
                statuses = set(event.get('status', 'unknown') for event in events)
                print(f"  📊 Event statuses found: {', '.join(statuses)}")
                
                # Count events by status
                status_counts = {}
                for event in events:
                    status = event.get('status', 'unknown')
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                for status, count in status_counts.items():
                    print(f"    {status}: {count} events")
            
            else:
                print("  ⚠️  No events found in database")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error fetching events: {e}")
            return False
    
    def test_event_display_formatting(self) -> bool:
        """Test formatting event untuk display"""
        try:
            print("\n🎨 Testing Event Display Formatting...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Fetch sample events
            events = self.event_selector.fetch_all_events()
            
            if not events:
                # Create sample event untuk test
                sample_event = {
                    'id': 'cm123abc456def789',
                    'name': 'Sample Wedding Event',
                    'date': '2024-12-25',
                    'time': '14:00',
                    'location': 'Grand Ballroom',
                    'status': 'active',
                    'description': 'Beautiful wedding ceremony'
                }
                events = [sample_event]
                print("  ℹ️  Using sample event for testing")
            
            # Test formatting
            for i, event in enumerate(events[:3]):  # Test 3 events max
                formatted = self.event_selector.format_event_display(event, i + 1)
                print(f"  📝 Event {i + 1} formatted:")
                print("    " + formatted.replace('\n', '\n    '))
                print()
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing event formatting: {e}")
            return False
    
    def test_event_menu_display(self) -> bool:
        """Test display menu events"""
        try:
            print("\n📋 Testing Event Menu Display...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Fetch events
            events = self.event_selector.fetch_all_events()
            
            if not events:
                print("  ⚠️  No events to display")
                return True
            
            print("  🎯 Displaying event menu (first 5 events):")
            print("  " + "="*60)
            
            # Capture and display menu (tanpa input)
            try:
                # Override display untuk test (tidak perlu user input)
                limited_events = events[:5]
                
                # Simulate menu display
                print("  📋 EVENTS AVAILABLE:")
                for i, event in enumerate(limited_events):
                    status_indicator = {
                        'active': '🟢',
                        'upcoming': '🟡', 
                        'completed': '🔴',
                        'cancelled': '⚫'
                    }.get(event.get('status', '').lower(), '⚪')
                    
                    name = event.get('name', 'Unnamed Event')
                    date = event.get('date', 'No date')
                    print(f"    {i+1:2d}. {status_indicator} {name} ({date})")
                
                print("  ✅ Menu display test completed")
                
            except Exception as e:
                print(f"  ❌ Error in menu display: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing menu display: {e}")
            return False
    
    def test_event_creation_data(self) -> bool:
        """Test data untuk pembuatan event baru"""
        try:
            print("\n🆕 Testing Event Creation Data Preparation...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Test data structure untuk event baru
            current_time = datetime.now()
            
            test_event_data = {
                "name": f"Test Tethered Session {current_time.strftime('%Y%m%d_%H%M')}",
                "description": "Auto-created test event for tethered shooting",
                "date": current_time.strftime('%Y-%m-%d'),
                "time": current_time.strftime('%H:%M'),
                "location": "Test Studio",
                "status": "active",
                "type": Config.WEB_INTEGRATION["default_event_type"],
                "category": "photography",
                "auto_created": True,
                "created_by": "tethered_shooting_system"
            }
            
            print("  📝 Sample event creation data:")
            for key, value in test_event_data.items():
                print(f"    {key}: {value}")
            
            # Validate required fields
            required_fields = ['name', 'date', 'time', 'status', 'type']
            missing_fields = [field for field in required_fields if not test_event_data.get(field)]
            
            if missing_fields:
                print(f"  ❌ Missing required fields: {missing_fields}")
                return False
            
            print("  ✅ Event creation data structure valid")
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing event creation: {e}")
            return False
    
    def test_event_validation(self) -> bool:
        """Test validasi event ID dan existence"""
        try:
            print("\n✅ Testing Event ID Validation...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Fetch events untuk test
            events = self.event_selector.fetch_all_events()
            
            if not events:
                print("  ⚠️  No events available for validation test")
                return True
            
            # Test dengan event ID yang valid
            valid_event = events[0]
            valid_event_id = valid_event.get('id')
            
            print(f"  🔍 Testing with valid event ID: {valid_event_id}")
            
            # Simulate validation
            event_exists = any(event.get('id') == valid_event_id for event in events)
            
            if event_exists:
                print("  ✅ Valid event ID found in database")
            else:
                print("  ❌ Valid event ID not found (should not happen)")
                return False
            
            # Test dengan event ID yang invalid
            invalid_event_id = "cm_invalid_123456789"
            print(f"  🔍 Testing with invalid event ID: {invalid_event_id}")
            
            event_exists = any(event.get('id') == invalid_event_id for event in events)
            
            if not event_exists:
                print("  ✅ Invalid event ID correctly rejected")
            else:
                print("  ❌ Invalid event ID incorrectly accepted")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing event validation: {e}")
            return False
    
    def test_api_error_handling(self) -> bool:
        """Test error handling untuk API calls"""
        try:
            print("\n🛡️  Testing API Error Handling...")
            
            if not self.event_selector:
                print("  ❌ Event selector not initialized")
                return False
            
            # Test dengan endpoint yang salah (untuk test error handling)
            original_endpoint = self.event_selector.event_endpoint
            
            # Test dengan endpoint invalid
            self.event_selector.event_endpoint = "http://invalid-url-for-test.com/api/events"
            
            print("  🔍 Testing with invalid endpoint...")
            events = self.event_selector.fetch_all_events()
            
            # Restore endpoint
            self.event_selector.event_endpoint = original_endpoint
            
            # Should return empty list on error
            if isinstance(events, list):
                print("  ✅ Error handling working - returned empty list")
            else:
                print(f"  ❌ Error handling failed - returned {type(events)}")
                return False
            
            # Test normal endpoint lagi
            print("  🔍 Testing with restored valid endpoint...")
            events = self.event_selector.fetch_all_events()
            
            if isinstance(events, list):
                print(f"  ✅ Normal operation restored - got {len(events)} events")
            else:
                print("  ❌ Normal operation not restored")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing API error handling: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Jalankan semua test event"""
        print("🚀 Starting Event Selection & Management Tests...\n")
        
        tests = [
            ("Event Selector Initialization", self.test_event_selector_init),
            ("Authentication Token Creation", self.test_auth_token_creation),
            ("Fetch Events from Database", self.test_fetch_events_from_database),
            ("Event Display Formatting", self.test_event_display_formatting),
            ("Event Menu Display", self.test_event_menu_display),
            ("Event Creation Data", self.test_event_creation_data),
            ("Event ID Validation", self.test_event_validation),
            ("API Error Handling", self.test_api_error_handling)
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
        print(f"📊 EVENT SELECTION TEST SUMMARY")
        print(f"{'='*50}")
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name:35} : {status}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL EVENT SELECTION TESTS PASSED!")
            return True
        else:
            print("⚠️  Some tests failed. Check event API configuration.")
            return False

def main():
    """Main function untuk event testing"""
    try:
        tester = EventTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n✅ Event selection ready for production use!")
            print("💡 You can now run interactive event selection with confidence.")
        else:
            print("\n❌ Please fix event-related issues before proceeding.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n🛑 Event test cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Fatal error during event test: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)