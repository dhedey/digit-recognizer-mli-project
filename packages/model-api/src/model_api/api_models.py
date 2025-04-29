from pydantic import BaseModel
from typing import List

class ApiDigitData(BaseModel):
    pixels: List[List[int]]

class ApiSubmittedDigit(BaseModel):
    digit: ApiDigitData
    label: int

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

class DigitClassification(BaseModel):
    model: str
    predicted_digit: int
    """Confidence in prediction, between 0 and 1"""
    confidence: float

class PreviousSubmission(BaseModel):
    timestamp: str
    png_base64: str
    label: int
    predictions: List[DigitClassification]
