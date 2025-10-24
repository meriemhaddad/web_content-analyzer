"""
Pydantic models for API requests.
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class URLAnalysisRequest(BaseModel):
    """Request model for single URL analysis."""
    
    url: HttpUrl = Field(..., description="The URL to analyze")
    analysis_depth: str = Field(
        default="comprehensive",
        description="Analysis depth: 'basic', 'detailed', or 'comprehensive'"
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include page metadata in analysis"
    )
    custom_categories: Optional[List[str]] = Field(
        default=None,
        description="Custom categories to focus analysis on"
    )

class BatchAnalysisRequest(BaseModel):
    """Request model for batch URL analysis."""
    
    urls: List[HttpUrl] = Field(..., description="List of URLs to analyze", max_length=10)
    analysis_depth: str = Field(
        default="comprehensive",
        description="Analysis depth: 'basic', 'detailed', or 'comprehensive'"
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include page metadata in analysis"
    )
    custom_categories: Optional[List[str]] = Field(
        default=None,
        description="Custom categories to focus analysis on"
    )
    parallel_processing: bool = Field(
        default=True,
        description="Whether to process URLs in parallel"
    )