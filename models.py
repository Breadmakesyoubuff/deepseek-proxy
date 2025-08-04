"""
Pydantic models for OpenAI-compatible request/response validation
"""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field
import time
import uuid

class Message(BaseModel):
    """Chat message model"""
    role: Literal["system", "user", "assistant"] = Field(..., description="Role of the message sender")
    content: str = Field(..., description="Content of the message")

class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request model"""
    model: str = Field(..., description="Model to use for completion")
    messages: List[Message] = Field(..., description="List of messages in the conversation")
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=None, ge=1, description="Maximum number of tokens to generate")
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")
    n: Optional[int] = Field(default=1, ge=1, le=128, description="Number of completions to generate")
    logit_bias: Optional[Dict[str, float]] = Field(default=None, description="Logit bias")
    user: Optional[str] = Field(default=None, description="User identifier")

class Choice(BaseModel):
    """Choice model for completion response"""
    index: int = Field(..., description="Index of the choice")
    message: Message = Field(..., description="Generated message")
    finish_reason: Optional[str] = Field(default=None, description="Reason for stopping generation")

class Usage(BaseModel):
    """Token usage information"""
    prompt_tokens: int = Field(..., description="Number of tokens in the prompt")
    completion_tokens: int = Field(..., description="Number of tokens in the completion")
    total_tokens: int = Field(..., description="Total number of tokens used")

class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response model"""
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}", description="Unique completion ID")
    object: str = Field(default="chat.completion", description="Object type")
    created: int = Field(default_factory=lambda: int(time.time()), description="Creation timestamp")
    model: str = Field(..., description="Model used for completion")
    choices: List[Choice] = Field(..., description="List of completion choices")
    usage: Usage = Field(..., description="Token usage information")
    system_fingerprint: Optional[str] = Field(default=None, description="System fingerprint")

class StreamChoice(BaseModel):
    """Choice model for streaming response"""
    index: int = Field(..., description="Index of the choice")
    delta: Dict[str, Any] = Field(..., description="Delta containing new content")
    finish_reason: Optional[str] = Field(default=None, description="Reason for stopping generation")

class ChatCompletionStreamResponse(BaseModel):
    """Streaming response chunk model"""
    id: str = Field(..., description="Unique completion ID")
    object: str = Field(default="chat.completion.chunk", description="Object type")
    created: int = Field(..., description="Creation timestamp")
    model: str = Field(..., description="Model used for completion")
    choices: List[StreamChoice] = Field(..., description="List of streaming choices")
    system_fingerprint: Optional[str] = Field(default=None, description="System fingerprint")

class ErrorDetail(BaseModel):
    """Error detail model"""
    message: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")
    code: Union[str, int] = Field(..., description="Error code")

class ErrorResponse(BaseModel):
    """OpenAI-compatible error response model"""
    error: ErrorDetail = Field(..., description="Error details")
