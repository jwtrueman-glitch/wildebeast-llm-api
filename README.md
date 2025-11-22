# Wildebeast LLM API

A secure, production-ready FastAPI service that provides forecast capabilities as a Tool-Calling endpoint for Large Language Model (LLM) agents like OpenAI GPT, Google Gemini, and other function-calling AI systems.

## 🎯 Purpose

This API serves as a **Tool-Calling endpoint** that LLM agents can use to:
- Get probability forecasts for any question
- Access structured forecast data with confidence intervals
- Receive detailed explanations of forecast calculations
- Make data-driven decisions based on probability estimates

## 🚀 Quick Start

### For LLM Agents

**Endpoint:** `POST /api/v1/forecast`

**Request:**
```json
{
  "question": "What is the probability of rain tomorrow in San Francisco?"
}
```

**Response:**
```json
{
  "final_probability": 0.75,
  "confidence_range_low": 0.68,
  "confidence_range_high": 0.82,
  "baseline_value": 0.70,
  "terrain_adjustments": [
    {
      "factor_name": "Historical Weather Patterns",
      "adjustment_percentage": 5.2
    }
  ],
  "full_explanation": "The forecast indicates a 75% probability based on..."
}
```

### OpenAPI Specification

FastAPI automatically generates a complete OpenAPI 3.0 specification that LLM agents can use for tool discovery:

- **Interactive Docs:** `https://your-domain.com/docs` (Swagger UI)
- **ReDoc:** `https://your-domain.com/redoc` (Alternative docs)
- **OpenAPI JSON:** `https://your-domain.com/openapi.json` (Machine-readable spec)

**For LLM Integration:**
Most LLM agents can directly consume the OpenAPI spec from `/openapi.json` to automatically discover and use this endpoint as a tool/function.

## 📋 API Documentation

### Endpoints

#### `POST /api/v1/forecast`

Generate a forecast based on a natural language question.

**Request Body:**
- `question` (string, required): A natural language question about a forecastable event

**Response:**
- `final_probability` (float): The calculated probability (0.0 to 1.0)
- `confidence_range_low` (float): Lower bound of confidence interval
- `confidence_range_high` (float): Upper bound of confidence interval
- `baseline_value` (float): Baseline probability before adjustments
- `terrain_adjustments` (array): List of factors that adjusted the probability
- `full_explanation` (string): Human-readable explanation

**Example Usage:**
```bash
curl -X POST "https://your-domain.com/api/v1/forecast" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the probability of success for this product launch?"}'
```

#### `GET /health`

Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "service": "wildebeast-llm-api"
}
```

## 🔧 LLM Agent Integration

### For OpenAI GPT Function Calling

```python
import openai

# The OpenAPI spec can be converted to OpenAI function format
functions = [
    {
        "type": "function",
        "function": {
            "name": "forecast",
            "description": "Get probability forecasts for any question",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "A natural language question about a forecastable event"
                    }
                },
                "required": ["question"]
            }
        }
    }
]

# Use in your OpenAI API call
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "What's the chance of rain tomorrow?"}],
    functions=functions,
    function_call="auto"
)
```

### For Google Gemini Function Calling

```python
import google.generativeai as genai

# Gemini can use the OpenAPI spec directly
# Fetch the OpenAPI spec from /openapi.json and use it as a tool
```

### Direct OpenAPI Consumption

Many LLM frameworks can automatically consume OpenAPI specs:

1. Fetch the OpenAPI spec: `GET /openapi.json`
2. Parse the spec to extract endpoint definitions
3. Convert to the LLM's function calling format
4. Use as a tool in your agent's toolset

## 🐳 Deployment

### Environment Variables

Required:
- `WILDEBEAST_RENDER_TOKEN`: Bearer token for authenticating with the Render API

### Docker

```bash
docker build -t wildebeast-llm-api .
docker run -p 8000:8000 -e WILDEBEAST_RENDER_TOKEN=your_token wildebeast-llm-api
```

### Render.com

The service is configured for Render.com deployment. Ensure:
1. `WILDEBEAST_RENDER_TOKEN` is set in your Render environment variables
2. The Dockerfile is properly configured (already done)
3. The service is set to listen on port 8000

## 🔍 Monitoring & Production Issues

### Three Most Common Production Issues for LLM Tool-Calling

#### 1. **Authentication Errors (401/403)**
**Symptoms:**
- `WILDEBEAST_RENDER_TOKEN` not set or invalid
- 401/403 errors in logs
- Service fails at startup

**Watch for in Render logs:**
```
RuntimeError: WILDEBEAST_RENDER_TOKEN environment variable is not set
```
or
```
Render API request failed with status code 401
```

**Solution:**
- Verify `WILDEBEAST_RENDER_TOKEN` is set in Render environment variables
- Check token hasn't expired
- Ensure token has proper permissions

#### 2. **Timeout Errors (504)**
**Symptoms:**
- LLM agents receive timeout errors
- Requests taking >30 seconds
- Service unavailable errors

**Watch for in Render logs:**
```
timeout_error: Request to forecast service timed out
```

**Solution:**
- Check Render API response times
- Consider increasing timeout (currently 30s) if needed
- Monitor downstream service health
- Implement request queuing if needed

#### 3. **JSON Parsing/Validation Errors (422)**
**Symptoms:**
- LLM agents send malformed requests
- Pydantic validation errors
- Missing required fields

**Watch for in Render logs:**
```
422 Unprocessable Entity
ValidationError: ...
```

**Solution:**
- Ensure LLM agents use correct request format
- Validate OpenAPI spec is correctly exposed
- Check Pydantic model definitions match expectations
- Provide clear error messages in responses

### Additional Issues to Monitor

- **Network Connectivity (503)**: Connection failures to Render API
- **Rate Limiting**: Too many requests from LLM agents
- **Response Format Mismatches**: LLM expecting different response structure

## 📊 Error Responses

The API returns structured error responses for LLM agents:

```json
{
  "error": "timeout_error",
  "message": "Request to forecast service timed out. The service may be overloaded.",
  "timeout_seconds": 30.0
}
```

Error types:
- `forecast_service_error`: Downstream service returned an error
- `timeout_error`: Request timed out
- `service_unavailable`: Cannot connect to forecast service
- `internal_error`: Unexpected server error

## 🛠️ Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export WILDEBEAST_RENDER_TOKEN=your_token

# Run the server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Testing

```bash
# Health check
curl http://localhost:8000/health

# Forecast endpoint
curl -X POST http://localhost:8000/api/v1/forecast \
  -H "Content-Type: application/json" \
  -d '{"question": "Test question"}'
```

## 📝 OpenAPI Specification

**Do you need an explicit OpenAPI file?**

**Answer: No, but it's helpful.**

FastAPI automatically generates a complete OpenAPI 3.0 specification at `/openapi.json`. This is sufficient for most LLM agents. However:

- **Automatic is sufficient**: Most LLM frameworks can consume `/openapi.json` directly
- **Explicit file is optional**: You can export and commit the spec if you want version control
- **Best practice**: Use the auto-generated spec and ensure it's accessible

To export the spec:
```bash
curl http://localhost:8000/openapi.json > openapi.json
```

## 🔐 Security

- Bearer token authentication for downstream API
- Input validation via Pydantic models
- Structured error responses (no sensitive data leakage)
- Health check endpoint for monitoring

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAPI Specification](https://swagger.io/specification/)
- [LLM Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)

## 📄 License

[Add your license here]

---

**Built for LLM Agents** 🤖 | **Production Ready** 🚀 | **OpenAPI Compliant** 📋

