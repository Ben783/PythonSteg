import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QTextEdit
from . import ApEn_reference_backend as ApEn  # Imports modified ApEn module


class ApEnApp(QWidget):
    def __init__(self, image_file_path=None, altered_file_path=None):
        super().__init__()
        self.image_file_path = image_file_path
        self.altered_file_path = altered_file_path
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        self.image_file_btn = QPushButton('Select Image File', self)
        self.image_file_btn.clicked.connect(self.load_image_file)
        button_layout.addWidget(self.image_file_btn)

        self.altered_file_btn = QPushButton('Select Altered File', self)
        self.altered_file_btn.clicked.connect(self.load_altered_file)
        button_layout.addWidget(self.altered_file_btn)

        layout.addLayout(button_layout)

        metadata_layout = QHBoxLayout()

        image_file_layout = QVBoxLayout()
        image_file_layout.addWidget(QLabel("Original File Entropy Analysis:"))
        self.image_result_area = QTextEdit(self)
        self.image_result_area.setReadOnly(True)
        self.image_result_area.setFixedWidth(350)
        image_file_layout.addWidget(self.image_result_area)
        metadata_layout.addLayout(image_file_layout)

        altered_file_layout = QVBoxLayout()
        altered_file_layout.addWidget(QLabel("Altered File Entropy Analysis:"))
        self.altered_result_area = QTextEdit(self)
        self.altered_result_area.setReadOnly(True)
        self.altered_result_area.setFixedWidth(350)
        altered_file_layout.addWidget(self.altered_result_area)
        metadata_layout.addLayout(altered_file_layout)

        layout.addLayout(metadata_layout)
        self.setLayout(layout)
        self.setWindowTitle('Approximate Entropy Report')
        self.setGeometry(100, 100, 800, 400)

        if self.image_file_path:
            self.load_metadata(self.image_file_path, self.image_result_area)

        if self.altered_file_path:
            self.load_metadata(self.altered_file_path, self.altered_result_area)

    def load_image_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Image File', '', 'Image Files (*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.*)')
        if file_path:
            self.image_file_path = file_path
            self.load_metadata(file_path, self.image_result_area)

    def load_altered_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Altered File', '', 'All Files (*.*)')
        if file_path:
            self.altered_file_path = file_path
            self.load_metadata(file_path, self.altered_result_area)

    def load_metadata(self, file_path, result_area): #Loads entropy analysis using ApEn function and appends it to the existing text.
        try:
            metadata = ApEn.analyze_image(file_path)  # Using imported module
            self.append_metadata(metadata, result_area, file_path)
        except Exception as e:
            result_area.append(f"\nError loading metadata: {str(e)}\n")

    def append_metadata(self, metadata, result_area, file_path):
        separator = "----------------------------"
        result_text = f"\n{separator}\nFile: {file_path}\n{separator}\n"
        result_text += "\n".join(f"{key}: {value}" for key, value in metadata.items())
        result_text += f"\n{separator}\n"

        result_area.append(result_text)  # Appends new data below the existing text


