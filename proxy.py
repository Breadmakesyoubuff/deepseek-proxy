"""
DeepSeek API proxy implementation with OpenAI compatibility
"""

import json
import httpx
import asyncio
import logging
import time
from typing import AsyncGenerator
from fastapi import HTTPException

from config import settings
from models import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    ChatCompletionStreamResponse,
    Choice, 
    StreamChoice,
    Usage, 
    Message
)

logger = logging.getLogger(__name__)

class DeepSeekProxy:
    """Proxy handler for DeepSeek API with OpenAI compatibility"""
    
    def __init__(self):
        """Initialize the proxy with HTTP client"""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=settings.CONNECT_TIMEOUT,
                read=settings.REQUEST_TIMEOUT,
                write=settings.REQUEST_TIMEOUT,
                pool=settings.REQUEST_TIMEOUT
            ),
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.client.aclose()
    
    def _prepare_deepseek_request(self, request: ChatCompletionRequest) -> dict:
        """Convert OpenAI request format to DeepSeek format"""
        # Map model names to DeepSeek API format
        model_mapping = {
            "deepseek-ai/DeepSeek-V3-0324-Free": "deepseek-chat",
            "deepseek-chat": "deepseek-chat",
            "deepseek-reasoner": "deepseek-reasoner"
        }
        
        deepseek_model = model_mapping.get(request.model, request.model)
        
        deepseek_request = {
            "model": deepseek_model,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in request.messages
            ],
            "stream": request.stream
        }
        
        # Add optional parameters if provided
        if request.temperature is not None and request.temperature != 1.0:
            deepseek_request["temperature"] = request.temperature
        
        if request.max_tokens is not None:
            deepseek_request["max_tokens"] = request.max_tokens
            
        if request.top_p is not None and request.top_p != 1.0:
            deepseek_request["top_p"] = request.top_p
            
        if request.frequency_penalty is not None and request.frequency_penalty != 0.0:
            deepseek_request["frequency_penalty"] = request.frequency_penalty
            
        if request.presence_penalty is not None and request.presence_penalty != 0.0:
            deepseek_request["presence_penalty"] = request.presence_penalty
            
        if request.stop is not None:
            deepseek_request["stop"] = request.stop
        
        return deepseek_request
    
    def _convert_to_openai_response(self, deepseek_response: dict, request_model: str) -> ChatCompletionResponse:
        """Convert DeepSeek response to OpenAI format"""
        try:
            # DeepSeek API is already OpenAI-compatible, but we ensure consistency
            choices = []
            for i, choice in enumerate(deepseek_response.get("choices", [])):
                openai_choice = Choice(
                    index=choice.get("index", i),
                    message=Message(
                        role=choice.get("message", {}).get("role", "assistant"),
                        content=choice.get("message", {}).get("content", "")
                    ),
                    finish_reason=choice.get("finish_reason")
                )
                choices.append(openai_choice)
            
            # Extract usage information
            usage_data = deepseek_response.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return ChatCompletionResponse(
                id=deepseek_response.get("id", f"chatcmpl-deepseek-{request_model}"),
                model=deepseek_response.get("model", request_model),
                choices=choices,
                usage=usage,
                created=deepseek_response.get("created", int(time.time())),
                system_fingerprint=deepseek_response.get("system_fingerprint")
            )
            
        except Exception as e:
            logger.error(f"Error converting DeepSeek response to OpenAI format: {str(e)}")
            raise HTTPException(status_code=500, detail="Error processing API response")
    
    async def health_check(self) -> bool:
        """Check if DeepSeek API is accessible"""
        try:
            # Simple request to check API accessibility
            test_request = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 1
            }
            
            response = await self.client.post(
                f"{settings.DEEPSEEK_API_URL}/chat/completions",
                headers=settings.deepseek_headers,
                json=test_request,
                timeout=10.0
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False
    
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Handle non-streaming chat completion request"""
        if not settings.is_api_key_configured():
            raise HTTPException(
                status_code=401,
                detail="DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable."
            )
        
        deepseek_request = self._prepare_deepseek_request(request)
        
        # Log request if enabled
        if settings.LOG_REQUESTS:
            logger.info(f"Sending request to DeepSeek API: {json.dumps(deepseek_request, indent=2)}")
        
        try:
            for attempt in range(settings.MAX_RETRIES):
                try:
                    response = await self.client.post(
                        f"{settings.DEEPSEEK_API_URL}/chat/completions",
                        headers=settings.deepseek_headers,
                        json=deepseek_request
                    )
                    
                    if response.status_code == 200:
                        deepseek_response = response.json()
                        
                        # Log response if enabled
                        if settings.LOG_REQUESTS:
                            logger.info(f"DeepSeek API response: {json.dumps(deepseek_response, indent=2)}")
                        
                        return self._convert_to_openai_response(deepseek_response, request.model)
                    
                    elif response.status_code == 401:
                        raise HTTPException(status_code=401, detail="Invalid DeepSeek API key")
                    
                    elif response.status_code == 429:
                        if attempt < settings.MAX_RETRIES - 1:
                            await asyncio.sleep(settings.RETRY_DELAY * (2 ** attempt))
                            continue
                        raise HTTPException(status_code=429, detail="Rate limit exceeded")
                    
                    elif response.status_code == 400:
                        error_detail = response.json().get("error", {}).get("message", "Bad request")
                        raise HTTPException(status_code=400, detail=error_detail)
                    
                    else:
                        error_detail = response.json().get("error", {}).get("message", f"HTTP {response.status_code}")
                        raise HTTPException(status_code=response.status_code, detail=error_detail)
                        
                except httpx.RequestError as e:
                    if attempt < settings.MAX_RETRIES - 1:
                        logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                        await asyncio.sleep(settings.RETRY_DELAY * (2 ** attempt))
                        continue
                    raise HTTPException(status_code=503, detail=f"Failed to connect to DeepSeek API: {str(e)}")
            
            # If we get here, all retries failed
            raise HTTPException(status_code=503, detail="All retry attempts failed")
                    
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in chat completion: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def stream_chat_completion(self, request: ChatCompletionRequest) -> AsyncGenerator[str, None]:
        """Handle streaming chat completion request"""
        if not settings.is_api_key_configured():
            raise HTTPException(
                status_code=401,
                detail="DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable."
            )
        
        deepseek_request = self._prepare_deepseek_request(request)
        deepseek_request["stream"] = True
        
        # Log request if enabled
        if settings.LOG_REQUESTS:
            logger.info(f"Sending streaming request to DeepSeek API: {json.dumps(deepseek_request, indent=2)}")
        
        try:
            async with self.client.stream(
                "POST",
                f"{settings.DEEPSEEK_API_URL}/chat/completions",
                headers=settings.deepseek_headers,
                json=deepseek_request
            ) as response:
                
                if response.status_code != 200:
                    error_detail = "Streaming request failed"
                    try:
                        error_data = await response.aread()
                        error_json = json.loads(error_data.decode())
                        error_detail = error_json.get("error", {}).get("message", error_detail)
                    except:
                        pass
                    
                    raise HTTPException(status_code=response.status_code, detail=error_detail)
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        
                        if data.strip() == "[DONE]":
                            yield "data: [DONE]\n\n"
                            break
                        
                        try:
                            # Parse the streaming chunk
                            chunk = json.loads(data)
                            
                            # Convert to OpenAI format if needed
                            openai_chunk = ChatCompletionStreamResponse(
                                id=chunk.get("id", f"chatcmpl-deepseek-{request.model}"),
                                model=chunk.get("model", request.model),
                                created=chunk.get("created"),
                                choices=[
                                    StreamChoice(
                                        index=choice.get("index", 0),
                                        delta=choice.get("delta", {}),
                                        finish_reason=choice.get("finish_reason")
                                    )
                                    for choice in chunk.get("choices", [])
                                ]
                            )
                            
                            yield f"data: {openai_chunk.json()}\n\n"
                            
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming chunk: {data}")
                            continue
                        except Exception as e:
                            logger.error(f"Error processing streaming chunk: {str(e)}")
                            continue
                            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")
