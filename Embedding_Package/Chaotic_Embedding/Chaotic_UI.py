import sys
import cv2
import numpy as np
import math
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QProgressBar, QMessageBox, QTabWidget, QComboBox, 
    QSpinBox, QDialog, QLineEdit, QTableWidget, QTableWidgetItem, QGridLayout, QCheckBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtCore
from . import chaos_backend as cb
import shutil
import os
import tempfile
from collections import Counter
import copy

class LogisticMapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Logistic Map Parameters")
        self.setGeometry(300, 300, 300, 200)

        layout = QVBoxLayout()
        
        self.let_run_label = QLabel("Let Run:")
        self.let_run_input = QLineEdit()
        self.x0_label = QLabel("X0:")
        self.x0_input = QLineEdit()
        self.y0_label = QLabel("Y0:")
        self.y0_input = QLineEdit()
        self.r_label = QLabel("R:")
        self.r_input = QLineEdit()
        
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_params)
        
        layout.addWidget(self.let_run_label)
        layout.addWidget(self.let_run_input)
        layout.addWidget(self.x0_label)
        layout.addWidget(self.x0_input)
        layout.addWidget(self.y0_label)
        layout.addWidget(self.y0_input)
        layout.addWidget(self.r_label)
        layout.addWidget(self.r_input)
        layout.addWidget(self.save_button)
        
        self.setLayout(layout)
        
    def save_params(self):
        self.let_run = int(self.let_run_input.text())
        self.x0 = float(self.x0_input.text())
        self.y0 = float(self.y0_input.text())
        self.r = float(self.r_input.text())
        self.accept()

class DictionaryEditor(QDialog):
    def __init__(self, parent=None, current_dict=None):
        super().__init__(parent)
        self.setWindowTitle("Dictionary Editor")
        self.setGeometry(200, 200, 650, 500)
        
        self.parent = parent
        self.original_dict = cb. embedding_alphabet.copy()
        self.current_dict = current_dict if current_dict is not None else getattr(parent, 'current_alpha_dict', self.original_dict.copy())
        self.modified_dict = None
        
        self.init_ui()
        self.populate_table()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Edit the character mapping below.\n"
            "Empty character fields are allowed.\n"
            "Format: Character → (RGB, Alpha)\n"
            "Changes apply to current session only."
        )
        layout.addWidget(info_label)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Character", "RGB Value", "Alpha Value"])
        self.table.setColumnWidth(0, 150)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        button_style = """
            QPushButton {
                min-width: 100px;
                padding: 6px;
                margin: 2px;
            }
        """
        
        self.add_btn = QPushButton("Add Row", self)
        self.del_btn = QPushButton("Delete Selected Row", self)
        self.save_dict_btn = QPushButton("Save Dictionary", self)
        self.load_dict_btn = QPushButton("Load Dictionary", self)
        self.apply_btn = QPushButton("Apply Changes", self)
        self.reset_btn = QPushButton("Reset to Default", self)
        self.cancel_btn = QPushButton("Cancel", self)
        
        for btn in [self.add_btn, self.del_btn, self.save_dict_btn, 
                self.load_dict_btn, self.apply_btn, self.reset_btn, self.cancel_btn]:
            btn.setStyleSheet(button_style)
        
        btn_grid = QGridLayout()
        btn_grid.setSpacing(10)
        
        btn_grid.addWidget(self.add_btn, 0, 0)
        btn_grid.addWidget(self.del_btn, 0, 1)
        btn_grid.addWidget(self.save_dict_btn, 0, 2)
        
        btn_grid.addWidget(self.load_dict_btn, 1, 0)
        btn_grid.addWidget(self.apply_btn, 1, 1)
        btn_grid.addWidget(self.reset_btn, 1, 2)
        btn_grid.addWidget(self.cancel_btn, 1, 3)
        
        btn_grid.setColumnStretch(0, 1)
        btn_grid.setColumnStretch(1, 1)
        btn_grid.setColumnStretch(2, 1)
        btn_grid.setColumnStretch(3, 1)
        
        layout.addWidget(self.table)
        layout.addLayout(btn_grid)
        
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        self.setLayout(layout)
        self.table.setSortingEnabled(True)
        
        self.add_btn.clicked.connect(self.add_row)
        self.del_btn.clicked.connect(self.delete_row)
        self.save_dict_btn.clicked.connect(self.save_dictionary)
        self.load_dict_btn.clicked.connect(self.load_dictionary)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.reset_btn.clicked.connect(self.reset_dictionary)
        self.cancel_btn.clicked.connect(self.reject)
        
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))
        self.table.setItem(row, 1, QTableWidgetItem("0"))
        self.table.setItem(row, 2, QTableWidgetItem("0"))
        self.table.scrollToBottom()
        self.table.editItem(self.table.item(row, 0))
    
    def delete_row(self):
        selected = self.table.selectedItems()
        if not selected:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Please select rows to delete")
            return
        
        rows_to_delete = sorted({item.row() for item in selected}, reverse=True)
        for row in rows_to_delete:
            self.table.removeRow(row)
    
    def populate_table(self):
        self.table.setRowCount(0)
        for char, (rgb, alpha) in self.current_dict.items():
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(char if char is not None else ""))
            self.table.setItem(row, 1, QTableWidgetItem(str(rgb)))
            self.table.setItem(row, 2, QTableWidgetItem(str(alpha)))
    
    def apply_changes(self):
        new_dict = {}
        errors = []
        
        for row in range(self.table.rowCount()):
            char_item = self.table.item(row, 0)
            rgb_item = self.table.item(row, 1)
            alpha_item = self.table.item(row, 2)
            
            if not (char_item or rgb_item or alpha_item):
                continue
                
            char = char_item.text() if char_item and char_item.text() else ""
            
            try:
                rgb = int(rgb_item.text()) if rgb_item and rgb_item.text() else 0
            except ValueError:
                errors.append(f"Row {row+1}: RGB must be an integer")
                continue
                
            try:
                alpha = int(alpha_item.text()) if alpha_item and alpha_item.text() else 0
            except ValueError:
                errors.append(f"Row {row+1}: Alpha must be an integer (0 is valid)")
                continue
                
            new_dict[char] = (rgb, alpha)
        
        if errors:
            QtWidgets.QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
            return
        
        self.modified_dict = new_dict
        self.accept()

    def reset_dictionary(self):
        reply = QtWidgets.QMessageBox.question(
            self, "Confirm Reset", "Reset to original values?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply == QtWidgets.QMessageBox.Yes:
            self.current_dict = self.original_dict.copy()
            self.populate_table()
    
    def get_modified_dict(self):
        return self.modified_dict if self.modified_dict is not None else self.current_dict

    def save_dictionary(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Dictionary", "", "Dictionary Files (*.dict);;All Files (*)")
        
        if file_path:
            try:
                if not file_path.lower().endswith('.dict'):
                    file_path += '.dict'
                
                with open(file_path, 'w') as f:
                    import json
                    json.dump(self.current_dict, f)
                    
                QMessageBox.information(self, "Success", 
                                    "Dictionary saved successfully!")
            except Exception as e:
                QMessageBox.warning(self, "Error", 
                                f"Failed to save dictionary: {str(e)}")

    def load_dictionary(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Dictionary", "", "Dictionary Files (*.dict);;All Files (*)")
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    import json
                    loaded_dict = json.load(f)
                    
                    validated_dict = {}
                    for char, values in loaded_dict.items():
                        if isinstance(values, (list, tuple)) and len(values) == 2:
                            rgb = int(values[0]) if values[0] is not None else 0
                            alpha = int(values[1]) if values[1] is not None else 0
                            validated_dict[str(char)] = (rgb, alpha)
                        else:
                            raise ValueError("Invalid value format")
                    
                    self.current_dict = validated_dict
                    self.populate_table()
                    QMessageBox.information(self, "Success", 
                                        "Dictionary loaded successfully.")
                    return True
                    
            except Exception as e:
                QMessageBox.warning(self, "Error", 
                                f"Failed to load dictionary: {str(e)}")
                return False

class ChaoticEmbeddingApp(QWidget):
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Chaotic Embedding Window")
        self.setGeometry(200, 200, 600, 400)
        self.progress = 0
        self.text_length = 0

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
        self.current_alpha_dict = copy.deepcopy(cb.embedding_alphabet)
        self.original_alpha_dict = copy.deepcopy(cb.embedding_alphabet)

        self.r = None
        self.x0 = None
        self.y0 = None
        self.let_run = None

        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setFixedHeight(20)
        main_layout.addWidget(self.status_label, alignment=QtCore.Qt.AlignLeft)

    def init_main_tab(self):
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Chaotic Embedding", self)
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
        advanced_layout.setSpacing(15)
        advanced_layout.setContentsMargins(10, 10, 10, 10)

        # Frequency Embedding Section
        freq_layout = QHBoxLayout()
        self.frequency_embedding_label = QLabel("Frequency Embedding:")
        self.frequency_embedding = QComboBox()
        self.frequency_embedding.addItems(["Off", "On"])
        self.frequency_embedding_status = QLabel("Standard")
        self.frequency_embedding_status.setStyleSheet("color: green;")
        
        freq_layout.addWidget(self.frequency_embedding_label)
        freq_layout.addWidget(self.frequency_embedding)
        freq_layout.addWidget(self.frequency_embedding_status)
        advanced_layout.addLayout(freq_layout)

        # Alpha Embedding Section
        alpha_layout = QHBoxLayout()
        self.alpha_embedding_label = QLabel("Alpha Embedding:")
        self.alpha_embedding = QComboBox()
        self.alpha_embedding.addItems(["Off", "On"])
        self.alpha_embedding_status = QLabel("Standard")
        self.alpha_embedding_status.setStyleSheet("color: green;")
        
        alpha_layout.addWidget(self.alpha_embedding_label)
        alpha_layout.addWidget(self.alpha_embedding)
        alpha_layout.addWidget(self.alpha_embedding_status)
        advanced_layout.addLayout(alpha_layout)

        btn_layout = QHBoxLayout()
        self.edit_alphabet_button = QPushButton("Edit Alphabet")
        self.edit_alphabet_button.clicked.connect(self.edit_alphabet)
        btn_layout.addWidget(self.edit_alphabet_button)
        advanced_layout.addLayout(btn_layout)

        controls_layout = QHBoxLayout()
        
        self.chaos_map_label = QLabel("Select Chaos Map:")
        self.chaos_map_dropdown = QComboBox()
        self.chaos_map_dropdown.addItems(["None", "Logistic", "Lorenz"])
        self.chaos_map_dropdown.currentIndexChanged.connect(self.chaos_map_changed)
        
        self.edit_params_button = QPushButton("Edit Parameters")
        self.edit_params_button.setEnabled(False)
        self.edit_params_button.clicked.connect(self.open_logistic_map_dialog)
        
        self.chaos_map_status = QLabel("Parameters: None")
        controls_layout.addWidget(self.chaos_map_label)
        controls_layout.addWidget(self.chaos_map_dropdown)
        controls_layout.addWidget(self.edit_params_button)
        controls_layout.addWidget(self.chaos_map_status)
        advanced_layout.addLayout(controls_layout)

        self.plot_layout = QHBoxLayout()
        
        self.plot_label_x = QLabel("X Logistic Map")
        self.plot_label_x_image = QLabel()
        
        self.plot_label_y = QLabel("Y Logistic Map")
        self.plot_label_y_image = QLabel()
        
        self.plot_layout.addWidget(self.plot_label_x)
        self.plot_layout.addWidget(self.plot_label_x_image)
        self.plot_layout.addWidget(self.plot_label_y)
        self.plot_layout.addWidget(self.plot_label_y_image)
        advanced_layout.addLayout(self.plot_layout)

        self.frequency_embedding.currentIndexChanged.connect( # Sets up connections
            lambda: self.update_status_label(
                self.frequency_embedding, 
                self.frequency_embedding_status, 
                "Off"
            )
        )
        
        alpha_enabled = cb.get_alpha_state()
        self.alpha_embedding.setCurrentIndex(1 if alpha_enabled else 0)
        self.alpha_embedding.currentIndexChanged.connect(self.toggle_alpha_embedding)
        self.alpha_embedding.currentIndexChanged.connect(
            lambda: self.update_status_label(
                self.alpha_embedding,
                self.alpha_embedding_status,
                "Off"
            )
        )

        self.advanced_tab.setLayout(advanced_layout)

    def update_text_length(self):
        self.text_length = len(self.text_input.toPlainText())
    
    def chaos_map_changed(self):
        selected = self.chaos_map_dropdown.currentText()
        if selected == "Logistic":
            self.edit_params_button.setEnabled(True)
        else:
            self.edit_params_button.setEnabled(False)
            self.chaos_map_status.setText("Parameters: None")
            self.plot_label_x_image.clear()
            self.plot_label_y_image.clear()
    
    def open_logistic_map_dialog(self):
        dialog = LogisticMapDialog(self)
        if dialog.exec_():
            self.let_run = dialog.let_run
            self.x0 = dialog.x0
            self.y0 = dialog.y0
            self.r = dialog.r

            self.chaos_map_params = f"Let Run: {self.let_run}, X0: {self.x0}, Y0: {self.y0}, R: {self.r}"
            self.chaos_map_status.setText(f"Parameters: {self.chaos_map_params}")

            self.plot_logistic_map(self.let_run, self.x0, self.y0, self.r)

    def plot_logistic_map(self, let_run, x0, y0, r):
        x = x0
        y = y0
        x_values = []
        y_values = []

        for _ in range(let_run):
            x = r * x * (1 - x)
            y = r * y * (1 - y)

        for _ in range(self.text_length):
            x = r * x * (1 - x)
            y = r * y * (1 - y)
            x_values.append(x)
            y_values.append(y)

        plt.figure()
        plt.plot(x_values, 'bo', markersize=2)
        plt.xlabel("Iteration")
        plt.ylabel("X")
        plt.title("Logistic Map - X Coordinates")
        plt.savefig("logistic_map_x.png")
        
        plt.figure()
        plt.plot(y_values, 'ro', markersize=2)
        plt.xlabel("Iteration")
        plt.ylabel("Y")
        plt.title("Logistic Map - Y Coordinates")
        plt.savefig("logistic_map_y.png")

        self.plot_label_x_image.setPixmap(QPixmap("logistic_map_x.png").scaled(400, 300))
        self.plot_label_y_image.setPixmap(QPixmap("logistic_map_y.png").scaled(400, 300))
        self.update_status("Chaotic (Lorenz) Mapping Plotted")

    def show_help(self):
        QMessageBox.information(self, "Help", "This window allows you to embed denary data into images.\n\n"
                                                "Instructions:\n"
                                                "1. Select an image file.\n"
                                                "2. Select a text file.\n"
                                                "3. Click 'Begin Embedding' to start the process.\n"
                                                "4. Save your work.")

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
            self.text_length = len(text_content) 

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
                file_path += ".png"

            shutil.copy(self.temp_embedded_path, file_path)
            self.update_status(f"Image saved to {file_path}")
            self.update_progress(100)

    def update_progress(self, value):
        self.progress = min(100, self.progress + value)
        self.progress_bar.setValue(self.progress)

    def update_status(self, status_text):
        self.status_label.setText(f"Status: {status_text}")

    def begin_embedding(self):
        if not self.image_path or not self.text_path:
            QMessageBox.warning(self, "Error", "Please select both an image and a text file first.")
            return

        if self.r is None or self.x0 is None or self.y0 is None or self.let_run is None:
            QMessageBox.warning(self, "Error", "Please set Logistic Map parameters first.")
            return

        missing_chars = self.find_missing_chars(self.text_path, self.current_alpha_dict)
        if missing_chars:
            char_warning = QMessageBox(self)
            char_warning.setIcon(QMessageBox.Warning)
            char_warning.setWindowTitle("Warning: Missing Characters")
            shown_chars = ", ".join(missing_chars)
            msg_text = (f"The following characters aren't in your dictionary:\n\n"
                       f"{shown_chars}\n\n"
                       "These characters will be skipped during embedding.\n"
                       "You can add them in the Alphabet Editor if needed.")
            char_warning.setText(msg_text)
            char_warning.exec_()
        
        if self.frequency_embedding.currentText() == "On":
            self.current_alpha_dict = self.reorder_dictionary_by_frequency(self.text_path)
            cb. embedding_alphabet = self.current_alpha_dict.copy()

        temp_dir = tempfile.gettempdir()
        self.temp_embedded_path = os.path.join(temp_dir, "embedded_image.png")

        try:
            current_dict = getattr(self, 'current_alpha_dict', cb. embedding_alphabet.copy())
            
            sanitized_dict = {}
            for char, (rgb, alpha) in current_dict.items():
                sanitized_rgb = int(rgb) if rgb is not None else 0
                sanitized_alpha = int(alpha) if alpha is not None else 0
                sanitized_dict[char] = (sanitized_rgb, sanitized_alpha)
            

            result = cb.embedding(
                self.text_path, 
                self.image_path, 
                self.r, 
                self.x0, 
                self.y0, 
                self.let_run, 
                self.temp_embedded_path,
                alphabet=sanitized_dict
            )

            if os.path.exists(self.temp_embedded_path):
                QMessageBox.information(self, "Success", "Embedding complete. You can now save the image.")
                self.update_progress(40)
                self.update_status("Embedding complete. Ready to save.")
                self.save_button.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "Embedding failed - no output file created")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Embedding failed: {str(e)}")
            self.update_status(f"Error: {str(e)}")

    def update_status_label(self, widget, status_label, default_value):
        if isinstance(widget, QComboBox):
            is_standard = widget.currentText() == default_value
        else:
            is_standard = widget.value() == default_value

        if is_standard:
            status_label.setText("Standard")
            status_label.setStyleSheet("color: green;")
        else:
            status_label.setText("Custom")
            status_label.setStyleSheet("color: black;")

    def edit_alphabet(self):
        use_frequency = (self.frequency_embedding.currentText() == "On" and 
                        hasattr(self, 'text_path') and 
                        self.text_path and 
                        os.path.exists(self.text_path))
        
        if use_frequency and not hasattr(self, 'original_alpha_dict_before_frequency'):
            self.original_alpha_dict_before_frequency = copy.deepcopy(self.current_alpha_dict)
        
        if use_frequency:
            current_dict = self.reorder_dictionary_by_frequency(self.text_path)
        else:
            current_dict = getattr(self, 'original_alpha_dict_before_frequency', 
                                copy.deepcopy(self.current_alpha_dict))
        
        editor = DictionaryEditor(self, current_dict)
        
        if editor.exec_() == QDialog.Accepted:
            self.current_alpha_dict = editor.get_modified_dict()
            cb. embedding_alphabet = self.current_alpha_dict.copy()
            
            if hasattr(self, 'original_alpha_dict_before_frequency'):
                del self.original_alpha_dict_before_frequency
            
            QMessageBox.information(self, "Success", 
                                "Alphabet changes saved for this session")

    def toggle_alpha_embedding(self, index):
        if index == 0:
            if not hasattr(self, 'original_alpha_dict'):
                self.original_alpha_dict = copy.deepcopy(self.current_alpha_dict)
            
            self.current_alpha_dict = {k: (v[0], 0) for k, v in self.current_alpha_dict.items()}
            cb.disable_alpha_embedding()
        else:
            if hasattr(self, 'original_alpha_dict'):
                self.current_alpha_dict = self.original_alpha_dict
                del self.original_alpha_dict
                cb.enable_alpha_embedding()
        
        self.update_status_label(self.alpha_embedding, self.alpha_embedding_status, "Off")
    
    def reorder_dictionary_by_frequency(self, text_path):
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read().lower()
            
            freq = Counter(char for char in text if char in self.current_alpha_dict)
            
            sorted_chars = sorted(self.current_alpha_dict.keys(),
                                key=lambda c: (-freq.get(c, 0), 
                                            list(self.current_alpha_dict.keys()).index(c)))
            
            return {char: self.current_alpha_dict[char] for char in sorted_chars}
            
        except Exception as e:
            print(f"Frequency analysis failed: {e}")
            return copy.deepcopy(self.current_alpha_dict)
        
    def toggle_distribution(self, state):
        enable = (state == Qt.Checked)
        self.pixel_distribution.setEnabled(enable)
        status = "enabled" if enable else "disabled"
        self.update_status(f"Pixel distribution {status}")
    
    def find_missing_chars(self, text_path, dictionary):
        try:
            with open(text_path, 'r', encoding='utf-8') as f:
                text = f.read().lower()
            
            text_chars = set(char for char in text if char.strip())
            dict_chars = set(dictionary.keys())
            missing_chars = sorted(text_chars - dict_chars)
            
            return missing_chars
            
        except Exception as e:
            print(f"Error finding missing characters: {e}")
            return []
    
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
    window = ChaoticEmbeddingApp()
    window.show()
    sys.exit(app.exec_())