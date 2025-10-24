"""
Bulk URL Analysis Test Script
============================

This script demonstrates the bulk analysis capabilities of the Web Content Analysis Agent
by testing various types of content from different sources and languages.
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any
from datetime import datetime

# Test URLs covering diverse content types
BULK_TEST_URLS = [
    # French News & Media
    {
        "url": "https://www.lemonde.fr/international/",
        "expected_category": "news",
        "description": "Le Monde - International News"
    },
    {
        "url": "https://www.leparisien.fr/sports/",
        "expected_category": "sports", 
        "description": "Le Parisien - Sports Section"
    },
    {
        "url": "https://www.legorafi.fr/",
        "expected_category": "satire",
        "description": "Le Gorafi - French Satirical News"
    },
    
    # English Content
    {
        "url": "https://www.bbc.com/news/technology",
        "expected_category": "technology",
        "description": "BBC Technology News"
    },
    {
        "url": "https://www.techcrunch.com/",
        "expected_category": "technology",
        "description": "TechCrunch - Startup News"
    },
    {
        "url": "https://www.reuters.com/business/",
        "expected_category": "business",
        "description": "Reuters Business News"
    },
    
    # Specialized Content
    {
        "url": "https://www.mayoclinic.org/diseases-conditions",
        "expected_category": "health",
        "description": "Mayo Clinic - Health Information"
    },
    {
        "url": "https://www.nationalgeographic.com/science/",
        "expected_category": "science",
        "description": "National Geographic Science"
    },
    {
        "url": "https://www.lonelyplanet.com/france",
        "expected_category": "travel",
        "description": "Lonely Planet - France Travel Guide"
    },
    
    # Business & Finance
    {
        "url": "https://www.bloomberg.com/markets",
        "expected_category": "finance",
        "description": "Bloomberg Markets"
    },
    {
        "url": "https://www.forbes.com/business/",
        "expected_category": "business",
        "description": "Forbes Business"
    },
    
    # Entertainment & Lifestyle
    {
        "url": "https://www.imdb.com/news/movie/",
        "expected_category": "entertainment",
        "description": "IMDB Movie News"
    },
    {
        "url": "https://www.allrecipes.com/",
        "expected_category": "lifestyle",
        "description": "AllRecipes - Cooking & Food"
    },
    
    # Educational & Documentation
    {
        "url": "https://docs.python.org/3/",
        "expected_category": "documentation",
        "description": "Python Documentation"
    },
    {
        "url": "https://stackoverflow.com/questions/tagged/python",
        "expected_category": "forum",
        "description": "Stack Overflow - Python Questions"
    }
]

class BulkURLTester:
    """Test bulk URL analysis capabilities."""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:8000"):
        self.api_base_url = api_base_url
        self.analyze_endpoint = f"{api_base_url}/api/v1/analyze"
        
    async def analyze_single_url(self, session: aiohttp.ClientSession, url_data: Dict[str, str]) -> Dict[str, Any]:
        """Analyze a single URL and return results with metadata."""
        url = url_data["url"]
        start_time = time.time()
        
        try:
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
            
            async with session.post(self.analyze_endpoint, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    processing_time = time.time() - start_time
                    
                    return {
                        "test_url": url,
                        "description": url_data["description"],
                        "expected_category": url_data["expected_category"],
                        "actual_category": result.get("primary_category", "unknown"),
                        "secondary_categories": result.get("secondary_categories", []),
                        "status": result.get("status", "unknown"),
                        "content_summary": result.get("content_summary", "")[:200] + "...",
                        "sentiment": result.get("sentiment", {}).get("overall", "unknown"),
                        "confidence": result.get("category_confidence", 0),
                        "processing_time": round(processing_time, 2),
                        "success": True
                    }
                else:
                    return {
                        "test_url": url,
                        "description": url_data["description"],
                        "expected_category": url_data["expected_category"],
                        "error": f"HTTP {response.status}",
                        "processing_time": round(time.time() - start_time, 2),
                        "success": False
                    }
                    
        except Exception as e:
            return {
                "test_url": url,
                "description": url_data["description"],
                "expected_category": url_data["expected_category"],
                "error": str(e),
                "processing_time": round(time.time() - start_time, 2),
                "success": False
            }
    
    async def run_bulk_test(self, max_concurrent: int = 5) -> Dict[str, Any]:
        """Run bulk analysis test with concurrent processing."""
        print(f"[RUNNING] Starting bulk URL analysis test...")
        print(f"[STATS] Testing {len(BULK_TEST_URLS)} URLs with max {max_concurrent} concurrent requests")
        print(f"[TARGET] API Endpoint: {self.analyze_endpoint}")
        print("-" * 80)
        
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(session, url_data):
            async with semaphore:
                return await self.analyze_single_url(session, url_data)
        
        # Run concurrent analysis
        async with aiohttp.ClientSession() as session:
            tasks = [analyze_with_semaphore(session, url_data) for url_data in BULK_TEST_URLS]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        
        # Process results
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed_results = [r for r in results if isinstance(r, dict) and not r.get("success")]
        exceptions = [r for r in results if not isinstance(r, dict)]
        
        # Calculate statistics
        category_matches = sum(1 for r in successful_results 
                             if r.get("actual_category") == r.get("expected_category"))
        
        avg_processing_time = sum(r.get("processing_time", 0) for r in successful_results) / len(successful_results) if successful_results else 0
        
        # Generate report
        report = {
            "test_summary": {
                "total_urls": len(BULK_TEST_URLS),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "exceptions": len(exceptions),
                "success_rate": round(len(successful_results) / len(BULK_TEST_URLS) * 100, 1),
                "category_accuracy": round(category_matches / len(successful_results) * 100, 1) if successful_results else 0,
                "total_processing_time": round(total_time, 2),
                "average_processing_time": round(avg_processing_time, 2),
                "urls_per_second": round(len(BULK_TEST_URLS) / total_time, 2)
            },
            "detailed_results": successful_results,
            "failed_results": failed_results,
            "exceptions": [str(e) for e in exceptions]
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted test report."""
        summary = report["test_summary"]
        
        print("\n" + "="*80)
        print("[TARGET] BULK URL ANALYSIS TEST RESULTS")
        print("="*80)
        
        print(f"[STATS] Overall Statistics:")
        print(f"   • Total URLs Tested: {summary['total_urls']}")
        print(f"   • Successful Analyses: {summary['successful']}")
        print(f"   • Failed Analyses: {summary['failed']}")
        print(f"   • Success Rate: {summary['success_rate']}%")
        print(f"   • Category Accuracy: {summary['category_accuracy']}%")
        
        print(f"\n[TIME]  Performance Metrics:")
        print(f"   • Total Processing Time: {summary['total_processing_time']} seconds")
        print(f"   • Average Time per URL: {summary['average_processing_time']} seconds")
        print(f"   • Processing Rate: {summary['urls_per_second']} URLs/second")
        
        print(f"\n[SUCCESS] Successful Results:")
        print("-" * 80)
        for result in report["detailed_results"]:
            match_indicator = "[SUCCESS]" if result["actual_category"] == result["expected_category"] else "[WARNING]"
            print(f"{match_indicator} {result['description']}")
            print(f"   URL: {result['test_url']}")
            print(f"   Expected: {result['expected_category']} | Actual: {result['actual_category']}")
            print(f"   Confidence: {result['confidence']:.2f} | Sentiment: {result['sentiment']}")
            print(f"   Time: {result['processing_time']}s | Status: {result['status']}")
            if result.get('secondary_categories'):
                print(f"   Secondary: {', '.join(result['secondary_categories'])}")
            print()
        
        if report["failed_results"]:
            print(f"\n[ERROR] Failed Results:")
            print("-" * 80)
            for result in report["failed_results"]:
                print(f"[ERROR] {result['description']}")
                print(f"   URL: {result['test_url']}")
                print(f"   Error: {result.get('error', 'Unknown error')}")
                print()
        
        print("="*80)
        print("[COMPLETE] Bulk test completed!")

async def main():
    """Run the bulk URL test."""
    tester = BulkURLTester()
    
    # Run the test
    report = await tester.run_bulk_test(max_concurrent=3)
    
    # Print results
    tester.print_report(report)
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bulk_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SYMBOL] Detailed results saved to: {filename}")

if __name__ == "__main__":
    asyncio.run(main())