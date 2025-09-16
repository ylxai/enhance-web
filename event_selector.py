# Interactive Event Selection dari Database Real
# =============================================

import requests
import json
import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import sys

from config import Config

logger = logging.getLogger(__name__)

class EventSelector:
    """Class untuk interactive selection event dari database real"""
    
    def __init__(self):
        """Inisialisasi event selector"""
        self.base_url = Config.WEB_INTEGRATION["web_api_base_url"]
        self.event_endpoint = Config.WEB_INTEGRATION["web_event_endpoint"]
        self.jwt_secret = Config.WEB_INTEGRATION["jwt_secret"]
        
        logger.info("Event selector initialized")
    
    def _create_auth_token(self) -> str:
        """Buat JWT token untuk authentication"""
        try:
            import jwt
            payload = {
                "source": "tethered_shooting",
                "timestamp": int(time.time()),
                "exp": int(time.time()) + 3600  # 1 hour expiry
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            return token
            
        except Exception as e:
            logger.error(f"Error creating auth token: {e}")
            return ""
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Dapatkan headers untuk authentication"""
        token = self._create_auth_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-Source": "tethered-shooting-system"
        }
    
    def fetch_all_events(self) -> List[Dict[str, Any]]:
        """Ambil semua event dari database real"""
        try:
            print("🔄 Mengambil data event dari database...")
            
            headers = self._get_auth_headers()
            
            # Ambil semua event (tidak hanya yang active)
            response = requests.get(
                self.event_endpoint,
                headers=headers,
                params={
                    "limit": 50,  # Ambil 50 event terbaru
                    "sort": "date",
                    "order": "desc"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                events = response.json()
                
                # Log info untuk debugging
                logger.info(f"✅ Berhasil mengambil {len(events)} event dari database")
                
                return events
            else:
                print(f"❌ Gagal mengambil data event: HTTP {response.status_code}")
                logger.error(f"Failed to fetch events: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error koneksi ke database: {e}")
            logger.error(f"Network error fetching events: {e}")
            return []
        except Exception as e:
            print(f"❌ Error mengambil event: {e}")
            logger.error(f"Error fetching events: {e}")
            return []
    
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
    
    def format_event_display(self, event: Dict[str, Any], index: int) -> str:
        """Format event untuk display yang menarik"""
        try:
            # Extract data event
            event_id = event.get('id', 'unknown')
            name = event.get('name', 'Unnamed Event')
            date = event.get('date', 'No date')
            time_str = event.get('time', 'No time')
            location = event.get('location', 'No location')
            status = event.get('status', 'unknown')
            
            # Format tanggal yang lebih readable
            try:
                if date and date != 'No date':
                    # Parse tanggal dan format ulang
                    date_obj = datetime.strptime(date, '%Y-%m-%d')
                    formatted_date = date_obj.strftime('%d %b %Y')
                else:
                    formatted_date = 'No date'
            except:
                formatted_date = date
            
            # Status indicator
            status_indicator = {
                'active': '🟢',
                'upcoming': '🟡', 
                'completed': '🔴',
                'cancelled': '⚫'
            }.get(status.lower(), '⚪')
            
            # Format untuk display
            display_text = f"{index:2d}. {status_indicator} {name}"
            
            # Tambah info detail
            details = []
            if formatted_date != 'No date':
                details.append(f"📅 {formatted_date}")
            if time_str and time_str != 'No time':
                details.append(f"🕒 {time_str}")
            if location and location != 'No location':
                details.append(f"📍 {location}")
            
            if details:
                display_text += f"\n     {' | '.join(details)}"
            
            # Tambah event ID untuk referensi
            display_text += f"\n     🆔 {event_id[:12]}..."
            
            return display_text
            
        except Exception as e:
            logger.error(f"Error formatting event display: {e}")
            return f"{index:2d}. ❌ Error displaying event"
    
    def display_events_menu(self, events: List[Dict[str, Any]]) -> None:
        """Display menu event selection yang menarik"""
        print("\n" + "="*80)
        print("🎯 PILIH EVENT UNTUK TETHERED SHOOTING SESSION")
        print("="*80)
        
        if not events:
            print("❌ Tidak ada event ditemukan di database")
            return
        
        # Kelompokkan berdasarkan status
        active_events = [e for e in events if e.get('status', '').lower() == 'active']
        upcoming_events = [e for e in events if e.get('status', '').lower() == 'upcoming']
        other_events = [e for e in events if e.get('status', '').lower() not in ['active', 'upcoming']]
        
        index = 1
        
        # Tampilkan active events dulu
        if active_events:
            print("\n🟢 ACTIVE EVENTS (Sedang Berlangsung)")
            print("-" * 50)
            for event in active_events:
                print(self.format_event_display(event, index))
                index += 1
        
        # Tampilkan upcoming events
        if upcoming_events:
            print(f"\n🟡 UPCOMING EVENTS (Akan Datang)")
            print("-" * 50)
            for event in upcoming_events:
                print(self.format_event_display(event, index))
                index += 1
        
        # Tampilkan other events
        if other_events:
            print(f"\n⚪ OTHER EVENTS (Lainnya)")
            print("-" * 50)
            for event in other_events[:10]:  # Limit 10 untuk avoid clutter
                print(self.format_event_display(event, index))
                index += 1
        
        # Opsi tambahan
        print(f"\n✨ OPSI LAINNYA")
        print("-" * 50)
        print(f"{index:2d}. 🆕 Buat Event Baru (Auto)")
        print(f"{index+1:2d}. 🔄 Refresh Data Event")
        print(f"{index+2:2d}. ❌ Keluar")
        
        print("\n" + "="*80)
    
    def get_user_selection(self, events: List[Dict[str, Any]]) -> Optional[str]:
        """Ambil pilihan user dan return event ID"""
        try:
            total_events = len(events)
            max_choice = total_events + 3  # events + 3 extra options
            
            while True:
                try:
                    print(f"\n📋 Masukkan pilihan Anda (1-{max_choice}): ", end="")
                    user_input = input().strip()
                    
                    if not user_input:
                        print("⚠️ Pilihan tidak boleh kosong")
                        continue
                    
                    choice = int(user_input)
                    
                    if choice < 1 or choice > max_choice:
                        print(f"⚠️ Pilihan harus antara 1-{max_choice}")
                        continue
                    
                    # Event selection
                    if choice <= total_events:
                        selected_event = events[choice - 1]
                        event_id = selected_event.get('id')
                        event_name = selected_event.get('name', 'Unnamed Event')
                        
                        print(f"\n✅ Event dipilih: {event_name}")
                        print(f"🆔 Event ID: {event_id}")
                        
                        # Konfirmasi
                        confirm = input("\n❓ Lanjutkan dengan event ini? (y/N): ").strip().lower()
                        if confirm in ['y', 'yes', 'ya']:
                            return event_id
                        else:
                            print("🔄 Pilih event lain...")
                            continue
                    
                    # Buat event baru
                    elif choice == total_events + 1:
                        return self._create_new_event_interactive()
                    
                    # Refresh data
                    elif choice == total_events + 2:
                        return "REFRESH"
                    
                    # Keluar
                    elif choice == total_events + 3:
                        print("👋 Keluar dari event selection...")
                        return None
                    
                except ValueError:
                    print("⚠️ Masukkan angka yang valid")
                    continue
                except KeyboardInterrupt:
                    print("\n👋 Event selection dibatalkan")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting user selection: {e}")
            print(f"❌ Error: {e}")
            return None
    
    def _create_new_event_interactive(self) -> Optional[str]:
        """Buat event baru secara interaktif"""
        try:
            print("\n🆕 BUAT EVENT BARU")
            print("=" * 40)
            
            # Input data event
            name = input("📝 Nama Event: ").strip()
            if not name:
                name = f"Tethered Shooting Session {datetime.now().strftime('%Y%m%d_%H%M')}"
            
            location = input("📍 Lokasi (optional): ").strip()
            if not location:
                location = "Studio"
            
            description = input("📄 Deskripsi (optional): ").strip()
            if not description:
                description = "Auto-created event for tethered shooting session"
            
            print(f"\n📋 Preview Event Baru:")
            print(f"   Nama: {name}")
            print(f"   Lokasi: {location}")
            print(f"   Deskripsi: {description}")
            print(f"   Tanggal: {datetime.now().strftime('%Y-%m-%d')}")
            print(f"   Waktu: {datetime.now().strftime('%H:%M')}")
            
            confirm = input("\n❓ Buat event ini? (y/N): ").strip().lower()
            if confirm not in ['y', 'yes', 'ya']:
                print("❌ Pembuatan event dibatalkan")
                return None
            
            # Buat event via API
            event_data = {
                "name": name,
                "description": description,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "time": datetime.now().strftime('%H:%M'),
                "location": location,
                "status": "active",
                "type": Config.WEB_INTEGRATION["default_event_type"],
                "category": "photography",
                "auto_created": True,
                "created_by": "tethered_shooting_system"
            }
            
            headers = self._get_auth_headers()
            response = requests.post(
                self.event_endpoint,
                headers=headers,
                json=event_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                event = response.json()
                event_id = event.get("id")
                print(f"\n✅ Event berhasil dibuat!")
                print(f"🆔 Event ID: {event_id}")
                return event_id
            else:
                print(f"❌ Gagal membuat event: HTTP {response.status_code}")
                logger.error(f"Failed to create event: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error membuat event: {e}")
            logger.error(f"Error creating new event: {e}")
            return None
    
    def select_event_interactive(self) -> Optional[str]:
        """Main function untuk interactive event selection"""
        try:
            while True:
                # Ambil data event real dari database
                events = self.fetch_all_events()
                
                if not events:
                    print("❌ Tidak dapat mengambil data event dari database")
                    print("🔄 Periksa koneksi dan coba lagi")
                    
                    retry = input("\n❓ Coba lagi? (y/N): ").strip().lower()
                    if retry not in ['y', 'yes', 'ya']:
                        return None
                    continue
                
                # Tampilkan menu
                self.display_events_menu(events)
                
                # Ambil pilihan user
                selection = self.get_user_selection(events)
                
                if selection == "REFRESH":
                    print("🔄 Mengrefresh data event...")
                    continue
                elif selection is None:
                    return None
                else:
                    return selection
                    
        except KeyboardInterrupt:
            print("\n👋 Event selection dibatalkan oleh user")
            return None
        except Exception as e:
            print(f"❌ Error dalam event selection: {e}")
            logger.error(f"Error in interactive event selection: {e}")
            return None

def test_event_selector():
    """Test function untuk event selector"""
    try:
        print("🧪 Testing Interactive Event Selector...")
        
        selector = EventSelector()
        
        # Test fetch events
        print("\n1. Testing fetch events from database...")
        events = selector.fetch_all_events()
        print(f"✅ Found {len(events)} events")
        
        if events:
            print("\n2. Testing display menu...")
            selector.display_events_menu(events[:5])  # Show first 5 for test
            
            print("\n3. Sample event format:")
            print(selector.format_event_display(events[0], 1))
        
        print("\n✅ Event selector test completed")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    # Jika dijalankan langsung, lakukan interactive selection
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_event_selector()
    else:
        selector = EventSelector()
        event_id = selector.select_event_interactive()
        
        if event_id:
            print(f"\n🎯 Selected Event ID: {event_id}")
        else:
            print("\n❌ No event selected")