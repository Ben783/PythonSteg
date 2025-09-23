import cv2
import numpy as np
from PIL import Image

def transfer_colour_preserve_grayscale(original_rgb_path, altered_greyscale_path, output_path):
    """
    Transfers color from the original RGB image to the altered greyscale image
    while preserving the exact greyscale values of the altered image.

    Args:
        original_rgb_path (str): Path to the original RGB image.
        altered_greyscale_path (str): Path to the altered greyscale image.
        output_path (str): Path to save the final colorized image.
    """
    # Load the original RGB image and the altered greyscale image
    original_rgb = cv2.imread(original_rgb_path)  # Original RGB image
    altered_greyscale = cv2.imread(altered_greyscale_path, cv2.IMREAD_GRAYSCALE)  # Altered greyscale image

    if original_rgb is None or altered_greyscale is None:
        raise ValueError("Could not load one or more images. Check file paths.")

    # Resize original RGB image to match greyscale size (if different)
    if original_rgb.shape[:2] != altered_greyscale.shape:
        original_rgb = cv2.resize(original_rgb, (altered_greyscale.shape[1], altered_greyscale.shape[0]))

    # Convert the original RGB image to YUV color space
    original_yuv = cv2.cvtColor(original_rgb, cv2.COLOR_BGR2YUV)

    # Replace the Y (luminance) channel with the altered greyscale values
    modified_yuv = original_yuv.copy()
    modified_yuv[:, :, 0] = altered_greyscale  # Set Y channel to altered greyscale values

    # Convert back to RGB
    modified_rgb = cv2.cvtColor(modified_yuv, cv2.COLOR_YUV2RGB)

    # Convert to PIL Image and save using Pillow
    pil_image = Image.fromarray(modified_rgb)
    pil_image.save(output_path, format="PNG")  # Save as PNG or any preferred format
    print(f"Colorized RGB image saved to {output_path}")

    # Verify greyscale values are perfectly preserved
    reconstructed_greyscale = cv2.cvtColor(modified_rgb, cv2.COLOR_RGB2GRAY)

    if np.array_equal(altered_greyscale, reconstructed_greyscale):
        preserved = True
        print("Success: The greyscale values are perfectly preserved.")
    else:
        preserved = False
        print("Warning: Some small differences in greyscale values were detected.")

    return preserved



