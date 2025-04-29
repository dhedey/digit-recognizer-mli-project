from typing import List
import numpy as np
from model import CenteredDigitModel
from dataclasses import dataclass

@dataclass
class PredictionClassification:
    model: str
    predicted_digit: int
    """Confidence in prediction, between 0 and 1"""
    confidence: float

@dataclass
class PredictionDigitData:
    pixels: np.array

    def create_predictions(self) -> List[PredictionClassification]:
        return [
            # predict_random(self),
            predict_nn(self),
        ]

def predict_random(data: PredictionDigitData) -> PredictionClassification:
    # Uses the whole image data to seed the RNG to make it deterministic
    rng = np.random.default_rng([i for i in data.pixels.data.tobytes()])
    random_label = rng.integers(0, 9).item()
    return PredictionClassification(
        model="random",
        predicted_digit=random_label,
        confidence=0,
    )

centered_digit_model = CenteredDigitModel()

def predict_nn(data: PredictionDigitData) -> PredictionClassification:
    from PIL import Image
    (predicted_digit, confidence) = centered_digit_model.predict(Image.fromarray(data.pixels))
    return PredictionClassification(
        model="nn-centered",
        predicted_digit=predicted_digit,
        confidence=confidence,
    )