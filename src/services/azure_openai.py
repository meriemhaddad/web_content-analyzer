"""
Azure OpenAI service for content analysis using GPT-4o.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import os
from openai import AsyncAzureOpenAI
from azure.identity import DefaultAzureCredential, ChainedTokenCredential, AzureCliCredential, ManagedIdentityCredential
from azure.core.credentials import TokenCredential
from src.config.settings import get_settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for interacting with Azure OpenAI GPT-4o."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = self._create_azure_openai_client()
    
    def _create_azure_openai_client(self) -> AsyncAzureOpenAI:
        """Create Azure OpenAI client with appropriate authentication."""
        endpoint = self.settings.get_azure_openai_endpoint()
        
        if not endpoint:
            raise ValueError(
                "Azure OpenAI endpoint must be provided via AZURE_OPENAI_ENDPOINT environment variable "
                "or configuration. Example: https://your-resource-name.openai.azure.com/"
            )
        
        # Try to get API key from various sources
        api_key = (
            self.settings.azure_openai_api_key or
            os.getenv("AZURE_OPENAI_API_KEY") or
            os.getenv("OPENAI_API_KEY")
        )
        
        if api_key:
            logger.info("Using API key authentication for Azure OpenAI")
            return AsyncAzureOpenAI(
                api_key=api_key,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=endpoint
            )
        elif self.settings.should_use_azure_credentials():
            logger.info("Using Azure credential chain for authentication")
            # Create credential chain for different authentication methods
            credentials = []
            
            if self.settings.use_managed_identity:
                credentials.append(ManagedIdentityCredential())
                
            if self.settings.use_azure_cli:
                credentials.append(AzureCliCredential())
            
            # Add default credential as fallback
            credentials.append(DefaultAzureCredential())
            
            credential = ChainedTokenCredential(*credentials)
            
            return AsyncAzureOpenAI(
                azure_ad_token_provider=self._get_token_provider(credential),
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=endpoint
            )
        else:
            raise ValueError(
                "No valid authentication method found. Please provide either:\n"
                "1. AZURE_OPENAI_API_KEY environment variable, or\n"
                "2. Ensure Azure CLI is logged in (az login), or\n"
                "3. Use Managed Identity in Azure environment"
            )
    
    def _get_token_provider(self, credential: TokenCredential):
        """Create token provider for Azure AD authentication."""
        def token_provider():
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            return token.token
        return token_provider
        
    async def analyze_content(
        self,
        content: str,
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        analysis_depth: str = "comprehensive",
        custom_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze content using GPT-4o for advanced semantic analysis.
        
        Args:
            content: The web page content to analyze
            url: The source URL
            metadata: Optional page metadata
            analysis_depth: Analysis depth level
            custom_categories: Custom categories to focus on
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Build the analysis prompt
            prompt = self._build_analysis_prompt(
                content, url, metadata, analysis_depth, custom_categories
            )
            
            # Call GPT-4o for analysis
            response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            analysis_result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Successfully analyzed content for URL: {url}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing content for URL {url}: {str(e)}")
            raise
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for content analysis."""
        
        return f"""
        You are an expert content analyst specializing in semantic analysis and categorization of web content. 
        Your task is to provide comprehensive, accurate, and structured analysis of web page content.
        
        Always respond with valid JSON following this exact structure:
        {{
            "primary_category": "category_name",
            "secondary_categories": ["category1", "category2"],
            "category_confidence": 0.95,
            "content_summary": "Brief summary of the content",
            "key_insights": ["insight1", "insight2", "insight3"],
            "semantic_analysis": {{
                "main_topics": ["topic1", "topic2"],
                "entities": [{{"name": "entity", "type": "PERSON|ORG|LOCATION|etc", "relevance": 0.8}}],
                "themes": ["theme1", "theme2"],
                "content_structure": {{"headers": 5, "paragraphs": 12, "links": 8}},
                "semantic_keywords": ["keyword1", "keyword2"]
            }},
            "sentiment": {{
                "overall": "positive|negative|neutral",
                "confidence": 0.85,
                "emotions": {{"joy": 0.3, "trust": 0.4, "fear": 0.1}}
            }},
            "content_quality_score": 0.88,
            "readability_score": 0.75
        }}
        
        For categorization, create appropriate category names based on the content. Use clear, descriptive categories like:
        "news", "sports", "technology", "business", "entertainment", "education", "health", "travel", 
        "politics", "science", "finance", "lifestyle", "blog", "ecommerce", "satire", "humor", "opinion", 
        "review", "documentation", "forum", "social_media", or any other relevant category that best describes the content.
        
        Be creative and accurate with categories - don't limit yourself to a predefined list.
        Use lowercase, single words or underscore-separated phrases (e.g., "social_media", "product_review").
        
        Provide deep semantic understanding, not just keyword matching.
        """
    
    def _build_analysis_prompt(
        self,
        content: str,
        url: str,
        metadata: Optional[Dict[str, Any]] = None,
        analysis_depth: str = "comprehensive",
        custom_categories: Optional[List[str]] = None
    ) -> str:
        """Build the analysis prompt for GPT-4o."""
        
        # Truncate content if too long
        max_content = self.settings.max_content_length
        if len(content) > max_content:
            content = content[:max_content] + "... [content truncated]"
        
        prompt_parts = [
            f"Analyze the following web page content from URL: {url}",
            f"Analysis depth required: {analysis_depth}",
        ]
        
        if metadata:
            prompt_parts.append(f"Page metadata: {json.dumps(metadata, indent=2)}")
        
        if custom_categories:
            prompt_parts.append(f"Focus on these custom categories: {', '.join(custom_categories)}")
        
        prompt_parts.extend([
            "Web page content:",
            "=" * 50,
            content,
            "=" * 50,
            "",
            "Provide a comprehensive semantic analysis including:",
            "1. Accurate categorization with confidence scores",
            "2. Deep content understanding and key insights",
            "3. Semantic analysis with topics, entities, and themes", 
            "4. Sentiment analysis with emotional nuances",
            "5. Content quality and readability assessment",
            "",
            "Focus on semantic meaning rather than surface-level keywords.",
            "Consider context, intent, and underlying themes.",
            "Provide actionable insights about the content's purpose and value."
        ])
        
        return "\n".join(prompt_parts)
    
    async def batch_analyze_content(
        self,
        content_list: List[Dict[str, Any]],
        analysis_depth: str = "comprehensive",
        custom_categories: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple pieces of content in parallel.
        
        Args:
            content_list: List of content dictionaries with 'content', 'url', and optional 'metadata'
            analysis_depth: Analysis depth level
            custom_categories: Custom categories to focus on
            
        Returns:
            List of analysis results
        """
        tasks = []
        for item in content_list:
            task = self.analyze_content(
                content=item['content'],
                url=item['url'],
                metadata=item.get('metadata'),
                analysis_depth=analysis_depth,
                custom_categories=custom_categories
            )
            tasks.append(task)
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and handle exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error analyzing content {i}: {str(result)}")
                    processed_results.append({
                        "error": str(result),
                        "url": content_list[i]['url']
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            raise