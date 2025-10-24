"""
Tests for service modules.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.mcp_client import MCPFetchClient
from src.services.content_analyzer import ContentAnalysisEngine

class TestMCPFetchClient:
    """Test MCP Fetch Client."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_initialization(self):
        """Test MCP client can be initialized."""
        async with MCPFetchClient() as client:
            assert client is not None
            assert client.session is not None
    
    @pytest.mark.asyncio
    async def test_fetch_content_invalid_url(self):
        """Test fetch content with invalid URL."""
        async with MCPFetchClient() as client:
            with pytest.raises(ValueError, match="Invalid URL format"):
                await client.fetch_content("not-a-valid-url")
    
    @pytest.mark.asyncio
    @patch('aiohttp.ClientSession.get')
    async def test_fetch_content_direct(self, mock_get):
        """Test direct content fetching."""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html><body>Test content</body></html>"
        mock_response.url = "https://example.com"
        mock_response.headers = {"content-type": "text/html"}
        mock_get.return_value.__aenter__.return_value = mock_response
        
        async with MCPFetchClient() as client:
            # Force direct fetch by not setting MCP server URL
            client.settings.mcp_server_url = None
            result = await client.fetch_content("https://example.com")
            
            assert result["status"] == "success"
            assert result["source"] == "direct_fetch"
            assert "content" in result

class TestContentAnalysisEngine:
    """Test Content Analysis Engine."""
    
    def test_engine_initialization(self):
        """Test engine can be initialized."""
        engine = ContentAnalysisEngine()
        assert engine is not None
        assert engine.openai_service is not None
    
    def test_extract_text_content(self):
        """Test text content extraction from HTML."""
        engine = ContentAnalysisEngine()
        html = """
        <html>
            <head><title>Test Page</title></head>
            <body>
                <nav>Navigation</nav>
                <main>
                    <h1>Main Heading</h1>
                    <p>This is the main content.</p>
                    <script>console.log('script');</script>
                </main>
                <footer>Footer content</footer>
            </body>
        </html>
        """
        
        text = engine._extract_text_content(html)
        assert "Main Heading" in text
        assert "This is the main content." in text
        assert "console.log" not in text  # Scripts should be removed
        assert "Navigation" not in text  # Nav should be removed
        assert "Footer content" not in text  # Footer should be removed
    
    def test_extract_metadata(self):
        """Test metadata extraction from HTML."""
        engine = ContentAnalysisEngine()
        html = """
        <html lang="en">
            <head>
                <title>Test Page Title</title>
                <meta name="description" content="This is a test description">
                <meta name="keywords" content="test, metadata, extraction">
                <meta name="author" content="Test Author">
            </head>
            <body>
                <p>Some content here.</p>
            </body>
        </html>
        """
        
        metadata = engine._extract_metadata(html, {})
        assert metadata.title == "Test Page Title"
        assert metadata.description == "This is a test description"
        assert "test" in metadata.keywords
        assert metadata.author == "Test Author"
        assert metadata.language == "en"
        assert metadata.word_count > 0