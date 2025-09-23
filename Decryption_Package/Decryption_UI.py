import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QPushButton, QRadioButton, QButtonGroup, QFrame, QComboBox, QLineEdit, QMainWindow, QDialog, QDialogButtonBox, QProgressBar, QHBoxLayout, QTabWidget, QWidget
import chaotic_decryption_backend as cdb
import noise_decryption as nd
import DCT_decryption_backend as ddb
import RGBA_decryption_backend as rdb
import Topo_decryption as td
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QAction, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout



class DecryptionPage(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Decryption Page")
        self.setGeometry(100, 100, 700, 500)

        self.tab_widget = QTabWidget()

        self.main_tab = QWidget()
        self.init_main_tab()
        self.tab_widget.addTab(self.main_tab, "Main")

        self.advanced_tab = QWidget()
        self.init_advanced_tab()
        self.tab_widget.addTab(self.advanced_tab, "Advanced Options")

        self.setCentralWidget(self.tab_widget)


        self.org_file_path = None # Initialise file paths and parameters
        self.alt_file_path = None
        self.r_value = None
        self.x_value = None
        self.y_value = None
        self.let_run_value = None
        self.map_type = None  # Stores selected map type

        self.status_label = QLabel("Status: Ready", self)
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")
        
        # Status label
        self.main_layout.addWidget(self.status_label, alignment=QtCore.Qt.AlignLeft)

    def init_main_tab(self):
        self.main_layout = QVBoxLayout(self.main_tab)


        self.title_label = QLabel("Decryption Page", self)
        self.title_label.setFont(QtGui.QFont('Aptos Body', 16, QtGui.QFont.Bold))
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.subtitle_label = QLabel("Select a decryption technique", self)
        self.subtitle_label.setFont(QtGui.QFont('Aptos Body', 12))
        self.subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.subtitle_label)

        file_buttons_layout = QHBoxLayout()
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

        self.mainPage_button = QPushButton("Main Page", self)
        self.mainPage_button.clicked.connect(self.go_home)
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

        option_layouts = [
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
    

    def go_home(self):
        self.tab_widget.setCurrentIndex(0)

    def change_subtitle(self):
        selected_technique = self.selected_technique.checkedButton().text()
        self.subtitle_label.setText(selected_technique)

        # Clears existing options
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
            # Parameter inputs
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

            # Connect inputs to update instance variables 
            self.r_input.textChanged.connect(self.update_chaotic_inputs)
            self.x_input.textChanged.connect(self.update_chaotic_inputs)
            self.y_input.textChanged.connect(self.update_chaotic_inputs)
            self.let_run_input.textChanged.connect(self.update_chaotic_inputs)
            self.map_dropdown.currentIndexChanged.connect(self.update_chaotic_inputs)

    def select_image1(self):
        selected_button = self.selected_technique.checkedButton()
        if selected_button and selected_button.text() == "Topological Domain Decryption":
            file_path, _ = QFileDialog.getOpenFileName(self, "Select a 3D object file", "", "3D Object files (*.obj *.stl *.ply);;All files (*.*)")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select an image", "", "Image files (*.jpg *.jpeg *.png *.gif);;All files (*.*)")
        
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
                print("Running Chaotic Decryption...")

                # Retrieve parameters
                r = float(self.r_input.text())
                x0 = float(self.x_input.text())
                y0 = float(self.y_input.text())
                let_run = int(self.let_run_input.text())

                decrypted_message = cdb.decrypt(r, x0, y0, let_run, self.org_file_path, self.alt_file_path)

                self.result_page = DecryptionResultPage(decrypted_message) # Opens a new window with the decryption result
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)

            if selected_technique == "Noise-Based Decryption":
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

            if selected_technique == "DCT Decryption":
                print("Running DCT Decryption...")
                result = ddb.extract_secret_message_from_image(self.alt_file_path)
                self.result_page = DecryptionResultPage(result)
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)   

            if selected_technique == "Denary Bit Decryption":
                print("Running D-B Decryption")
                result = rdb.decode(self.org_file_path, self.alt_file_path)  
                self.result_page = DecryptionResultPage(result)
                self.result_page.show()

                self.status_label.setText("Status: Decryption Completed")
                self.progress_bar.setValue(100)   

            if selected_technique == "Topological Domain Decryption":
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
            self.map_type = self.map_dropdown.currentText()  # Stores selected map type
        except ValueError:
            print("Invalid input detected in chaotic parameters.")

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
        """Ensure self.error_correction remains a QComboBox and store the selected method separately."""
        self.selected_error_correction = selected_method 
        print(f"Error correction method updated to: {self.selected_error_correction}")
    
    def go_home(self):
        pass


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

    def save_message(self): # Saving decrypted message to a file path
        text = self.text_area.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Decrypted Message", "", "Text Files (*.txt);;All Files (*.*)")
        if file_path:
            with open(file_path, "w") as file:
                file.write(text)
            print("Message saved to file:", file_path)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DecryptionPage()
    window.show()
    sys.exit(app.exec_())
