"""
FastAPI endpoints for web content analysis.
"""

import asyncio
import logging
import csv
import io
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Dict, Any, Optional
from pathlib import Path
import time
from datetime import datetime

from src.models.requests import URLAnalysisRequest, BatchAnalysisRequest
from src.models.responses import (
    ContentAnalysisResult, 
    BatchAnalysisResult, 
    HealthResponse, 
    ErrorResponse
)
from src.services.content_analyzer import ContentAnalysisEngine
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Dependency to get content analyzer
async def get_content_analyzer() -> ContentAnalysisEngine:
    """Dependency to get content analyzer instance."""
    return ContentAnalysisEngine()

# Dependency to get settings
def get_app_settings():
    """Dependency to get application settings."""
    return get_settings()

@router.post(
    "/analyze",
    response_model=ContentAnalysisResult,
    summary="Analyze single URL",
    description="Perform comprehensive semantic analysis of a web page URL"
)
async def analyze_url(
    request: URLAnalysisRequest,
    analyzer: ContentAnalysisEngine = Depends(get_content_analyzer),
    settings = Depends(get_app_settings)
):
    """
    Analyze content from a single URL with advanced semantic analysis.
    
    - **url**: The URL to analyze (required)
    - **analysis_depth**: Depth of analysis - basic, detailed, or comprehensive
    - **include_metadata**: Whether to include page metadata analysis
    - **custom_categories**: Optional custom categories to focus analysis on
    
    Returns comprehensive analysis including categorization, sentiment, and semantic insights.
    """
    try:
        logger.info(f"Starting analysis for URL: {request.url}")
        
        result = await analyzer.analyze_url(
            url=str(request.url),
            analysis_depth=request.analysis_depth,
            include_metadata=request.include_metadata,
            custom_categories=request.custom_categories
        )
        
        logger.info(f"Analysis completed for URL: {request.url}")
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing URL {request.url}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post(
    "/batch-analyze",
    response_model=BatchAnalysisResult,
    summary="Analyze multiple URLs",
    description="Perform batch analysis of multiple web page URLs"
)
async def batch_analyze_urls(
    request: BatchAnalysisRequest,
    analyzer: ContentAnalysisEngine = Depends(get_content_analyzer),
    settings = Depends(get_app_settings)
):
    """
    Analyze content from multiple URLs with batch processing.
    
    - **urls**: List of URLs to analyze (max 10)
    - **analysis_depth**: Depth of analysis for all URLs
    - **include_metadata**: Whether to include metadata analysis
    - **custom_categories**: Optional custom categories to focus on
    - **parallel_processing**: Whether to process URLs in parallel
    
    Returns batch analysis results with individual URL results and aggregate statistics.
    """
    try:
        if len(request.urls) > settings.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Batch size exceeds maximum allowed ({settings.max_batch_size})"
            )
        
        logger.info(f"Starting batch analysis for {len(request.urls)} URLs")
        start_time = time.time()
        
        # Convert URLs to strings
        url_strings = [str(url) for url in request.urls]
        
        # Perform batch analysis
        individual_results = await analyzer.batch_analyze_urls(
            urls=url_strings,
            analysis_depth=request.analysis_depth,
            include_metadata=request.include_metadata,
            custom_categories=request.custom_categories,
            parallel_processing=request.parallel_processing
        )
        
        processing_time = time.time() - start_time
        
        # Calculate aggregate statistics
        successful_results = [r for r in individual_results if r.status == "success"]
        failed_results = [r for r in individual_results if r.status == "error"]
        
        # Category distribution
        category_distribution = {}
        total_quality_score = 0.0
        
        for result in successful_results:
            category = result.primary_category.value
            category_distribution[category] = category_distribution.get(category, 0) + 1
            total_quality_score += result.content_quality_score
        
        average_quality = (
            total_quality_score / len(successful_results) 
            if successful_results else None
        )
        
        # Build error list
        errors = []
        for result in failed_results:
            errors.append({
                "url": result.url,
                "error": result.key_insights[0] if result.key_insights else "Unknown error"
            })
        
        batch_result = BatchAnalysisResult(
            total_urls=len(request.urls),
            successful_analyses=len(successful_results),
            failed_analyses=len(failed_results),
            results=individual_results,
            errors=errors,
            category_distribution=category_distribution,
            average_quality_score=average_quality,
            processing_time_seconds=processing_time
        )
        
        logger.info(f"Batch analysis completed: {len(successful_results)}/{len(request.urls)} successful")
        return batch_result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch analysis failed: {str(e)}"
        )

@router.post(
    "/upload-urls",
    response_model=BatchAnalysisResult,
    summary="Upload URL file for batch analysis",
    description="Upload a file containing URLs (CSV, TXT) for batch content analysis"
)
async def upload_urls_file(
    file: UploadFile = File(..., description="CSV or TXT file containing URLs"),
    include_sentiment: bool = Form(True, description="Include sentiment analysis"),
    include_entities: bool = Form(True, description="Include entity extraction"),
    include_summary: bool = Form(True, description="Include content summary"),
    include_category: bool = Form(True, description="Include category analysis"),
    include_keywords: bool = Form(True, description="Include keyword extraction"),
    analyzer: ContentAnalysisEngine = Depends(get_content_analyzer)
):
    """
    Upload a file containing URLs for batch analysis.
    
    **Supported file formats:**
    - **CSV**: First column should contain URLs, optional second column for descriptions
    - **TXT**: One URL per line
    
    **File requirements:**
    - Maximum file size: 10MB
    - Maximum URLs: 50 per file
    - Supported formats: .csv, .txt
    
    **Example CSV format:**
    ```
    url,description
    https://example.com,Example website
    https://news.com,News article
    ```
    
    **Example TXT format:**
    ```
    https://example.com
    https://news.com
    https://blog.com
    ```
    
    Returns comprehensive batch analysis results with individual URL analyses and aggregate statistics.
    """
    settings = get_settings()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        # Check file extension
        file_extension = file.filename.lower().split('.')[-1]
        if file_extension not in ['csv', 'txt']:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload CSV or TXT files only."
            )
        
        # Read file content
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Parse URLs from file
        urls_data = []
        content_str = content.decode('utf-8')
        
        if file_extension == 'csv':
            # Parse CSV file
            csv_reader = csv.reader(io.StringIO(content_str))
            headers = next(csv_reader, None)
            
            for row_num, row in enumerate(csv_reader, start=2):
                if row and row[0].strip():  # Skip empty rows
                    url = row[0].strip()
                    description = row[1].strip() if len(row) > 1 else f"URL {row_num-1}"
                    urls_data.append({"url": url, "description": description})
        
        elif file_extension == 'txt':
            # Parse TXT file (one URL per line)
            lines = content_str.strip().split('\n')
            for line_num, line in enumerate(lines, start=1):
                url = line.strip()
                if url:  # Skip empty lines
                    urls_data.append({"url": url, "description": f"URL {line_num}"})
        
        # Validate URL count
        if len(urls_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No valid URLs found in the file."
            )
        
        if len(urls_data) > settings.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Too many URLs. Maximum allowed: {settings.max_batch_size}, found: {len(urls_data)}"
            )
        
        # Extract just the URLs for processing
        urls = [item["url"] for item in urls_data]
        
        logger.info(f"Processing uploaded file: {file.filename} with {len(urls)} URLs")
        
        # Create analysis options
        options = {
            "include_sentiment": include_sentiment,
            "include_entities": include_entities,
            "include_summary": include_summary,
            "include_category": include_category,
            "include_keywords": include_keywords
        }
        
        # Perform batch analysis
        individual_results = await analyzer.batch_analyze_urls(
            urls, 
            analysis_depth="comprehensive",
            options=options
        )
        
        # Calculate statistics
        successful_results = [r for r in individual_results if r.status == "success"]
        failed_results = [r for r in individual_results if r.status != "success"]
        
        # Category distribution
        category_dist = {}
        for result in successful_results:
            cat = result.primary_category
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Average quality score
        quality_scores = [r.content_quality_score for r in successful_results if r.content_quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Build batch result
        batch_result = BatchAnalysisResult(
            total_urls=len(urls),
            successful_analyses=len(successful_results),
            failed_analyses=len(failed_results),
            results=individual_results,
            errors=[{"url": r.url, "error": getattr(r, 'error', 'Unknown error')} for r in failed_results],
            category_distribution=category_dist,
            average_quality_score=avg_quality,
            processing_time_seconds=sum(r.processing_time_seconds for r in individual_results)
        )
        
        logger.info(f"File upload analysis completed: {len(successful_results)}/{len(urls)} successful")
        return batch_result
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Unable to decode file. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"File processing failed: {str(e)}"
        )

@router.post(
    "/upload-urls-advanced",
    response_model=BatchAnalysisResult,
    summary="Advanced URL upload with custom options",
    description="Upload URLs with advanced configuration options via form data"
)
async def upload_urls_advanced(
    urls_text: str = Form(..., description="URLs separated by newlines or commas"),
    analysis_depth: str = Form("comprehensive", description="Analysis depth: basic, standard, comprehensive"),
    max_concurrent: int = Form(3, description="Maximum concurrent analyses (1-10)"),
    include_sentiment: bool = Form(True),
    include_entities: bool = Form(True),
    include_summary: bool = Form(True),
    include_category: bool = Form(True),
    include_keywords: bool = Form(True),
    custom_categories: Optional[str] = Form(None, description="Custom categories to focus on (comma-separated)"),
    analyzer: ContentAnalysisEngine = Depends(get_content_analyzer)
):
    """
    Advanced URL upload via form data with custom analysis options.
    
    **Input format:**
    - URLs can be separated by newlines or commas
    - Supports up to 50 URLs per request
    
    **Example:**
    ```
    https://example.com
    https://news.com,https://blog.com
    ```
    
    **Advanced options:**
    - **analysis_depth**: Controls analysis detail level
    - **max_concurrent**: Number of simultaneous analyses
    - **custom_categories**: Focus on specific content categories
    """
    settings = get_settings()
    
    try:
        # Parse URLs from text input
        urls_text = urls_text.strip()
        if not urls_text:
            raise HTTPException(status_code=400, detail="No URLs provided")
        
        # Split by newlines first, then by commas
        lines = urls_text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        urls = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Check if line contains comma-separated URLs
                if ',' in line:
                    line_urls = [u.strip() for u in line.split(',') if u.strip()]
                    urls.extend(line_urls)
                else:
                    urls.append(line)
        
        # Remove duplicates while preserving order
        unique_urls = []
        seen = set()
        for url in urls:
            if url not in seen:
                unique_urls.append(url)
                seen.add(url)
        urls = unique_urls
        
        # Validate URL count
        if len(urls) == 0:
            raise HTTPException(status_code=400, detail="No valid URLs found")
        
        if len(urls) > settings.max_batch_size:
            raise HTTPException(
                status_code=400,
                detail=f"Too many URLs. Maximum: {settings.max_batch_size}, provided: {len(urls)}"
            )
        
        # Validate concurrent limit
        max_concurrent = max(1, min(max_concurrent, 10))
        
        # Parse custom categories
        custom_cats = None
        if custom_categories:
            custom_cats = [cat.strip() for cat in custom_categories.split(',') if cat.strip()]
        
        logger.info(f"Advanced upload analysis: {len(urls)} URLs, depth: {analysis_depth}, concurrent: {max_concurrent}")
        
        # Create analysis options
        options = {
            "include_sentiment": include_sentiment,
            "include_entities": include_entities,
            "include_summary": include_summary,
            "include_category": include_category,
            "include_keywords": include_keywords
        }
        
        # Perform batch analysis with custom options
        individual_results = await analyzer.batch_analyze_urls(
            urls,
            analysis_depth=analysis_depth,
            options=options,
            custom_categories=custom_cats,
            max_concurrent=max_concurrent
        )
        
        # Calculate statistics
        successful_results = [r for r in individual_results if r.status == "success"]
        failed_results = [r for r in individual_results if r.status != "success"]
        
        # Category distribution
        category_dist = {}
        for result in successful_results:
            cat = result.primary_category
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        # Average quality score
        quality_scores = [r.content_quality_score for r in successful_results if r.content_quality_score > 0]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Build batch result
        batch_result = BatchAnalysisResult(
            total_urls=len(urls),
            successful_analyses=len(successful_results),
            failed_analyses=len(failed_results),
            results=individual_results,
            errors=[{"url": r.url, "error": getattr(r, 'error', 'Unknown error')} for r in failed_results],
            category_distribution=category_dist,
            average_quality_score=avg_quality,
            processing_time_seconds=sum(r.processing_time_seconds for r in individual_results)
        )
        
        logger.info(f"Advanced analysis completed: {len(successful_results)}/{len(urls)} successful")
        return batch_result
        
    except Exception as e:
        logger.error(f"Error in advanced URL upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Advanced analysis failed: {str(e)}"
        )

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Check the health status of the content analysis service"
)
async def health_check():
    """
    Health check endpoint to verify service status.
    
    Returns service status, version, and timestamp.
    """
    return HealthResponse(
        status="healthy",
        service="web-content-analysis-agent",
        version="1.0.0"
    )

@router.get(
    "/categories",
    summary="Get available categories",
    description="Get list of available content categories for analysis"
)
async def get_categories():
    """
    Get the list of available content categories.
    
    Returns common content categories that the AI can classify content into.
    Note: The AI can generate any appropriate category - this list shows common examples.
    """
    
    # Common categories as examples - AI can generate any appropriate category
    common_categories = [
        "news", "sports", "blog", "ecommerce", "educational", "entertainment", 
        "business", "technology", "health", "travel", "lifestyle", "politics", 
        "science", "finance", "satire", "humor", "opinion", "review", 
        "social_media", "documentation", "forum", "portfolio", "landing_page", "other"
    ]
    
    categories = [
        {
            "value": category,
            "name": category.replace("_", " ").title(),
            "description": _get_category_description(category)
        }
        for category in common_categories
    ]
    
    return {
        "categories": categories,
        "total": len(categories),
        "note": "AI can generate any appropriate category beyond these common examples"
    }

def _get_category_description(category: str) -> str:
    """Get description for content category."""
    descriptions = {
        "news": "News articles, journalism, current events, and press releases",
        "blog": "Personal blogs, opinion pieces, and informal articles",
        "ecommerce": "Online stores, product pages, shopping sites, and marketplaces",
        "educational": "Educational content, tutorials, courses, and learning materials",
        "entertainment": "Entertainment content, media, games, and leisure activities",
        "business": "Corporate websites, professional services, and business information",
        "technology": "Technical content, software, hardware, and tech industry news",
        "social_media": "Social networking platforms and user-generated content",
        "documentation": "Technical documentation, manuals, and reference materials",
        "forum": "Discussion forums, Q&A sites, and community platforms",
        "portfolio": "Personal or professional portfolios and showcase websites",
        "landing_page": "Marketing landing pages and promotional content",
        "other": "Content that doesn't fit into standard categories"
    }
    return descriptions.get(category, "No description available")

# Error handlers are defined in main.py for the FastAPI app
# Router-level exception handlers are not supported


@router.get("/bulk-upload", response_class=FileResponse)
async def get_bulk_upload_interface():
    """
    Serve the bulk upload HTML interface.
    """
    # Get the path to the HTML file
    html_path = Path(__file__).parent.parent.parent / "bulk_upload_interface.html"
    
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Upload interface not found")
    
    return FileResponse(
        path=str(html_path),
        media_type="text/html",
        filename="bulk_upload_interface.html"
    )