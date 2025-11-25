from fastapi import FastAPI, HTTPException
import httpx
import os
from models import ForecastQuestion, ForecastResult, AdjustmentDetail

app = FastAPI(
    title="Wildebeast LLM API",
    description="A secure Tool-Calling endpoint for LLM agents to access forecast capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Get API key from environment variable (for wildebeast API authentication)
RENDER_AUTH_TOKEN = os.getenv("WILDEBEAST_RENDER_TOKEN")
if not RENDER_AUTH_TOKEN:
    raise RuntimeError("WILDEBEAST_RENDER_TOKEN environment variable is not set")


@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    """
    return {
        "service": "Wildebeast LLM API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "forecast": "/api/v1/forecast",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    Returns 200 if the service is operational.
    """
    return {"status": "healthy", "service": "wildebeast-llm-api"}


@app.post("/api/v1/forecast", response_model=ForecastResult)
async def forecast(question: ForecastQuestion):
    """
    Generate a forecast based on a natural language question.
    
    This endpoint accepts a forecast question and returns detailed probability
    analysis including confidence ranges, baseline values, terrain adjustments,
    and a full explanation.
    
    **Use Case for LLM Agents:**
    - LLM agents can call this endpoint as a tool/function to get forecast
      probabilities for any question
    - The response includes structured data that can be easily parsed and
      presented to users
    - Ideal for decision-making scenarios where probability estimates are needed
    
    **Example Questions:**
    - "What is the probability of rain tomorrow in San Francisco?"
    - "What are the chances of a successful product launch?"
    - "How likely is it that the stock market will rise next week?"
    
    **Returns:**
    - `final_probability`: The calculated probability (0.0 to 1.0)
    - `confidence_range_low`: Lower bound of confidence interval
    - `confidence_range_high`: Upper bound of confidence interval
    - `baseline_value`: The baseline probability before adjustments
    - `terrain_adjustments`: List of factors that adjusted the probability
    - `full_explanation`: Human-readable explanation of the forecast
    """
    # wildebeast API expects X-Api-Key header, not Authorization Bearer
    headers = {"X-Api-Key": RENDER_AUTH_TOKEN}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wildebeast.onrender.com/api/forecast",
                json={"message": question.question},
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                wildebeast_response = response.json()
                # Transform wildebeast response format to our ForecastResult format
                forecast_data = wildebeast_response.get("response", {})
                rationale = wildebeast_response.get("rationale", "")
                
                # Extract and convert probability values
                final_prob_str = forecast_data.get("final_probability", "0%").replace("%", "")
                try:
                    final_probability = float(final_prob_str) / 100.0
                except (ValueError, TypeError):
                    final_probability = 0.0
                
                # Parse confidence range
                confidence_range = forecast_data.get("confidence_range", "0%-0%")
                try:
                    low_str, high_str = confidence_range.split("-")
                    confidence_range_low = float(low_str.replace("%", "")) / 100.0
                    confidence_range_high = float(high_str.replace("%", "")) / 100.0
                except (ValueError, AttributeError):
                    confidence_range_low = max(0.0, final_probability - 0.05)
                    confidence_range_high = min(1.0, final_probability + 0.05)
                
                # Extract baseline
                baseline_str = forecast_data.get("baseline", "0%").replace("%", "")
                try:
                    baseline_value = float(baseline_str) / 100.0
                except (ValueError, TypeError):
                    baseline_value = final_probability
                
                # Transform adjustments
                adjustments = forecast_data.get("adjustments", [])
                terrain_adjustments = [
                    AdjustmentDetail(
                        factor_name=adj.get("label", "Unknown"),
                        adjustment_percentage=float(adj.get("impact", "0%").replace("%", "").replace("+", ""))
                    )
                    for adj in adjustments
                ]
                
                return ForecastResult(
                    final_probability=final_probability,
                    confidence_range_low=confidence_range_low,
                    confidence_range_high=confidence_range_high,
                    baseline_value=baseline_value,
                    terrain_adjustments=terrain_adjustments,
                    full_explanation=rationale
                )
            else:
                # Return structured error for LLM agents
                error_detail = f"Render API request failed with status code {response.status_code}"
                try:
                    error_body = response.json()
                    # Try to get the actual error message from wildebeast API
                    if "error" in error_body:
                        error_detail = error_body["error"]
                    elif "message" in error_body:
                        error_detail = error_body["message"]
                    elif "detail" in error_body:
                        error_detail = error_body["detail"]
                    else:
                        error_detail = str(error_body)
                except:
                    error_detail = response.text or error_detail
                
                raise HTTPException(
                    status_code=500,
                    detail={
                        "error": "forecast_service_error",
                        "message": error_detail,
                        "status_code": response.status_code
                    }
                )
    except httpx.TimeoutException as e:
        raise HTTPException(
            status_code=504,
            detail={
                "error": "timeout_error",
                "message": "Request to forecast service timed out. The service may be overloaded.",
                "timeout_seconds": 30.0
            }
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "service_unavailable",
                "message": f"Failed to connect to forecast service: {str(e)}"
            }
        )
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"An unexpected error occurred: {str(e)}"
            }
        )

