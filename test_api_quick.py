"""
Quick API Test Script for BrandAI Demo
Run this to quickly test all endpoints before your presentation
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test if server is running"""
    print_section("1. Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Server Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Server Error: {e}")
        return False

def test_create_brand_kit():
    """Create a test brand kit"""
    print_section("2. Create Brand Kit")
    
    brand_kit = {
        "brand_name": "TestBrand",
        "primary_colors": ["#2E7D32", "#66BB6A"],
        "tone_of_voice": ["natural", "authentic"],
        "brand_values": ["eco-friendly", "sustainable"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/brand-kit",
            json=brand_kit
        )
        
        if response.status_code == 200:
            data = response.json()
            brand_id = data.get('brand_id')
            print(f"✅ Brand Kit Created!")
            print(f"Brand ID: {brand_id}")
            print(f"Full Response: {json.dumps(data, indent=2)}")
            return brand_id
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_multi_agent_workflow(brand_id):
    """Test the multi-agent workflow"""
    print_section("3. Multi-Agent Workflow")
    
    if not brand_id:
        print("⚠️ Skipping - no brand_id available")
        return
    
    workflow_request = {
        "brand_id": brand_id,
        "prompt": "Create an ad for eco-friendly water bottles",
        "max_iterations": 2
    }
    
    try:
        print("🚀 Starting workflow (this may take 30-60 seconds)...")
        print(f"Request: {json.dumps(workflow_request, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/multi-agent/generate-and-critique",
            json=workflow_request
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Workflow Completed!")
            print(f"\nWorkflow ID: {data.get('workflow_id')}")
            print(f"Status: {data.get('status')}")
            print(f"Iterations: {len(data.get('iterations', []))}")
            
            # Show first iteration details
            if data.get('iterations'):
                iter1 = data['iterations'][0]
                print(f"\n📊 Iteration 1 Scores:")
                if iter1.get('critique', {}).get('scores'):
                    scores = iter1['critique']['scores']
                    print(f"  - Brand Alignment: {scores.get('brand_alignment', 0)*100:.0f}%")
                    print(f"  - Visual Quality: {scores.get('visual_quality', 0)*100:.0f}%")
                    print(f"  - Message Clarity: {scores.get('message_clarity', 0)*100:.0f}%")
                    print(f"  - Safety: {scores.get('safety', 0)*100:.0f}%")
                
                # Show confidence scores if available
                if iter1.get('critique', {}).get('confidence_scores'):
                    conf = iter1['critique']['confidence_scores']
                    print(f"\n🎯 Confidence Scores:")
                    print(f"  - Overall: {conf.get('overall', 0)*100:.0f}%")
                    
                # Show category detection
                if iter1.get('critique', {}).get('detected_elements', {}).get('category_detected'):
                    category = iter1['critique']['detected_elements']['category_detected']
                    print(f"\n🏷️ Detected Category: {category.upper()}")
            
            return data.get('workflow_id')
            
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_workflow_status(workflow_id):
    """Check workflow status"""
    print_section("4. Workflow Status")
    
    if not workflow_id:
        print("⚠️ Skipping - no workflow_id available")
        return
    
    try:
        response = requests.get(f"{BASE_URL}/api/multi-agent/workflow-status")
        
        if response.status_code == 200:
            workflows = response.json()
            print(f"✅ Found {len(workflows)} workflow(s)")
            
            # Find our workflow
            for wf in workflows:
                if wf.get('workflow_id') == workflow_id:
                    print(f"\n📋 Workflow {workflow_id}:")
                    print(f"  Status: {wf.get('status')}")
                    print(f"  Iterations: {wf.get('current_iteration')}/{wf.get('max_iterations')}")
                    break
        else:
            print(f"❌ Failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def run_full_test():
    """Run complete test suite"""
    print("\n" + "🎯"*30)
    print("  BrandAI API Test Suite")
    print("🎯"*30)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server not running! Start with: python -m uvicorn backend.main:app --reload")
        return
    
    time.sleep(1)
    
    # Test 2: Create brand kit
    brand_id = test_create_brand_kit()
    time.sleep(1)
    
    # Test 3: Multi-agent workflow
    workflow_id = test_multi_agent_workflow(brand_id)
    time.sleep(1)
    
    # Test 4: Check status
    test_workflow_status(workflow_id)
    
    print("\n" + "✅"*30)
    print("  Test Suite Complete!")
    print("✅"*30)
    print("\n💡 Next Steps:")
    print("  1. Open http://localhost:8000 in browser")
    print("  2. Go to 'Brand Kits' tab")
    print("  3. Paste brand_id:", brand_id)
    print("  4. Go to 'Multi-Agent Workflow' tab")
    print("  5. Try a custom prompt!")

if __name__ == "__main__":
    run_full_test()
