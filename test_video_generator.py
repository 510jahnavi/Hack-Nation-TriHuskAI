"""
Quick Test: Video Generator with Uploads
"""
import requests
import json
from pathlib import Path

API_BASE = "http://127.0.0.1:8000/api"

print("🎬 Testing AI Video Ad Generator with File Uploads\n")
print("=" * 60)

# Test 1: Check server health
print("\n1️⃣ Checking server health...")
try:
    response = requests.get(f"{API_BASE.replace('/api', '')}/health")
    if response.ok:
        print("✅ Server is healthy!")
        print(f"   Response: {response.json()}")
    else:
        print("❌ Server health check failed")
        exit(1)
except Exception as e:
    print(f"❌ Error connecting to server: {e}")
    exit(1)

# Test 2: List available brand kits
print("\n2️⃣ Loading brand kits...")
try:
    response = requests.get(f"{API_BASE}/brand-kits")
    if response.ok:
        brands = response.json()
        print(f"✅ Found {len(brands)} brand kit(s)")
        for brand in brands[:3]:  # Show first 3
            print(f"   - {brand['brand_name']} (ID: {brand['brand_id']})")
            print(f"     Colors: {', '.join(brand['primary_colors'][:3])}")
    else:
        print("❌ Failed to load brand kits")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Upload sample files (if you have them)
print("\n3️⃣ Testing file upload endpoints...")
print("   ℹ️  Upload API available at:")
print(f"      POST {API_BASE}/upload/brand-logo")
print(f"      POST {API_BASE}/upload/product-image")
print("   📝 To test manually:")
print('      curl -X POST http://127.0.0.1:8000/api/upload/brand-logo -F "file=@logo.png"')

# Test 4: Check static file serving
print("\n4️⃣ Static file serving...")
print("   ✅ Generated ads accessible at: http://127.0.0.1:8000/generated_ads/[filename]")
print("   ✅ Uploads accessible at: http://127.0.0.1:8000/uploads/[type]/[filename]")

# Test 5: List generated ads
print("\n5️⃣ Checking generated ads folder...")
try:
    ads_dir = Path("backend/generated_ads")
    if ads_dir.exists():
        files = list(ads_dir.glob("*.*"))
        print(f"   Found {len(files)} generated file(s)")
        for f in files[:3]:  # Show first 3
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name} ({size_kb:.1f} KB)")
            print(f"     URL: http://127.0.0.1:8000/generated_ads/{f.name}")
    else:
        print("   ℹ️  No generated ads yet")
except Exception as e:
    print(f"   ℹ️  {e}")

# Test 6: Sample video generation request
print("\n6️⃣ Sample Video Generation Request:")
sample_request = {
    "prompt": "Create a vibrant video ad for organic juice with fresh fruits",
    "brand_kit_id": "purevita_food",
    "media_type": "video",
    "duration": 10,
    "aspect_ratio": "16:9",
    "max_iterations": 2,
    "score_threshold": 0.75,
    "brand_logo_path": None,  # Optional: path to uploaded logo
    "product_image_path": None  # Optional: path to uploaded product
}

print(f"   POST {API_BASE}/multi-agent/generate-and-refine")
print(f"   Body: {json.dumps(sample_request, indent=4)}")

print("\n" + "=" * 60)
print("🎯 Next Steps:")
print("1. Open http://127.0.0.1:8000/video_generator.html in browser")
print("2. Select brand kit and write prompt")
print("3. Upload brand logo and product image (optional)")
print("4. Click 'Generate AI Video Ad'")
print("5. View generated video with quality scores")
print("6. Download final video ad")
print("\n📚 Documentation: VIDEO_GENERATOR_GUIDE.md")
print("=" * 60)
