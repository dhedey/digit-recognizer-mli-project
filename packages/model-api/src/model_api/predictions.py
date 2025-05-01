from typing import List
import numpy as np
from model import FirstModel, SecondModel
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
            predict_cnn_v1(self),
            predict_cnn_v2(self),
        ]

def predict_random(data: PredictionDigitData) -> PredictionClassification:
    # Uses the whole image data to seed the RNG to make it deterministic
    rng = np.random.default_rng([i for i in data.pixels.data.tobytes()])
    random_label = rng.integers(0, 9).item()
    return PredictionClassification(
        model="random",
        predicted_digit=random_label,
        confidence=0.1,
    )

first_model = FirstModel()

def predict_cnn_v1(data: PredictionDigitData) -> PredictionClassification:
    from PIL import Image
    (predicted_digit, confidence) = first_model.predict(Image.fromarray(data.pixels), 0.1, scale=False)
    return PredictionClassification(
        model="cnn-v1",
        predicted_digit=predicted_digit,
        confidence=confidence,
    )

second_model = SecondModel()

def predict_cnn_v2(data: PredictionDigitData) -> PredictionClassification:
    from PIL import Image
    (predicted_digit, confidence) = second_model.predict(Image.fromarray(data.pixels), 0.4, scale=True)
    return PredictionClassification(
        model="cnn-v2",
        predicted_digit=predicted_digit,
        confidence=confidence,
    )