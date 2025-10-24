# Security Configuration Guide

This application is designed to be security compliant and avoid storing sensitive credentials in configuration files.

## Authentication Methods (In Order of Preference)

### 1. Azure CLI Authentication (Recommended for Development)
```bash
# Login to Azure CLI
az login

# Set the Azure OpenAI endpoint as environment variable
$env:AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
$env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# Run the application
uvicorn src.main:app --reload
```

### 2. System Environment Variables
```powershell
# Set environment variables in PowerShell
$env:AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
$env:AZURE_OPENAI_API_KEY="your-api-key-here"  # Only if not using Azure CLI
$env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"

# For persistent environment variables, use Windows System Properties
# or add to your PowerShell profile
```

### 3. Azure Managed Identity (Production/Azure Hosting)
When deploying to Azure (App Service, Container Instances, etc.):

```bash
# Enable system-assigned managed identity in Azure
# Grant the managed identity "Cognitive Services OpenAI User" role on your Azure OpenAI resource
# Set environment variable:
USE_MANAGED_IDENTITY=true
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
```

## Security Best Practices

### ✅ What This Application Does:
- Uses Azure DefaultAzureCredential chain
- Prioritizes Azure CLI credentials for local development
- Supports Managed Identity for Azure deployments  
- Never stores credentials in code or config files
- Uses environment variables for non-sensitive configuration

### ❌ What to Avoid:
- Don't commit .env files with credentials
- Don't hardcode API keys in source code
- Don't store credentials in configuration files
- Don't use API keys in production when Managed Identity is available

## Required Environment Variables

### Minimal Configuration:
```
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
```

### Optional Configuration:
```
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o  # Default: gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-01  # Default: 2024-02-01
HOST=127.0.0.1                       # Default: 127.0.0.1
PORT=8000                            # Default: 8000
DEBUG=false                          # Default: false
USE_MANAGED_IDENTITY=true            # Default: false
USE_AZURE_CLI=true                   # Default: true
```

## Troubleshooting Authentication

### Error: "No valid authentication method found"
1. Ensure Azure CLI is installed and logged in: `az login`
2. Verify you have access to the Azure OpenAI resource: `az cognitiveservices account show --name your-openai-resource --resource-group your-rg`
3. Check environment variables are set: `echo $env:AZURE_OPENAI_ENDPOINT`

### Error: "DefaultAzureCredential failed to retrieve a token"
1. Run `az account show` to verify you're logged in
2. Check your Azure subscription and tenant
3. Ensure the Azure CLI account has appropriate permissions

### For Azure Deployments:
1. Enable system-assigned managed identity
2. Assign "Cognitive Services OpenAI User" role to the managed identity
3. Set `USE_MANAGED_IDENTITY=true` environment variable

## Local Development Setup

1. Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. Login: `az login`
3. Set environment variables:
   ```powershell
   $env:AZURE_OPENAI_ENDPOINT="https://your-resource-name.openai.azure.com/"
   $env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
   ```
4. Install dependencies: `pip install -r requirements.txt`
5. Run application: `uvicorn src.main:app --reload`

The application will automatically use your Azure CLI credentials without requiring API keys!