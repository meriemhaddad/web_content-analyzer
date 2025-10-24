"""
Quick Bulk Test Example
======================

A simple script to test multiple URLs quickly using curl or requests.
"""

import requests
import json
import time
from typing import List, Dict

# Quick test URLs - diverse content types
QUICK_TEST_URLS = [
    # French satirical content
    "https://www.legorafi.fr/",
    
    # Sports content
    "https://www.leparisien.fr/sports/",
    
    # Technology news
    "https://www.lemonde.fr/pixels/",
    
    # Health information
    "https://www.doctissimo.fr/",
    
    # Travel content
    "https://www.routard.com/"
]

def analyze_url_batch(urls: List[str], api_url: str = "http://127.0.0.1:8000/api/v1/analyze") -> List[Dict]:
    """Analyze a batch of URLs and return results."""
    results = []
    
    print(f"[RUNNING] Testing {len(urls)} URLs...")
    print("-" * 60)
    
    for i, url in enumerate(urls, 1):
        print(f"[STATS] [{i}/{len(urls)}] Analyzing: {url}")
        
        start_time = time.time()
        
        payload = {
            "url": url,
            "options": {
                "include_sentiment": True,
                "include_entities": True,
                "include_summary": True,
                "include_category": True,
                "include_keywords": True
            }
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=30)
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"   [SUCCESS] Category: {result.get('primary_category', 'unknown')}")
                print(f"   [SUMMARY] Confidence: {result.get('category_confidence', 0):.2f}")
                print(f"   [EMOJI] Sentiment: {result.get('sentiment', {}).get('overall', 'unknown')}")
                print(f"   [TIME]  Time: {processing_time:.2f}s")
                
                # Add processing metadata
                result['processing_time'] = round(processing_time, 2)
                result['test_url'] = url
                results.append(result)
                
            else:
                print(f"   [ERROR] Error: HTTP {response.status_code}")
                results.append({
                    "test_url": url,
                    "error": f"HTTP {response.status_code}",
                    "processing_time": round(processing_time, 2)
                })
                
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"   [ERROR] Error: {str(e)}")
            results.append({
                "test_url": url,
                "error": str(e),
                "processing_time": round(processing_time, 2)
            })
        
        print()
    
    return results

def print_summary(results: List[Dict]):
    """Print a summary of the test results."""
    successful = [r for r in results if 'primary_category' in r]
    failed = [r for r in results if 'error' in r]
    
    print("=" * 60)
    print("[RESULTS] BULK TEST SUMMARY")
    print("=" * 60)
    
    print(f"[STATS] Total URLs: {len(results)}")
    print(f"[SUCCESS] Successful: {len(successful)}")
    print(f"[ERROR] Failed: {len(failed)}")
    print(f"[SUMMARY] Success Rate: {len(successful)/len(results)*100:.1f}%")
    
    if successful:
        avg_time = sum(r.get('processing_time', 0) for r in successful) / len(successful)
        print(f"[TIME]  Average Processing Time: {avg_time:.2f}s")
        
        print(f"\n[TARGET] Categories Detected:")
        categories = {}
        for result in successful:
            cat = result.get('primary_category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in sorted(categories.items()):
            print(f"   • {cat}: {count}")
        
        print(f"\n[EMOJI] Sentiment Distribution:")
        sentiments = {}
        for result in successful:
            sent = result.get('sentiment', {}).get('overall', 'unknown')
            sentiments[sent] = sentiments.get(sent, 0) + 1
        
        for sent, count in sorted(sentiments.items()):
            print(f"   • {sent}: {count}")
    
    if failed:
        print(f"\n[ERROR] Failed URLs:")
        for result in failed:
            print(f"   • {result['test_url']}: {result['error']}")

def main():
    """Run the quick bulk test."""
    print("[TARGET] Quick Bulk URL Analysis Test")
    print("=" * 60)
    
    # Run the analysis
    results = analyze_url_batch(QUICK_TEST_URLS)
    
    # Print summary
    print_summary(results)
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"quick_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SYMBOL] Results saved to: {filename}")

if __name__ == "__main__":
    main()