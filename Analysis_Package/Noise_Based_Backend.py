import cv2
import numpy as np
import matplotlib.pyplot as plt
import math

def normalise_values(value_dict):
    max_value = max(value_dict.values())
    min_value = min(value_dict.values())
    return {key: (value - min_value) / (max_value - min_value) for key, value in value_dict.items()}

def create_block_coord_dictionary(block_size, image_shape):
    block_dict = {}
    block_index = 0
    num_rows, num_cols = image_shape

    for row in range(0, num_rows, block_size):
        for col in range(0, num_cols, block_size):
            coordinates = [(r, c) for r in range(row, min(row + block_size, num_rows))
                           for c in range(col, min(col + block_size, num_cols))]
            block_dict[block_index] = coordinates
            block_index += 1

    return block_dict

def create_block_values_dictionary(image, block_size):
    block_values_dict = {}
    block_index = 0
    num_rows, num_cols = image.shape

    for row in range(0, num_rows, block_size):
        for col in range(0, num_cols, block_size):
            block = image[row:row + block_size, col:col + block_size]
            block_values_dict[block_index] = block
            block_index += 1

    return block_values_dict

def block_variance_dictionary(block_values_dict):
    variance_dict = {}

    def measure_variance(block_values):
        total_pixels = len(block_values) * len(block_values[0])
        sum_intensities = sum(float(pixel) for row in block_values for pixel in row)
        sum_of_squares = sum(float(pixel) ** 2 for row in block_values for pixel in row)
        mean_intensity = sum_intensities / total_pixels
        mean_of_squares = sum_of_squares / total_pixels
        variance = mean_of_squares - (mean_intensity ** 2)
        return variance

    for key, block_values in block_values_dict.items():
        variance_dict[key] = measure_variance(block_values)

    return variance_dict

def block_entropy_dictionary(block_values_dict):
    entropy_dict = {}

    def measure_entropy(block_values):
        pixel_counts = {}
        total_pixels = 0

        for row in block_values:
            for pixel in row:
                pixel_counts[pixel] = pixel_counts.get(pixel, 0) + 1
                total_pixels += 1

        entropy = sum(-prob * math.log2(prob) for prob in (count / total_pixels for count in pixel_counts.values()))
        return entropy

    for key, block_values in block_values_dict.items():
        entropy_dict[key] = measure_entropy(block_values)

    return entropy_dict

def overlay_grid(image, block_size):
    image_with_grid = image.copy()
    num_rows, num_cols = image_with_grid.shape
    for row in range(0, num_rows, block_size):
        image_with_grid[row:row + 1, :] = 255  # Horizontal lines
    for col in range(0, num_cols, block_size):
        image_with_grid[:, col:col + 1] = 255  # Vertical lines
    return image_with_grid

def create_overlay(image, value_dict, block_dict):
    overlay = np.zeros_like(image, dtype=np.float32)
    for block_index, coords in block_dict.items():
        intensity = value_dict[block_index]
        for r, c in coords:
            overlay[r, c] = intensity
    return overlay

def plot_comparison(image1, image2, values1, values2, block_dict, block_size, main_title, colorbar_title):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    overlay1 = create_overlay(image1, values1, block_dict)
    overlay2 = create_overlay(image2, values2, block_dict)

    im1 = axes[0].imshow(overlay1, cmap='jet')
    axes[0].imshow(overlay_grid(image1, block_size), cmap='gray', alpha=0.5)
    axes[0].set_title("Stego Image")

    im2 = axes[1].imshow(overlay2, cmap='jet')
    axes[1].imshow(overlay_grid(image2, block_size), cmap='gray', alpha=0.5)
    axes[1].set_title("Original Image")

    cbar = fig.colorbar(im1, ax=axes, orientation='vertical', fraction=0.02, pad=0.05)
    cbar.set_label(colorbar_title, rotation=270, labelpad=15)

    fig.suptitle(main_title, fontsize=16)
    plt.show()

def show_analysis(stegImagePath, originalImagePath, block_size):
    steg_image = cv2.imread(stegImagePath, cv2.IMREAD_GRAYSCALE)
    original_image = cv2.imread(originalImagePath, cv2.IMREAD_GRAYSCALE)

    if steg_image.shape != original_image.shape: # Error Correction
        print("Error: The images must have the same dimensions.")
        return

    block_coord_dict = create_block_coord_dictionary(block_size, steg_image.shape)

    steg_block_values_dict = create_block_values_dictionary(steg_image, block_size)
    orig_block_values_dict = create_block_values_dictionary(original_image, block_size)

    steg_variances = block_variance_dictionary(steg_block_values_dict)
    orig_variances = block_variance_dictionary(orig_block_values_dict)

    steg_entropies = block_entropy_dictionary(steg_block_values_dict)
    orig_entropies = block_entropy_dictionary(orig_block_values_dict)

    norm_steg_variances = normalise_values(steg_variances)
    norm_orig_variances = normalise_values(orig_variances)
    norm_steg_entropies = normalise_values(steg_entropies)
    norm_orig_entropies = normalise_values(orig_entropies)

    plot_comparison(steg_image, original_image, norm_steg_variances, norm_orig_variances, block_coord_dict, block_size, 
                    "Variance Comparison", "Variance (Redder = Higher)")

    plot_comparison(steg_image, original_image, norm_steg_entropies, norm_orig_entropies, block_coord_dict, block_size, 
                    "Entropy Comparison", "Entropy (Redder = Higher)")

# Example usage
# show_analysis("stego.png", "original.png", block_size=8)
