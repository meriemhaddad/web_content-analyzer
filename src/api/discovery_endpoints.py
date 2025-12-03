"""
FastAPI endpoints for Microsoft Advertising URL discovery and eligibility analysis.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field, validator
from datetime import datetime

from src.services.bing_discovery import BingDiscoveryService
from src.services.microsoft_advertising_analyzer import MicrosoftAdvertisingEligibilityAnalyzer
from src.services.content_analyzer import ContentAnalysisEngine
from src.services.mcp_client import MCPFetchClient

logger = logging.getLogger(__name__)

# Create router for scraping endpoints
router = APIRouter(prefix="/api/v1/discovery", tags=["Microsoft Advertising Discovery"])

# Request/Response Models
class DiscoveryRequest(BaseModel):
    """Request model for URL discovery."""
    query: str = Field(..., description="Search query for content discovery")
    count: int = Field(default=20, ge=1, le=50, description="Number of URLs to discover")
    market: str = Field(default="en-US", description="Market/language code")
    category_filter: Optional[str] = Field(None, description="Content category filter")
    analyze_immediately: bool = Field(default=False, description="Whether to analyze discovered URLs immediately")

class CategoryDiscoveryRequest(BaseModel):
    """Request model for category-based discovery."""
    categories: List[str] = Field(..., description="List of advertising categories to search")
    urls_per_category: int = Field(default=10, ge=1, le=25, description="URLs to discover per category")
    analyze_immediately: bool = Field(default=False, description="Whether to analyze discovered URLs immediately")

class EligibilityAnalysisRequest(BaseModel):
    """Request model for Microsoft Advertising eligibility analysis."""
    url: str = Field(..., description="URL to analyze for advertising eligibility")
    force_reanalysis: bool = Field(default=False, description="Force re-analysis even if recently analyzed")

class BatchEligibilityRequest(BaseModel):
    """Request model for batch eligibility analysis."""
    urls: List[str] = Field(..., min_items=1, max_items=10, description="List of URLs to analyze")
    
    @validator('urls')
    def validate_urls(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 URLs allowed per batch request')
        return v

class DiscoveryResponse(BaseModel):
    """Response model for URL discovery."""
    urls: List[Dict[str, Any]]
    total_found: int
    query: str
    search_engine: str
    compliance_level: str
    metadata: Dict[str, Any]

class EligibilityResponse(BaseModel):
    """Response model for advertising eligibility analysis."""
    url: str
    microsoft_advertising_eligible: bool
    compliance_level: str
    overall_score: float
    brand_safety: Dict[str, Any]
    technical_compliance: Dict[str, Any]
    content_policy: Dict[str, Any]
    recommendations: List[str]
    analysis_timestamp: str

# Endpoints
@router.post("/discover", response_model=DiscoveryResponse)
async def discover_urls(request: DiscoveryRequest, background_tasks: BackgroundTasks):
    """
    Discover URLs using Microsoft Bing Search API with advertising compliance filters.
    """
    try:
        async with BingDiscoveryService() as discovery_service:
            results = await discovery_service.discover_urls(
                query=request.query,
                count=request.count,
                market=request.market,
                category_filter=request.category_filter
            )
            
            # If immediate analysis requested, queue background analysis
            if request.analyze_immediately and results.get("urls"):
                background_tasks.add_task(
                    analyze_discovered_urls_background,
                    [url["url"] for url in results["urls"]]
                )
            
            return DiscoveryResponse(
                urls=results["urls"],
                total_found=results["total_found"],
                query=results["query"],
                search_engine=results["search_engine"],
                compliance_level=results["compliance_level"],
                metadata=results.get("api_response_metadata", {})
            )
            
    except Exception as e:
        logger.error(f"Error in URL discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@router.post("/discover-by-category", response_model=Dict[str, List[Dict[str, Any]]])
async def discover_by_category(request: CategoryDiscoveryRequest, background_tasks: BackgroundTasks):
    """
    Discover URLs by Microsoft Advertising approved categories.
    """
    try:
        async with BingDiscoveryService() as discovery_service:
            results = await discovery_service.discover_by_category(
                categories=request.categories,
                urls_per_category=request.urls_per_category
            )
            
            # If immediate analysis requested, queue background analysis
            if request.analyze_immediately:
                all_urls = []
                for category_urls in results.values():
                    all_urls.extend([url["url"] for url in category_urls if isinstance(url, dict)])
                
                if all_urls:
                    background_tasks.add_task(analyze_discovered_urls_background, all_urls)
            
            return results
            
    except Exception as e:
        logger.error(f"Error in category discovery: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Category discovery failed: {str(e)}")

@router.post("/analyze-eligibility", response_model=EligibilityResponse)
async def analyze_advertising_eligibility(request: EligibilityAnalysisRequest):
    """
    Analyze a URL for Microsoft Advertising eligibility and compliance.
    """
    try:
        # First, fetch and analyze the content
        async with MCPFetchClient() as mcp_client:
            content_data = await mcp_client.fetch_content(request.url)
            
        if content_data["status"] == "error":
            raise HTTPException(
                status_code=400, 
                detail=f"Failed to fetch content: {content_data.get('error', 'Unknown error')}"
            )
        
        # Perform content analysis using existing pipeline
        analyzer = ContentAnalysisEngine()
        content_analysis = await analyzer.analyze_url(
            url=request.url,
            analysis_depth="comprehensive",
            include_metadata=True
        )
        
        # Perform Microsoft Advertising eligibility analysis
        eligibility_analyzer = MicrosoftAdvertisingEligibilityAnalyzer()
        eligibility_result = await eligibility_analyzer.analyze_eligibility(
            content_analysis=content_analysis.model_dump(),
            url_metadata=content_data["metadata"]
        )
        
        return EligibilityResponse(**eligibility_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in eligibility analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Eligibility analysis failed: {str(e)}")

@router.post("/batch-analyze-eligibility", response_model=List[EligibilityResponse])
async def batch_analyze_eligibility(request: BatchEligibilityRequest):
    """
    Analyze multiple URLs for Microsoft Advertising eligibility (batch processing).
    """
    try:
        results = []
        
        # Process URLs concurrently (limited to prevent overwhelming)
        async with MCPFetchClient() as mcp_client:
            # Fetch content for all URLs
            content_results = await mcp_client.batch_fetch_content(request.urls)
        
        analyzer = ContentAnalysisEngine()
        eligibility_analyzer = MicrosoftAdvertisingEligibilityAnalyzer()
        
        for i, url in enumerate(request.urls):
            try:
                content_data = content_results[i]
                
                if content_data["status"] == "error":
                    # Create error response for failed URL
                    error_result = EligibilityResponse(
                        url=url,
                        microsoft_advertising_eligible=False,
                        compliance_level="prohibited",
                        overall_score=0.0,
                        brand_safety={"score": 0, "safety_level": "unsafe"},
                        technical_compliance={"score": 0, "compliant": False},
                        content_policy={"score": 0, "compliant": False},
                        recommendations=["Failed to fetch content for analysis"],
                        analysis_timestamp=datetime.utcnow().isoformat()
                    )
                    results.append(error_result)
                    continue
                
                # Perform content analysis
                content_analysis = await analyzer.analyze_url(
                    url=url,
                    analysis_depth="comprehensive",
                    include_metadata=True
                )
                
                # Perform eligibility analysis
                eligibility_result = await eligibility_analyzer.analyze_eligibility(
                    content_analysis=content_analysis.model_dump(),
                    url_metadata=content_data["metadata"]
                )
                
                results.append(EligibilityResponse(**eligibility_result))
                
            except Exception as e:
                    logger.error(f"Error analyzing URL {url}: {str(e)}")
                    # Create error response for this specific URL
                    error_result = EligibilityResponse(
                        url=url,
                        microsoft_advertising_eligible=False,
                        compliance_level="prohibited",
                        overall_score=0.0,
                        brand_safety={"score": 0, "safety_level": "unsafe"},
                        technical_compliance={"score": 0, "compliant": False},
                        content_policy={"score": 0, "compliant": False},
                        recommendations=[f"Analysis failed: {str(e)}"],
                        analysis_timestamp=datetime.utcnow().isoformat()
                    )
                    results.append(error_result)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch eligibility analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@router.get("/trending-topics")
async def get_trending_topics(
    category: str = Query(default="business", description="Category for trending topics")
):
    """
    Get trending topics for Microsoft Advertising campaigns.
    """
    try:
        async with BingDiscoveryService() as discovery_service:
            trends = await discovery_service.get_trending_topics(category)
            
        return {
            "category": category,
            "trending_topics": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting trending topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get trending topics: {str(e)}")

@router.get("/compliance-categories")
async def get_compliance_categories():
    """
    Get available Microsoft Advertising compliance categories.
    """
    return {
        "approved_categories": [
            "business", "finance", "technology", "health", "education",
            "retail", "travel", "automotive", "real_estate", "sports"
        ],
        "prohibited_categories": [
            "adult_content", "violence", "illegal_activities", 
            "gambling", "hate_speech", "misleading"
        ],
        "compliance_levels": [
            "approved", "conditional", "restricted", "prohibited"
        ],
        "minimum_scores": {
            "brand_safety": 60,
            "technical_compliance": 70,
            "content_policy": 70,
            "overall_eligibility": 70
        }
    }

# Background task functions
async def analyze_discovered_urls_background(urls: List[str]):
    """Background task to analyze discovered URLs."""
    try:
        logger.info(f"Starting background analysis of {len(urls)} discovered URLs")
        
        # Process in smaller batches to avoid overwhelming the system
        batch_size = 5
        for i in range(0, len(urls), batch_size):
            batch = urls[i:i + batch_size]
            
            try:
                # This would ideally save results to a database or queue
                # For now, just log the analysis
                async with MCPFetchClient() as mcp_client:
                    content_results = await mcp_client.batch_fetch_content(batch)
                
                logger.info(f"Analyzed batch {i//batch_size + 1}: {len(batch)} URLs")
                
                # Add delay between batches to be respectful
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error in background analysis batch {i//batch_size + 1}: {str(e)}")
        
        logger.info(f"Completed background analysis of {len(urls)} URLs")
        
    except Exception as e:
        logger.error(f"Error in background analysis task: {str(e)}")