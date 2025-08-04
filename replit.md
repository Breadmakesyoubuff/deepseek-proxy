# DeepSeek OpenAI-Compatible Proxy

## Overview

This is a FastAPI-based proxy server that provides OpenAI-compatible endpoints for the DeepSeek API. The project is specifically designed for integration with Janitor AI and other applications that expect OpenAI's API format. The proxy translates incoming OpenAI-formatted requests to DeepSeek's API format, handles the communication, and returns responses in the expected OpenAI format.

## User Preferences

Preferred communication style: Simple, everyday language.
Preferred model name: deepseek-ai/DeepSeek-V3-0324-Free (mapped to deepseek-chat internally)

## System Architecture

### API Proxy Pattern
The application implements a proxy pattern where it acts as an intermediary between clients expecting OpenAI API format and the DeepSeek API. This allows existing OpenAI-compatible applications to use DeepSeek models without code changes.

### Framework Choice: FastAPI
The project uses FastAPI as the web framework, chosen for its built-in async support, automatic API documentation generation, and strong type validation through Pydantic models. This is ideal for a proxy service that needs to handle concurrent requests efficiently.

### Request/Response Model Validation
Pydantic models are used extensively to validate both incoming requests and outgoing responses, ensuring OpenAI API compatibility. The models include proper field validation, default values, and type constraints that match OpenAI's specification.

### Configuration Management
Environment-based configuration is implemented through a centralized Settings class, allowing easy deployment across different environments. All sensitive data like API keys are managed through environment variables.

### Async HTTP Client
The proxy uses httpx for making HTTP requests to the DeepSeek API, with configurable timeouts, connection pooling, and retry mechanisms to ensure reliable communication.

### CORS Support
Cross-Origin Resource Sharing (CORS) is enabled to allow web-based applications to access the proxy, which is essential for browser-based integrations.

### Logging and Monitoring
Comprehensive logging is implemented to track requests, responses, and errors, with configurable log levels for different deployment environments.

## External Dependencies

### DeepSeek API
- Primary external service that provides the actual AI model capabilities
- Requires API key authentication
- Uses bearer token authentication pattern

### HTTP Client Libraries
- **httpx**: Modern async HTTP client for making requests to DeepSeek API
- **uvicorn**: ASGI server for running the FastAPI application

### Web Framework Dependencies
- **FastAPI**: Core web framework for API endpoints
- **Pydantic**: Data validation and serialization

### Development and Runtime
- **Python 3.7+**: Runtime environment
- Environment variables for configuration management
- No database dependencies (stateless proxy design)