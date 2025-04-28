import streamlit as st
import pandas as pd
import numpy as np
from streamlit_drawable_canvas import st_canvas
from datetime import datetime
import helpers
import api_client

RAW_IMAGE_SIZE = 28
DRAWING_SCALE = 8

st.title("Digit Recognizer")
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
            # Have it update the prediction in realtime
            update_streamlit=True,
        )

        with st.form("submission_form", border = False):
            expected_label = st.number_input("Drawn digit", 0, 9, )
            form_submitted = st.form_submit_button("Submit drawing / label pair")

# When the canvas first loads, it has a shape of (300, 600, 4) briefly
# which causes errors in the scaling code, so go to the fallback then.
if canvas_result.image_data is not None and canvas_result.image_data.shape == (RAW_IMAGE_SIZE * DRAWING_SCALE, RAW_IMAGE_SIZE * DRAWING_SCALE, 4):
    vision_pixels = helpers.rgba_to_downscaled_greyscale(
        canvas_result.image_data,
        output_shape=(RAW_IMAGE_SIZE, RAW_IMAGE_SIZE)
    )
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
                    # Broadcast these 4 values to a block of size DRAWING_SCALE * DRAWING_SCALE
                    (DRAWING_SCALE, DRAWING_SCALE, 4),
                )
                for vision_pixel in vision_pixels_row
            ]) for vision_pixels_row in vision_pixels
        ])
        st.image(canvas_pixels)

        predictions = api_client.recognize_digit(vision_pixels)

        table_data = pd.DataFrame({
            "Model": [prediction["model"] for prediction in predictions],
            "Prediction": [prediction["predicted_digit"] for prediction in predictions],
            "Confidence": [f'{prediction["confidence"]:2.1%}' for prediction in predictions],
        })
        table_data.set_index('Model', inplace=True)
        st.table(table_data)

if "submissions" not in st.session_state:
    st.session_state.submissions = []

submissions = st.session_state.submissions

if form_submitted:
    # TODO - Move to postgres in API
    submissions.append({
        "image_png": helpers.pixels_to_png_bytes(vision_pixels),
        "label": expected_label,
        "predictions": predictions,
        "timestamp": datetime.now()
    })

with st.container(border = True):
    st.subheader("Previous submissions")
    display_submissions = [
        {
            "Time": submission["timestamp"],
            "Image": helpers.png_bytes_to_data_uri(submission["image_png"]),
            "Label": submission["label"],
        } | {
            f"Model: {prediction["model"]}": f"{prediction["predicted_digit"]} ({prediction["confidence"]:2.1%})" for prediction in submission["predictions"]
        }
        for submission in submissions
    ]
    columns = ["Time", "Image", "Label"] if len(display_submissions) == 0 else None
    uploads_table = pd.DataFrame(display_submissions, columns=columns)
    uploads_table.set_index('Time', inplace=True)

    st.dataframe(
        uploads_table,
        column_config = {
            "Image": st.column_config.ImageColumn()
        }
    )
