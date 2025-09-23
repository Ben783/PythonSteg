from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help - Analysis Window")
        self.setGeometry(150, 150, 500, 600)

        layout = QVBoxLayout()
        
        title_label = QLabel("<h2>Analysis Window - Help Guide</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        scroll_area = QScrollArea() # Scrollable window
        scroll_area.setWidgetResizable(True)
        
        help_content = QTextEdit()
        help_content.setReadOnly(True)
        help_text = """
        <h3>Overview</h3>
        <p>The Analysis Window provides tools for steganalysis, allowing you to analyse steg images, original images, 
        and embedded text files using visual and statistical methods.</p>
        
        <h3>Getting Started</h3>
        <ul>
            <li><b>Load a Steg File</b> (Modified Image)</li>
            <li><b>Load an Original File</b> (Unmodified Image)</li>
            <li><b>Load an Embedded Text File</b> (if applicable)</li>
            <li><b>Select an analysis method</b> to proceed.</li>
        </ul>
        
        <h3>Features & Functionalities</h3>
        
        <p><b>1. File Selection</b></p>
        <ul>
            <li><b>Select Steg File:</b> Load the modified image.</li>
            <li><b>Select Original File:</b> Load the original (cover) image.</li>
            <li><b>Select Text File:</b> Load the embedded text file (if required).</li>
        </ul>
        
        <p><b>2. Analysis Tools</b></p>
        <ul>
            <li><b>Visual Analysis:</b>
                <ul>
                    <li><b>Noise-based Analysis:</b> Detects anomalies using noise analysis.</li>
                    <li><b>Histogram Analysis:</b> Compares histograms of original and steg images.</li>
                    <li><b>LSB Analysis:</b> Analyses the Least Significant Bit pattern changes.</li>
                </ul>
            </li>
            <li><b>Statistical Analysis:</b>
                <ul>
                    <li><b>Regular Singular Analysis (RSU):</b> Examines pixel variation to detect hidden data.</li>
                    <li><b>Variance Analysis:</b> Computes statistical variations in pixel intensities.</li>
                    <li><b>Entropy Analysis:</b> Evaluates differences in randomness between images.</li>
                </ul>
            </li>
            <li><b>Comparison Metrics:</b>
                <ul>
                    <li><b>Side-by-Side Comparison:</b> Displays images for manual inspection.</li>
                    <li><b>Bit Error Rate (BER):</b> Calculates differences between extracted & original text.</li>
                </ul>
            </li>
        </ul>
        
        <p><b>3. Report Generation</b></p>
        <ul>
            <li><b>Quick Report:</b> Generates a summary of detected artefacts.</li>
            <li><b>Extensive Report:</b> Provides an in-depth, detailed analysis.</li>
        </ul>
        
        <p><b>4. Additional Options</b></p>
        <ul>
            <li><b>Return to Main Window:</b> Exits the analysis screen and returns to the main interface.</li>
            <li><b>Help ("i" Button):</b> Opens this help guide.</li>
        </ul>
        
        <h3>Error Handling</h3>
        <p>If required files are missing, a warning will be displayed.</p>
        <p>Ensure you select both steg and original files for comparative analysis.</p>
        <p>Some tools may not function without an embedded text file.</p>
        """
        
        help_content.setHtml(help_text)
        scroll_area.setWidget(help_content)
        layout.addWidget(scroll_area)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button, alignment=Qt.AlignCenter)
        
        self.setLayout(layout)
