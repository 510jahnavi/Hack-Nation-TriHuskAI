"""
Test script to check if brand kit is being loaded and used properly
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def test_brand_kit():
    from app.services.brand_service import BrandService
    
    brand_service = BrandService()
    
    # List all brand kits
    print("🔍 Listing all brand kits...")
    kits = await brand_service.list_brand_kits()
    
    if not kits:
        print("❌ No brand kits found!")
        print("Please create one in the UI first.")
        return
    
    print(f"✅ Found {len(kits)} brand kit(s):\n")
    
    for kit in kits:
        print(f"   Brand: {kit.brand_name}")
        print(f"   ID: {kit.brand_id}")
        print(f"   Colors: {kit.primary_colors}")
        print(f"   Tone: {kit.tone_of_voice}")
        print()

    # Test loading a specific kit
    if kits:
        test_kit = kits[0]
        print(f"🧪 Testing load of '{test_kit.brand_name}'...")
        loaded = await brand_service.get_brand_kit(test_kit.brand_id)
        
        if loaded:
            print(f"✅ Successfully loaded brand kit")
            print(f"   Primary colors: {loaded.primary_colors}")
            print(f"   Has {len(loaded.primary_colors)} color(s)")
        else:
            print(f"❌ Failed to load brand kit!")

if __name__ == "__main__":
    asyncio.run(test_brand_kit())
