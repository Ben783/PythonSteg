import sys
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QMessageBox, QPushButton, QRadioButton, QButtonGroup, QFrame, QComboBox, QLineEdit, QMainWindow, QDialog, QDialogButtonBox, QProgressBar, QHBoxLayout, QTabWidget, QWidget, QGridLayout, QCheckBox
from .  import chaotic_decryption_backend as cdb
from . import noise_decryption as nd
from . import DCT_decryption_backend as ddb
from . import RGBA_decryption_backend as rdb
from . import distributed_RGBA_decryption as drdb
from . import Topo_decryption as td
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QAction, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
import importlib.util
import os
import json
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class DecryptionPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decryption Page")
        self.setGeometry(100, 100, 700, 500)

        #title_label = QLabel("Decryption Page")
        #title_label.setFont(QtGui.QFont('Aptos Body', 16, QtGui.QFont.Bold))
        #title_label.setAlignment(Qt.AlignCenter)

        self.tab_widget = QTabWidget()

        self.main_tab = QWidget()
        self.init_main_tab()  # creates self.main_layout, which belongs to self.main_tab
        self.tab_widget.addTab(self.main_tab, "Main")

        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced Options")

        # Status label (outside tabs)
        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_label.setFixedHeight(20)

        window_layout = QVBoxLayout()
        #window_layout.addWidget(title_label)
        window_layout.addWidget(self.tab_widget)
        window_layout.addWidget(self.status_label, alignment=Qt.AlignLeft)

        central_widget = QWidget()
        central_widget.setLayout(window_layout)
        self.setCentralWidget(central_widget)

        # Initialise parameters as None
        self.org_file_path = None
        self.alt_file_path = None
        self.r_value = None
        self.x_value = None
        self.y_value = None
        self.let_run_value = None
        self.map_type = None


    def init_main_tab(self):
        self.main_layout = QVBoxLayout(self.main_tab)

        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)  # Removes extra margins

        self.title_label = QLabel("Decryption Page", self)
        self.title_label.setFont(QtGui.QFont('Aptos Body', 16, QtGui.QFont.Bold))
        title_layout.addWidget(self.title_label, alignment=QtCore.Qt.AlignCenter)

        self.help_button = QPushButton("i", self)
        self.help_button.setFixedSize(20, 20)
        self.help_button.setStyleSheet("""
            color: blue; 
            font-weight: bold; 
            border: 1px solid gray; 
            border-radius: 5px;
            margin-left: 5px;  # Small gap between title and button
        """)
        self.help_button.clicked.connect(self.show_help)
        title_layout.addWidget(self.help_button, alignment=QtCore.Qt.AlignLeft)

        self.main_layout.addWidget(title_container, alignment=QtCore.Qt.AlignCenter)

        self.subtitle_label = QLabel("Select a decryption technique", self)
        self.subtitle_label.setFont(QtGui.QFont('Aptos Body', 12))
        self.subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.subtitle_label)

        file_buttons_layout = QHBoxLayout() # File selection buttons (side by side)
        self.main_layout.addLayout(file_buttons_layout)

        self.select_image1_button = QPushButton("Select Original Image", self)
        self.select_image1_button.clicked.connect(self.select_image1)
        file_buttons_layout.addWidget(self.select_image1_button)

        self.select_image2_button = QPushButton("Select Steg Image", self)
        self.select_image2_button.clicked.connect(self.select_image2)
        file_buttons_layout.addWidget(self.select_image2_button)

        self.image1_path_label = QLabel("Original File: None", self)
        self.image1_path_label.setStyleSheet("color: red;")
        self.main_layout.addWidget(self.image1_path_label)

        self.image2_path_label = QLabel("Cover File: None", self)
        self.image2_path_label.setStyleSheet("color: red;")
        self.main_layout.addWidget(self.image2_path_label)

        self.selected_technique = QButtonGroup(self)
        self.selected_technique.buttonClicked.connect(self.change_subtitle)

        techniques = ["Denary Bit Decryption", "Noise-Based Decryption", "DCT Decryption", "Chaotic Decryption", "Topological Domain Decryption"]
        radio_frame = QFrame(self)
        radio_layout = QVBoxLayout(radio_frame)
        self.main_layout.addWidget(radio_frame)

        for technique in techniques:
            radio_button = QRadioButton(technique, self)
            self.selected_technique.addButton(radio_button)
            radio_layout.addWidget(radio_button)

        self.options_frame = QFrame(self)
        self.options_frame.setHidden(True)  # Initially hidden
        self.options_layout = QVBoxLayout(self.options_frame)

        main_h_layout = QHBoxLayout()
        self.main_layout.addLayout(main_h_layout)
        main_h_layout.addWidget(radio_frame)
        main_h_layout.addWidget(self.options_frame)

        self.begin_button = QPushButton("Begin Decryption", self)
        self.begin_button.clicked.connect(self.begin_decryption)
        self.main_layout.addWidget(self.begin_button, alignment = QtCore.Qt.AlignCenter)
        self.begin_button.setFixedSize(150, 25)

        self.mainPage_button = QPushButton("Central Window", self)
        self.mainPage_button.clicked.connect(self.MainWindow)
        self.main_layout.addWidget(self.mainPage_button, alignment=QtCore.Qt.AlignCenter)
        self.mainPage_button.setFixedSize(200, 30)


        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        self.main_layout.addWidget(self.progress_bar)
        

    def init_advanced_tab(self):
        advanced_layout = QVBoxLayout()


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

        self.edit_dictionary_button = QPushButton("Edit Dictionary", self)
        self.edit_dictionary_button.clicked.connect(self.show_dictionary_editor)


        option_layouts = [
            (self.block_size_label, self.block_size, self.block_size_status),
            (self.error_correction_label, self.error_correction, self.error_correction_status),
            (self.edit_dictionary_button, None, None)
        ]

        for label, widget, status in option_layouts:
            row = QHBoxLayout()
            row.addWidget(label)
            row.addWidget(widget)
            row.addWidget(status)
            advanced_layout.addLayout(row)

        self.error_correction.currentTextChanged.connect(self.update_error_correction)

        self.advanced_tab.setLayout(advanced_layout)
    

    def go_home(self):
        self.tab_widget.setCurrentIndex(0)

    def change_subtitle(self):
        selected_technique = self.selected_technique.checkedButton().text()
        self.subtitle_label.setText(selected_technique)

        # Updates file selection button text based on technique (object for 3D)
        if selected_technique == "Topological Domain Decryption":
            self.select_image1_button.setText("Select Original Object")
            self.select_image2_button.setText("Select Steg Object")
            self.image1_path_label.setText("Original Object: None")
            self.image2_path_label.setText("Steg Object: None")
        else:
            self.select_image1_button.setText("Select Original Image")
            self.select_image2_button.setText("Select Steg Image") 
            self.image1_path_label.setText("Original File: None")
            self.image2_path_label.setText("Cover File: None")

        for i in reversed(range(self.options_layout.count())):
            widget = self.options_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        self.options_frame.setHidden(False)
        if selected_technique == "Noise-Based Decryption":
            group_box = QGroupBox("Noise-Based Decryption Settings")
            group_layout = QVBoxLayout()

            self.block_size_status = QLabel("Current Selected Block Size: " + str(self.block_size.currentText()))
            self.error_correction_status = QLabel("Current Selected ECC: " + self.error_correction.currentText())

            group_layout.addWidget(self.block_size_status)
            group_layout.addWidget(self.error_correction_status)

            group_box.setLayout(group_layout)
            self.options_layout.addWidget(group_box)

        elif selected_technique == "Chaotic Decryption":
            # Chaotic parameters inputs
            self.options_layout.addWidget(QLabel("Enter r value:"))
            self.r_input = QLineEdit(self)
            self.options_layout.addWidget(self.r_input)

            self.options_layout.addWidget(QLabel("Enter x value:"))
            self.x_input = QLineEdit(self)
            self.options_layout.addWidget(self.x_input)

            self.options_layout.addWidget(QLabel("Enter y value:"))
            self.y_input = QLineEdit(self)
            self.options_layout.addWidget(self.y_input)

            self.options_layout.addWidget(QLabel("Enter let run value:"))
            self.let_run_input = QLineEdit(self)
            self.options_layout.addWidget(self.let_run_input)

            self.options_layout.addWidget(QLabel("Select Map Type:"))
            self.map_dropdown = QComboBox(self)
            self.map_dropdown.addItems(["Logistic Map", "Henon Map", "Lorenz Map"])
            self.options_layout.addWidget(self.map_dropdown)

            self.r_input.textChanged.connect(self.update_chaotic_inputs)
            self.x_input.textChanged.connect(self.update_chaotic_inputs)
            self.y_input.textChanged.connect(self.update_chaotic_inputs)
            self.let_run_input.textChanged.connect(self.update_chaotic_inputs)
            self.map_dropdown.currentIndexChanged.connect(self.update_chaotic_inputs)
        
        elif selected_technique == "Denary Bit Decryption":
            self.distributed_checkbox = QCheckBox("Enable Distributed Decryption")
            self.distributed_checkbox.stateChanged.connect(self.toggle_distributed_options)
            self.options_layout.addWidget(self.distributed_checkbox)
            
            self.options_layout.addWidget(QLabel("Group Size:"))
            self.distributed_block_size = QComboBox()
            self.distributed_block_size.addItems(["4", "8", "16", "32", "64", "128", "256"])
            self.distributed_block_size.setCurrentIndex(2)  # Default to 16
            self.distributed_block_size.setEnabled(False)
            self.options_layout.addWidget(self.distributed_block_size)

            self.edit_dict_button = QPushButton("Edit Dictionary", self)
            self.edit_dict_button.clicked.connect(self.show_dictionary_editor)
            self.options_layout.addWidget(self.edit_dict_button)

        else:
            self.options_frame.setHidden(True)

    def select_image1(self):
        selected_button = self.selected_technique.checkedButton()
        if selected_button and selected_button.text() == "Topological Domain Decryption":
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a 3D object file", "", "3D Object files (*.obj *.stl *.ply);;All files (*.*)")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.webp)")
        
        if file_path:
            self.org_file_path = file_path
            self.image1_path_label.setText(f"Original File: {file_path}")
            self.image1_path_label.setStyleSheet("color: green;")

    def select_image2(self):
        selected_button = self.selected_technique.checkedButton()
        if selected_button and selected_button.text() == "Topological Domain Decryption":
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a 3D object file", "", "3D Object files (*.obj *.stl *.ply);;All files (*.*)")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select an image", "", "Image files (*.jpg *.jpeg *.png *.gif);;All files (*.*)")
        
        if file_path:
            self.alt_file_path = file_path
            self.image2_path_label.setText(f"Cover File: {file_path}")
            self.image2_path_label.setStyleSheet("color: green;")

    def begin_decryption(self):
        selected_button = self.selected_technique.checkedButton()
        if selected_button and self.org_file_path and self.alt_file_path:
            selected_technique = selected_button.text()
            self.status_label.setText(f"Status: {selected_technique} in progress...")
            self.progress_bar.setValue(50)

            if selected_technique == "Chaotic Decryption":
                if not self.r_value or not self.x_value or not self.y_value or not self.let_run_value:
                    self.status_label.setText("Status: Please fill in all chaotic parameters.")
                else:
                    print("Running Chaotic Decryption...")

                    # Retrieving parameters
                    r = float(self.r_input.text())
                    x0 = float(self.x_input.text())
                    y0 = float(self.y_input.text())
                    let_run = int(self.let_run_input.text())

                    custom_dictionary = getattr(self, 'current_rgba_dict', cdb.embedding_alphabet) 

                    decrypted_message = cdb.decrypt(r, x0, y0, let_run, self.org_file_path, self.alt_file_path, alphabet = custom_dictionary) # Calls decryption function

                    self.result_page = DecryptionResultPage(decrypted_message)
                    self.result_page.show()

                    self.status_label.setText("Status: Decryption Completed")
                    self.progress_bar.setValue(100)

            elif selected_technique == "Noise-Based Decryption":
                print("Running Noise-Based Decryption...")
                block_size = int(self.block_size.currentText())
                ecc = self.error_correction.currentText()
                if ecc == "Hamming Code":
                    print("Hamming")
                    ecc = True
                else:
                    ecc = False

                result = nd.decryption(self.org_file_path, self.alt_file_path, block_size, ecc)

                self.result_page = DecryptionResultPage(result)
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)

            elif selected_technique == "DCT Decryption":
                print("Running DCT Decryption...")
                result = ddb.extract_secret_message_from_image(self.alt_file_path)
                self.result_page = DecryptionResultPage(result)
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)   

            elif selected_technique == "Denary Bit Decryption":
                print("Running D-B Decryption")
                try:
                    custom_dict = getattr(self, 'current_rgba_dict', rdb.dictionary)

                    if hasattr(self, 'distributed_checkbox') and self.distributed_checkbox.isChecked():
                        block_size = int(self.distributed_block_size.currentText())
                        self.status_label.setText("Status: Running distributed decryption...")
                        result = drdb.RGBA_decryption_distributed(
                            self.org_file_path,
                            self.alt_file_path,
                            groupSize=block_size,
                            dictionary=custom_dict
                        )
                    else:
                        self.status_label.setText("Status: Running standard decryption...")
                        result = rdb.decode(
                            self.org_file_path,
                            self.alt_file_path,
                            alpha_dict=custom_dict
                        )
                    
                    self.result_page = DecryptionResultPage(result)
                    self.result_page.show()
                    self.status_label.setText("Status: Decryption Completed")
                    self.progress_bar.setValue(100)
                except Exception as e:
                    self.status_label.setText(f"Error: {str(e)}")
                    self.progress_bar.setValue(0)

            elif selected_technique == "Topological Domain Decryption":
                print("Running Topological Domain Decryption...")
                result = td.extract_hidden_message(self.alt_file_path)
                
                self.result_page = DecryptionResultPage(result)
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)

            else:
                self.status_label.setText("Status: Selected method not implemented.")
        else:
            self.status_label.setText("Status: Please select a decryption technique and files.")

    def update_chaotic_inputs(self):
        try:
            self.r_value = float(self.r_input.text()) if self.r_input.text() else None
            self.x_value = float(self.x_input.text()) if self.x_input.text() else None
            self.y_value = float(self.y_input.text()) if self.y_input.text() else None
            self.let_run_value = int(self.let_run_input.text()) if self.let_run_input.text() else None
            self.map_type = self.map_dropdown.currentText()
        except ValueError:
            print("Invalid input detected in chaotic parameters.")
    
    def show_help(self):
        QMessageBox.information(self, "Help", "This window allows you to retrieve the data that you have embedded.\n\n"
                                              "Instructions:\n"
                                              "1. Choose a decryption technique.\n"
                                              "2. Select the original and altered files.\n"
                                              "3. Adjust embedding settings in 'Advanced Options'.\n"
                                              "4. Begin embedding.\n"
                                              "5. Save the resulting text file, if desired.")

    def edit_dictionary(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Dictionary")
        
        layout = QVBoxLayout(dialog)

        label = QLabel("Enter new dictionary values:", dialog)
        layout.addWidget(label)

        text_edit = QLineEdit(dialog)
        layout.addWidget(text_edit)

        save_button = QPushButton("Save", dialog)
        save_button.clicked.connect(self.save_dictionary)
        layout.addWidget(save_button)

        dialog.exec_()

    def save_dictionary(self):
        print("Dictionary saved!")

    def update_error_correction(self, selected_method):
        self.selected_error_correction = selected_method
        print(f"Error correction method updated to: {self.selected_error_correction}")

    def show_dictionary_editor(self):
        """Show the dictionary editor dialog and store the modified dictionary"""
        editor = DictionaryEditor(self)
        if editor.exec_() == QDialog.Accepted:
            self.current_rgba_dict = editor.get_modified_dict()
            QtWidgets.QMessageBox.information(
                self,
                "Success",
                "Dictionary changes saved for this session",
                QtWidgets.QMessageBox.Ok
            )

    def go_home(self):
        pass

    def toggle_distributed_options(self, state):
        enable = (state == Qt.Checked)
        self.distributed_block_size.setEnabled(enable)
    
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


class DecryptionResultPage(QWidget):
    def __init__(self, decrypted_message):
        super().__init__()

        self.setWindowTitle("Decryption Result")
        self.setGeometry(200, 200, 600, 400)

        self.layout = QVBoxLayout()

        self.label = QLabel("Decrypted Message:")
        self.layout.addWidget(self.label)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        self.text_area.setText(decrypted_message)
        self.layout.addWidget(self.text_area)

        self.save_button = QPushButton("Save Message", self)
        self.save_button.clicked.connect(self.save_message)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_message(self): # Saves decrypted text to a text file
        text = self.text_area.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted Message", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            with open(file_path, "w") as file:
                file.write(text)
            print("Message saved to file:", file_path)
    

    



class DictionaryEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dictionary Editor")
        self.setGeometry(200, 200, 650, 500)
        
        self.parent = parent
        self.original_dict = rdb.dictionary.copy()
        self.current_dict = getattr(parent, 'current_rgba_dict', self.original_dict.copy())
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
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        
        button_style = """
            QPushButton {
                min-width: 100px;
                padding: 6px;
                margin: 2px;
            }
        """
        
        self.add_btn = QPushButton("Add Row", self)
        self.del_btn = QPushButton("Delete Selected", self)
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
        
        for col in range(4):
            btn_grid.setColumnStretch(col, 1)
        
        # Adds widgets to main layout
        layout.addWidget(self.table)
        layout.addLayout(btn_grid)
        
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        self.setLayout(layout)
        self.table.setSortingEnabled(True)
        
        # Connection signals
        self.add_btn.clicked.connect(self.add_row)
        self.del_btn.clicked.connect(self.delete_row)
        self.save_dict_btn.clicked.connect(self.save_dictionary)
        self.load_dict_btn.clicked.connect(self.load_dictionary)
        self.apply_btn.clicked.connect(self.apply_changes)
        self.reset_btn.clicked.connect(self.reset_dictionary)
        self.cancel_btn.clicked.connect(self.reject)
    
    def save_dictionary(self): # Saves current dictionary to a .dict/JSON file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Dictionary", 
            "", 
            "Dictionary Files (*.dict);;All Files (*)"
        )
        
        if file_path:
            try:
                if not file_path.lower().endswith('.dict'):
                    file_path += '.dict'
                
                save_dict = self.modified_dict if self.modified_dict is not None else self.current_dict
                
                with open(file_path, 'w') as f:
                    json.dump(save_dict, f, indent=4)
                    
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Dictionary saved successfully to:\n{file_path}"
                )
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to save dictionary:\n{str(e)}"
                )
    
    def load_dictionary(self): # Loads dictionary from a .dict/JSON file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Load Dictionary", 
            "", 
            "Dictionary Files (*.dict);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    loaded_dict = json.load(f)
                
                if not isinstance(loaded_dict, dict):
                    raise ValueError("Invalid dictionary format")
                
                # Converts to proper format (handles JSON's automatic conversion)
                validated_dict = {}
                for char, values in loaded_dict.items():
                    if isinstance(values, (list, tuple)) and len(values) == 2:
                        validated_dict[str(char)] = (int(values[0]), int(values[1]))
                    else:
                        raise ValueError(f"Invalid value format for character '{char}'")
                
                self.current_dict = validated_dict # Updates the current dictionary
                self.populate_table()
                
                QtWidgets.QMessageBox.information(
                    self, 
                    "Success", 
                    f"Dictionary loaded successfully from:\n{file_path}"
                )
                
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, 
                    "Error", 
                    f"Failed to load dictionary:\n{str(e)}"
                )
    
    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(""))  # Empty characters allowed
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
                
            char = char_item.text() if char_item else ""
            rgb_text = rgb_item.text().strip() if rgb_item else ""
            alpha_text = alpha_item.text().strip() if alpha_item else ""
            
            if not rgb_text or not alpha_text:
                errors.append(f"Row {row+1}: RGB and Alpha values are required")
                continue
                
            try:
                rgb = int(rgb_text)
                alpha = int(alpha_text)
            except ValueError:
                errors.append(f"Row {row+1}: RGB and Alpha must be integers")
                continue
                
            key = char
            
            if key in new_dict:
                display_key = f"'{key}'" if key else "empty"
                errors.append(f"Row {row+1}: Duplicate entry {display_key}")
                continue
                
            new_dict[key] = (rgb, alpha)
        
        if errors:
            QtWidgets.QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
            return
        
        if not new_dict:
            QtWidgets.QMessageBox.warning(self, "Empty Dictionary", "No valid entries found")
            return
        
        self.modified_dict = new_dict
        self.parent.current_rgba_dict = new_dict
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
    

    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DecryptionPage()
    window.show()
    sys.exit(app.exec_())
