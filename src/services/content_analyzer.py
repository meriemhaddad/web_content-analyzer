"""
Content analysis engine that orchestrates web content fetching and AI analysis.
"""

import asyncio
import logging
import time
import json
import os
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

# Directory for checkpoint files
CHECKPOINT_DIR = "batch_checkpoints"

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
        custom_categories: Optional[List[str]] = None,
        model_selection: str = "auto"
    ) -> ContentAnalysisResult:
        """
        Perform complete analysis of a single URL.
        
        Args:
            url: URL to analyze
            analysis_depth: Depth of analysis
            include_metadata: Whether to include metadata analysis
            custom_categories: Custom categories to focus on
            model_selection: Model to use - 'auto', 'gpt-4o-mini', or 'gpt-4o'
            
        Returns:
            Complete analysis result
        """
        start_time = time.time()
        
        try:
            # Normalize URL - add https:// if missing
            url = self._normalize_url(url)
            
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
                custom_categories=custom_categories,
                model_selection=model_selection
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
    
    def _normalize_url(self, url: str) -> str:
        """
        Normalize URL by adding https:// if no scheme is present.
        
        Args:
            url: URL string to normalize
            
        Returns:
            Normalized URL with scheme
        """
        url = url.strip()
        
        # Check if URL has a scheme (http:// or https://)
        if not url.startswith(('http://', 'https://')):
            # Add https:// by default
            url = f'https://{url}'
            logger.info(f"Added https:// scheme to URL: {url}")
        
        return url
    
    async def batch_analyze_urls(
        self,
        urls: List[str],
        analysis_depth: str = "comprehensive",
        include_metadata: bool = True,
        custom_categories: Optional[List[str]] = None,
        parallel_processing: bool = True,
        options: Optional[Dict[str, Any]] = None,
        max_concurrent: int = None,  # Use settings default if not specified
        batch_size: int = 1000  # Process URLs in batches of this size
    ) -> List[ContentAnalysisResult]:
        """
        Analyze multiple URLs with smart batch processing.
        
        URLs are processed in batches (default 1000) with concurrency control.
        After each batch, results are logged and errors are tracked.
        This reduces overhead and provides better visibility into progress.
        
        Args:
            urls: List of URLs to analyze
            analysis_depth: Depth of analysis
            include_metadata: Whether to include metadata analysis
            custom_categories: Custom categories to focus on
            parallel_processing: Whether to process in parallel
            options: Analysis options dictionary (can include model_selection)
            max_concurrent: Maximum concurrent analyses (default: from settings)
            batch_size: Number of URLs per batch (default: 1000)
            
        Returns:
            List of analysis results
        """
        # Use settings default if not specified
        if max_concurrent is None:
            max_concurrent = self.settings.max_concurrent_requests
        
        # Extract model_selection from options
        model_selection = options.get("model_selection", "auto") if options else "auto"
        
        total_urls = len(urls)
        all_results = []
        total_success = 0
        total_errors = 0
        total_blocked = 0
        
        # Calculate number of batches
        num_batches = (total_urls + batch_size - 1) // batch_size
        
        logger.info(f"🚀 Starting batch processing: {total_urls} URLs in {num_batches} batch(es) of up to {batch_size}")
        logger.info(f"   Settings: max_concurrent={max_concurrent}, analysis_depth={analysis_depth}, model={model_selection}")
        
        overall_start_time = time.time()
        
        for batch_num in range(num_batches):
            batch_start = batch_num * batch_size
            batch_end = min(batch_start + batch_size, total_urls)
            batch_urls = urls[batch_start:batch_end]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"📦 BATCH {batch_num + 1}/{num_batches}: Processing URLs {batch_start + 1}-{batch_end} of {total_urls}")
            logger.info(f"{'='*60}")
            
            batch_start_time = time.time()
            
            if parallel_processing:
                batch_results = await self._process_batch_parallel(
                    batch_urls, analysis_depth, include_metadata, 
                    custom_categories, model_selection, max_concurrent
                )
            else:
                batch_results = await self._process_batch_sequential(
                    batch_urls, analysis_depth, include_metadata, custom_categories
                )
            
            batch_time = time.time() - batch_start_time
            
            # Analyze batch results
            batch_success = sum(1 for r in batch_results if r.status == "success")
            batch_errors = sum(1 for r in batch_results if r.status == "error")
            batch_blocked = sum(1 for r in batch_results if "blocked" in r.content_summary.lower() or "403" in r.content_summary)
            
            total_success += batch_success
            total_errors += batch_errors
            total_blocked += batch_blocked
            
            # Log batch summary
            logger.info(f"\n📊 BATCH {batch_num + 1} COMPLETE:")
            logger.info(f"   ✅ Success: {batch_success}/{len(batch_urls)}")
            logger.info(f"   ❌ Errors: {batch_errors}")
            logger.info(f"   🚫 Blocked: {batch_blocked}")
            logger.info(f"   ⏱️  Time: {batch_time:.2f}s ({batch_time/len(batch_urls):.2f}s per URL)")
            
        # Log any errors in this batch
            if batch_errors > 0:
                error_urls = [r.url for r in batch_results if r.status == "error"][:5]
                logger.warning(f"   Failed URLs (first 5): {error_urls}")
            
            all_results.extend(batch_results)
            
            # Save checkpoint after each batch
            await self._save_batch_checkpoint(
                batch_num + 1,
                batch_results,
                all_results,
                total_success,
                total_errors,
                total_blocked,
                time.time() - overall_start_time
            )
            
            # Brief pause between batches to avoid rate limits
            if batch_num < num_batches - 1:
                logger.info(f"   ⏸️  Pausing 2s before next batch...")
                await asyncio.sleep(2)
        
        # Final summary
        total_time = time.time() - overall_start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"🏁 BATCH PROCESSING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"   📈 Total URLs: {total_urls}")
        logger.info(f"   ✅ Successful: {total_success} ({100*total_success/total_urls:.1f}%)")
        logger.info(f"   ❌ Errors: {total_errors} ({100*total_errors/total_urls:.1f}%)")
        logger.info(f"   🚫 Blocked: {total_blocked}")
        logger.info(f"   ⏱️  Total time: {total_time:.2f}s")
        logger.info(f"   📊 Avg per URL: {total_time/total_urls:.2f}s")
        
        return all_results
    
    async def _save_batch_checkpoint(
        self,
        batch_num: int,
        batch_results: List[ContentAnalysisResult],
        all_results: List[ContentAnalysisResult],
        total_success: int,
        total_errors: int,
        total_blocked: int,
        elapsed_time: float
    ):
        """Save checkpoint after each batch for recovery if interrupted."""
        try:
            # Create checkpoint directory if it doesn't exist
            os.makedirs(CHECKPOINT_DIR, exist_ok=True)
            
            # Generate timestamp for this run
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save cumulative results to checkpoint file
            checkpoint_file = os.path.join(CHECKPOINT_DIR, f"checkpoint_batch_{batch_num}_{timestamp}.json")
            
            # Convert results to serializable format
            serializable_results = []
            for r in all_results:
                result_dict = {
                    "url": r.url,
                    "status": r.status,
                    "primary_category": r.primary_category,
                    "content_summary": r.content_summary,
                    "content_quality_score": r.content_quality_score,
                    "processing_time_seconds": r.processing_time_seconds,
                    "category_confidence": r.category_confidence,
                    "key_insights": r.key_insights,
                    "token_usage": r.token_usage if isinstance(r.token_usage, dict) else None
                }
                # Add sentiment if available
                if r.sentiment:
                    result_dict["sentiment"] = {
                        "overall": r.sentiment.overall,
                        "confidence": r.sentiment.confidence
                    }
                serializable_results.append(result_dict)
            
            checkpoint_data = {
                "batch_num": batch_num,
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "total_processed": len(all_results),
                    "successful": total_success,
                    "errors": total_errors,
                    "blocked": total_blocked,
                    "elapsed_time_seconds": round(elapsed_time, 2)
                },
                "results": serializable_results
            }
            
            with open(checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"   💾 Checkpoint saved: {checkpoint_file} ({len(all_results)} results)")
            
            # Also save a "latest" file that gets overwritten each batch
            latest_file = os.path.join(CHECKPOINT_DIR, "latest_checkpoint.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"   ⚠️ Failed to save checkpoint: {e}")
    
    async def _process_batch_parallel(
        self,
        urls: List[str],
        analysis_depth: str,
        include_metadata: bool,
        custom_categories: Optional[List[str]],
        model_selection: str,
        max_concurrent: int
    ) -> List[ContentAnalysisResult]:
        """Process a batch of URLs in parallel with concurrency control."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(url):
            async with semaphore:
                return await self.analyze_url(url, analysis_depth, include_metadata, custom_categories, model_selection)
        
        tasks = [analyze_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_msg = str(result)
                logger.error(f"Error analyzing {urls[i]}: {error_msg}")
                error_result = ContentAnalysisResult(
                    url=urls[i],
                    status="error",
                    primary_category="other",
                    content_summary=f"Analysis failed: {error_msg}",
                    semantic_analysis=SemanticAnalysis(),
                    sentiment=SentimentScore(overall="neutral", confidence=0.0),
                    metadata=ContentMetadata(),
                    content_quality_score=0.0,
                    processing_time_seconds=0.0,
                    category_confidence=0.0,
                    key_insights=[f"Error: {error_msg}"]
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _process_batch_sequential(
        self,
        urls: List[str],
        analysis_depth: str,
        include_metadata: bool,
        custom_categories: Optional[List[str]]
    ) -> List[ContentAnalysisResult]:
        """Process a batch of URLs sequentially."""
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
                processing_time_seconds=processing_time,
                token_usage=ai_analysis.get("_token_usage")  # Extract token usage for cost tracking
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