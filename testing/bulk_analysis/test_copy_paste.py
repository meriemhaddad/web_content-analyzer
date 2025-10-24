"""
Test script for the copy/paste URL functionality
"""
import requests
import json

def test_copy_paste_urls():
    """Test the copy/paste URL endpoint"""
    
    # Test URLs
    test_urls = """https://www.github.com
https://www.openai.com
https://www.microsoft.com
https://stackoverflow.com"""
    
    # Prepare form data
    data = {
        'urls_text': test_urls,
        'include_sentiment': True,
        'include_entities': True,
        'include_summary': True,
        'include_category': True,
        'include_keywords': True,
        'analysis_depth': 'standard',
        'max_concurrent': 3
    }
    
    try:
        print("[TEST] Testing copy/paste URL analysis...")
        print(f"URLs to analyze:\n{test_urls}\n")
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/upload-urls-advanced',
            data=data,
            timeout=120
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"[SUCCESS] Success! Analyzed {results['total_urls']} URLs")
            print(f"[STATS] Success rate: {results['successful_analyses']}/{results['total_urls']}")
            print(f"[TIME]  Total time: {results['processing_time_seconds']:.1f}s")
            
            print("\n[RESULTS] Results summary:")
            for result in results['results']:
                status = "[SUCCESS]" if result['status'] == 'success' else "[ERROR]"
                category = result.get('primary_category', 'Unknown')
                print(f"{status} {result['url']} - {category}")
                
        else:
            print(f"[ERROR] Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")

if __name__ == "__main__":
    test_copy_paste_urls()