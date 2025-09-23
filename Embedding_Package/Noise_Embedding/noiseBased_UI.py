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
from . import backend_noise_embedding as backend
from . import colour_output as co
import shutil
import os
import tempfile

class NoiseEmbeddingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Noise-Based Embedding Window")
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
        self.analysisWindow = None
        #self.block_size = 4

        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label, alignment=QtCore.Qt.AlignLeft)

    def init_main_tab(self):
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Noise-Based Embedding", self)
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

        self.central_button = QPushButton("Central Window", self)
        self.central_button.setFixedSize(200, 30)
        self.central_button.clicked.connect(self.go_to_central_window)

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
        main_layout.addWidget(self.central_button, alignment=QtCore.Qt.AlignCenter)

        self.main_tab.setLayout(main_layout)

    def init_advanced_tab(self):
        advanced_layout = QVBoxLayout()

        self.output_label = QLabel("File Output:")
        self.output = QComboBox()
        self.output.addItems(["Colour", "GreyScale"])
        self.output_status = QLabel("Standard")
        self.output_status.setStyleSheet("color: green;") 

        self.block_size_label = QLabel("Block Size:")
        self.block_size = QComboBox()
        self.block_size.addItems(["4", "8", "16", "32", "64", "128", "256"])
        self.block_size_status = QLabel("Standard")
        self.block_size_status.setStyleSheet("color: green;")

        self.error_correction_label = QLabel("Error Correcting Code:")
        self.error_correction = QComboBox()
        self.error_correction.addItems(["None", "Hamming Code"])
        self.error_correction_status = QLabel("Standard")
        self.error_correction_status.setStyleSheet("color: green;")

        option_layouts = [
            (self.output_label, self.output, self.output_status),
            (self.block_size_label, self.block_size, self.block_size_status),
            (self.error_correction_label, self.error_correction, self.error_correction_status),
        ]

        # Adding the options to the layout
        for label, widget, status in option_layouts:
            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(widget)
            row.addWidget(status)
            advanced_layout.addLayout(row)

        self.error_correction.currentTextChanged.connect(self.update_error_correction)

        self.advanced_tab.setLayout(advanced_layout)

    def update_error_correction(self, selected_method):
        self.error_correction = selected_method
        print(f"Error correction method updated to: {self.error_correction}") # Debugging

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
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
            self.thumbnail_label.setPixmap(pixmap)
            self.update_status(f"Image selected: {file_path}")

    def update_progress(self, value):
        self.progress = min(100, self.progress + value)
        self.progress_bar.setValue(self.progress)

    def update_status(self, status_text):
        self.status_label.setText(f"Status: {status_text}")

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
                file_path += ".png"  # Ensures PNG extension

            shutil.copy(self.temp_embedded_path, file_path)
            self.update_status(f"Image saved to {file_path}")
            self.update_progress(100)

            self.show_save_confirmation(file_path)

    def show_save_confirmation(self, file_path):
        confirmation_msg = f"Image saved successfully!\nFile: {file_path}"
        QMessageBox.information(
            self, 
            "Save Successful", 
            confirmation_msg)




    def begin_embedding(self):
        if not self.image_path or not self.text_path:
            QMessageBox.warning(self, "Error", "Please select both an image and a text file first.")
            return

        # Generates a temporary file path for embedding
        temp_dir = tempfile.gettempdir()
        self.temp_embedded_path = os.path.join(temp_dir, "embedded_image.png")  # PNG format


        imageEligibility_and_Embedding = backend.complete_save(self.text_path, self.image_path, self.temp_embedded_path, 
                                    int(self.block_size.currentText()), self.error_correction)

        if self.output.currentText() == "Colour":
            print("Applying additional colour processing...")  # Debugging
            
            processed_output_path = os.path.join(temp_dir, "processed_embedded_image.png")
            
            preserved = co.transfer_colour_preserve_grayscale(self.image_path, self.temp_embedded_path, processed_output_path)  
            if preserved == False:
                QMessageBox.warning(self, "Warning", "Some differences in greyscale values were detected. Decryption may not be perfect.")

            self.temp_embedded_path = processed_output_path  

        if os.path.exists(self.temp_embedded_path):
            if imageEligibility_and_Embedding == True:
                QMessageBox.information(self, "Success", "Embedding complete. You can now save the image.")
                self.update_progress(40)
                self.update_status("Embedding complete. Ready to save.")
                self.save_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Warning", "The embedding is partially complete.\nNote that part of the message cannot be embedded due to limited size.\nTo fix this, use a larger image or a smaller text file.")
                self.save_button.setEnabled(True)  # Enables save button
        else:
            QMessageBox.warning(self, "Error", "Embedding failed.")

    def set_controller(self, controller):
        self.controller = controller

    def go_to_central_window(self):
        if hasattr(self, 'controller') and self.controller:
            self.controller.show_main_window()
        else:
            from MainPage_Package.MainPage import MainWindow
            self.main_window = MainWindow()
            self.close()
            self.main_window.show()





if __name__ == "__main__":
     app = QApplication(sys.argv)
     window = NoiseEmbeddingApp()
     window.show()
     sys.exit(app.exec_())

