from pydantic import BaseModel


class ForecastQuestion(BaseModel):
    """Input model for forecast questions."""
    question: str


class AdjustmentDetail(BaseModel):
    """Model for terrain adjustment details."""
    factor_name: str
    adjustment_percentage: float


class ForecastResult(BaseModel):
    """Main output model for forecast results."""
    final_probability: float
    confidence_range_low: float
    confidence_range_high: float
    baseline_value: float
    terrain_adjustments: list[AdjustmentDetail]
    full_explanation: str

