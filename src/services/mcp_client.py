"""
MCP (Model Context Protocol) client for fetching web content using the Fetch server.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
import aiohttp
import json
from urllib.parse import urlparse
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class MCPFetchClient:
    """Client for MCP Fetch server to retrieve web content."""
    
    def __init__(self):
        self.settings = get_settings()
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.settings.analysis_timeout)
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_content(self, url: str) -> Dict[str, Any]:
        """
        Fetch web page content using MCP Fetch server.
        
        Args:
            url: The URL to fetch content from
            
        Returns:
            Dictionary containing content, metadata, and status
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f"Invalid URL format: {url}")
            
            # If MCP server is configured, use it
            if self.settings.mcp_server_url:
                return await self._fetch_via_mcp_server(url)
            else:
                # Fallback to direct HTTP fetch
                return await self._fetch_direct(url)
                
        except Exception as e:
            logger.error(f"Error fetching content from {url}: {str(e)}")
            raise
    
    async def _fetch_via_mcp_server(self, url: str) -> Dict[str, Any]:
        """Fetch content via MCP Fetch server."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        try:
            # MCP Fetch server request format
            mcp_request = {
                "method": "fetch",
                "params": {
                    "url": url,
                    "options": {
                        "include_raw_content": True,
                        "include_metadata": True,
                        "follow_redirects": True,
                        "user_agent": "Web-Content-Analysis-Agent/1.0"
                    }
                }
            }
            
            async with self.session.post(
                self.settings.mcp_server_url,
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    return self._process_mcp_response(result, url)
                else:
                    logger.warning(f"MCP server returned status {response.status}, falling back to direct fetch")
                    return await self._fetch_direct(url)
                    
        except Exception as e:
            logger.warning(f"MCP server fetch failed: {str(e)}, falling back to direct fetch")
            return await self._fetch_direct(url)
    
    async def _fetch_direct(self, url: str, retry_count: int = 0) -> Dict[str, Any]:
        """Direct HTTP fetch as fallback."""
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
            
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0"
        }
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    content = await response.text()
                    
                    # Extract basic metadata
                    metadata = {
                        "url": str(response.url),
                        "status_code": response.status,
                        "content_type": response.headers.get("content-type", ""),
                        "content_length": len(content),
                        "final_url": str(response.url),  # After redirects
                        "server": response.headers.get("server", ""),
                        "last_modified": response.headers.get("last-modified", "")
                    }
                    
                    return {
                        "content": content,
                        "metadata": metadata,
                        "status": "success",
                        "source": "direct_fetch"
                    }
                else:
                    # Handle retryable errors
                    if response.status == 429 and retry_count < 2:  # Rate limited
                        logger.warning(f"Rate limited for {url}, retrying in {2 ** retry_count} seconds...")
                        await asyncio.sleep(2 ** retry_count)
                        return await self._fetch_direct(url, retry_count + 1)
                    
                    # Create more informative error messages based on status code
                    error_msg = f"HTTP {response.status}"
                    if response.status == 403:
                        error_msg += ": Forbidden - Website blocked automated access"
                    elif response.status == 404:
                        error_msg += ": Not Found - URL does not exist"
                    elif response.status == 429:
                        error_msg += ": Too Many Requests - Rate limited"
                    elif response.status == 500:
                        error_msg += ": Server Error - Website experiencing issues"
                    elif response.status == 503:
                        error_msg += ": Service Unavailable - Website temporarily down"
                    else:
                        error_msg += f": {response.reason}"
                    
                    raise aiohttp.ClientError(error_msg)
                    
        except Exception as e:
            logger.error(f"Direct fetch failed for {url}: {str(e)}")
            return {
                "content": "",
                "metadata": {"url": url, "status_code": None, "error": str(e)},
                "status": "error",
                "source": "direct_fetch",
                "error": str(e)
            }
    
    def _process_mcp_response(self, mcp_result: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Process MCP server response."""
        try:
            if "result" in mcp_result and mcp_result["result"]:
                result_data = mcp_result["result"]
                
                return {
                    "content": result_data.get("content", ""),
                    "metadata": {
                        "url": url,
                        "title": result_data.get("title", ""),
                        "description": result_data.get("description", ""),
                        "content_type": result_data.get("content_type", ""),
                        "content_length": len(result_data.get("content", "")),
                        "status_code": result_data.get("status_code"),
                        "final_url": result_data.get("final_url", url),
                        "mcp_metadata": result_data.get("metadata", {})
                    },
                    "status": "success",
                    "source": "mcp_server"
                }
            else:
                error_msg = mcp_result.get("error", {}).get("message", "Unknown MCP error")
                raise Exception(f"MCP server error: {error_msg}")
                
        except Exception as e:
            logger.error(f"Error processing MCP response: {str(e)}")
            return {
                "content": "",
                "metadata": {"url": url, "error": str(e)},
                "status": "error",
                "source": "mcp_server",
                "error": str(e)
            }
    
    async def batch_fetch_content(self, urls: list[str]) -> list[Dict[str, Any]]:
        """
        Fetch content from multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            
        Returns:
            List of fetch results
        """
        tasks = [self.fetch_content(url) for url in urls]
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching URL {urls[i]}: {str(result)}")
                    processed_results.append({
                        "content": "",
                        "metadata": {"url": urls[i], "error": str(result)},
                        "status": "error",
                        "source": "batch_fetch",
                        "error": str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch fetch: {str(e)}")
            raise