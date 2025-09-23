import sys
sys.path.append(r'C:\Users\HOME\PYTHON CS\Project\Complete')

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QGroupBox,
    QLabel, QRadioButton, QFileDialog, QGridLayout, QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation
from . import Noise_Based_Backend as nb
from .Quick_Report_Backend import MetadataApp  # Relative import
from .ApEn_backend import ApEnApp
from . import LSB_Backend as lsb
from . import text_freq_backend as tfb
from . import Histogram_images_backend as hib
from . import bit_error_rate_backend as bebe
from .Detailed_report_backend import DetailedReport
from . import variance_analysis_backend as vab
from . import RSU_analysis_backend as rab
from . help_page import HelpWindow as hp
from . side_by_side  import analyse_image_lsb as ail
from . SSIM_backend import show_differences as ssim


import os

class AnalysisWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Analysis Window")
        self.setGeometry(100, 100, 800, 600)

        self.steg_file_path = None
        self.original_file_path = None
        self.text_file_path = None
        self.AnalysisWindow = None  # Placeholder for MetadataApp instance
        self.apen_window = None  # Placeholder for ApEnApp instance
        self.detailed_report_window = None
        self.metadata_window = None  # All of these are placeholders
        self.helpWindow = None

        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)

        title_layout = QHBoxLayout()
        self.title_label = QLabel("Analysis") # Title and help buttons
        self.title_label.setFont(QFont("Aptos Body", 20, QFont.Bold))

        self.help_button = QPushButton("i")
        self.help_button.setFixedSize(20, 20)
        self.help_button.clicked.connect(self.show_help)

        title_layout.addStretch()
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.help_button)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        thumbnail_layout = QHBoxLayout()

        self.image_label1 = QLabel() # Steg Image
        self.image_label1.setFixedSize(150, 150)
        self.select_image_button1 = QPushButton("Select Steg File")
        self.select_image_button1.setFixedWidth(150)
        self.select_image_button1.clicked.connect(lambda: self.select_image(1))

        steg_layout = QVBoxLayout()
        steg_layout.addWidget(self.image_label1)
        steg_layout.addWidget(self.select_image_button1)
        thumbnail_layout.addLayout(steg_layout)

        self.image_label2 = QLabel()# Original Image
        self.image_label2.setFixedSize(150, 150)
        self.select_image_button2 = QPushButton("Select Original File")
        self.select_image_button2.setFixedWidth(150)
        self.select_image_button2.clicked.connect(lambda: self.select_image(2))

        orig_layout = QVBoxLayout()
        orig_layout.addWidget(self.image_label2)
        orig_layout.addWidget(self.select_image_button2)
        thumbnail_layout.addLayout(orig_layout)

        self.text_label = QLabel() # Text File (no thumbnail/extract)
        self.text_label.setFixedSize(150, 150)
        self.select_text_button = QPushButton("Select Text File")
        self.select_text_button.setFixedWidth(150)
        self.select_text_button.clicked.connect(self.select_text_file)

        text_layout = QVBoxLayout()
        text_layout.addWidget(self.text_label)
        text_layout.addWidget(self.select_text_button)
        thumbnail_layout.addLayout(text_layout)

        main_layout.addLayout(thumbnail_layout)

        analysis_layout = QHBoxLayout() #Analysis techniques separation


        visual_group = QGroupBox("Visual Analysis") # Visual analysis
        visual_layout = QVBoxLayout()
        self.noise_button = QPushButton("Noise-based Analysis")
        self.noise_button.clicked.connect(self.show_noise)
        self.histogram_button = QPushButton("Histogram Analysis")
        self.histogram_button.clicked.connect(self.show_histograms)
        self.lsb_button = QPushButton("LSB Analysis")
        self.lsb_button.clicked.connect(self.show_lsbs)

        for btn in [self.noise_button, self.histogram_button, self.lsb_button]:
            btn.setFixedWidth(150)
            visual_layout.addWidget(btn)

        visual_group.setLayout(visual_layout)
        analysis_layout.addWidget(visual_group)

        statistical_group = QGroupBox("Statistical Analysis") # Stats analysis
        statistical_layout = QVBoxLayout()
        self.rsa_button = QPushButton("Regular Singular Analysis")
        self.rsa_button.clicked.connect(self.visualise_RSU)
        self.variance_button = QPushButton("Variance Analysis")
        self.variance_button.clicked.connect(self.show_variance_analysis)
        self.entropy_button = QPushButton("Entropy Analysis")
        self.entropy_button.clicked.connect(self.show_entropy_analysis)

        for btn in [self.rsa_button, self.variance_button, self.entropy_button]:
            btn.setFixedWidth(150)
            statistical_layout.addWidget(btn)

        statistical_group.setLayout(statistical_layout)
        analysis_layout.addWidget(statistical_group)

        comparison_group = QGroupBox("Comparison") # Comparisons
        comparison_layout = QVBoxLayout()
        self.sidecomp_button = QPushButton("Side-by-Side Comparison")
        self.sidecomp_button.clicked.connect(self.sidecomp)
        self.biterror_button = QPushButton("Bit Error Rate")
        self.biterror_button.clicked.connect(self.show_error_bit_rate)

        for btn in [self.sidecomp_button, self.biterror_button]:
            btn.setFixedWidth(150)
            comparison_layout.addWidget(btn)

        comparison_group.setLayout(comparison_layout)
        analysis_layout.addWidget(comparison_group)

        main_layout.addLayout(analysis_layout)

        report_type_group = QGroupBox("Select Report Type") # Report Types
        report_type_layout = QVBoxLayout()
        self.quick_report_rb = QRadioButton("Quick Report")
        self.extensive_report_rb = QRadioButton("Extensive Report")
        self.quick_report_rb.setChecked(True)

        report_type_layout.addWidget(self.quick_report_rb)
        report_type_layout.addWidget(self.extensive_report_rb)
        report_type_group.setLayout(report_type_layout)
        main_layout.addWidget(report_type_group)

        self.generate_report_button = QPushButton("Generate Report") # Generate Reports
        self.generate_report_button.setFixedWidth(160)
        self.generate_report_button.clicked.connect(self.generate_report)
        main_layout.addWidget(self.generate_report_button, alignment=Qt.AlignCenter)

        self.main_screen_button = QPushButton("Central Window") # Returning to main screen 
        self.main_screen_button.setFixedWidth(200)
        self.main_screen_button.setFixedHeight(30)
        self.main_screen_button.clicked.connect(self.MainWindow)
        main_layout.addWidget(self.main_screen_button, alignment=Qt.AlignCenter)

        self.status_label = QLabel("Status: Ready") # Status label
        self.status_label.setStyleSheet("font-size: 12px; color: gray;")

        main_layout.addWidget(self.status_label, alignment=Qt.AlignLeft)


        bottom_container = QHBoxLayout()  # Wrapper layout to align to the left
        bottom_layout = QVBoxLayout()  # Places file paths vertically

        self.image_file_path_label1 = QLabel("Steg File: None")
        self.image_file_path_label2 = QLabel("Original File: None")
        self.text_file_path_label = QLabel("Text File: None")

        bottom_layout.addWidget(self.image_file_path_label1)
        bottom_layout.addWidget(self.image_file_path_label2)
        bottom_layout.addWidget(self.text_file_path_label)

        bottom_container.addLayout(bottom_layout)
        bottom_container.addStretch()

        main_layout.addLayout(bottom_container)  # Add to main layout

        self.setLayout(main_layout)

    def select_image(self, image_num): # Prompt to select image file
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.webp)")
        if file_path:
            if image_num == 1:  # Steg Image
                self.steg_file_path = file_path
                self.load_image(file_path, self.image_label1, "Steg File")
                self.image_file_path_label1.setStyleSheet("color: green; font-weight: bold;")
                self.image_file_path_label1.setText(f"Steg File: {file_path}")
                self.status_label.setText(f"Status: Steg File ({os.path.basename(file_path)}) loaded successfully.")
            else:  # Original Image
                self.original_file_path = file_path
                self.load_image(file_path, self.image_label2, "Original File")
                self.image_file_path_label2.setStyleSheet("color: green; font-weight: bold;")
                self.image_file_path_label2.setText(f"Original File: {file_path}")
                self.status_label.setText(f"Status: Original File ({os.path.basename(file_path)}) loaded successfully.")


    def load_image(self, file_path, image_label, image_type): # Thumbnail
        pixmap = QPixmap(file_path)
        pixmap = pixmap.scaled(150, 150, aspectRatioMode=Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        self.status_label.setText(f"Status: {image_type} loaded successfully.")

    def select_text_file(self): # Prompt to select text file
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
            self.text_file_path = file_path
            self.status_label.setText("Status: Text file loaded successfully.")
            self.text_file_path_label.setText(f"Text File: {file_path}")
            self.text_file_path_label.setStyleSheet("color: green; font-weight: bold;")

    def show_variance_analysis(self):
        if self.steg_file_path and self.original_file_path:
            vab.complete(self.steg_file_path, self.original_file_path)
            figure = ssim(self.steg_file_path, self.original_file_path)
            figure.show()

        else:
            QMessageBox.warning(self, "Warning", "Select both steg and original files.")

    def show_noise(self):
        if self.steg_file_path and self.original_file_path:
            nb.show_analysis(self.steg_file_path, self.original_file_path, block_size=16)
        else:
            self.status_label.setText("Error: Please select both Steg and Original images first.")
            QMessageBox.warning(self, "Warning", "Select both steg and original files.")


    def generate_report(self):
        if self.quick_report_rb.isChecked():
            if self.metadata_window is None or not self.metadata_window.isVisible():
                self.metadata_window = MetadataApp(self.text_file_path, self.original_file_path, self.steg_file_path)
                self.metadata_window.show()
            else:
                self.status_label.setText("Status: Quick Report already open.")
        elif self.extensive_report_rb.isChecked():
            if self.detailed_report_window is None or not self.detailed_report_window.isVisible():
                self.detailed_report_window = DetailedReport(self.original_file_path, self.steg_file_path, self.text_file_path)
                self.detailed_report_window.show()

    def show_histograms(self):
        if self.text_file_path:
            tfb.plotting(self.text_file_path)
        if self.steg_file_path and self.original_file_path:
            hib.analyse_images(self.original_file_path, self.steg_file_path)
        else:
            QMessageBox.warning(self, "Warning", "Select:\nA text file.\nOriginal and Steg files.", QMessageBox.Ok)

    
    def show_lsbs(self):
        if self.steg_file_path and self.original_file_path:
            lsb.plot_normalised_LSBs(self.original_file_path, self.steg_file_path)
        else:
            QMessageBox.warning(self, "Warning", "Select both a steg and original file.", QMessageBox.Ok)
    
    def show_error_bit_rate(self):
        if self.text_file_path:
            bebe.open_metrics_window(self.text_file_path, parent=self)
        else:
            QMessageBox.warning(self, "Warning", "Select a text file to calculate bit error rate.", QMessageBox.Ok)

    def show_entropy_analysis(self):
        if self.steg_file_path and self.original_file_path:
            self.apen_window = ApEnApp(self.original_file_path, self.steg_file_path)
            self.apen_window.show()
        else:
            QMessageBox.warning(self, "Warning", "Select both a steg file and an original file.", QMessageBox.Ok)

    def visualise_RSU(self):
        if self.steg_file_path and self.original_file_path:
            rab.main(self.original_file_path, self.steg_file_path)
        else:
            QMessageBox.warning(self, "Warning", "Select both a steg file and an original file.", QMessageBox.Ok)

    def show_help(self):
        self.help_window = hp()
        self.help_window.show()

    
    def set_controller(self, controller): # Setting controller here
        self.controller = controller

    def MainWindow(self): # Returning to main window
        if hasattr(self, 'controller') and self.controller:
            self.controller.show_main_window()
        else:
            from MainPage_Package.MainPage import MainWindow
            self.main_window = MainWindow()
            self.close()
            self.main_window.show()
    
    def sidecomp(self):
        if self.steg_file_path and self.original_file_path:
            ail(self.original_file_path, self.steg_file_path)
        else:
            QMessageBox.warning(self, "Warning", "Select both a steg file and an original file.", QMessageBox.Ok)






if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AnalysisWindow()
    window.show()
    sys.exit(app.exec_())
