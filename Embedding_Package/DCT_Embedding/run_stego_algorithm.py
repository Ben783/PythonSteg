import cv2
import struct
import bitstring
import numpy as np
from . import zigzag as zz
from . import image_preparation as img
from . import data_embedding as stego

def embed_secret_message_in_image(secret_message, cover_image_filepath, stego_image_filepath):

    with open(secret_message, "r") as messageFile:
        secret_message = messageFile.read()
    """
    Embeds a secret message into an image using DCT-based steganography.

    Args:
    cover_image_filepath (str): The file path of the cover image.
    stego_image_filepath (str): The file path where the stego image will be saved.
    secret_message (str): The secret message to be embedded into the image.
    """
    NUM_CHANNELS = 3

    # Read the cover image
    raw_cover_image = cv2.imread(cover_image_filepath, flags=cv2.IMREAD_COLOR)
    height, width = raw_cover_image.shape[:2]

    # Force image dimensions to be 8x8 compliant
    while height % 8: height += 1  # Rows
    while width % 8: width += 1  # Cols
    valid_dim = (width, height)
    padded_image = cv2.resize(raw_cover_image, valid_dim)

    cv2.imwrite('Cover_image_8x8.png', padded_image)

    # Convert image to float32 and YCC color space
    cover_image_f32 = np.float32(padded_image)
    cover_image_YCC = img.YCC_Image(cv2.cvtColor(cover_image_f32, cv2.COLOR_BGR2YCrCb))

    # Placeholder for holding stego image data
    stego_image = np.empty_like(cover_image_f32)

    for chan_index in range(NUM_CHANNELS):
        # FORWARD DCT STAGE
        dct_blocks = [cv2.dct(block) for block in cover_image_YCC.channels[chan_index]]

        # QUANTIZATION STAGE
        dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]

        # Sort DCT coefficients by frequency
        sorted_coefficients = [zz.zigzag(block) for block in dct_quants]

        # Embed data in Luminance layer (channel 0)
        if chan_index == 0:
            # DATA INSERTION STAGE
            secret_data = ""
            for char in secret_message.encode('ascii'):
                secret_data += bitstring.pack('uint:8', char)
            embedded_dct_blocks = stego.embed_encoded_data_into_DCT(secret_data, sorted_coefficients)
            desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in embedded_dct_blocks]
        else:
            # Reorder coefficients to how they originally were (for non-luminance channels)
            desorted_coefficients = [zz.inverse_zigzag(block, vmax=8, hmax=8) for block in sorted_coefficients]

        # DEQUANTIZATION STAGE
        dct_dequants = [np.multiply(data, img.JPEG_STD_LUM_QUANT_TABLE) for data in desorted_coefficients]

        # Inverse DCT Stage
        idct_blocks = [cv2.idct(block) for block in dct_dequants]

        # Rebuild full image channel
        stego_image[:, :, chan_index] = np.asarray(img.stitch_8x8_blocks_back_together(cover_image_YCC.width, idct_blocks))

    # Convert back to RGB (BGR) Colorspace
    stego_image_BGR = cv2.cvtColor(stego_image, cv2.COLOR_YCR_CB2BGR)

    # Clamp pixel values to [0 - 255]
    final_stego_image = np.uint8(np.clip(stego_image_BGR, 0, 255))

    # Save the stego image
    cv2.imwrite(stego_image_filepath, final_stego_image)

# Example usage
#COVER_IMAGE_FILEPATH = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenPNG.png"  # Choose your cover image (PNG)
#STEGO_IMAGE_FILEPATH = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NewDCTBen.png"
#SECRET_MESSAGE_STRING = "YOOOOOOOOOOOOOOOOOOOOO"

#embed_secret_message_in_image(COVER_IMAGE_FILEPATH, STEGO_IMAGE_FILEPATH, SECRET_MESSAGE_STRING)
