from fastapi import FastAPI, status, HTTPException
from typing import List
import numpy as np
from .api_models import HealthCheck, ApiDigitData, ApiSubmittedDigit, DigitClassification, PreviousSubmission
from .submission_store import InMemorySubmissionStore
from dataclasses import dataclass
from model import CenteredDigitModel

app = FastAPI()

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

def create_digit_data(api_data: ApiDigitData) -> DigitData:
    try:
        pixels = np.array(api_data.pixels, dtype=np.uint8)
        pixels = pixels.reshape((28, 28))
    except ValueError as e:
        raise HTTPException(status_code=400,
                            detail="Invalid pixel data shape, expected 28 x 28 integers from 0-255") from e
    return DigitData(
        pixels=pixels
    )

@app.post("/recognize-digit")
async def recognize_digit(data: ApiDigitData) -> list[DigitClassification]:
    pixel_data = create_digit_data(data)
    return create_predictions(pixel_data)

submission_store = InMemorySubmissionStore()

def pixels_to_png_bytes(pixels: np.array) -> bytes:
    """Convert a numpy array of pixels to a PNG image in bytes"""
    from PIL import Image
    import io
    image_io = io.BytesIO()
    image = Image.fromarray(pixels)
    image.save(image_io, format="PNG")
    return image_io.getvalue()

def png_bytes_to_base64(png_bytes: bytes) -> str:
    import base64
    return base64.b64encode(png_bytes).decode('ascii')


@app.post("/submit-digit")
async def submit_digit(data: ApiSubmittedDigit):
    import datetime
    pixel_data = create_digit_data(data.digit)
    label = data.label
    if not (0 <= label <= 9):
        raise HTTPException(status_code=400, detail="Label must be between 0 and 9")
    predictions = create_predictions(pixel_data)
    submission_store.add_submission(
        PreviousSubmission(
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            png_base64=png_bytes_to_base64(pixels_to_png_bytes(pixel_data.pixels)),
            label=label,
            predictions=predictions,
        )
    )

@app.get("/recent-submissions")
async def recent_submissions() -> List[PreviousSubmission]:
    return submission_store.get_recent_submissions(20)

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
