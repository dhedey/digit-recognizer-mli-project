from pydantic import BaseModel
from typing import List, Self
from fastapi import HTTPException
import numpy as np

from .submission_store import DbSubmission
from .predictions import PredictionDigitData, PredictionClassification

class ApiDigitData(BaseModel):
    pixels: List[List[int]]

    def to_prediction_model(self) -> PredictionDigitData:
        try:
            pixels = np.array(self.pixels, dtype=np.uint8)
            pixels = pixels.reshape((28, 28))
        except ValueError as e:
            raise HTTPException(status_code=400,
                                detail="Invalid pixel data shape, expected 28 x 28 integers from 0-255") from e
        return PredictionDigitData(
            pixels=pixels
        )

class ApiSubmittedDigit(BaseModel):
    digit: ApiDigitData
    label: int

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

class ApiDigitClassification(BaseModel):
    model: str
    predicted_digit: int
    """Confidence in prediction, between 0 and 1"""
    confidence: float

    @classmethod
    def from_db_model(cls, db_model: dict) -> Self:
        return cls(
            model=db_model["model"],
            predicted_digit=db_model["predicted_digit"],
            confidence=db_model["confidence"],
        )

    def to_db_model(self) -> dict:
        return {
            "model": self.model,
            "predicted_digit": self.predicted_digit,
            "confidence": self.confidence,
        }

    @classmethod
    def from_prediction_model(cls, prediction_model: PredictionClassification) -> Self:
        return cls(
            model=prediction_model.model,
            predicted_digit=prediction_model.predicted_digit,
            confidence=prediction_model.confidence,
        )

def png_bytes_to_base64(png_bytes: bytes) -> str:
    import base64
    return base64.b64encode(png_bytes).decode('ascii')

class ApiPreviousSubmission(BaseModel):
    timestamp: str
    png_base64: str
    label: int
    predictions: List[ApiDigitClassification]

    @classmethod
    def from_db_model(cls, db_model: DbSubmission) -> Self:
        return cls(
            timestamp=db_model.timestamp.isoformat(),
            png_base64=png_bytes_to_base64(db_model.png_bytes),
            label=db_model.label,
            predictions=[ApiDigitClassification.from_db_model(x) for x in db_model.predictions],
        )
