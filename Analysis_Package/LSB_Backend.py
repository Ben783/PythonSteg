from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def plot_normalised_LSBs(img, alt_image):

    img = Image.open(img).convert("L")
    alt_image = Image.open(alt_image).convert("L")

    img_array = np.array(img)
    alt_array = np.array(alt_image)

    lsb_array = img_array & 1   # Uses '& 1' , meaning it compares each pixel of binary to '00000001', and performs an AND operation. This returns '1' if the last bit is 1, and '0' if it is zero.
    alt_lsb_array = alt_array & 1

    lsb_array = lsb_array * 255  # Scales the LSB values to [0, 255]
    alt_lsb_array = alt_lsb_array * 255

    lsb_image = Image.fromarray(lsb_array.astype(np.uint8)) # Convert back to image for visualization
    alt_lsb_image = Image.fromarray(alt_lsb_array.astype(np.uint8))

    fig, ax = plt.subplots(1, 2, figsize=(10,5))

    ax[0].imshow(lsb_image)
    ax[0].axis('off')
    ax[0].set_title("Original Image")

    ax[1].imshow(alt_lsb_image)
    ax[1].axis('off') 
    ax[1].set_title("Cover File")

    plt.tight_layout()
    plt.show()

