from skimage import io, img_as_float
from skimage.metrics import structural_similarity as ssim
import numpy as np
import matplotlib.pyplot as plt

def calculate_ssim(image_file1, image_file2):

    image1 = img_as_float(io.imread(image_file1, as_gray=True))
    image2 = img_as_float(io.imread(image_file2, as_gray=True))

    ssim_index, ssim_map = ssim(image1, image2, full=True, data_range=1.0)  #SSIM calculation
    
    # Normalising SSIM map 
    ssim_map = (ssim_map - np.min(ssim_map)) / (np.max(ssim_map) - np.min(ssim_map))

    return ssim_index, ssim_map

def show_differences(image_file1, image_file2):
    ssim_index, ssim_map = calculate_ssim(image_file1, image_file2)

    fig, ax = plt.subplots(1, 3, figsize=(15, 5))

    image1 = io.imread(image_file1)
    image2 = io.imread(image_file2)

    ax[0].imshow(image1, cmap='gray')
    ax[0].set_title('Image 1')
    ax[0].axis('off')

    ax[1].imshow(image2, cmap='gray')
    ax[1].set_title('Image 2')
    ax[1].axis('off')

    ax[2].imshow(ssim_map, cmap='hot')
    ax[2].set_title('Difference Map')
    ax[2].axis('off')

    plt.suptitle(f'SSIM: {ssim_index:.4f}')
    return fig

