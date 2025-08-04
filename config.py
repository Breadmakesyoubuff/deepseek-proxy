"""
Configuration settings for the DeepSeek proxy server
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    # DeepSeek API configuration
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
    DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")
    
    # Request timeout settings
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "300"))  # 5 minutes
    CONNECT_TIMEOUT: int = int(os.getenv("CONNECT_TIMEOUT", "30"))   # 30 seconds
    
    # Retry settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_REQUESTS: bool = os.getenv("LOG_REQUESTS", "true").lower() == "true"
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    @property  
    def deepseek_headers(self) -> dict:
        """Get headers for DeepSeek API requests"""
        return {
            "Authorization": f"Bearer {self.DEEPSEEK_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "DeepSeek-OpenAI-Proxy/1.0.0"
        }
    
    def is_api_key_configured(self) -> bool:
        """Check if DeepSeek API key is properly configured"""
        return self.DEEPSEEK_API_KEY != "your-deepseek-api-key" and len(self.DEEPSEEK_API_KEY) > 0

# Global settings instance
settings = Settings()
