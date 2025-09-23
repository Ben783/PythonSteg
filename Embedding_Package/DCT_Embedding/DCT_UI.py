import sys 
import cv2
import numpy as np
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QProgressBar, QMessageBox, QTabWidget, QComboBox, QSpinBox, QSlider
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore
import copy
import shutil
import os
import tempfile
from . import run_stego_algorithm as backend


class DCTEmbeddingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DCT Embedding Window")
        self.setGeometry(200, 200, 600, 400)
        self.progress = 0

        self.tab_widget = QTabWidget()
        self.main_tab = QWidget()
        self.init_main_tab()
        self.tab_widget.addTab(self.main_tab, "Main")
        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced Options")
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

        self.image_path = None
        self.text_path = None
        self.hamming_text = None

        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label, alignment=QtCore.Qt.AlignLeft)

    def init_main_tab(self):
        title_layout = QHBoxLayout()
        self.title_label = QLabel("DCT Embedding\n(Discrete Cosine Transform)", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.help_button = QPushButton("i", self)
        self.help_button.setFixedSize(20, 20) 
        self.help_button.setStyleSheet("color: blue; font-weight: bold; border: 1px solid gray; border-radius: 5px;")
        self.help_button.clicked.connect(self.show_help)
        title_layout.addStretch()
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.help_button)
        title_layout.addStretch()

        self.image_label = QLabel("Image File: None", self)
        self.image_label.setStyleSheet("color: red;")
        self.image_button = QPushButton("Select Image", self)
        self.image_button.clicked.connect(self.select_image)

        self.text_label = QLabel("Text File: None", self)
        self.text_label.setStyleSheet("color: red;")
        self.text_button = QPushButton("Select Text File", self)
        self.text_button.clicked.connect(self.select_text_file)

        text_image_layout = QHBoxLayout()
        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)
        self.text_display.setFixedHeight(100)
        self.text_display.setMaximumWidth(350) 
        self.text_display.setVisible(False)

        self.thumbnail_label = QLabel(self)
        self.thumbnail_label.setFixedSize(100, 100)
        text_image_layout.addWidget(self.text_display)
        text_image_layout.addWidget(self.thumbnail_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)

        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setFixedSize(100, 20)
        self.save_button.setEnabled(False)

        self.embed_button = QPushButton("Begin Embedding", self)
        self.embed_button.clicked.connect(self.begin_embedding)
        self.embed_button.setFixedSize(150, 25)

        self.encryption_button = QPushButton("Central Window", self)
        self.encryption_button.clicked.connect(self.MainWindow)
        self.encryption_button.setFixedSize(200, 30)

        main_layout = QVBoxLayout()
        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.image_button)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.text_button)
        main_layout.addWidget(self.text_label)
        main_layout.addLayout(text_image_layout)
        
        main_layout.addWidget(self.save_button, alignment=QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.embed_button, alignment=QtCore.Qt.AlignCenter)
        main_layout.addWidget(self.encryption_button, alignment=QtCore.Qt.AlignCenter)

        self.main_tab.setLayout(main_layout)

    def init_advanced_tab(self):
        advanced_layout = QVBoxLayout()

        self.options_label = QLabel("No Advanced Options available yet.")
        self.options_label.setAlignment(Qt.AlignCenter)
        advanced_layout.addWidget(self.options_label)
        self.advanced_tab.setLayout(advanced_layout)

    def show_help(self):
        QMessageBox.information(self, "Help", "This window allows you to embed noise-based data into images.\n\n"
                                              "Instructions:\n"
                                              "1. Select an image file.\n"
                                              "2. Select a text file.\n"
                                              "3. Adjust embedding settings in 'Advanced Options'.\n"
                                              "4. Click 'Begin Embedding' to start the process.\n"
                                              "5. Save your work.")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.webp)")
        if file_path:
            self.image_path = file_path
            self.image_label.setText(f"Image File: {file_path}")
            self.image_label.setStyleSheet("color: green;")
            self.update_progress(30)

            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(100, 100)
            self.thumbnail_label.setPixmap(pixmap)
            self.update_status(f"Image selected: {file_path}")

    def update_progress(self, value):
        self.progress = min(100, self.progress + value)
        self.progress_bar.setValue(self.progress)

    def update_status(self, status_text):
        self.status_label.setText(f"Status: {status_text}")


    def show_help(self):
        QMessageBox.information(self, "Help", "This window allows you to embed noise-based data into images.\n\n"
                                              "Instructions:\n"
                                              "1. Select an image file.\n"
                                              "2. Select a text file.\n"
                                              "3. Click 'Begin Embedding' to start the process.\n"
                                              "4. Save your work.")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.gif)")
        if file_path:
            self.image_path = file_path
            self.image_label.setText(f"Image File: {file_path}")
            self.image_label.setStyleSheet("color: green;")
            self.update_progress(30)

            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(100, 100)
            self.thumbnail_label.setPixmap(pixmap)
            self.update_status(f"Image selected: {file_path}")

    def select_text_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File", 
            "", 
            "All Supported Files (*.sty *.txt *.json *.html *.py *.docx *.pdf *.xlsx *.csv);;"
            "Text Files (*.txt);;"
            "JSON Files (*.json);;"
            "HTML Files (*.html);;"
            "Python Files (*.py);;"
            "Word Documents (*.docx);;"
            "PDF Files (*.pdf);;"
            "Excel Files (*.xlsx);;"
            "CSV Files (*.csv);;"
            "All Files (*)"
        )
        if file_path:
            self.text_path = file_path
            with open(file_path, "r") as file:
                text_content = file.read(500) + "..."
            self.text_label.setText(f"Text File: {file_path}")
            self.text_label.setStyleSheet("color: green;")
            self.text_display.setText(text_content)
            self.text_display.setVisible(True)
            self.update_progress(30)
            self.update_status(f"Text File Selected: {file_path}")

    def split_doc(self, filepath):
        with open(filepath, "r") as file:
            doc = [char.lower() for line in file for char in line]
        return doc

    def save_file(self):
        if not hasattr(self, "temp_embedded_path") or not os.path.exists(self.temp_embedded_path):
            QMessageBox.warning(self, "Error", "No embedded image to save. Please perform embedding first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image File", "", "PNG Files (*.png);;All Files (*)")

        if file_path:
            if not file_path.lower().endswith(".png"):
                file_path += ".png"  # Ensures file is PNG 

            shutil.copy(self.temp_embedded_path, file_path)
            self.update_status(f"Image saved to {file_path}")
            self.update_progress(100)

    def update_progress(self, value):
        self.progress = min(100, self.progress + value)
        self.progress_bar.setValue(self.progress)

    def update_status(self, status_text):
        """Update the status label with the provided text."""
        self.status_label.setText(f"Status: {status_text}")

    def begin_embedding(self):
        if not self.image_path or not self.text_path:
            QMessageBox.warning(self, "Error", "Please select both an image and a text file first.")
            return



        # Generates a temporary file path for embedding
        temp_dir = tempfile.gettempdir()
        self.temp_embedded_path = os.path.join(temp_dir, "embedded_image.png")  # Ensure .png extension

        # Performs embedding and pass the error correction method
        result = backend.embed_secret_message_in_image(self.text_path, self.image_path, self.temp_embedded_path)


        if os.path.exists(self.temp_embedded_path):
            QMessageBox.information(self, "Success", "Embedding complete. You can now save the image.")
            self.update_progress(40)
            self.update_status("Embedding complete. Ready to save.")
            self.save_button.setEnabled(True)  # Enables save button
        else:
            QMessageBox.warning(self, "Error", "Embedding failed.")
    
    def set_controller(self, controller):
        self.controller = controller

    def MainWindow(self):
        if hasattr(self, 'controller') and self.controller:
            self.controller.show_main_window()
        else:
            from MainPage_Package.MainPage import MainWindow
            self.main_window = MainWindow()
            self.close()
            self.main_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DCTEmbeddingApp()
    window.show()
    sys.exit(app.exec_())

