import helpers
import requests
import numpy as np

API_ROOT = helpers.load_env_string("MODEL_API_BASE_URL")

def digit_json(pixels: np.array):
    return {
        # Convert to JSON array
        "pixels": [[pixel.item() for pixel in row] for row in pixels]
    }

def recognize_digit(pixels: np.array):
    return requests.post(
        f'{API_ROOT}/recognize-digit',
        json = digit_json(pixels),
    ).json()

def submit_digit(pixels: np.array, label: int):
    return requests.post(
        f'{API_ROOT}/submit-digit',
        json = {
            "digit": digit_json(pixels),
            "label": label,
        }
    ).json()

def recent_submissions():
    return requests.get(
        f'{API_ROOT}/recent-submissions'
    ).json()