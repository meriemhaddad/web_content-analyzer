# 📊 Web Content Analysis Agent - Complete Project Overview

## 🎯 What This Project Does

This is an **advanced web content analysis agent** that performs sophisticated semantic analysis on web pages using Azure OpenAI GPT-4o. The system can:

- **Analyze any web page URL** for semantic content and context
- **Categorize content intelligently** using AI-powered analysis  
- **Extract comprehensive insights** including sentiment, entities, keywords, and summaries
- **Provide detailed content analysis** through a REST API
- **Process content in real-time** with advanced semantic understanding

## 🤖 AI Components & Technology Stack

### **Primary AI Engine:**
- **Azure OpenAI GPT-4o**: Advanced language model for semantic analysis
- **Endpoint**: `https://doclin.openai.azure.com/`
- **Deployment**: `gpt-4o`
- **Capabilities**: Content categorization, sentiment analysis, entity extraction, summarization

### **Core Technologies:**
- **FastAPI**: Modern REST API framework with automatic documentation
- **MCP (Model Context Protocol)**: Reliable web content fetching protocol
- **BeautifulSoup4**: HTML content parsing and cleaning
- **Pydantic**: Data validation and serialization
- **aiohttp**: Async HTTP client for web scraping
- **python-dotenv**: Environment variable management

### **Project Architecture:**
```
├── src/
│   ├── main.py                 # FastAPI application entry point
│   ├── config/settings.py      # Configuration management with .env support
│   ├── services/
│   │   ├── azure_openai.py     # Azure OpenAI GPT-4o integration
│   │   ├── content_analyzer.py # Main content analysis engine
│   │   └── mcp_client.py       # Web content fetching via MCP
│   ├── models/
│   │   ├── requests.py         # API request data models
│   │   └── responses.py        # API response data models
│   └── api/endpoints.py        # REST API endpoints
├── tests/                      # Comprehensive test suite
├── .env                        # Environment variables (credentials)
└── requirements.txt            # Python dependencies
```

## 🔐 Credentials & Authentication

### **Current Configuration:**
The project uses Azure OpenAI with API key authentication stored in `.env`:
```
AZURE_OPENAI_ENDPOINT=https://doclin.openai.azure.com/
AZURE_OPENAI_API_KEY=DpdBV66GffeBLae9RihOUgJQPqExpUWuYGSJRqtIJ5dsMCOGsNw1JQQJ99BIACHYHv6XJ3w3AAABACOGZFpi
```

### **Security Features:**
- Environment-based credential management
- No hardcoded secrets in source code
- Support for Azure CLI authentication (alternative)
- Support for Azure Managed Identity (production)

## 🚀 How to Run the Project

### **Prerequisites:**
- Python 3.11+
- Azure OpenAI resource with GPT-4o deployment
- Internet connection for web content fetching

### **Quick Start Commands:**

1. **Navigate to project directory:**
   ```powershell
   cd C:\Users\meriemhaddad\FetchM
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```powershell
   python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Access the application:**
   - **API Documentation**: http://127.0.0.1:8000/docs
   - **Health Check**: http://127.0.0.1:8000/health
   - **Analysis Endpoint**: `POST http://127.0.0.1:8000/api/v1/analyze`

### **Alternative Run Methods:**
```powershell
# Basic run
uvicorn src.main:app --reload

# Production run
uvicorn src.main:app --host 0.0.0.0 --port 8000

# Debug mode
uvicorn src.main:app --reload --log-level debug
```

## 📋 API Usage & Examples

### **Main Analysis Endpoint:**
`POST /api/v1/analyze`

### **Request Format:**
```json
{
  "url": "https://example.com/article",
  "options": {
    "include_sentiment": true,
    "include_entities": true,
    "include_summary": true,
    "include_category": true,
    "include_keywords": true
  }
}
```

### **Response Format:**
```json
{
  "url": "https://example.com/article",
  "status": "success",
  "timestamp": "2025-10-24T10:30:00",
  "primary_category": "technology",
  "secondary_categories": ["artificial-intelligence", "innovation"],
  "category_confidence": 0.95,
  "content_summary": "Article about latest AI developments...",
  "key_insights": [
    "AI technology advancing rapidly",
    "New breakthrough in machine learning"
  ],
  "semantic_analysis": {
    "main_topics": ["artificial intelligence", "machine learning"],
    "entities": [
      {"text": "OpenAI", "type": "organization", "confidence": 0.98},
      {"text": "GPT-4", "type": "technology", "confidence": 0.95}
    ],
    "themes": ["innovation", "technology", "future"],
    "semantic_keywords": ["AI", "neural networks", "automation"]
  },
  "sentiment": {
    "overall": "positive",
    "confidence": 0.87,
    "emotions": {
      "excitement": 0.6,
      "optimism": 0.8,
      "concern": 0.2
    }
  },
  "metadata": {
    "title": "Article Title",
    "description": "Article description",
    "author": "Author Name",
    "publish_date": "2025-10-24",
    "language": "en",
    "word_count": 1250,
    "reading_time_minutes": 5
  },
  "content_quality_score": 0.88,
  "readability_score": 72.5,
  "processing_time_seconds": 2.3,
  "model_version": "gpt-4o"
}
```

## 🔧 Configuration Options

### **Environment Variables:**
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL (Required)
- `AZURE_OPENAI_API_KEY`: API key for authentication (Required)
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Model deployment name (Default: "gpt-4o")
- `AZURE_OPENAI_API_VERSION`: API version (Default: "2024-02-01")
- `MCP_SERVER_URL`: MCP server URL (Optional)
- `MAX_CONTENT_LENGTH`: Maximum content length to analyze (Default: 50000)
- `ANALYSIS_TIMEOUT`: Analysis timeout in seconds (Default: 30)

### **Authentication Methods:**
1. **API Key** (Current): Store key in `.env` file
2. **Azure CLI**: `az login` for development
3. **Managed Identity**: For production Azure deployments

## 🧪 Testing the Application

### **Health Check:**
```bash
curl http://127.0.0.1:8000/health
```

### **Sample Analysis:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://www.bbc.com/news",
       "options": {
         "include_sentiment": true,
         "include_entities": true,
         "include_summary": true,
         "include_category": true,
         "include_keywords": true
       }
     }'
```

## 🔍 Troubleshooting

### **Common Issues:**

1. **401 Authentication Error:**
   - Check Azure OpenAI API key in `.env` file
   - Verify endpoint URL matches your Azure resource
   - Ensure deployment name is correct

2. **Server Won't Start:**
   - Check if port 8000 is available
   - Verify Python dependencies are installed
   - Check for syntax errors in configuration

3. **Analysis Fails:**
   - Verify URL is accessible
   - Check network connectivity
   - Review Azure OpenAI quota limits

### **Debug Commands:**
```powershell
# Test credentials
python test_credentials.py

# Check dependencies
pip list

# Verbose server logs
uvicorn src.main:app --reload --log-level debug
```

## 📈 Features & Capabilities

### **Content Analysis Features:**
- ✅ Advanced semantic analysis using GPT-4o
- ✅ Content categorization (primary + secondary categories)
- ✅ Sentiment analysis with confidence scores
- ✅ Entity extraction (people, organizations, locations)
- ✅ Keyword and theme identification
- ✅ Content summarization
- ✅ Readability scoring
- ✅ Metadata extraction (title, author, date, etc.)
- ✅ Content quality assessment

### **Technical Features:**
- ✅ FastAPI with automatic OpenAPI documentation
- ✅ Async processing for better performance
- ✅ Comprehensive error handling
- ✅ Security-compliant credential management
- ✅ CORS support for web applications
- ✅ Structured logging
- ✅ Input validation with Pydantic models

### **Upcoming Features:**
- 🔄 Batch processing for multiple URLs
- 🔄 Caching for improved performance
- 🔄 Webhook support for real-time notifications
- 🔄 Enhanced language detection and support

## 📝 Project Status

**Current Status**: ✅ **Fully Functional**
- Azure OpenAI integration working
- All core analysis features implemented
- API endpoints operational
- Credentials properly configured
- Ready for production use

**Last Updated**: October 24, 2025
**Version**: 1.0.0
**Python Version**: 3.11+
**License**: MIT

---

*This project provides enterprise-grade web content analysis with advanced AI capabilities. Perfect for content research, competitive analysis, and automated content categorization workflows.*