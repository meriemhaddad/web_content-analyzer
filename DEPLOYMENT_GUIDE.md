# Production Deployment Guide

## 🚀 Deploy Your Web Content Analysis Agent

### **Quick Deploy Options:**

## 1. 🚂 Railway (Easiest - Recommended)

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Production ready"
   git push origin main
   ```

2. **Deploy to Railway**:
   - Go to [railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your repository
   - Railway will detect `railway.toml` automatically

3. **Set Environment Variables**:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
   ENV=production
   ```

4. **Access your app**: Railway provides a public URL

## 2. 🎨 Render (Free Tier Available)

1. **Connect GitHub**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Select "Web Service"

2. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables** (same as Railway)

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

### Railway:
1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS CNAME to point to Railway

### Render:
1. Go to Settings → Custom Domains
2. Add domain and follow DNS instructions

## 📊 **Monitoring**

Add these endpoints to your monitoring:
- `GET /health` - Health check
- `GET /` - Root endpoint
- Monitor response times and success rates

## 🚀 **Scaling Considerations**

- **Railway**: Automatically scales, usage-based pricing
- **Render**: Free tier limited, paid plans scale
- **Azure**: Full control, enterprise scaling

## 📝 **Team Access**

Once deployed, share the public URL:
- `https://your-app-name.railway.app`
- `https://your-app-name.onrender.com`
- `https://your-domain.com`

Your team can access:
- `/api/v1/bulk-upload` - Web interface
- `/api/v1/docs` - API documentation (dev only)
- API endpoints for integration

---

**Next Steps:**
1. Choose deployment platform
2. Set up GitHub repository
3. Configure environment variables
4. Deploy and test
5. Share URL with team! 🎉