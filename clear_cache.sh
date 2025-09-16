#!/bin/bash

# Clear Python Cache Script
# =========================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 CLEAR PYTHON CACHE & RELOAD${NC}"
echo "================================="
echo

# Function untuk print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "event_selector.py" ]; then
    print_error "Script harus dijalankan dari direktori tethered-shooting-system"
    print_info "Pindah ke direktori yang benar:"
    print_info "cd gemini/tethered-shooting-system"
    exit 1
fi

print_info "Current directory: $(pwd)"
echo

# Step 1: Clear Python Cache Files
print_info "Step 1: Clearing Python cache files..."

# Remove .pyc files
pyc_count=$(find . -name "*.pyc" -type f | wc -l)
if [ "$pyc_count" -gt 0 ]; then
    find . -name "*.pyc" -type f -delete
    print_status "Removed $pyc_count .pyc files"
else
    print_info "No .pyc files found"
fi

# Remove __pycache__ directories
pycache_count=$(find . -name "__pycache__" -type d | wc -l)
if [ "$pycache_count" -gt 0 ]; then
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    print_status "Removed $pycache_count __pycache__ directories"
else
    print_info "No __pycache__ directories found"
fi

# Remove .pyo files (Python optimized)
pyo_count=$(find . -name "*.pyo" -type f | wc -l)
if [ "$pyo_count" -gt 0 ]; then
    find . -name "*.pyo" -type f -delete
    print_status "Removed $pyo_count .pyo files"
fi

echo

# Step 2: Check Method Exists in File
print_info "Step 2: Checking if get_active_event method exists in file..."

if grep -q "def get_active_event" event_selector.py; then
    line_number=$(grep -n "def get_active_event" event_selector.py | cut -d: -f1)
    print_status "Method found at line $line_number"
else
    print_error "Method get_active_event NOT found in event_selector.py"
    print_warning "Method might need to be added to the file"
    exit 1
fi

echo

# Step 3: Test Python Import
print_info "Step 3: Testing Python import..."

python3 -c "
import sys
import os
sys.path.insert(0, '.')

try:
    from event_selector import EventSelector
    print('✅ EventSelector imported successfully')
    
    es = EventSelector()
    print('✅ EventSelector instantiated successfully')
    
    has_method = hasattr(es, 'get_active_event')
    print(f'✅ get_active_event method exists: {has_method}')
    
    if not has_method:
        available_methods = [m for m in dir(es) if not m.startswith('_') and callable(getattr(es, m))]
        print(f'Available methods: {available_methods}')
        sys.exit(1)
    
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Python import test passed"
else
    print_error "Python import test failed"
    echo
    print_info "Trying alternative import method..."
    
    # Alternative method with fresh interpreter
    python3 << 'EOF'
import sys
import importlib
import os

# Clear any existing modules
modules_to_clear = [m for m in sys.modules.keys() if m.startswith('event_selector')]
for module in modules_to_clear:
    del sys.modules[module]

# Set working directory
os.chdir('.')

try:
    import event_selector
    importlib.reload(event_selector)
    
    es = event_selector.EventSelector()
    if hasattr(es, 'get_active_event'):
        print('✅ Alternative import method successful')
    else:
        print('❌ Method still not found after reload')
        exit(1)
        
except Exception as e:
    print(f'❌ Alternative import failed: {e}')
    exit(1)
EOF

    if [ $? -eq 0 ]; then
        print_status "Alternative import method passed"
    else
        print_error "All import methods failed"
        exit 1
    fi
fi

echo

# Step 4: Test Actual Method Call
print_info "Step 4: Testing actual method call..."

python3 -c "
import sys
sys.path.insert(0, '.')

try:
    from event_selector import EventSelector
    es = EventSelector()
    
    # Test method call (akan error jika API tidak available, tapi method ada)
    try:
        result = es.get_active_event()
        print(f'✅ Method call successful, result: {result}')
    except Exception as e:
        if 'get_active_event' in str(e):
            print(f'❌ Method still not found: {e}')
            sys.exit(1)
        else:
            print(f'✅ Method exists but API call failed (expected): {e}')
    
except Exception as e:
    print(f'❌ Method test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Method call test passed"
else
    print_error "Method call test failed"
fi

echo

# Step 5: Test Folder Watcher
print_info "Step 5: Testing folder_watcher.py import..."

python3 -c "
import sys
sys.path.insert(0, '.')

try:
    # Test import without running
    import folder_watcher
    print('✅ folder_watcher.py imports successfully')
    
    # Test EventSelector import within folder_watcher context
    from event_selector import EventSelector
    es = EventSelector()
    
    if hasattr(es, 'get_active_event'):
        print('✅ get_active_event method available in folder_watcher context')
    else:
        print('❌ get_active_event method NOT available in folder_watcher context')
        sys.exit(1)
        
except Exception as e:
    print(f'❌ folder_watcher import test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_status "Folder watcher import test passed"
else
    print_error "Folder watcher import test failed"
fi

echo
print_status "🎉 Cache cleared and all tests passed!"
echo
print_info "You can now run:"
print_info "python3 folder_watcher.py"
print_info "python3 manual_trigger.py"
print_info "python3 auto_capture_ai_enhanced.py"
echo
print_warning "If you still get errors, restart your terminal and try again."