"""
Bing Web Search API integration for Microsoft Advertising compliant URL discovery.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
import aiohttp
from urllib.parse import urljoin
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class BingDiscoveryService:
    """
    Microsoft Bing Web Search API service for discovering advertising-eligible URLs.
    Designed for Microsoft Advertising compliance and brand safety.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Bing Search API configuration
        self.bing_search_url = "https://api.bing.microsoft.com/v7.0/search"
        self.bing_custom_search_url = "https://api.bing.microsoft.com/v7.0/custom/search"
        
        # Microsoft Advertising content policy filters
        self.safe_search = "Strict"  # Strict, Moderate, Off
        self.content_filters = {
            "adult": "Strict",
            "violence": "Strict", 
            "gambling": "Moderate",
            "healthcare": "Moderate"
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def discover_urls(
        self, 
        query: str, 
        count: int = 50,
        market: str = "en-US",
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Discover URLs using Bing Web Search API with Microsoft Advertising compliance.
        
        Args:
            query: Search query for content discovery
            count: Number of results to return (max 50 per request)
            market: Market/language code (en-US, en-GB, etc.)
            category_filter: Content category filter for advertising compliance
            
        Returns:
            Dictionary containing discovered URLs and metadata
        """
        if not self.settings.bing_search_api_key:
            raise ValueError("BING_SEARCH_API_KEY not configured")
            
        headers = {
            "Ocp-Apim-Subscription-Key": self.settings.bing_search_api_key,
            "User-Agent": "Microsoft-Advertising-Content-Discovery/1.0"
        }
        
        params = {
            "q": query,
            "count": min(count, 50),  # Bing API limit
            "mkt": market,
            "safeSearch": self.safe_search,
            "responseFilter": "Webpages",
            "textDecorations": False,
            "textFormat": "Raw"
        }
        
        # Add category filter for advertising compliance
        if category_filter:
            params["category"] = category_filter
            
        try:
            async with self.session.get(
                self.bing_search_url,
                headers=headers,
                params=params
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return await self._process_bing_results(result, query)
                else:
                    error_text = await response.text()
                    logger.error(f"Bing API error {response.status}: {error_text}")
                    raise aiohttp.ClientError(f"Bing API error: {response.status}")
                    
        except Exception as e:
            logger.error(f"Error discovering URLs with Bing: {str(e)}")
            raise
    
    async def discover_by_category(
        self,
        categories: List[str],
        urls_per_category: int = 20
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Discover URLs by Microsoft Advertising approved categories.
        
        Args:
            categories: List of advertising-safe categories
            urls_per_category: Number of URLs to discover per category
            
        Returns:
            Dictionary mapping categories to discovered URLs
        """
        # Microsoft Advertising preferred categories
        advertising_categories = {
            "business": "business news technology",
            "finance": "finance investment banking",
            "technology": "technology software innovation",
            "health": "health wellness fitness",
            "education": "education learning training",
            "retail": "shopping retail e-commerce",
            "travel": "travel tourism hospitality",
            "automotive": "automotive cars vehicles",
            "real_estate": "real estate property housing",
            "sports": "sports recreation fitness"
        }
        
        results = {}
        
        for category in categories:
            if category in advertising_categories:
                query = advertising_categories[category]
                try:
                    category_results = await self.discover_urls(
                        query=query,
                        count=urls_per_category,
                        category_filter=category
                    )
                    results[category] = category_results.get("urls", [])
                except Exception as e:
                    logger.error(f"Error discovering URLs for category {category}: {str(e)}")
                    results[category] = []
                    
        return results
    
    async def _process_bing_results(
        self, 
        bing_response: Dict[str, Any], 
        query: str
    ) -> Dict[str, Any]:
        """Process Bing API response for Microsoft Advertising compliance."""
        
        urls = []
        
        if "webPages" in bing_response and "value" in bing_response["webPages"]:
            for item in bing_response["webPages"]["value"]:
                url_data = {
                    "url": item.get("url", ""),
                    "title": item.get("name", ""),
                    "description": item.get("snippet", ""),
                    "display_url": item.get("displayUrl", ""),
                    "date_last_crawled": item.get("dateLastCrawled", ""),
                    "language": item.get("language", "en"),
                    "is_family_friendly": item.get("isFamilyFriendly", True),
                    "source": "bing_search",
                    "search_query": query,
                    "advertising_eligible": True,  # Pre-filtered by Bing SafeSearch
                    "microsoft_compliant": True
                }
                
                # Additional Microsoft Advertising compliance checks
                if self._is_advertising_eligible_url(item):
                    urls.append(url_data)
        
        return {
            "urls": urls,
            "total_found": len(urls),
            "query": query,
            "search_engine": "bing",
            "compliance_level": "microsoft_advertising",
            "safe_search_applied": self.safe_search,
            "api_response_metadata": {
                "total_estimated_matches": bing_response.get("webPages", {}).get("totalEstimatedMatches", 0),
                "query_context": bing_response.get("queryContext", {})
            }
        }
    
    def _is_advertising_eligible_url(self, bing_item: Dict[str, Any]) -> bool:
        """
        Determine if a Bing search result meets Microsoft Advertising eligibility criteria.
        
        Args:
            bing_item: Individual Bing search result item
            
        Returns:
            Boolean indicating advertising eligibility
        """
        # Microsoft Advertising compliance checks
        url = bing_item.get("url", "").lower()
        title = bing_item.get("name", "").lower()
        snippet = bing_item.get("snippet", "").lower()
        
        # Exclude non-HTTPS sites (Microsoft Advertising requirement)
        if not url.startswith("https://"):
            return False
            
        # Exclude known problematic domains for advertising
        excluded_domains = [
            "adult", "xxx", "porn", "gambling", "casino", "pharma",
            "weapon", "gun", "violence", "hate", "illegal"
        ]
        
        for excluded in excluded_domains:
            if excluded in url or excluded in title:
                return False
        
        # Require family-friendly content
        if not bing_item.get("isFamilyFriendly", True):
            return False
            
        # Prefer established domains (basic check)
        if any(domain in url for domain in [".gov", ".edu", ".org"]):
            return True
            
        # Check for commercial viability indicators
        commercial_indicators = [
            "business", "company", "service", "product", "solution",
            "technology", "innovation", "professional", "industry"
        ]
        
        content_text = f"{title} {snippet}".lower()
        commercial_score = sum(1 for indicator in commercial_indicators if indicator in content_text)
        
        return commercial_score >= 1
    
    async def get_trending_topics(self, category: str = "business") -> List[str]:
        """
        Get trending topics for Microsoft Advertising campaigns.
        
        Args:
            category: Category for trending topics
            
        Returns:
            List of trending search queries
        """
        # This would integrate with Bing Trends API when available
        # For now, return category-specific trending topics
        
        trending_by_category = {
            "business": [
                "digital transformation", "remote work solutions", "enterprise software",
                "business intelligence", "cloud migration", "cybersecurity"
            ],
            "technology": [
                "artificial intelligence", "machine learning", "cloud computing",
                "software development", "tech innovation", "digital solutions"
            ],
            "finance": [
                "financial technology", "investment strategies", "business loans",
                "financial planning", "corporate finance", "fintech solutions"
            ]
        }
        
        return trending_by_category.get(category, trending_by_category["business"])