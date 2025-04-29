from fastapi import FastAPI, status, HTTPException
from typing import List, Self
import numpy as np
from .api_models import HealthCheck, ApiDigitData, ApiSubmittedDigit, ApiDigitClassification, ApiPreviousSubmission
from .submission_store import submission_store, DbSubmission

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

@app.post("/recognize-digit")
async def recognize_digit(data: ApiDigitData) -> list[ApiDigitClassification]:
    return [ApiDigitClassification.from_prediction_model(x) for x in data.to_prediction_model().create_predictions()]

def pixels_to_png_bytes(pixels: np.array) -> bytes:
    """Convert a numpy array of pixels to a PNG image in bytes"""
    from PIL import Image
    import io
    image_io = io.BytesIO()
    image = Image.fromarray(pixels)
    image.save(image_io, format="PNG")
    return image_io.getvalue()

@app.post("/submit-digit")
async def submit_digit(data: ApiSubmittedDigit):
    import datetime
    pixel_data = data.digit.to_prediction_model()
    label = data.label
    if not (0 <= label <= 9):
        raise HTTPException(status_code=400, detail="Label must be between 0 and 9")
    predictions = pixel_data.create_predictions()
    submission_store.add_submission(
        DbSubmission(
            timestamp=datetime.datetime.now(datetime.UTC),
            png_bytes=pixels_to_png_bytes(pixel_data.pixels),
            label=label,
            predictions=[ApiDigitClassification.from_prediction_model(x).to_db_model() for x in predictions],
        )
    )

@app.get("/recent-submissions")
async def recent_submissions() -> List[ApiPreviousSubmission]:
    return [ApiPreviousSubmission.from_db_model(x) for x in submission_store.get_recent_submissions(20)]
