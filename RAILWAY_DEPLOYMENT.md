# 🚀 Railway Deployment Guide

## Quick Deploy Steps

### 1. **Push to GitHub** (if not already done)
```bash
git add .
git commit -m "Add Railway deployment configuration"
git push origin main
```

### 2. **Connect to Railway**
1. Go to [railway.app](https://railway.app)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository
5. Railway will auto-detect the configuration

### 3. **Set Environment Variables**
In Railway dashboard → **Variables** tab, add:
```
ANTHROPIC_API_KEY = your_actual_anthropic_api_key_here
```
*Note: Use your real API key from your .env file*

### 4. **Deploy!**
Railway will automatically:
- ✅ Install dependencies with `uv`
- ✅ Install Playwright browsers
- ✅ Start the web server
- ✅ Provide you with a live URL

## 🌐 **Your Live App Will Have:**

### **Web Interface**
- Beautiful HTML interface at your Railway URL
- Input field for any website URL
- Real-time keyword analysis results

### **API Endpoints**
- `POST /api/analyze` - Single URL analysis
- `POST /api/batch` - Batch URL analysis (up to 10 URLs)
- `GET /health` - Health check

### **Example API Usage**
```bash
# Single URL
curl -X POST https://your-app.railway.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Batch URLs
curl -X POST https://your-app.railway.app/api/batch \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://example.com", "https://github.com"]}'
```

## 🔄 **Auto-Deploy Setup**
Once connected, **every git push will automatically deploy**:
```bash
git add .
git commit -m "Update feature"
git push origin main
# 🚀 Automatic deployment triggered!
```

## 📊 **Monitoring**
Railway provides:
- **Live logs** - See real-time application output
- **Metrics** - CPU, memory, request tracking
- **Custom domains** - Add your own domain
- **Scaling** - Automatic scaling based on traffic

## 💰 **Pricing**
- **Free tier**: $0/month (hobby projects)
- **Pro tier**: ~$5/month (production apps)

## 🔧 **Local Testing**
Before deploying, test locally:
```bash
uv run python server.py
# Visit http://localhost:8000
```

---

**Your Web Content Analyzer will be live and accessible worldwide in minutes!** 🌍