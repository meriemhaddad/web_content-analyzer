"""
Configuration settings for the Web Content Analysis Agent.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Environment settings
    environment: str = "development"  # development, staging, production
    env: str = "development"  # Alternative field name for Railway ENV variable
    
    # Server settings
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    
    # Azure OpenAI settings - will use Azure Default Credential if api_key not provided
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None  # Optional - will use DefaultAzureCredential if not provided
    azure_openai_api_version: str = "2024-02-01"
    azure_openai_deployment_name: str = "gpt-4o"
    
    # Azure authentication settings
    use_managed_identity: bool = False  # Set to True for Azure Managed Identity
    use_azure_cli: bool = True  # Use Azure CLI credentials by default
    
    # MCP Fetch server settings
    mcp_server_url: Optional[str] = None
    
    # Content analysis settings
    max_content_length: int = 50000  # Maximum content length to analyze
    analysis_timeout: int = 30  # Timeout in seconds for analysis
    
    # Batch processing settings
    max_batch_size: int = 10
    batch_timeout: int = 300  # 5 minutes
    
    class Config:
        # Load from environment variables for security compliance
        env_file = None  # Don't load .env file automatically
        case_sensitive = False
        
    def get_azure_openai_endpoint(self) -> str:
        """Get Azure OpenAI endpoint from environment or settings."""
        return (
            self.azure_openai_endpoint or 
            os.getenv("AZURE_OPENAI_ENDPOINT") or
            os.getenv("OPENAI_API_BASE") or
            ""
        )
    
    def should_use_azure_credentials(self) -> bool:
        """Determine if we should use Azure credential providers."""
        return (
            self.azure_openai_api_key is None and 
            not os.getenv("AZURE_OPENAI_API_KEY") and
            not os.getenv("OPENAI_API_KEY")
        )

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()