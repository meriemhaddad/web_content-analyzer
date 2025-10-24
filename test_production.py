"""
Production readiness test script
"""
import requests
import json
import time
import sys
from typing import Dict, Any

def test_production_app(base_url: str = "http://localhost:8000") -> bool:
    """Test the production deployment of the app."""
    
    print(f"🚀 Testing Production App: {base_url}")
    print("="*50)
    
    tests_passed = 0
    total_tests = 0
    
    def run_test(test_name: str, test_func) -> bool:
        nonlocal tests_passed, total_tests
        total_tests += 1
        try:
            print(f"\n🧪 {test_name}...")
            result = test_func()
            if result:
                print(f"✅ {test_name} - PASSED")
                tests_passed += 1
                return True
            else:
                print(f"❌ {test_name} - FAILED")
                return False
        except Exception as e:
            print(f"❌ {test_name} - ERROR: {str(e)}")
            return False
    
    # Test 1: Health Check
    def test_health():
        response = requests.get(f"{base_url}/health", timeout=10)
        return response.status_code == 200
    
    # Test 2: Root Endpoint
    def test_root():
        response = requests.get(f"{base_url}/", timeout=10)
        return response.status_code == 200
    
    # Test 3: Bulk Upload Interface
    def test_bulk_interface():
        response = requests.get(f"{base_url}/api/v1/bulk-upload", timeout=10)
        return response.status_code == 200 and "html" in response.headers.get("content-type", "").lower()
    
    # Test 4: API Documentation (should be disabled in production)
    def test_docs_disabled():
        try:
            response = requests.get(f"{base_url}/docs", timeout=10)
            # In production, docs should be disabled (404) or redirected
            return response.status_code in [404, 403]
        except:
            return True  # Docs endpoint not accessible is good for production
    
    # Test 5: Copy/Paste URL Analysis
    def test_api_functionality():
        test_data = {
            'urls_text': 'https://example.com',
            'include_sentiment': True,
            'include_entities': True,
            'include_summary': True,
            'include_category': True,
            'include_keywords': True,
            'analysis_depth': 'basic',
            'max_concurrent': 1
        }
        
        response = requests.post(
            f"{base_url}/api/v1/upload-urls-advanced",
            data=test_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('total_urls') == 1
        return False
    
    # Run all tests
    run_test("Health Check", test_health)
    run_test("Root Endpoint", test_root)
    run_test("Bulk Upload Interface", test_bulk_interface)
    run_test("API Documentation Disabled", test_docs_disabled)
    run_test("URL Analysis Functionality", test_api_functionality)
    
    # Summary
    print("\n" + "="*50)
    print(f"📊 TEST SUMMARY")
    print(f"✅ Passed: {tests_passed}/{total_tests}")
    print(f"📈 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("\n🎉 Production app is ready for deployment!")
        return True
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Check the logs above.")
        return False

def test_deployment_urls():
    """Test common deployment platform URLs."""
    deployment_urls = [
        "http://localhost:8000",
        # Add your actual deployment URLs here:
        # "https://your-app.railway.app",
        # "https://your-app.onrender.com",
    ]
    
    for url in deployment_urls:
        print(f"\n🌐 Testing: {url}")
        if test_production_app(url):
            print(f"✅ {url} is working correctly!")
        else:
            print(f"❌ {url} has issues")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_url = sys.argv[1]
        test_production_app(test_url)
    else:
        test_deployment_urls()