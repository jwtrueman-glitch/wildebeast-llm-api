from fastapi import FastAPI, HTTPException
import httpx
import os
from models import ForecastQuestion, ForecastResult

app = FastAPI()

# Get Bearer token from environment variable
RENDER_AUTH_TOKEN = os.getenv("WILDEBEAST_RENDER_TOKEN")
if not RENDER_AUTH_TOKEN:
    raise RuntimeError("WILDEBEAST_RENDER_TOKEN environment variable is not set")


@app.post("/api/v1/forecast", response_model=ForecastResult)
async def forecast(question: ForecastQuestion):
    """
    Forecast endpoint that sends the question to the Render API.
    """
    headers = {"Authorization": f"Bearer {RENDER_AUTH_TOKEN}"}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://wildebeast.onrender.com/api/forecast",
                json={"question": question.question},
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Render API request failed with status code {response.status_code}"
                )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Render API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the forecast: {str(e)}"
        )

