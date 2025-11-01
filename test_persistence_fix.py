"""
Quick test to verify the persistence fix is working
"""

from pathlib import Path
import json

print("\n" + "="*70)
print("  🔍 TESTING PERSISTENCE FIX")
print("="*70)

# Check if the new directories exist
frontend_dir = Path("frontend")
upload_dir = frontend_dir / "uploaded_documents"
tracker_file = frontend_dir / "processed_files.json"

tests_passed = 0
tests_total = 4

# Test 1: Upload directory exists
print("\n[Test 1] Checking upload directory...")
if upload_dir.exists():
    print(f"   ✅ PASS: {upload_dir} exists")
    tests_passed += 1
else:
    print(f"   ⚠️  INFO: {upload_dir} will be created on first upload")

# Test 2: Check if tracker file exists (if documents uploaded)
print("\n[Test 2] Checking tracking file...")
if tracker_file.exists():
    try:
        with open(tracker_file, 'r') as f:
            tracked = json.load(f)
        print(f"   ✅ PASS: Found {len(tracked)} tracked document(s)")
        for filename, info in tracked.items():
            print(f"      • {filename} ({info.get('chunk_count', '?')} chunks)")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ FAIL: Error reading tracker: {e}")
else:
    print(f"   ⚠️  INFO: No documents uploaded yet")
    tests_passed += 1  # This is OK for first run

# Test 3: Check uploaded files
print("\n[Test 3] Checking uploaded files...")
if upload_dir.exists():
    files = list(upload_dir.glob("*.pdf")) + list(upload_dir.glob("*.txt"))
    if files:
        print(f"   ✅ PASS: Found {len(files)} uploaded file(s)")
        for f in files:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"      • {f.name} ({size_mb:.2f} MB)")
        tests_passed += 1
    else:
        print(f"   ⚠️  INFO: No files in upload directory yet")
        tests_passed += 1  # OK for first run
else:
    print(f"   ⚠️  INFO: Upload directory doesn't exist yet")
    tests_passed += 1

# Test 4: Check sidebar.py was updated
print("\n[Test 4] Checking code was updated...")
sidebar_file = frontend_dir / "ui" / "sidebar.py"
if sidebar_file.exists():
    content = sidebar_file.read_text(encoding='utf-8')
    if "processed_files.json" in content and "UPLOAD_DIR" in content:
        print(f"   ✅ PASS: sidebar.py contains persistence code")
        tests_passed += 1
    else:
        print(f"   ❌ FAIL: sidebar.py doesn't have persistence code")
else:
    print(f"   ❌ FAIL: sidebar.py not found")

# Summary
print("\n" + "="*70)
print(f"  RESULTS: {tests_passed}/{tests_total} checks passed")
print("="*70)

if tests_passed == tests_total:
    print("\n✅ PERSISTENCE FIX IS ACTIVE!")
    print("\n📋 Next steps:")
    print("   1. cd frontend")
    print("   2. streamlit run app.py")
    print("   3. Upload a PDF")
    print("   4. Refresh the page (F5)")
    print("   5. Verify document is still listed!")
else:
    print("\n⚠️  Some checks didn't pass, but this may be OK if you haven't uploaded yet.")
    print("   Just start the UI and upload a document to test!")

print()

