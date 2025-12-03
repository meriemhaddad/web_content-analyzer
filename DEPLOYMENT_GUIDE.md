# Production Deployment Guide

## 🚀 Deploy Your Web Content Analysis Agent


### **Production Deployment: Azure Container Apps (Recommended)**

1. **Build and Push Image**:
   ```bash
   # Build Docker image
   docker build -t web-content-analyzer .
   # Tag for Azure Container Registry
   docker tag web-content-analyzer your-registry.azurecr.io/web-content-analyzer:latest
   # Push to registry
   docker push your-registry.azurecr.io/web-content-analyzer:latest
   ```

2. **Deploy to Azure**:
   ```bash
   # Create resource group
   az group create --name rg-web-analyzer --location eastus
   # Create container app environment
   az containerapp env create --name env-web-analyzer --resource-group rg-web-analyzer --location eastus
   # Deploy container app
   az containerapp create \
     --name web-content-analyzer \
     --resource-group rg-web-analyzer \
     --environment env-web-analyzer \
     --image your-registry.azurecr.io/web-content-analyzer:latest \
     --target-port 8000 \
     --ingress external \
     --min-replicas 1 \
     --max-replicas 3
   ```

## 3. ☁️ Azure Container Apps (Production Scale)

1. **Build and Push Image**:
   ```bash
   # Build Docker image
   docker build -t web-content-analyzer .
   
   # Tag for Azure Container Registry
   docker tag web-content-analyzer your-registry.azurecr.io/web-content-analyzer:latest
   
   # Push to registry
   docker push your-registry.azurecr.io/web-content-analyzer:latest
   ```

2. **Deploy to Azure**:
   ```bash
   # Create resource group
   az group create --name rg-web-analyzer --location eastus
   
   # Create container app environment
   az containerapp env create --name env-web-analyzer --resource-group rg-web-analyzer --location eastus
   
   # Deploy container app
   az containerapp create \
     --name web-content-analyzer \
     --resource-group rg-web-analyzer \
     --environment env-web-analyzer \
     --image your-registry.azurecr.io/web-content-analyzer:latest \
     --target-port 8000 \
     --ingress external \
     --min-replicas 1 \
     --max-replicas 3
   ```

## 4. 🐳 Local Docker Testing

```bash
# Build and run locally
docker build -t web-content-analyzer .
docker run -p 8000:8000 --env-file .env.production web-content-analyzer

# Or use docker-compose
docker-compose up --build
```

## 🔒 **Security Checklist**

- [ ] Set `ENV=production` to disable docs endpoints
- [ ] Configure proper CORS origins (replace `*` with your domain)
- [ ] Use environment variables for all secrets
- [ ] Enable HTTPS in production
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting if needed

## 🌐 **Custom Domain Setup**


### Custom Domain Setup (Azure):
See Azure documentation for [custom domain setup](https://learn.microsoft.com/en-us/azure/container-apps/custom-domains).

## 📊 **Monitoring**

Add these endpoints to your monitoring:
- `GET /health` - Health check
- `GET /` - Root endpoint
- Monitor response times and success rates

## 🚀 **Scaling Considerations**

- **Azure**: Full control, enterprise scaling

## 📝 **Team Access**


Once deployed, share your Azure Container App public URL with your team.

---

**Next Steps:**
1. Choose deployment platform
2. Set up GitHub repository
3. Configure environment variables
4. Deploy and test
5. Share URL with team! 🎉