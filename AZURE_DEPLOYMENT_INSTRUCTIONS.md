# Azure Deployment Instructions

This guide provides step-by-step instructions to deploy the Web Content Analysis Agent to Azure using Container Apps and Key Vault for secure secret management.

---

## 1. Prerequisites
- Azure CLI installed and logged in (`az login`)
- Docker installed
- Azure subscription and resource group
- Azure Container Registry (ACR) created

## 2. Build and Push Docker Image
```bash
# Build Docker image
docker build -t web-content-analyzer .

# Tag for ACR
docker tag web-content-analyzer <your-acr-name>.azurecr.io/web-content-analyzer:latest

# Login to ACR
az acr login --name <your-acr-name>

# Push image to ACR
docker push <your-acr-name>.azurecr.io/web-content-analyzer:latest
```

## 3. Create Azure Container App Environment
```bash
az group create --name <resource-group> --location <location>
az containerapp env create --name <env-name> --resource-group <resource-group> --location <location>
```

## 4. Deploy Container App Using Bicep
Edit `azure-container-app.bicep` with your values, then deploy:
```bash
az deployment group create \
  --resource-group <resource-group> \
  --template-file azure-container-app.bicep \
  --parameters \
    containerAppName=<app-name> \
    environmentName=<env-name> \
    containerRegistryServer=<your-acr-name>.azurecr.io \
    containerRegistryUsername=<acr-username> \
    containerRegistryPassword=<acr-password> \
    containerImage=<your-acr-name>.azurecr.io/web-content-analyzer:latest \
    azureOpenAiEndpoint=<your-openai-endpoint> \
    azureOpenAiApiKey=<your-api-key>
```

## 5. Integrate Azure Key Vault (Recommended)
See `KEY_VAULT_GUIDE.md` for secure secret management.

## 6. Test Your Deployment
- Access the app at the Azure-provided URL
- Run: `python test_production.py https://<your-app-url>`

## 7. Additional Resources
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [KEY_VAULT_GUIDE.md](KEY_VAULT_GUIDE.md)
- [AZURE_DEPLOYMENT_CHECKLIST.md](AZURE_DEPLOYMENT_CHECKLIST.md)
