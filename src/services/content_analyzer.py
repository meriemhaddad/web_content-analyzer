"""
Content analysis engine that orchestrates web content fetching and AI analysis.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from bs4 import BeautifulSoup

from src.services.mcp_client import MCPFetchClient
from src.services.azure_openai import AzureOpenAIService
from src.models.responses import (
    ContentAnalysisResult, 
    SemanticAnalysis, 
    SentimentScore, 
    ContentMetadata
)
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class ContentAnalysisEngine:
    """Main engine for comprehensive web content analysis."""
    
    def __init__(self):
        self.settings = get_settings()
        self.openai_service = AzureOpenAIService()
        
    async def analyze_url(
        self,
        url: str,
        analysis_depth: str = "comprehensive",
        include_metadata: bool = True,
        custom_categories: Optional[List[str]] = None
    ) -> ContentAnalysisResult:
        """
        Perform complete analysis of a single URL.
        
        Args:
            url: URL to analyze
            analysis_depth: Depth of analysis
            include_metadata: Whether to include metadata analysis
            custom_categories: Custom categories to focus on
            
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        
        try:
            # Step 1: Fetch content using MCP client
            async with MCPFetchClient() as mcp_client:
                fetch_result = await mcp_client.fetch_content(url)
            
            if fetch_result["status"] == "error":
                raise Exception(f"Failed to fetch content: {fetch_result.get('error', 'Unknown error')}")
            
            # Step 2: Extract and clean content
            cleaned_content = self._extract_text_content(fetch_result["content"])
            
            # Step 3: Extract metadata if requested
            metadata = None
            if include_metadata:
                metadata = self._extract_metadata(
                    fetch_result["content"], 
                    fetch_result.get("metadata", {})
                )
            
            # Step 4: Perform AI analysis
            ai_analysis = await self.openai_service.analyze_content(
                content=cleaned_content,
                url=url,
                metadata=metadata.__dict__ if metadata else None,
                analysis_depth=analysis_depth,
                custom_categories=custom_categories
            )
            
            # Step 5: Build comprehensive result
            processing_time = time.time() - start_time
            
            result = self._build_analysis_result(
                url=url,
                ai_analysis=ai_analysis,
                metadata=metadata,
                processing_time=processing_time
            )
            
            logger.info(f"Successfully analyzed URL: {url} in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing URL {url}: {str(e)}")
            # Return error result
            return ContentAnalysisResult(
                url=url,
                status="error",
                primary_category="other",
                content_summary=f"Analysis failed: {str(e)}",
                semantic_analysis=SemanticAnalysis(),
                sentiment=SentimentScore(overall="neutral", confidence=0.0),
                metadata=ContentMetadata(),
                content_quality_score=0.0,
                processing_time_seconds=time.time() - start_time,
                category_confidence=0.0,
                key_insights=[f"Error: {str(e)}"]
            )
    
    async def batch_analyze_urls(
        self,
        urls: List[str],
        analysis_depth: str = "comprehensive",
        include_metadata: bool = True,
        custom_categories: Optional[List[str]] = None,
        parallel_processing: bool = True,
        options: Optional[Dict[str, Any]] = None,
        max_concurrent: int = 5
    ) -> List[ContentAnalysisResult]:
        """
        Analyze multiple URLs with optional parallel processing.
        
        Args:
            urls: List of URLs to analyze
            analysis_depth: Depth of analysis
            include_metadata: Whether to include metadata analysis
            custom_categories: Custom categories to focus on
            parallel_processing: Whether to process in parallel
            options: Analysis options dictionary
            max_concurrent: Maximum concurrent analyses
            
        Returns:
            List of analysis results
        """
        if parallel_processing:
            # Process URLs in parallel with concurrency limit
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def analyze_with_semaphore(url):
                async with semaphore:
                    return await self.analyze_url(url, analysis_depth, include_metadata, custom_categories)
            
            tasks = [analyze_with_semaphore(url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in batch analysis for URL {urls[i]}: {str(result)}")
                    # Create error result
                    error_result = ContentAnalysisResult(
                        url=urls[i],
                        status="error",
                        primary_category="other",
                        content_summary=f"Batch analysis failed: {str(result)}",
                        semantic_analysis=SemanticAnalysis(),
                        sentiment=SentimentScore(overall="neutral", confidence=0.0),
                        metadata=ContentMetadata(),
                        content_quality_score=0.0,
                        processing_time_seconds=0.0,
                        category_confidence=0.0,
                        key_insights=[f"Error: {str(result)}"]
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)
            
            return processed_results
        else:
            # Process URLs sequentially
            results = []
            for url in urls:
                result = await self.analyze_url(url, analysis_depth, include_metadata, custom_categories)
                results.append(result)
            
            return results
    
    def _extract_text_content(self, html_content: str) -> str:
        """Extract clean text content from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text from main content areas
            main_content = ""
            
            # Try to find main content area
            main_selectors = [
                "main", "article", "#content", ".content", 
                "#main", ".main", ".post-content", ".entry-content"
            ]
            
            for selector in main_selectors:
                main_element = soup.select_one(selector)
                if main_element:
                    main_content = main_element.get_text()
                    break
            
            # Fallback to body content
            if not main_content:
                body = soup.find("body")
                if body:
                    main_content = body.get_text()
                else:
                    main_content = soup.get_text()
            
            # Clean up text
            main_content = re.sub(r'\s+', ' ', main_content)  # Replace multiple whitespace
            main_content = main_content.strip()
            
            return main_content
            
        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return html_content  # Return raw content as fallback
    
    def _extract_metadata(self, html_content: str, fetch_metadata: Dict[str, Any]) -> ContentMetadata:
        """Extract metadata from HTML and fetch results."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract title
            title = None
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Extract description
            description = None
            desc_meta = soup.find("meta", attrs={"name": "description"}) or \
                       soup.find("meta", attrs={"property": "og:description"})
            if desc_meta:
                description = desc_meta.get("content", "").strip()
            
            # Extract keywords
            keywords = []
            keywords_meta = soup.find("meta", attrs={"name": "keywords"})
            if keywords_meta:
                keywords_content = keywords_meta.get("content", "")
                keywords = [k.strip() for k in keywords_content.split(",") if k.strip()]
            
            # Extract author
            author = None
            author_meta = soup.find("meta", attrs={"name": "author"}) or \
                        soup.find("meta", attrs={"property": "article:author"})
            if author_meta:
                author = author_meta.get("content", "").strip()
            
            # Extract language
            language = None
            html_tag = soup.find("html")
            if html_tag:
                language = html_tag.get("lang", "").strip()
            
            # Calculate word count and reading time
            text_content = self._extract_text_content(html_content)
            word_count = len(text_content.split()) if text_content else 0
            reading_time = max(1, round(word_count / 200))  # Assume 200 words per minute
            
            return ContentMetadata(
                title=title,
                description=description,
                keywords=keywords,
                author=author,
                language=language,
                word_count=word_count,
                reading_time_minutes=reading_time
            )
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return ContentMetadata()
    
    def _build_analysis_result(
        self,
        url: str,
        ai_analysis: Dict[str, Any],
        metadata: Optional[ContentMetadata],
        processing_time: float
    ) -> ContentAnalysisResult:
        """Build the final analysis result from AI analysis and metadata."""
        try:
            # Parse AI analysis results - now using dynamic categories
            primary_category = ai_analysis.get("primary_category", "other")
            secondary_categories = ai_analysis.get("secondary_categories", [])
            
            # Build semantic analysis
            semantic_data = ai_analysis.get("semantic_analysis", {})
            semantic_analysis = SemanticAnalysis(
                main_topics=semantic_data.get("main_topics", []),
                entities=semantic_data.get("entities", []),
                themes=semantic_data.get("themes", []),
                content_structure=semantic_data.get("content_structure", {}),
                semantic_keywords=semantic_data.get("semantic_keywords", [])
            )
            
            # Build sentiment analysis
            sentiment_data = ai_analysis.get("sentiment", {})
            sentiment = SentimentScore(
                overall=sentiment_data.get("overall", "neutral"),
                confidence=sentiment_data.get("confidence", 0.0),
                emotions=sentiment_data.get("emotions", {})
            )
            
            return ContentAnalysisResult(
                url=url,
                status="success",
                primary_category=primary_category,
                secondary_categories=secondary_categories,
                category_confidence=ai_analysis.get("category_confidence", 0.0),
                content_summary=ai_analysis.get("content_summary", ""),
                key_insights=ai_analysis.get("key_insights", []),
                semantic_analysis=semantic_analysis,
                sentiment=sentiment,
                metadata=metadata or ContentMetadata(),
                content_quality_score=ai_analysis.get("content_quality_score", 0.0),
                readability_score=ai_analysis.get("readability_score"),
                processing_time_seconds=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error building analysis result: {str(e)}")
            # Return a basic result in case of error
            return ContentAnalysisResult(
                url=url,
                status="partial_error",
                primary_category="other",
                content_summary="Analysis completed with errors",
                semantic_analysis=SemanticAnalysis(),
                sentiment=SentimentScore(overall="neutral", confidence=0.0),
                metadata=metadata or ContentMetadata(),
                content_quality_score=0.0,
                processing_time_seconds=processing_time,
                category_confidence=0.0,
                key_insights=[f"Processing error: {str(e)}"]
            )