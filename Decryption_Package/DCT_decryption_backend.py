import cv2
import struct
import bitstring
import numpy as np
from . import zigzag as zz
from . import data_embedding as stego
from . import image_preparation as img

def extract_secret_message_from_image(stego_image_filepath):
    """
    Extracts a secret message embedded in an image using DCT-based steganography.

    Args:
    stego_image_filepath (str): The file path of the stego image.
    
    Returns:
    str: The decoded secret message.
    """
    # Read the stego image
    stego_image = cv2.imread(stego_image_filepath, flags=cv2.IMREAD_COLOR)
    stego_image_f32 = np.float32(stego_image)
    stego_image_YCC = img.YCC_Image(cv2.cvtColor(stego_image_f32, cv2.COLOR_BGR2YCrCb))

    # FORWARD DCT STAGE
    dct_blocks = [cv2.dct(block) for block in stego_image_YCC.channels[0]]  # Only care about Luminance layer

    # QUANTIZATION STAGE
    dct_quants = [np.around(np.divide(item, img.JPEG_STD_LUM_QUANT_TABLE)) for item in dct_blocks]

    # Sort DCT coefficients by frequency
    sorted_coefficients = [zz.zigzag(block) for block in dct_quants]

    # DATA EXTRACTION STAGE
    recovered_data = stego.extract_encoded_data_from_DCT(sorted_coefficients)
    recovered_data.pos = 0

    # Determine length of secret message
    data_len = int(recovered_data.read('uint:32') / 8)

    # Extract secret message from DCT coefficients
    extracted_data = bytes()
    for _ in range(data_len):
        extracted_data += struct.pack('>B', recovered_data.read('uint:8'))

    # Return the decoded secret message
    return extracted_data.decode('ascii')

# Example usage
#STEGO_IMAGE_FILEPATH = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenDCT.png"
#secret_message = extract_secret_message_from_image(STEGO_IMAGE_FILEPATH)
#print(secret_message)
