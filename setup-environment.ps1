# PowerShell script to set up environment for Web Content Analysis Agent
# Run this script in PowerShell to configure your local development environment

Write-Host "🔐 Setting up Web Content Analysis Agent - Security Compliant Configuration" -ForegroundColor Green
Write-Host ""

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>$null
    if ($azVersion) {
        Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Azure CLI not found. Please install it from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Red
    exit 1
}

# Check if user is logged in
try {
    $account = az account show 2>$null | ConvertFrom-Json
    if ($account) {
        Write-Host "✅ Logged in to Azure as: $($account.user.name)" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Not logged in to Azure. Running 'az login'..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Successfully logged in to Azure" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to login to Azure" -ForegroundColor Red
        exit 1
    }
}

# Prompt for Azure OpenAI endpoint
Write-Host ""
Write-Host "📝 Please provide your Azure OpenAI configuration:" -ForegroundColor Cyan
$endpoint = Read-Host "Azure OpenAI Endpoint (e.g., https://your-resource-name.openai.azure.com/)"

if (-not $endpoint) {
    Write-Host "❌ Azure OpenAI endpoint is required" -ForegroundColor Red
    exit 1
}

# Optional: Deployment name
$deploymentName = Read-Host "Deployment Name (default: gpt-4o, press Enter to use default)"
if (-not $deploymentName) {
    $deploymentName = "gpt-4o"
}

# Set environment variables
Write-Host ""
Write-Host "🔧 Setting environment variables..." -ForegroundColor Cyan

$env:AZURE_OPENAI_ENDPOINT = $endpoint
$env:AZURE_OPENAI_DEPLOYMENT_NAME = $deploymentName
$env:AZURE_OPENAI_API_VERSION = "2024-02-01"
$env:USE_AZURE_CLI = "true"

Write-Host "✅ Environment variables set:" -ForegroundColor Green
Write-Host "   AZURE_OPENAI_ENDPOINT = $env:AZURE_OPENAI_ENDPOINT"
Write-Host "   AZURE_OPENAI_DEPLOYMENT_NAME = $env:AZURE_OPENAI_DEPLOYMENT_NAME"
Write-Host "   AZURE_OPENAI_API_VERSION = $env:AZURE_OPENAI_API_VERSION"
Write-Host "   USE_AZURE_CLI = $env:USE_AZURE_CLI"

# Check if Python is available
Write-Host ""
Write-Host "🐍 Checking Python installation..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "✅ Python is available: $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python not found. Please install Python from: https://www.python.org/" -ForegroundColor Red
    exit 1
}

# Offer to install dependencies
Write-Host ""
$installDeps = Read-Host "Install Python dependencies? (y/N)"
if ($installDeps -eq "y" -or $installDeps -eq "Y") {
    Write-Host "📦 Installing Python dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    }
}

# Offer to start the application
Write-Host ""
$startApp = Read-Host "Start the application? (y/N)"
if ($startApp -eq "y" -or $startApp -eq "Y") {
    Write-Host ""
    Write-Host "🚀 Starting Web Content Analysis Agent..." -ForegroundColor Green
    Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "   Health Check: http://localhost:8000/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    uvicorn src.main:app --reload
} else {
    Write-Host ""
    Write-Host "🎉 Setup complete! To start the application, run:" -ForegroundColor Green
    Write-Host "   uvicorn src.main:app --reload" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📚 Documentation available at: http://localhost:8000/docs" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "💡 Note: Environment variables are set for this session only." -ForegroundColor Yellow
Write-Host "   To make them permanent, add them to your system environment variables" -ForegroundColor Yellow
Write-Host "   or add them to your PowerShell profile." -ForegroundColor Yellow