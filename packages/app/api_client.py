import helpers
import requests
import numpy as np

API_ROOT = helpers.load_env_string("MODEL_API_BASE_URL")

def recognize_digit(pixels: np.array):
    return requests.post(
        f'{API_ROOT}/recognize-digit',
        json = {
            # Convert to JSON array
            "pixels": [[pixel.item() for pixel in row] for row in pixels]
        }
    ).json()