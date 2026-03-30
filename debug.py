import os

print("=" * 60)
print("DEBUGGING HTML SERVING")
print("=" * 60)

# Check current directory
print(f"\nCurrent directory: {os.getcwd()}")

# Check if index.html exists
print(f"index.html exists: {os.path.exists('index.html')}")

# List all files
print(f"\nFiles in current directory:")
for file in os.listdir():
    print(f"  - {file}")

# Try to read index.html
print("\nTrying to read index.html:")
try:
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        print(f"✅ Successfully read index.html")
        print(f"   File size: {len(content)} bytes")
        print(f"   First 200 chars: {content[:200]}")
except Exception as e:
    print(f"❌ Error reading index.html: {e}")

# Try to read with different encoding
print("\nTrying with different encoding (utf-8-sig):")
try:
    with open("index.html", "r", encoding="utf-8-sig") as f:
        content = f.read()
        print(f"✅ Successfully read with utf-8-sig")
        print(f"   First 200 chars: {content[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)