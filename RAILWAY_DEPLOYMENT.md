# Deploy Your DeepSeek Proxy to Railway (FREE)

Your code is ready for Railway deployment! Follow these steps:

## Step 1: Create Railway Account
1. Go to **[railway.app](https://railway.app)**
2. Click "Login" and sign in with your **GitHub account**
3. Authorize Railway to access your repositories

## Step 2: Upload Your Code to GitHub
You need to put your Replit code into a GitHub repository:

### Option A: Export from Replit (Easiest)
1. In Replit, click the **three dots menu** (⋯) next to your project name
2. Select **"Export as zip"**
3. Download and extract the zip file
4. Go to **[github.com](https://github.com)** and create a **new repository**
5. Upload all your files to the GitHub repo

### Option B: Use Git Commands (If available)
```bash
git init
git add .
git commit -m "DeepSeek proxy for Janitor AI"
git push origin main
```

## Step 3: Deploy on Railway
1. Go back to **Railway** and click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository with the DeepSeek proxy code
4. Railway will automatically detect it's a Python app

## Step 4: Set Environment Variables
1. In Railway dashboard, go to your project
2. Click **"Variables"** tab
3. Add: `DEEPSEEK_API_KEY` = `your_deepseek_api_key_here`
4. Click **"Add"**

## Step 5: Get Your URL
1. Railway will automatically deploy and give you a URL like:
   `https://your-app-name.railway.app`
2. Your Janitor AI endpoint will be:
   `https://your-app-name.railway.app/v1/chat/completions`

## For Janitor AI Configuration:
- **Configuration Name:** DeepSeek
- **Model Name:** `deepseek-ai/DeepSeek-V3-0324-Free`
- **Proxy URL:** `https://your-app-name.railway.app/v1/chat/completions`
- **API Key:** (leave empty)

## Files Ready for Railway:
✅ `main.py` - Your FastAPI proxy server
✅ `models.py` - Request/response models
✅ `proxy.py` - DeepSeek API proxy logic
✅ `config.py` - Configuration settings
✅ `railway.json` - Railway deployment config
✅ `Procfile` - Process definition
✅ `runtime.txt` - Python version

## Cost: FREE
- Railway gives you **$5 in free credits monthly**
- Your API proxy will use minimal resources
- Perfect for personal Janitor AI usage

## Next Steps:
1. Export/upload your code to GitHub
2. Deploy on Railway
3. Set your DeepSeek API key
4. Use the Railway URL in Janitor AI
5. Start chatting!

Need help? The Railway dashboard is very user-friendly and guides you through each step.