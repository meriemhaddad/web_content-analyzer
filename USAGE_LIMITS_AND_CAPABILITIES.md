# Web Content Analyzer - Usage Limits & Capabilities

**Project**: Web Content Analysis Agent  
**Deployment**: Railway Production Environment  
**URL**: `https://web-content-analyzer-production-88c3.up.railway.app`  
**Last Updated**: October 24, 2025

---

## 🚀 **Core Capabilities**

### **Analysis Features**
- ✅ **Single URL Analysis**: Instant AI-powered content analysis
- ✅ **Batch Processing**: Multiple URLs simultaneously (1-10 concurrent)
- ✅ **File Upload Support**: CSV and TXT files with bulk URLs
- ✅ **Copy/Paste Interface**: Line-separated URL input
- ✅ **Dynamic Categorization**: AI generates relevant categories (no predefined limits)
- ✅ **Comprehensive Analysis**: Sentiment, entities, summaries, quality scores
- ✅ **Real-time Results**: Live progress tracking and results display

### **AI Integration**
- 🤖 **Azure OpenAI GPT-4o**: Latest model for advanced analysis
- 📊 **Content Metadata**: Title, description, language detection
- 🏷️ **Smart Categorization**: Context-aware category assignment
- 💭 **Sentiment Analysis**: Positive/Negative/Neutral scoring
- 📈 **Quality Assessment**: Content quality scoring (0-10)
- 🔍 **Entity Extraction**: Key topics and entities identification

### **Technical Architecture**
- ⚡ **FastAPI Framework**: High-performance async API
- 🐳 **Docker Containerized**: Production-ready deployment
- 🌐 **CORS Enabled**: Cross-origin requests supported
- 🔒 **Environment-based Config**: Secure credential management
- 📱 **Responsive Web Interface**: Mobile-friendly bulk upload
- 🚥 **Health Monitoring**: Built-in health checks

---

## 📊 **Processing Limits & Performance**

### **Concurrency Settings**
```
Default Concurrent URLs: 5 simultaneous
Maximum Concurrent URLs: 10 simultaneous
Processing Speed: ~2-5 seconds per URL
Batch Size: Unlimited (memory permitting)
```

### **Technical Constraints**
- **Memory Usage**: ~100MB RAM per instance
- **Request Timeout**: 300 seconds (Railway default)
- **File Upload Size**: Limited by Railway (typically ~100MB)
- **API Response Size**: No hard limit, but optimized for efficiency

### **Practical Performance**
| **Usage Scenario** | **URLs/Hour** | **Daily Capacity** | **Recommended For** |
|-------------------|---------------|-------------------|-------------------|
| **Light Usage** | 50-200 | 1,000-5,000 | Small teams (5-10 people) |
| **Medium Usage** | 200-500 | 5,000-12,000 | Research teams, content analysis |
| **Heavy Usage** | 500-1,000+ | 12,000+ | Enterprise, large-scale analysis |

---

## 💰 **Cost Analysis & Hosting Limits**

### **Railway Free Tier (Monthly)**
```
✅ Credit Allowance: $5 USD/month
✅ Execution Hours: 500 hours/month (~20 days continuous)
✅ Memory: 1GB RAM per service
✅ Storage: 1GB persistent storage
✅ Bandwidth: Fair use policy
✅ Custom Domains: Included
✅ HTTPS: Automatic SSL certificates
```

### **Railway Usage Estimates**
| **Component** | **Resource Usage** | **Monthly Cost** |
|--------------|-------------------|------------------|
| **API Server** | ~0.1GB RAM, minimal CPU | ~$2-5/month |
| **Data Transfer** | Depends on usage volume | Included in fair use |
| **Storage** | Minimal (stateless app) | Free tier sufficient |

### **Azure OpenAI Costs** (Your Main Expense)
| **Usage Level** | **Monthly URLs** | **Estimated Cost** | **Cost Per URL** |
|----------------|------------------|-------------------|------------------|
| **Light** | 1,000-5,000 | $10-25 | ~$0.005-0.01 |
| **Medium** | 5,000-20,000 | $25-100 | ~$0.003-0.008 |
| **Heavy** | 20,000+ | $100+ | ~$0.002-0.005 |

---

## 🎯 **Usage Recommendations**

### **Optimal Team Sizes**
- **Small Team (5-10 people)**: 100-500 URLs/day - Perfect for free tier
- **Medium Team (10-25 people)**: 500-2000 URLs/day - May need Railway Pro
- **Large Team (25+ people)**: 2000+ URLs/day - Requires paid plans

### **Cost-Effective Usage Patterns**
1. **Batch Processing**: Upload files during off-peak hours
2. **Concurrent Optimization**: Use 5-8 concurrent requests for best balance
3. **Content Filtering**: Pre-filter URLs to analyze only relevant content
4. **Team Coordination**: Schedule heavy analysis tasks to avoid conflicts

### **Scaling Recommendations**
- **Stay on Free Tier**: Keep under 500 execution hours/month
- **Upgrade to Railway Pro ($20/month)**: When exceeding free tier limits
- **Azure OpenAI Optimization**: Monitor token usage and optimize prompts

---

## 🔧 **Configuration Limits**

### **Environment Variables**
```
AZURE_OPENAI_ENDPOINT: Required
AZURE_OPENAI_API_KEY: Required (main cost driver)
AZURE_OPENAI_DEPLOYMENT_NAME: Default "gpt-4o"
AZURE_OPENAI_API_VERSION: Default "2024-02-01"
ENV: "production" (disables docs for security)
```

### **API Rate Limits**
- **Azure OpenAI**: Depends on your subscription tier
- **Railway**: No specific API rate limits on free tier
- **Concurrent Requests**: Limited by semaphore configuration (5-10)

### **File Upload Constraints**
- **Supported Formats**: CSV, TXT
- **URL Validation**: Must start with http:// or https://
- **Line Limits**: Practically unlimited (memory dependent)
- **Processing Time**: Scales linearly with URL count

---

## 📈 **Monitoring & Analytics**

### **Available Metrics**
- ✅ **Processing Time**: Per-URL and batch analysis duration
- ✅ **Success Rate**: Percentage of successful analyses
- ✅ **Error Tracking**: Failed URLs with error categories
- ✅ **Category Distribution**: Most common content categories
- ✅ **Quality Scores**: Average content quality metrics

### **Health Check Endpoints**
```
Health Status: GET /health
API Info: GET /
Bulk Interface: GET /bulk-upload
API Endpoints: /api/v1/* (with prefix)
```

---

## 🚨 **Known Limitations**

### **Content Restrictions**
- **Password-Protected Sites**: Cannot analyze authenticated content
- **JavaScript-Heavy Sites**: Limited analysis of dynamic content
- **Large Files**: May timeout on very large web pages
- **Rate-Limited Sites**: Some sites may block automated requests

### **Technical Limitations**
- **Single Region**: Currently deployed in europe-west4
- **No Data Persistence**: Results not stored permanently
- **Session-Based**: No user authentication or personal dashboards
- **Synchronous Processing**: No background job queuing

### **Usage Constraints**
- **Team Sharing**: Public URL accessible to anyone with link
- **No User Management**: No individual accounts or permissions
- **Limited Customization**: Categories generated by AI, not customizable
- **No API Keys**: Public access (consider adding authentication for production)

---

## 🔮 **Future Scaling Options**

### **When to Upgrade Railway**
- **Pro Plan ($20/month)**: When exceeding 500 hours/month
- **Enterprise**: For dedicated resources and support

### **Azure OpenAI Optimization**
- **Dedicated Capacity**: For predictable costs at scale
- **Custom Models**: Fine-tuned models for specific content types
- **Batch API**: For non-real-time processing cost savings

### **Architecture Improvements**
- **Background Processing**: Queue system for large batches
- **Result Caching**: Store and reuse previous analyses
- **User Authentication**: Individual accounts and API keys
- **Database Integration**: Persistent storage for historical data

---

## 📞 **Support & Resources**

### **Technical Support**
- **Railway Documentation**: https://docs.railway.app
- **Azure OpenAI Docs**: https://docs.microsoft.com/azure/cognitive-services/openai/
- **Project Repository**: https://github.com/meriemhaddad/web_content-analyzer

### **Monitoring & Alerts**
- **Railway Dashboard**: Monitor usage and costs
- **Azure Portal**: Track OpenAI usage and costs
- **Health Checks**: Automated monitoring via `/health` endpoint

### **Cost Management**
- **Railway Billing**: Monitor execution hours and costs
- **Azure Cost Management**: Set up billing alerts for OpenAI usage
- **Usage Analytics**: Track URL processing patterns

---

**📝 Note**: This document should be reviewed monthly to ensure accuracy as usage patterns and platform limits evolve.

**🔄 Last Review**: October 24, 2025 - All limits and capabilities verified for current deployment.