#!/usr/bin/env python3

"""
Fix Event Selector - Add Missing get_active_event Method
=======================================================

Script untuk menambahkan method get_active_event yang hilang ke event_selector.py
"""

import os
import re

def fix_event_selector():
    """Add missing get_active_event method to event_selector.py"""
    
    # Read current file
    with open('event_selector.py', 'r') as f:
        content = f.read()
    
    # Check if method already exists
    if 'def get_active_event(' in content:
        print("✅ Method get_active_event already exists!")
        return True
    
    print("🔧 Adding missing get_active_event method...")
    
    # Method to add
    method_code = '''    
    def get_active_event(self) -> Optional[str]:
        """Dapatkan event ID yang sedang aktif"""
        try:
            logger.info("Fetching active event...")
            
            headers = self._get_auth_headers()
            response = requests.get(
                self.event_endpoint,
                headers=headers,
                params={"status": "active", "limit": 1},
                timeout=30
            )
            
            if response.status_code == 200:
                events = response.json()
                if events and len(events) > 0:
                    event_id = events[0].get("id")
                    logger.info(f"✅ Active event found: {event_id}")
                    return event_id
                else:
                    logger.warning("⚠️ No active event found")
                    return None
            else:
                logger.error(f"❌ Failed to fetch events: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching active event: {e}")
            return None
'''
    
    # Find insertion point after fetch_all_events method
    pattern = r'(\s+return \[\]\s+)(def format_event_display)'
    
    if re.search(pattern, content):
        # Insert method before format_event_display
        new_content = re.sub(pattern, r'\1' + method_code + r'\n    \2', content)
        
        # Write back to file
        with open('event_selector.py', 'w') as f:
            f.write(new_content)
        
        print("✅ Method get_active_event added successfully!")
        print("📍 Added before format_event_display method")
        return True
    else:
        print("❌ Could not find insertion point")
        print("🔍 Looking for alternative insertion point...")
        
        # Alternative: Add after fetch_all_events method ends
        pattern2 = r'(def fetch_all_events.*?return \[\])\s*\n'
        
        if re.search(pattern2, content, re.DOTALL):
            new_content = re.sub(pattern2, r'\1' + method_code + '\n', content, flags=re.DOTALL)
            
            with open('event_selector.py', 'w') as f:
                f.write(new_content)
            
            print("✅ Method get_active_event added successfully!")
            print("📍 Added after fetch_all_events method")
            return True
        else:
            print("❌ Could not find suitable insertion point")
            return False

def verify_method():
    """Verify that method was added correctly"""
    try:
        with open('event_selector.py', 'r') as f:
            content = f.read()
        
        if 'def get_active_event(' in content:
            print("✅ Verification: Method exists in file")
            
            # Count lines
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'def get_active_event(' in line:
                    print(f"📍 Found at line {i}")
                    break
            
            return True
        else:
            print("❌ Verification failed: Method not found")
            return False
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def test_import():
    """Test that EventSelector can be imported with the new method"""
    try:
        print("🧪 Testing import...")
        
        # Clear cache
        import sys
        if 'event_selector' in sys.modules:
            del sys.modules['event_selector']
        
        # Import fresh
        from event_selector import EventSelector
        
        es = EventSelector()
        
        if hasattr(es, 'get_active_event'):
            print("✅ Import test passed: Method available")
            return True
        else:
            print("❌ Import test failed: Method not available")
            available_methods = [m for m in dir(es) if not m.startswith('_') and callable(getattr(es, m))]
            print(f"Available methods: {available_methods}")
            return False
            
    except Exception as e:
        print(f"❌ Import test error: {e}")
        return False

def main():
    """Main function"""
    print("🔧 FIX EVENT SELECTOR - Add Missing Method")
    print("=" * 50)
    
    # Check if file exists
    if not os.path.exists('event_selector.py'):
        print("❌ event_selector.py not found!")
        print("💡 Make sure you're in the tethered-shooting-system directory")
        return
    
    # Fix the file
    if fix_event_selector():
        print("\n🔍 Verifying fix...")
        if verify_method():
            print("\n🧪 Testing import...")
            if test_import():
                print("\n🎉 SUCCESS! event_selector.py fixed successfully!")
                print("\n💡 You can now run:")
                print("   python3 folder_watcher.py")
                print("   python3 manual_trigger.py")
                print("   python3 auto_capture_ai_enhanced.py")
            else:
                print("\n⚠️ Method added but import test failed")
                print("💡 Try restarting your terminal")
        else:
            print("\n❌ Verification failed")
    else:
        print("\n❌ Failed to add method")
        print("\n💡 Manual fix needed:")
        print("   1. Open event_selector.py")
        print("   2. Add the get_active_event method after fetch_all_events")
        print("   3. Copy method code from the GitHub repository")

if __name__ == "__main__":
    main()