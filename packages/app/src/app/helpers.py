import numpy as np

def load_env_string(name: str) -> str:
    """Load string environment variable"""
    import os
    loaded = os.getenv(name)
    if loaded is None:
        raise ValueError(f"Environment variable {name} not set")
    return loaded

def pixels_to_png_bytes(pixels: np.array) -> bytes:
    """Convert a numpy array of pixels to a PNG image in bytes"""
    from PIL import Image
    import io
    image_io = io.BytesIO()
    image = Image.fromarray(pixels)
    image.save(image_io, format="PNG")
    return image_io.getvalue()

def png_bytes_to_data_uri(png_bytes: bytes) -> str:
    import base64
    return f"data:image/png;base64,{base64.b64encode(png_bytes).decode('ascii')}"

# Could probably use torchvision to help here, but I wanted to get some numpy experience
def rgba_to_downscaled_greyscale(rgba: np.array, output_shape: (int, int)) -> np.array:
    """
    Takes an RGBA image from a canvas and downscales it to a greyscale image of the given shape.

    More specifically, let (Y, X) = (output_height, output_width) = output_shape.

    > Our input should be a (Y * y_scale, X * x_scale, 4 = (R, G, B, A)) shaped byte array with
      y_scale and x_scale being integers.
    > This function outputs a (Y, X) shaped byte array, created by:
      * Flattening the RGBA channels into one greyscale channel
      * Downscaling by taking the mean of this greyscale channel over (y_scale, x_scale) blocks
    """

    # STEP 1: Sanity check the inputs and calculate the scale factors
    (input_height, input_width, channel_count) = rgba.shape
    (output_height, output_width) = output_shape
    if not input_height % output_height == 0 or not input_width % output_width == 0:
        raise ValueError(f"The output shape {output_shape} is not an integer scale of the input shape {(input_height, input_width)}")
    if not channel_count == 4:
        raise ValueError(f"Expected 4 channels, got {channel_count}")

    y_scale = input_height // output_height
    x_scale = input_width // output_width

    # STEP 2: Handle the greyscale conversion and alpha blending assuming a white background
    greyscale_foreground = np.matmul(rgba, [1.0/3, 1.0/3, 1.0/3, 0])
    alpha_mask = np.matmul(rgba, [0, 0, 0, 1.0/256])
    background_mask = np.ones_like(alpha_mask) - alpha_mask
    background = np.full_like(alpha_mask, 255, dtype=np.float64)
    opaque_greyscale = (background * background_mask + greyscale_foreground * alpha_mask)

    # STEP 3: Downscale the image by taking the mean of the greyscale values in each block
    reshaped_data: np.array = np.reshape(opaque_greyscale, shape=(output_height, y_scale, output_width, x_scale))
    meaned_data = np.mean(reshaped_data, axis=(1, 3))
    return meaned_data.astype(np.uint8)