"""
Test script to demonstrate the BrandAI critique engine

This script shows how to:
1. Create a brand kit
2. Generate a sample ad (or use existing)
3. Critique the ad
4. Display results
"""

import asyncio
from backend.app.core.critique_engine import CritiqueEngine
from backend.app.models.schemas import BrandKit
from backend.app.services.brand_service import BrandService


async def demo_critique():
    """Demonstrate the critique engine"""
    
    print("=" * 60)
    print("BrandAI - AI Ad Critique Engine Demo")
    print("=" * 60)
    
    # Initialize services
    critique_engine = CritiqueEngine()
    brand_service = BrandService()
    
    # Step 1: Create a sample brand kit
    print("\n📋 Step 1: Creating Brand Kit...")
    
    sample_brand = BrandKit(
        brand_id="nike-demo",
        brand_name="Nike Demo",
        primary_colors=["#FF0000", "#000000", "#FFFFFF"],
        secondary_colors=["#808080"],
        tone_of_voice=["energetic", "inspiring", "bold"],
        brand_values=["innovation", "performance", "authenticity"],
        guidelines="Always show movement and energy. Use bold typography."
    )
    
    await brand_service.save_brand_kit(sample_brand)
    print(f"✅ Created brand kit: {sample_brand.brand_name}")
    print(f"   Colors: {', '.join(sample_brand.primary_colors)}")
    print(f"   Tone: {', '.join(sample_brand.tone_of_voice)}")
    
    # Step 2: Instructions for testing
    print("\n📸 Step 2: Testing Critique")
    print("\nTo test the critique engine, you need an ad image.")
    print("\nOptions:")
    print("1. Use the web interface (frontend/index.html)")
    print("2. Place a test image in 'uploads/test_ad.jpg'")
    print("3. Generate an ad using the API")
    
    # Check if test image exists
    import os
    test_image_path = "uploads/test_ad.jpg"
    
    if os.path.exists(test_image_path):
        print(f"\n✅ Found test image: {test_image_path}")
        print("\n🔍 Running critique...")
        
        try:
            # Critique the ad
            critique = await critique_engine.critique_ad(
                image_path=test_image_path,
                brand_kit=sample_brand,
                ad_description="Nike running shoes advertisement"
            )
            
            # Display results
            print("\n" + "=" * 60)
            print("CRITIQUE RESULTS")
            print("=" * 60)
            
            print(f"\n📊 Overall Score: {critique.overall_score:.2f} ({critique.overall_level.value.upper()})")
            print(f"✅ Ready to Deploy: {'YES' if critique.ready_to_deploy else 'NO'}")
            
            print("\n📈 Dimension Scores:")
            print(f"  • Brand Alignment: {critique.brand_alignment.score:.2f} - {critique.brand_alignment.feedback}")
            print(f"  • Visual Quality:  {critique.visual_quality.score:.2f} - {critique.visual_quality.feedback}")
            print(f"  • Message Clarity: {critique.message_clarity.score:.2f} - {critique.message_clarity.feedback}")
            print(f"  • Safety & Ethics: {critique.safety_ethics.score:.2f} - {critique.safety_ethics.feedback}")
            
            if critique.improvements_needed:
                print("\n💡 Suggested Improvements:")
                for i, suggestion in enumerate(critique.improvements_needed, 1):
                    print(f"  {i}. {suggestion}")
            
            print("\n" + "=" * 60)
            
        except Exception as e:
            print(f"\n❌ Error during critique: {e}")
            print("\nNote: Make sure you have:")
            print("1. Set GEMINI_API_KEY in .env file")
            print("2. Installed all dependencies (pip install -r requirements.txt)")
    
    else:
        print(f"\n⚠️  No test image found at: {test_image_path}")
        print("\nTo test the critique:")
        print("1. Place an ad image at: uploads/test_ad.jpg")
        print("2. Run this script again")
        print("3. Or use the web interface (frontend/index.html)")
    
    # Step 3: Show API endpoints
    print("\n🌐 API Endpoints Available:")
    print("  POST /api/critique-ad - Critique an uploaded ad")
    print("  POST /api/brand-kit - Create/update brand kit")
    print("  GET  /api/brand-kits - List all brand kits")
    print("  POST /api/generate-ad - Generate new ad")
    print("  GET  /docs - Interactive API documentation")
    
    print("\n💡 Next Steps:")
    print("1. Start the server: python backend/main.py")
    print("2. Open frontend/index.html in your browser")
    print("3. Upload an ad image to test the critique engine")
    print("4. Review detailed scores and suggestions")
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_critique())
