# Web Content Analysis Agent

An advanced web content analysis agent using FastAPI, Azure OpenAI GPT-4o, and Model Context Protocol (MCP) Fetch server for sophisticated semantic content categorization.

## Features

- **URL Content Analysis**: Analyze any web page URL for content and context
- **Advanced Semantic Analysis**: Leverage GPT-4o for deep content understanding
- **Content Categorization**: Intelligent categorization with semantic analysis
- **Batch Processing**: Support for analyzing multiple URLs (future feature)
- **MCP Integration**: Uses Model Context Protocol Fetch server for reliable web content retrieval
- **REST API**: FastAPI-based API for easy integration

## Project Structure

```
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Configuration management
│   ├── services/
│   │   ├── __init__.py
│   │   ├── azure_openai.py     # Azure OpenAI service
│   │   ├── content_analyzer.py # Content analysis engine
│   │   └── mcp_client.py       # MCP Fetch client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── requests.py         # API request models
│   │   └── responses.py        # API response models
│   └── api/
│       ├── __init__.py
│       └── endpoints.py        # API endpoints
├── testing/                    # All test files organized by category
│   ├── bulk_analysis/          # Bulk URL analysis tests
│   ├── integration/            # Integration and system tests
│   ├── scripts/               # Testing scripts (PowerShell, Bash)
│   ├── data/                  # Test data and results
│   ├── run_tests.py           # Test runner script
│   └── README.md              # Testing documentation
├── tests/                     # Unit tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_services.py
│   └── api/
│       ├── __init__.py
│       └── endpoints.py        # API endpoints
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_services.py
│   └── conftest.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### Security-Compliant Authentication Setup

1. **Install Azure CLI** (if not already installed):
   ```bash
   # Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
   ```

2. **Login to Azure**:
   ```bash
   az login
   ```

3. **Set Environment Variables** (PowerShell):
   ```powershell
   $env:AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
   $env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**:
   ```bash
   uvicorn src.main:app --reload
   ```

> **Security Note**: This application uses Azure DefaultAzureCredential for secure authentication without storing API keys in files. See [SECURITY.md](SECURITY.md) for detailed authentication options.

## API Endpoints

- `POST /analyze` - Analyze a single URL
- `POST /batch-analyze` - Analyze multiple URLs (coming soon)
- `GET /health` - Health check endpoint

## Configuration

### Required Environment Variables:
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint (Required)

### Optional Environment Variables:
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Deployment name (Default: "gpt-4o")
- `AZURE_OPENAI_API_VERSION`: API version (Default: "2024-02-01")
- `MCP_SERVER_URL`: MCP Fetch server URL (Optional)
- `USE_MANAGED_IDENTITY`: Use Azure Managed Identity (Default: false)

### Authentication Methods:
1. **Azure CLI** (Recommended for development): `az login`
2. **Managed Identity** (Production): Enable in Azure and set `USE_MANAGED_IDENTITY=true`
3. **API Key** (Fallback): Set `AZURE_OPENAI_API_KEY` environment variable

See [SECURITY.md](SECURITY.md) for detailed security configuration.

## Testing

The project includes comprehensive testing organized in the `testing/` directory:

### Quick Test Run
```bash
# Run all tests with the test runner
python testing/run_tests.py
```

### Individual Test Categories

**Bulk Analysis Tests:**
```bash
python testing/bulk_analysis/test_copy_paste.py
python testing/bulk_analysis/test_comprehensive.py
python testing/bulk_analysis/quick_bulk_test.py
```

**Integration Tests:**
```bash
python testing/integration/test_credentials.py
```

**Unit Tests:**
```bash
pytest tests/
```

For detailed testing documentation, see [testing/README.md](testing/README.md).

## 🚀 Production Deployment

This app is ready for production deployment! Choose from these options:

### **Quick Deploy (Recommended for Teams)**

#### 🚂 Railway (Easiest)
1. Push to GitHub: `git push origin main`
2. Connect at [railway.app](https://railway.app)
3. Set environment variables
4. Deploy automatically!

#### 🎨 Render (Free Tier)
1. Connect GitHub repo at [render.com](https://render.com)
2. Configure environment variables
3. Deploy with zero config

#### ☁️ Azure Container Apps (Enterprise)
- Full Azure integration
- Auto-scaling
- Enterprise security

### **Environment Variables for Production:**
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
ENV=production
```

**📋 Complete deployment guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### **Test Your Deployment:**
```bash
python test_production.py https://your-app-url.com
```

## Documentation

- [EFFICIENCY_ANALYSIS.md](EFFICIENCY_ANALYSIS.md) - Performance analysis and optimization roadmap
- [BULK_TESTING_GUIDE.md](BULK_TESTING_GUIDE.md) - Guide for bulk URL testing
- [SECURITY.md](SECURITY.md) - Security configuration and best practices

## License

MIT License