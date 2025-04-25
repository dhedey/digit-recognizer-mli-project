import streamlit as st
import pandas as pd
import numpy as np
import requests
import random
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import io
import base64
from datetime import datetime

RAW_IMAGE_SIZE = 28
DRAWING_SCALE = 8

input_column, predictions_column = st.columns([1, 1])

with input_column:
    with st.container(border = True):
        st.subheader("Input")
        # https://github.com/andfanilo/streamlit-drawable-canvas
        canvas_result = st_canvas(
            stroke_width=10,
            height=RAW_IMAGE_SIZE * DRAWING_SCALE,
            width=RAW_IMAGE_SIZE * DRAWING_SCALE,
            key="canvas",
            # display_toolbar=False,
            update_streamlit=True,  # Can't seem to put it in a form, so instead have it update in realtime
        )

        with st.form("submission_form", border = False):
            expected_label = st.number_input("Actual digit", 0, 9, )
            form_submitted = st.form_submit_button("Submit drawing and expected label")

if canvas_result.image_data is not None:
    # We have an N = RAW_IMAGE_SIZE * DRAWING_SCALE image as an (N, N, 4 = (R, G, B, A)) dimensional array
    # We want to down-scale to a (RAW_IMAGE_SIZE, RAW_IMAGE_SIZE, 4) array by taking means of (DRAWING_SCALE * DRAWING_SCALE) blocks
    greyscale_data = np.matmul(canvas_result.image_data, [1.0/3, 1.0/3, 1.0/3, 0])
    alpha_channel = np.matmul(canvas_result.image_data, [0, 0, 0, 1.0/256])
    background_mask = np.ones_like(alpha_channel) - alpha_channel
    # The canvas assumes a white background
    background = np.full_like(alpha_channel, 255, dtype=np.float64)
    single_channel_data = (background * background_mask + greyscale_data * alpha_channel)
    reshaped_data: np.array = np.reshape(single_channel_data, shape=(RAW_IMAGE_SIZE, DRAWING_SCALE, RAW_IMAGE_SIZE, DRAWING_SCALE))
    meaned_data = np.mean(reshaped_data, axis=(1, 3))
    vision_pixels = meaned_data.astype(np.uint8)
else:
    vision_pixels = np.full(shape=(RAW_IMAGE_SIZE, RAW_IMAGE_SIZE), fill_value=255, dtype=np.uint8)

with predictions_column:
    with st.container(border=True):
        st.subheader("Predictions")
        canvas_pixels = np.vstack([
            np.hstack([
                np.broadcast_to(
                    # Three copies of greyscale value, then alpha channel
                    # The min just makes the background slightly blue
                    np.array([min(vision_pixel, 240), min(vision_pixel, 245), min(vision_pixel, 255), 255]),
                    # Repeat using broadcasting to SCALE * SCALE
                    (DRAWING_SCALE, DRAWING_SCALE, 4),
                )
                for vision_pixel in vision_pixels_row
            ]) for vision_pixels_row in vision_pixels
        ])
        st.image(canvas_pixels)

        predictions = [
            { "model": "random", "label": random.randint(0, 9), "confidence": 0.0, }
        ]

        table_data = pd.DataFrame({
                "Model": [prediction["model"] for prediction in predictions],
                "Prediction": [
                    # f'<span style="font-size: 30px; font-weight: bold">`{prediction["label"]}`</span>'
                    prediction["label"]
                    for prediction in predictions
                ],
                "Confidence": [f'{prediction["confidence"]:2.1%}' for prediction in predictions],
        })
        table_data.set_index('Model', inplace=True)
        st.table(table_data)

if "predictions" not in st.session_state:
    st.session_state.predictions = []

predictions = st.session_state.predictions

if form_submitted:
    image_io = io.BytesIO()
    image = Image.fromarray(vision_pixels)
    image.save(image_io, format="PNG")
    base64_bytes = base64.b64encode(image_io.getvalue())
    data_url = f"data:image/png;base64,{base64_bytes.decode('ascii')}"
    predictions.append({
        "Image": data_url,
        "Expected": expected_label,
        "Timestamp": datetime.now()
    })

with st.container(border = True):
    st.subheader("Previous uploads")
    uploads_table = pd.DataFrame(predictions, columns=["Image", "Expected", "Timestamp"])
    uploads_table.set_index('Timestamp', inplace=True)

    st.dataframe(
        uploads_table,
        column_config = {
            "Image": st.column_config.ImageColumn()
        }
    )


def load_env_string(name: str) -> str:
    """Load string environment variable"""
    import os
    loaded = os.getenv(name)
    if loaded is None:
        raise ValueError(f"Environment variable {name} not set")
    return loaded


API_ROOT = load_env_string("MODEL_API_BASE_URL")

def fetch_data():
    return requests.get(API_ROOT).json()["value"]

st.write(f"API response is: {fetch_data()}")