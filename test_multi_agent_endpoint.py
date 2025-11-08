"""
Quick test script for the multi-agent endpoint
"""
import requests
import json

# Test 1: Workflow status
print("Testing /api/multi-agent/workflow-status...")
try:
    response = requests.get("http://localhost:8000/api/multi-agent/workflow-status")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("✅ Workflow status endpoint works!\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Generate and refine (minimal test)
print("Testing /api/multi-agent/generate-and-refine...")
payload = {
    "prompt": "Create a simple ad for running shoes",
    "max_iterations": 1,
    "score_threshold": 0.5,
    "aspect_ratio": "1:1",
    "include_logo": False
}

try:
    response = requests.post(
        "http://localhost:8000/api/multi-agent/generate-and-refine",
        json=payload,
        timeout=60
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success')}")
        print(f"Message: {result.get('message')}")
        print(f"Iterations: {result.get('iterations_count')}")
        print("✅ Multi-agent endpoint works!")
    else:
        print(f"Response: {response.text}")
        print("⚠️ Non-200 status code")
except requests.exceptions.ConnectionError:
    print("❌ Server not running or not accessible at localhost:8000")
except Exception as e:
    print(f"❌ Error: {e}")
