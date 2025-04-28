from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
import numpy as np
from dataclasses import dataclass
from model import CenteredDigitModel

app = FastAPI()

class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""
    status: str = "OK"

@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
async def health_check() -> HealthCheck:
    return HealthCheck(status="OK")

@dataclass
class DigitData:
    pixels: np.array

class ApiDigitData(BaseModel):
    pixels: List[List[int]]

    def to_numpy(self) -> DigitData:
        try:
            pixels = np.array(self.pixels, dtype=np.uint8)
            pixels = pixels.reshape((28, 28))
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Invalid pixel data shape, expected 28 x 28 integers from 0-255") from e
        return DigitData(
            pixels=pixels
        )

class ApiSubmittedDigit(BaseModel):
    digit: ApiDigitData
    label: int

class DigitClassification(BaseModel):
    model: str
    predicted_digit: int
    """Confidence in prediction, between 0 and 1"""
    confidence: float

@app.post("/recognize-digit")
async def recognize_digit(data: ApiDigitData) -> list[DigitClassification]:
    pixel_data = data.to_numpy()
    return create_predictions(pixel_data)

@app.post("/submit-digit")
async def submit_digit(data: ApiSubmittedDigit):
    pixel_data = data.to_numpy()
    label = data.label
    if not (0 <= label <= 9):
        raise HTTPException(status_code=400, detail="Label must be between 0 and 9")
    predictions = create_predictions(pixel_data)
    # TODO: Move pixels_to_png_bytes here
    # TODO: Store the label and predictions in a database

def create_predictions(data: DigitData) -> List[DigitClassification]:
    return [
        predict_random(data),
        predict_nn(data),
    ]

def predict_random(data: DigitData) -> DigitClassification:
    # Uses the whole image data to seed the RNG to make it deterministic
    rng = np.random.default_rng([i for i in data.pixels.data.tobytes()])
    random_label = rng.integers(0, 9).item()
    return DigitClassification(
        model="random",
        predicted_digit=random_label,
        confidence=0,
    )

centered_digit_model = CenteredDigitModel()

def predict_nn(data: DigitData) -> DigitClassification:
    from PIL import Image
    (predicted_digit, confidence) = centered_digit_model.predict(Image.fromarray(data.pixels))
    return DigitClassification(
        model="nn-centered",
        predicted_digit=predicted_digit,
        confidence=confidence,
    )

@app.get("/")
async def root():
    return {"value": 1337}