import cv2
import numpy as np
from scipy.stats import chisquare
import matplotlib.pyplot as plt
from PIL import Image

def analyse_images(original_path, modified_path):
    try:
        original = Image.open(original_path).convert("RGB") # Load in as RGB, not L
        modified = Image.open(modified_path).convert("RGB")

        original_arr = np.array(original) # Image to numpy arrays
        modified_arr = np.array(modified)

        r, g, b = original_arr[:, :, 0], original_arr[:, :, 1], original_arr[:, :, 2]  # Extracts RGB channels
        rAlt, gAlt, bAlt = modified_arr[:, :, 0], modified_arr[:, :, 1], modified_arr[:, :, 2]

        # Computing histograms...
        hist_r, bins = np.histogram(r.flatten(), bins=256, range=(0, 256))
        hist_g, _ = np.histogram(g.flatten(), bins=256, range=(0, 256))
        hist_b, _ = np.histogram(b.flatten(), bins=256, range=(0, 256))
        hist_Ar, _ = np.histogram(rAlt.flatten(), bins=256, range=(0, 256))
        hist_Ag, _ = np.histogram(gAlt.flatten(), bins=256, range=(0, 256))
        hist_Ab, _ = np.histogram(bAlt.flatten(), bins=256, range=(0, 256))

        # Compacts RGB histograms
        def compact_RGB(hist_r, hist_g, hist_b):
            return (hist_r / hist_r.sum() + hist_g / hist_g.sum() + hist_b / hist_b.sum()) / 3

        compactedHist = compact_RGB(hist_r, hist_g, hist_b)
        AltCompactHist = compact_RGB(hist_Ar, hist_Ag, hist_Ab)

        plt.figure(figsize=(10, 5))
        plt.xlim([0, 256])
        plt.yscale("linear")
        plt.plot(bins[:-1], hist_r / hist_r.sum(), color="red", label="Red Channel")
        plt.plot(bins[:-1], hist_g / hist_g.sum(), color="green", label="Green Channel")
        plt.plot(bins[:-1], hist_b / hist_b.sum(), color="blue", label="Blue Channel")
        plt.legend()
        plt.title("Original Image RGB Histograms")
        plt.show()

        plt.figure(figsize=(10, 5))
        plt.xlim([0, 256])
        plt.yscale("linear")
        plt.plot(bins[:-1], compactedHist, color='black', label="Original Normalised Histogram")
        plt.plot(bins[:-1], AltCompactHist, color='red', label="Modified Normalised Histogram")
        plt.legend()
        plt.title("Compacted Histogram Comparison")
        plt.show()

        original_gray = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE) # Performs Chi-Square test using L images
        modified_gray = cv2.imread(modified_path, cv2.IMREAD_GRAYSCALE)

        original_hist, _ = np.histogram(original_gray, bins=256, range=(0, 256))
        modified_hist, _ = np.histogram(modified_gray, bins=256, range=(0, 256))

        original_hist = original_hist / original_hist.sum()
        modified_hist = modified_hist / modified_hist.sum()

        chi_stat, p_value = chisquare(original_hist, modified_hist)

        # Plotting for comparison
        plt.figure(figsize=(10, 5))
        plt.bar(range(256), original_hist, color='blue', alpha=0.6, label="Original")
        plt.bar(range(256), modified_hist, color='red', alpha=0.4, label="Modified")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Normalised Frequency")
        plt.legend()
        plt.title("Pixel Intensity Histogram Comparison")
        plt.show()

        print(f"Chi-Square Statistic: {chi_stat:.4f}, P-Value: {p_value:.4f}")
        if p_value < 0.05:
            print("Significant difference detected between the two images.")
        else:
            print("No significant difference detected.")

    except FileNotFoundError as e:
        print(f"File error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage
#original_image = r"c:\Users\HOME\PYTHON CS\Project\Encryption Algorithms\BenPNG.png"
#modified_image = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NoiseBen.png"

#analyse_images(original_image, modified_image)
