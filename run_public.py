#!/usr/bin/env python3
"""
Alternative server runner that forces public access
"""
import uvicorn
import os

if __name__ == "__main__":
    # Try to force public access without deployment
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    print(f"Starting server on {host}:{port}")
    print(f"Development URL: https://{os.environ.get('REPLIT_DEV_DOMAIN', 'localhost')}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level="info",
        reload=False,
        access_log=True
    )