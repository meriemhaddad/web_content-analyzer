"""
Comprehensive test script for various URL types and error scenarios
"""
import requests
import json

def test_comprehensive_urls():
    """Test various URL types including error-prone ones"""
    
    # Test URLs with different characteristics
    test_urls = """https://www.github.com
https://www.stackoverflow.com
https://www.wikipedia.org
https://httpbin.org/status/200
https://httpbin.org/status/404
https://httpbin.org/status/403
https://httpbin.org/status/500
https://example.com
https://www.bbc.com
https://www.reddit.com"""
    
    # Prepare form data
    data = {
        'urls_text': test_urls,
        'include_sentiment': True,
        'include_entities': True,
        'include_summary': True,
        'include_category': True,
        'include_keywords': True,
        'analysis_depth': 'standard',
        'max_concurrent': 2  # Lower concurrency to be respectful
    }
    
    try:
        print("[TEST] Testing comprehensive URL analysis...")
        print("[RESULTS] URLs to test:")
        for i, url in enumerate(test_urls.strip().split('\n'), 1):
            print(f"  {i:2d}. {url}")
        print()
        
        response = requests.post(
            'http://127.0.0.1:8000/api/v1/upload-urls-advanced',
            data=data,
            timeout=180  # 3 minutes timeout
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"[SUCCESS] Analysis complete!")
            print(f"[STATS] Results: {results['successful_analyses']}/{results['total_urls']} successful")
            print(f"[TIME]  Total time: {results['processing_time_seconds']:.1f}s")
            print(f"[MISC] Avg time per URL: {results['processing_time_seconds']/results['total_urls']:.1f}s")
            
            print("\n[RESULTS] Detailed Results:")
            print("-" * 80)
            for i, result in enumerate(results['results'], 1):
                status_icon = "[SUCCESS]" if result['status'] == 'success' else "[ERROR]"
                category = result.get('primary_category', 'N/A')
                
                if result['status'] == 'error':
                    error_msg = result.get('error_message', 'Unknown error')
                    # Truncate long error messages
                    if len(error_msg) > 60:
                        error_msg = error_msg[:60] + "..."
                    print(f"{i:2d}. {status_icon} {result['url']}")
                    print(f"     [EXCEPTION] Error: {error_msg}")
                else:
                    confidence = result.get('category_confidence')
                    conf_str = f" ({confidence*100:.0f}%)" if confidence else ""
                    sentiment = result.get('sentiment', {}).get('overall', 'N/A')
                    print(f"{i:2d}. {status_icon} {result['url']}")
                    print(f"     [SYMBOL] Category: {category}{conf_str}")
                    print(f"     [EMOJI] Sentiment: {sentiment}")
                print()
                
        else:
            print(f"[ERROR] Error: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Details: {error_detail}")
            except:
                print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")

if __name__ == "__main__":
    test_comprehensive_urls()