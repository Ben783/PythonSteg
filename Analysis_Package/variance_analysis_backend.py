import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
import matplotlib.pyplot as plt
import seaborn as sns

def calculate_differences(img1_path, img2_path):
    img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)

    difference = cv2.absdiff(img1, img2)
    
    psnr_value = psnr(img1, img2)
    ssim_value = ssim(img1, img2)


    variance_diff = np.var(difference)
    variance_img1 = np.var(img1)
    variance_img2 = np.var(img2)

    return difference, psnr_value, ssim_value, variance_diff, variance_img1, variance_img2

def plot_heatmap(difference, title):
    plt.figure(figsize=(10, 8))
    sns.heatmap(difference, cmap='viridis')
    plt.title(title)
    plt.show()

# Example usage
#img1_path = r"C:\Users\HOME\PYTHON CS\Project\Encryption Algorithms\BenPNG.png"
#img2_path = r"C:\Users\HOME\PYTHON CS\Project\Encryption Algorithms\RGBAben.png"
#difference, psnr_value, ssim_value, variance_diff, variance_img1, variance_img2 = calculate_differences(img1_path, img2_path)

#print(f"PSNR: {psnr_value}")
#print(f"SSIM: {ssim_value}")
#print(f"Variance of difference: {variance_diff}")
#print(f"Variance of image 1: {variance_img1}")
#print(f"Variance of image 2: {variance_img2}")

#plot_heatmap(difference, 'Heatmap of Image Differences')
def complete(img1_path, img2_path):
    difference, psnr_value, ssim_value, variance_diff, variance_img1, variance_img2 = calculate_differences(img1_path, img2_path)
    plot_heatmap(difference, "Heatmap of Image Differences")
