# DeepSeek OpenAI-Compatible Proxy

A FastAPI-based proxy server that provides OpenAI-compatible endpoints for the DeepSeek API, designed for integration with Janitor AI.

## Features

- OpenAI-compatible `/v1/chat/completions` endpoint
- Support for multiple model names including `deepseek-ai/DeepSeek-V3-0324-Free`
- Streaming and non-streaming responses
- Proper error handling with OpenAI-compatible format
- Health check endpoint

## Free Deployment Options

### Option 1: Railway (Recommended)
1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Create new project from GitHub repo
4. Add environment variable: `DEEPSEEK_API_KEY=your_key_here`
5. Deploy automatically gets a URL like `https://your-app.railway.app`

### Option 2: Render
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Create new Web Service
4. Add environment variable: `DEEPSEEK_API_KEY=your_key_here`
5. Use build command: `pip install -r requirements.txt`
6. Use start command: `python main.py`

### Option 3: Fly.io
1. Install flyctl CLI
2. Run `flyctl launch`
3. Set secrets: `flyctl secrets set DEEPSEEK_API_KEY=your_key_here`

## Environment Variables

- `DEEPSEEK_API_KEY` - Your DeepSeek API key (required)
- `PORT` - Server port (default: 5000)
- `DEEPSEEK_API_URL` - DeepSeek API URL (default: https://api.deepseek.com)

## For Janitor AI

Use these settings in Janitor AI:
- **Configuration Name:** DeepSeek
- **Model Name:** deepseek-ai/DeepSeek-V3-0324-Free
- **Proxy URL:** `https://your-deployed-url/v1/chat/completions`
- **API Key:** (leave empty)

## Local Development

```bash
python main.py
```

Server runs on http://localhost:5000