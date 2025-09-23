import sys
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import peak_signal_noise_ratio as psnr
from scipy.stats import chisquare, skew
import itertools
import math
import matplotlib.pyplot as plt
from PIL import Image
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QScrollArea, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from .SSIM_backend import show_differences


class CollapsibleSection(QWidget):
    def __init__(self, title, content_widget):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        self.toggle_button.setFixedWidth(150)
        self.toggle_button.clicked.connect(self.toggle)
        
        self.content = QFrame()
        self.content.setLayout(QVBoxLayout())
        self.content.layout().addWidget(content_widget)
        self.content.setMaximumHeight(0)
        self.content.setSizePolicy(self.content.sizePolicy().horizontalPolicy(), 1)

        self.animation = QPropertyAnimation(self.content, b"maximumHeight")
        self.animation.setDuration(300)

        self.layout.addWidget(self.toggle_button)
        self.layout.addWidget(self.content)

    def toggle(self):
        if self.toggle_button.isChecked():
            self.animation.setEndValue(self.content.sizeHint().height())
        else:
            self.animation.setEndValue(0)
        self.animation.start()


class DetailedReport(QWidget):
    def __init__(self, original_path=None, modified_path=None, text_path=None):
        super().__init__()
        self.setWindowTitle("Image Analysis")
        self.setGeometry(100, 100, 800, 600)

        # Layout
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.container = QWidget()
        self.layout = QVBoxLayout()
        self.container.setLayout(self.layout)
        self.scroll_area.setWidget(self.container)

        # Add file paths
        self.add_file_info(original_path, modified_path, text_path)
        self.add_sections(original_path, modified_path, text_path)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.scroll_area)
        self.setLayout(main_layout)

    def add_file_info(self, original_path, modified_path, text_path):
        file_info_layout = QVBoxLayout()

        # Add file paths
        for path in [original_path, modified_path, text_path]:
            if path:
                path_label = QLabel(f"File Path: {path}")
                file_info_layout.addWidget(path_label)

        self.layout.addLayout(file_info_layout)

    def add_sections(self, original_path, modified_path, text_path):
        image_analysis_widget = self.analyse_images(original_path, modified_path)
        text_analysis_widget = self.analyse_text(text_path)
        variance_statistics_widget = self.variance_statistics(original_path, modified_path)
        stats_analysis_widget = self.stats_analysis(original_path, modified_path)
        entropy_analysis_widget = self.entropy_analysis(original_path, modified_path)

        self.layout.addWidget(CollapsibleSection("Image Analysis", image_analysis_widget))
        self.layout.addWidget(CollapsibleSection("Text Analysis", text_analysis_widget))
        self.layout.addWidget(CollapsibleSection("Variance Statistics", variance_statistics_widget))
        self.layout.addWidget(CollapsibleSection("Stats Analysis", stats_analysis_widget))
        self.layout.addWidget(CollapsibleSection("Entropy Analysis", entropy_analysis_widget))

    def analyse_images(self, original_path, modified_path):
        try:
            fig = show_differences(original_path, modified_path)  # Get the figure
            canvas = FigureCanvas(fig)  # Embed in PyQt5
            canvas.setMinimumSize(800, 400)  # Adjust size if necessary
            return canvas  # Return widget to display
        except Exception as e:
            return QLabel(f"Error: {e}")


    def analyse_text(self, text_path):
        try:
            def splitDoc(filepath):
                with open(filepath, "r") as file:
                    return [char.lower() for line in file for char in line]

            def frequencyAnalysis(doc):
                frequency = {}
                for char in doc:
                    frequency[char] = frequency.get(char, 0) + 1
                return dict(sorted(frequency.items(), key=lambda item: item[1], reverse=True))

            splitTxt = splitDoc(text_path)
            freqAn = frequencyAnalysis(splitTxt)
            keys, values = list(freqAn.keys()), list(freqAn.values())

            fig, ax = plt.subplots(figsize=(10, 5))
            ax.bar(keys, values, color='skyblue')
            ax.set_xlabel('Characters')
            ax.set_ylabel('Frequency')
            ax.set_title('Character Frequency')

            canvas = FigureCanvas(fig)
            canvas.setMinimumSize(800, 400)
            return canvas
        except Exception as e:
            return QLabel(f"Error: {e}")

    def variance_statistics(self, original_path, modified_path):
        try:
            difference, psnr_value, ssim_value, variance_diff, variance_img1, variance_img2 = calculate_differences(original_path, modified_path)

            stats_text = (
                f"PSNR: {psnr_value:.2f}\n"
                f"SSIM: {ssim_value:.2f}\n"
                f"Variance of Differences: {variance_diff:.2f}\n"
                f"Variance of Original Image: {variance_img1:.2f}\n"
                f"Variance of Modified Image: {variance_img2:.2f}\n\n"
                "Explanation:\n"
                "PSNR (Peak Signal-to-Noise Ratio): A higher PSNR indicates that the images are more similar. "
                "It measures the ratio between the maximum possible power of a signal and the power of corrupting noise.\n"
                "SSIM (Structural Similarity Index): A higher SSIM indicates that the images are more similar. "
                "It measures the similarity between two images based on luminance, contrast, and structure.\n"
                "Variance of Differences: A higher variance indicates greater differences between the images.\n"
                "Variance of Original Image: Measures the spread of pixel intensity values in the original image.\n"
                "Variance of Modified Image: Measures the spread of pixel intensity values in the modified image."
            )

            stats_label = QLabel(stats_text)
            return stats_label
        except Exception as e:
            return QLabel(f"Error: {e}")

    def stats_analysis(self, original_path, modified_path):
        try:
            chi_stat, p_value = chi_square_test(original_path, modified_path)
            skew1, skew2 = calculate_image_skew(original_path, modified_path)
            stats_text = (
                f"Chi-Square Statistic: {chi_stat:.2f}\n"
                f"P-Value: {p_value:.2e}\n"
                f"Skew of original image: {skew1}\n"
                f"Skew of modified image: {skew2}\n"

                "Explanation:\n"
                "Chi-Square Statistic: Measures the difference between the observed and expected frequencies. "
                "A higher value indicates greater differences between the histograms.\n"
                "P-Value: Indicates the probability that the observed differences are due to chance. "
                "A lower value suggests that the differences are statistically significant."
            )

            stats_label = QLabel(stats_text)
            return stats_label
        except Exception as e:
            return QLabel(f"Error: {e}")

    def entropy_analysis(self, original_path, modified_path):
        try:
            analysis_results = analyze_images_for_entropy(original_path, modified_path)

            original_entropy = analysis_results['Original Image Approximate Entropy']
            modified_entropy = analysis_results['Modified Image Approximate Entropy']
            entropy_difference = abs(original_entropy - modified_entropy)

            stats_text = (
                "Approximate Entropy: A measure of the complexity of the image. Higher entropy indicates more complexity.\n"
                "Average Similarity: An inverse measure of how different image blocks are from each other. If the similarity is high, the image has more uniformity; if it is low, there is more structural complexity or noise.\n\n"
            
                f"Original Image Approximate Entropy: {original_entropy}\n"
                f"Modified Image Approximate Entropy: {modified_entropy}\n"
                f"Original Image Average Similarity: {analysis_results['Original Image Average Similarity']}\n"
                f"Modified Image Average Similarity: {analysis_results['Modified Image Average Similarity']}\n"
                f"Total Pairs: {analysis_results['Total Pairs']}\n\n"
            )

            if original_entropy > modified_entropy:
                stats_text += (
                    f"\nDifference in Entropy: {entropy_difference}\n"
                    "This difference is likely due to noise-based embedding.\nThis might be because the embedding technique targets high entropy areas, for example.\nLook at the LSB alterations: if more uniform patterns are found, this would explain a decrease in entropy."
                )
            
            if original_entropy < modified_entropy:
                stats_text += (
                    f"\nDifference in Entropy: {entropy_difference}\n"
                    "This difference is likely due to Chaotic-style Embeddings.\nIntroduction of random noise causes a spike in entropy, especially if the alterations are made in low entropy regions."
                )

            stats_label = QLabel(stats_text)
            return stats_label
        except Exception as e:
            return QLabel(f"Error: {e}")


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


def chi_square_test(original_path, modified_path): # Chi-square test function
    original = cv2.imread(original_path, cv2.IMREAD_GRAYSCALE) # Converts both files to greyscale
    modified = cv2.imread(modified_path, cv2.IMREAD_GRAYSCALE)
    
    original_hist, _ = np.histogram(original, bins=256, range=(0, 256)) # Computes histograms
    modified_hist, _ = np.histogram(modified, bins=256, range=(0, 256))

    original_hist, modified_hist = original_hist / original_hist.sum(), modified_hist / modified_hist.sum()
    chi_stat, p_value = chisquare(original_hist, modified_hist) # Performs the test

    return chi_stat, p_value


def load_image(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError("Image not found or invalid format.")
    return img


def divide_into_blocks(image, block_size):
    h, w = image.shape
    blocks = []
    
    for i in range(0, h, block_size):
        for j in range(0, w, block_size):
            block = image[i:i+block_size, j:j+block_size]
            if block.shape == (block_size, block_size): 
                blocks.append(block.flatten())  
                
    return np.array(blocks)


def compute_embedding(blocks, scale_factor=1.0):
    return blocks * scale_factor  


def compute_distances(embedded_vectors):
    num_vectors = len(embedded_vectors)
    distances = []
    
    for (vec1, vec2) in itertools.combinations(embedded_vectors, 2):
        dist = np.linalg.norm(vec1 - vec2) 
        distances.append(dist)
    
    return np.array(distances)


def count_similar_pairs(distances, threshold):
    return np.sum(distances < threshold)


def compute_average_similarity(distances):
    return np.mean(distances)


def compute_entropy(similar_pairs, total_pairs):
    if total_pairs == 0:
        return 0 
    
    p = similar_pairs / total_pairs
    if p == 0 or p == 1:
        return 0 
    
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def analyze_images_for_entropy(original_path, modified_path, block_size=8, scale_factor=1.0, similarity_threshold=10.0):
    original_img = load_image(original_path)
    modified_img = load_image(modified_path)

    original_blocks = divide_into_blocks(original_img, block_size)
    modified_blocks = divide_into_blocks(modified_img, block_size)

    original_vectors = compute_embedding(original_blocks, scale_factor)
    modified_vectors = compute_embedding(modified_blocks, scale_factor)

    original_distances = compute_distances(original_vectors)
    modified_distances = compute_distances(modified_vectors)

    similar_pairs_original = count_similar_pairs(original_distances, similarity_threshold)
    similar_pairs_modified = count_similar_pairs(modified_distances, similarity_threshold)

    total_pairs = len(original_distances)
    original_avg_similarity = compute_average_similarity(original_distances)
    modified_avg_similarity = compute_average_similarity(modified_distances)

    original_entropy = compute_entropy(similar_pairs_original, total_pairs)
    modified_entropy = compute_entropy(similar_pairs_modified, total_pairs)

    return {
        "Original Image Approximate Entropy": round(original_entropy, 4),
        "Modified Image Approximate Entropy": round(modified_entropy, 4),
        "Original Image Average Similarity": round(original_avg_similarity, 4),
        "Modified Image Average Similarity": round(modified_avg_similarity, 4),
        "Total Pairs": total_pairs
    }


def calculate_image_skew(image_path1, image_path2):

    img1 = cv2.imread(image_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image_path2, cv2.IMREAD_GRAYSCALE)

    if img1 is None or img2 is None:
        raise ValueError("Error loading images. Check the file paths.")

    pixel_values1 = img1.flatten() # Flattens images to 1D arrays of pixel intensities
    pixel_values2 = img2.flatten()

    skew1 = skew(pixel_values1) # Computes skew
    skew2 = skew(pixel_values2)

    return skew1, skew2




# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     original_path = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\BenPNG.png"  # Replace with actual path
#     modified_path = r"C:\Users\HOME\PYTHON CS\Project\Complete\Images\NoiseBen1Chap.png"  # Replace with actual path
#     text_path = r"C:\Users\HOME\PYTHON CS\Project\Complete\Text\1st Chapter Animal Farm.sty"  # Replace with actual path

#     window = DetailedReport(original_path, modified_path, text_path)
#     window.show()
#     sys.exit(app.exec_())





