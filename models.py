from pydantic import BaseModel, Field


class ForecastQuestion(BaseModel):
    """
    Input model for forecast questions.
    
    LLM agents should provide a natural language question about any forecastable event.
    The question will be processed to generate probability estimates and analysis.
    """
    question: str = Field(
        ...,
        description="A natural language question about a forecastable event or outcome",
        example="What is the probability of rain tomorrow in San Francisco?"
    )


class AdjustmentDetail(BaseModel):
    """
    Model for terrain adjustment details.
    
    Represents a factor that adjusted the baseline probability calculation.
    """
    factor_name: str = Field(
        ...,
        description="The name of the factor that influenced the forecast",
        example="Historical Weather Patterns"
    )
    adjustment_percentage: float = Field(
        ...,
        description="The percentage adjustment applied to the baseline (can be positive or negative)",
        example=5.2
    )


class ForecastResult(BaseModel):
    """
    Main output model for forecast results.
    
    Provides comprehensive probability analysis including confidence intervals,
    baseline values, adjustment factors, and a human-readable explanation.
    """
    final_probability: float = Field(
        ...,
        description="The final calculated probability as a decimal (0.0 to 1.0)",
        example=0.75,
        ge=0.0,
        le=1.0
    )
    confidence_range_low: float = Field(
        ...,
        description="Lower bound of the 95% confidence interval",
        example=0.68,
        ge=0.0,
        le=1.0
    )
    confidence_range_high: float = Field(
        ...,
        description="Upper bound of the 95% confidence interval",
        example=0.82,
        ge=0.0,
        le=1.0
    )
    baseline_value: float = Field(
        ...,
        description="The baseline probability before any adjustments were applied",
        example=0.70,
        ge=0.0,
        le=1.0
    )
    terrain_adjustments: list[AdjustmentDetail] = Field(
        ...,
        description="List of factors that adjusted the baseline probability",
        example=[
            {"factor_name": "Historical Patterns", "adjustment_percentage": 3.5},
            {"factor_name": "Current Conditions", "adjustment_percentage": 1.5}
        ]
    )
    full_explanation: str = Field(
        ...,
        description="A comprehensive human-readable explanation of the forecast and how it was calculated",
        example="The forecast indicates a 75% probability based on historical data showing..."
    )

