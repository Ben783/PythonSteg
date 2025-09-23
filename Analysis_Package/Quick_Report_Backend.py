import sys
import os
import chardet
import magic
from PIL import Image
from PIL.ExifTags import TAGS
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
import numpy as np

class MetadataApp(QWidget):
    def __init__(self, text_file_path=None, image_file_path=None, altered_file_path=None):
        super().__init__()
        self.text_file_path = text_file_path
        self.image_file_path = image_file_path
        self.altered_file_path = altered_file_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        self.text_file_btn = QPushButton('Select Text File', self)
        self.text_file_btn.clicked.connect(self.load_text_file)
        button_layout.addWidget(self.text_file_btn)

        self.image_file_btn = QPushButton('Select Image File', self)
        self.image_file_btn.clicked.connect(self.load_image_file)
        button_layout.addWidget(self.image_file_btn)

        self.altered_file_btn = QPushButton('Select Altered File', self)
        self.altered_file_btn.clicked.connect(self.load_altered_file)
        button_layout.addWidget(self.altered_file_btn)

        layout.addLayout(button_layout)

        metadata_layout = QHBoxLayout()

        text_file_layout = QVBoxLayout()
        text_file_layout.addWidget(QLabel("Text File Metadata:"))
        self.text_result_area = QTextEdit(self)
        self.text_result_area.setReadOnly(True)
        self.text_result_area.setFixedWidth(250)
        text_file_layout.addWidget(self.text_result_area)
        metadata_layout.addLayout(text_file_layout)

        image_file_layout = QVBoxLayout()
        image_file_layout.addWidget(QLabel("Original File Metadata:"))
        self.image_result_area = QTextEdit(self)
        self.image_result_area.setReadOnly(True)
        self.image_result_area.setFixedWidth(250)
        image_file_layout.addWidget(self.image_result_area)
        metadata_layout.addLayout(image_file_layout)


        altered_file_layout = QVBoxLayout()
        altered_file_layout.addWidget(QLabel("Altered File Metadata:"))
        self.altered_result_area = QTextEdit(self)
        self.altered_result_area.setReadOnly(True)
        self.altered_result_area.setFixedWidth(250)  
        altered_file_layout.addWidget(self.altered_result_area)
        metadata_layout.addLayout(altered_file_layout)

        layout.addLayout(metadata_layout)

        self.setLayout(layout)
        self.setWindowTitle('Quick Report')
        self.setGeometry(100, 100, 800, 400)

        # If initial paths are provided, load in their metadata
        if self.text_file_path:
            metadata = get_file_metadata(self.text_file_path)
            self.display_metadata(metadata, self.text_result_area)

        if self.image_file_path:
            metadata = get_file_metadata(self.image_file_path)
            self.display_metadata(metadata, self.image_result_area)
            self.check_suitability()

        if self.altered_file_path:
            metadata = get_file_metadata(self.altered_file_path)
            self.display_metadata(metadata, self.altered_result_area)

    def load_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Text File', '', 'Text Files (*.txt;*.csv;*.log;*.*)')
        if file_path:
            self.text_file_path = file_path
            metadata = get_file_metadata(file_path)
            self.display_metadata(metadata, self.text_result_area)
            self.check_suitability()

    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Image File', '', 'Image Files (*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.*)')
        if file_path:
            self.image_file_path = file_path
            metadata = get_file_metadata(file_path)
            self.display_metadata(metadata, self.image_result_area)
            self.check_suitability()

    def load_altered_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Altered File', '', 'All Files (*.*)')
        if file_path:
            self.altered_file_path = file_path
            metadata = get_file_metadata(file_path)
            self.display_metadata(metadata, self.altered_result_area)

    def display_metadata(self, metadata, result_area):
        if metadata:
            result_text = "\n".join(f"{key}: {value}" for key, value in metadata.items())
            result_area.setPlainText(result_text)
        else:
            result_area.setPlainText("No metadata available or file type not supported.")

    def check_suitability(self):
        if self.text_file_path and self.image_file_path:
            suitability = findSuitability(self.text_file_path, self.image_file_path)
            suitability_text = (
                f"\n{'-'*50}\n"  # Adds line of dashes before the suitability text
                f"Suitability Check ({os.path.basename(self.text_file_path)}):\n"
                f"RGB Embedding: {suitability[0]}\n"
                f"RGBA Embedding: {suitability[1]}\n"
                f"Noise-Based Binary Embedding: {suitability[2]}\n\n"
                f"Ratio Pixels to Char (RGB): {suitability[3]:.2f}\n"
                f"Ratio Pixels to Char (RGBA): {suitability[4]:.2f}\n"
                f"{'-'*50}\n"  # Adds line of dashes after the suitability text
            )
            self.image_result_area.append(suitability_text)


def get_file_metadata(file_path):
    if not os.path.exists(file_path):
        return {"Error": "File not found"}
    
    file_type = magic.Magic(mime=True).from_file(file_path)
    
    if "text" in file_type:
        return get_text_file_metadata(file_path)
    elif "image" in file_type:
        return get_image_file_metadata(file_path)
    else:
        return {"Error": f"Unsupported file type: {file_type}"}


def get_text_file_metadata(file_path):
    try:
        file_stats = os.stat(file_path)
        with open(file_path, 'rb') as file:
            file_content = file.read()
            encoding = chardet.detect(file_content)['encoding']
        
        with open(file_path, 'r', encoding=encoding, errors='ignore') as file:
            lines = file.readlines()
            num_lines = len(lines)
            num_words = sum(len(line.split()) for line in lines)
            num_characters = sum(len(line) for line in lines)

        return {
            'File Name': os.path.basename(file_path),
            'File Size (bytes)': file_stats.st_size,
            'Encoding': encoding,
            'Number of Lines': num_lines,
            'Number of Words': num_words,
            'Number of Characters': num_characters
        }
    except Exception as e:
        print(f"Error reading text file {file_path}: {str(e)}")
        return {"Error": str(e)}

def get_image_file_metadata(file_path):
    try:
        with Image.open(file_path) as img:
            metadata = {
                'File Name': os.path.basename(file_path),
                'File Size (bytes)': os.path.getsize(file_path),
                'File Format': img.format,
                'Image Size': img.size,
                'Image Mode': img.mode,
                'Image Width': img.width,
                'Image Height': img.height,
                'DPI': img.info.get('dpi', 'N/A')
            }
            exif_data = img._getexif()
            if exif_data:
                metadata['EXIF'] = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            return metadata
    except Exception as e:
        print(f"Error reading image file {file_path}: {str(e)}")
        return {"Error": str(e)}

def findSuitability(textFile, imageFile):
    try:
        image = Image.open(imageFile).convert("RGBA")
        image = np.array(image)
        
        with open(textFile, 'r') as file:
            lines = file.readlines()
            num_characters = sum(len(line) for line in lines)

        height, width, channels = image.shape
        total_RGBA_channels = height * width * channels
        total_RGB_channels = height * width * 3
        total_binary_text_bits = num_characters * 8
        
        RGB_suitability = total_RGB_channels > num_characters
        RGBA_suitability = total_RGBA_channels > num_characters
        binary_suitability = (height * width) > total_binary_text_bits

        ratioPixelsToChar_RGB = total_RGB_channels / num_characters if num_characters else 0
        ratioPixelsToChar_RGBA = total_RGBA_channels / num_characters if num_characters else 0
        
        return RGB_suitability, RGBA_suitability, binary_suitability, ratioPixelsToChar_RGB, ratioPixelsToChar_RGBA
    except Exception as e:
        print(f"Error during suitability check: {str(e)}")
        return (False, False, False, 0, 0)

