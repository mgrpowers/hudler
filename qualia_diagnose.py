"""
Diagnostic script to check Qualia library installation
Run this on ESP32-S3 to see what's wrong
"""

import os
import sys

print("=" * 60)
print("Qualia Library Diagnostic")
print("=" * 60)

# Check filesystem
print("\n1. Checking filesystem...")
try:
    lib_path = '/lib'
    if os.path.exists(lib_path):
        print(f"✓ /lib exists")
        contents = os.listdir(lib_path)
        print(f"  Contents: {contents}")
        
        if 'adafruit_qualia' in contents:
            print("\n2. Checking adafruit_qualia folder...")
            qualia_path = os.path.join(lib_path, 'adafruit_qualia')
            qualia_files = os.listdir(qualia_path)
            print(f"  Files found: {len(qualia_files)}")
            
            # Check for Python files
            py_files = [f for f in qualia_files if f.endswith(('.py', '.mpy'))]
            print(f"  Python files (.py/.mpy): {len(py_files)}")
            if py_files:
                print(f"    {py_files[:5]}")
            else:
                print("  ✗ No Python files found! Only metadata files.")
                print("  You need to copy the actual library code, not just metadata.")
            
            # Check for __init__
            has_init = any(f.startswith('__init__') for f in qualia_files)
            if has_init:
                print("  ✓ __init__ file found")
            else:
                print("  ✗ No __init__ file - library won't import")
                
        else:
            print("  ✗ adafruit_qualia folder not found in /lib")
    else:
        print("✗ /lib folder doesn't exist")
except Exception as e:
    print(f"Error: {e}")

# Try imports
print("\n3. Trying imports...")
try:
    import adafruit_qualia
    print("  ✓ import adafruit_qualia worked!")
    print(f"  Contents: {dir(adafruit_qualia)[:10]}")
    try:
        from adafruit_qualia import Qualia
        print("  ✓ from adafruit_qualia import Qualia worked!")
    except ImportError as e:
        print(f"  ✗ Cannot import Qualia: {e}")
except ImportError as e:
    print(f"  ✗ Cannot import adafruit_qualia: {e}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Check sys.path
print("\n4. Python path:")
for path in sys.path:
    print(f"  {path}")

print("\n" + "=" * 60)
print("Diagnosis complete!")
print("=" * 60)

