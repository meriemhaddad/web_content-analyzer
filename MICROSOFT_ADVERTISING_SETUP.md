# Microsoft Advertising Discovery API - Environment Setup

## Required Environment Variables

Add these to your `.env` file for Microsoft Advertising URL discovery:

```bash
# Existing variables
AZURE_OPENAI_ENDPOINT=https://doclin.openai.azure.com/
AZURE_OPENAI_API_KEY=your_existing_key

# New Microsoft Advertising Discovery variables
BING_SEARCH_API_KEY=your_bing_search_api_key
BING_CUSTOM_SEARCH_ID=your_custom_search_id (optional)

# Azure Content Moderator (optional - for enhanced brand safety)
AZURE_CONTENT_MODERATOR_ENDPOINT=https://your-region.api.cognitive.microsoft.com/
AZURE_CONTENT_MODERATOR_KEY=your_content_moderator_key
```

## How to Get Microsoft API Keys

### 1. Bing Search API Key
1. Go to [Azure Portal](https://portal.azure.com)
2. Create a new "Bing Search v7" resource
3. Get the API key from "Keys and Endpoint"
4. **Cost**: $4 per 1,000 queries (first 1,000 free monthly)

### 2. Bing Custom Search (Optional)
1. Go to [Bing Custom Search](https://customsearch.ai)
2. Create a custom search instance
3. Configure for advertising-safe domains
4. Get the Custom Search ID

### 3. Azure Content Moderator (Optional)
1. In Azure Portal, create "Content Moderator" resource
2. Get endpoint and key for enhanced brand safety
3. **Cost**: $1 per 1,000 text moderation calls

## New API Endpoints

Once configured, you'll have these new endpoints:

### URL Discovery
- `POST /api/v1/discovery/discover` - Discover URLs with Bing Search
- `POST /api/v1/discovery/discover-by-category` - Discover by advertising categories

### Eligibility Analysis  
- `POST /api/v1/discovery/analyze-eligibility` - Analyze single URL for Microsoft Advertising
- `POST /api/v1/discovery/batch-analyze-eligibility` - Batch analyze multiple URLs

### Utilities
- `GET /api/v1/discovery/trending-topics` - Get trending topics for campaigns
- `GET /api/v1/discovery/compliance-categories` - Get Microsoft Advertising categories

## Testing the New Features

1. **Start your server**: `python -m uvicorn src.main:app --reload`
2. **Visit**: `http://127.0.0.1:8000/docs` to see the new endpoints
3. **Test discovery without API key** (will show endpoint structure)
4. **Add Bing API key** to `.env` for full functionality

## Example Usage

```python
# Discover technology URLs for advertising
curl -X POST "http://127.0.0.1:8000/api/v1/discovery/discover" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "enterprise software solutions",
    "count": 10,
    "category_filter": "technology",
    "analyze_immediately": true
  }'

# Analyze URL for Microsoft Advertising eligibility
curl -X POST "http://127.0.0.1:8000/api/v1/discovery/analyze-eligibility" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/business-article"
  }'
```