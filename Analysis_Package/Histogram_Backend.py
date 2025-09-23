import cv2
import numpy as np
from scipy.stats import chisquare
import matplotlib.pyplot as plt
from PIL import Image

def compact_RGB(hist_r, hist_g, hist_b):
    N_r, N_g, N_b = hist_r.sum(), hist_g.sum(), hist_b.sum()
    return (hist_r / N_r + hist_g / N_g + hist_b / N_b) / 3

def compute_histograms(image_path, alpha_channel=False):
    image = Image.open(image_path).convert("RGBA" if alpha_channel else "RGB")
    channels = np.array(image).T  # Transpose for easy unpacking
    
    histograms = [np.histogram(channel.flatten(), bins=256, range=(0, 256))[0] for channel in channels[:3]]
    if alpha_channel:
        histograms.append(np.histogram(channels[3].flatten(), bins=256, range=(0, 256))[0])  # Alpha channel
    return histograms

def plot_histograms(hist_r, hist_g, hist_b, bins):
    plt.figure(figsize=(10, 5))
    plt.xlim([0, 256])
    plt.yscale("linear")
    plt.plot(bins[:-1], hist_r, color="red", label="Red Channel")
    plt.plot(bins[:-1], hist_g, color="green", label="Green Channel")
    plt.plot(bins[:-1], hist_b, color="blue", label="Blue Channel")
    plt.legend()
    plt.title("RGB Histogram")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.show()

def chi_square_test(original_path, modified_path):
    original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE)
    modified = cv2.imread(modified_path, cv2.IMREAD_GRAYSCALE)
    
    original_hist, _ = np.histogram(original, bins=256, range=(0, 256))
    modified_hist, _ = np.histogram(modified, bins=256, range=(0, 256))

    original_hist, modified_hist = original_hist / original_hist.sum(), modified_hist / modified_hist.sum()
    chi_stat, p_value = chisquare(original_hist, modified_hist)

    plt.figure(figsize=(10, 5))
    plt.bar(range(256), original_hist, color='blue', alpha=0.6, label="Original")
    plt.bar(range(256), modified_hist, color='red', alpha=0.4, label="Modified")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Normalised Frequency")
    plt.title("Pixel Intensity Histogram Comparison")
    plt.legend()
    plt.show()
    
    return chi_stat, p_value

#original_image = r"c:\Users\HOME\PYTHON CS\Project\Encryption Algorithms\BenPNG.png"
#modified_image = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NoiseBen.png"

# try:
#    
#     hist_r, hist_g, hist_b, _ = compute_histograms(original_image, alpha_channel=True)
#     alt_hist_r, alt_hist_g, alt_hist_b = compute_histograms(modified_image)

#    
#     bins = np.linspace(0, 256, num=257)

#    
#     plot_histograms(hist_r, hist_g, hist_b, bins)
    
#   
#     chi_stat, p_value = chi_square_test(original_image, modified_image)
#     print(f"Chi-Square Statistic: {chi_stat}, P-Value: {p_value}")
#     print("Significant difference detected." if p_value < 0.05 else "No significant difference detected.")


