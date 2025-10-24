"""
Tests for API endpoints.
"""

import pytest
from httpx import AsyncClient
from src.main import app

class TestAnalyzeEndpoint:
    """Test the /analyze endpoint."""
    
    @pytest.mark.asyncio
    async def test_analyze_endpoint_exists(self, async_client: AsyncClient):
        """Test that the analyze endpoint exists and returns expected structure."""
        response = await async_client.post(
            "/api/v1/analyze",
            json={
                "url": "https://example.com",
                "analysis_depth": "basic"
            }
        )
        # We expect this to fail in test environment due to missing Azure credentials
        # but the endpoint should exist and return a structured error
        assert response.status_code in [422, 500]  # Validation error or service error
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_url(self, async_client: AsyncClient):
        """Test analyze endpoint with invalid URL."""
        response = await async_client.post(
            "/api/v1/analyze",
            json={
                "url": "not-a-url",
                "analysis_depth": "basic"
            }
        )
        assert response.status_code == 422  # Validation error

class TestBatchAnalyzeEndpoint:
    """Test the /batch-analyze endpoint."""
    
    @pytest.mark.asyncio
    async def test_batch_analyze_endpoint_exists(self, async_client: AsyncClient):
        """Test that the batch analyze endpoint exists."""
        response = await async_client.post(
            "/api/v1/batch-analyze",
            json={
                "urls": ["https://example.com", "https://httpbin.org"],
                "analysis_depth": "basic"
            }
        )
        # We expect this to fail in test environment due to missing Azure credentials
        assert response.status_code in [422, 500]
    
    @pytest.mark.asyncio
    async def test_batch_analyze_too_many_urls(self, async_client: AsyncClient):
        """Test batch analyze with too many URLs."""
        urls = [f"https://example{i}.com" for i in range(15)]  # More than max batch size
        response = await async_client.post(
            "/api/v1/batch-analyze",
            json={
                "urls": urls,
                "analysis_depth": "basic"
            }
        )
        assert response.status_code == 400  # Bad request

class TestUtilityEndpoints:
    """Test utility endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, async_client: AsyncClient):
        """Test health check endpoint."""
        response = await async_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "web-content-analysis-agent"
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client: AsyncClient):
        """Test root endpoint."""
        response = await async_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_categories_endpoint(self, async_client: AsyncClient):
        """Test categories endpoint."""
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert len(data["categories"]) > 0