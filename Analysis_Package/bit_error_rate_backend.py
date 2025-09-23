import sys
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QTextEdit, QPushButton, QFileDialog
from sklearn.metrics import precision_score, recall_score

def string_to_bits(message): # Message to binary
    return ''.join(format(ord(c), '08b') for c in message)

def calculate_steganography_metrics(original_message, extracted_message):
    original_bits = string_to_bits(original_message)
    extracted_bits = string_to_bits(extracted_message)

    # Ensure both bitstrings are of the same length by padding the shorter one with '0'
    max_len = max(len(original_bits), len(extracted_bits))
    original_bits = original_bits.ljust(max_len, '0')
    extracted_bits = extracted_bits.ljust(max_len, '0')

    # Confusion matrix components
    TP = sum(1 for i in range(len(original_bits)) if original_bits[i] == '1' and extracted_bits[i] == '1')  
    FP = sum(1 for i in range(len(original_bits)) if original_bits[i] == '0' and extracted_bits[i] == '1')  
    TN = sum(1 for i in range(len(original_bits)) if original_bits[i] == '0' and extracted_bits[i] == '0')  
    FN = sum(1 for i in range(len(original_bits)) if original_bits[i] == '1' and extracted_bits[i] == '0')  

    # Calculate metrics
    FPR = FP / (FP + TN) if (FP + TN) > 0 else 0
    FNR = FN / (FN + TP) if (FN + TP) > 0 else 0
    Precision = precision_score(list(original_bits), list(extracted_bits), pos_label='1')
    Recall = recall_score(list(original_bits), list(extracted_bits), pos_label='1')
    missed_message_ratio = FN / (TP + FN) if (TP + FN) > 0 else 0
    BDA = TP / (TP + FP + TN + FN) if (TP + FP + TN + FN) > 0 else 0
    BER = sum(1 for i in range(len(original_bits)) if original_bits[i] != extracted_bits[i]) / len(original_bits)

    return {
        'FPR (False Positive Rate)': FPR,
        'FNR (False Negative Rate)': FNR,
        'Precision': Precision,
        'Recall': Recall,
        'Missed Message Ratio': missed_message_ratio,
        'Bit Detection Accuracy (BDA)': BDA,
        'Bit Error Rate (BER)': BER
    }

class MetricsDialog(QDialog):
    def __init__(self, metrics):
        super().__init__()

        self.setWindowTitle("Bit Error Rate")
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        result_text = "\n".join(f"{metric}: {value:.4f}" for metric, value in metrics.items())
        self.text_area.setText(result_text)

        self.setLayout(layout)

def open_metrics_window(original_file_path, parent=None):

    extracted_file_path, _ = QFileDialog.getOpenFileName(parent, "Choose Extracted Message File", "", "Text Files (*.txt)")     # Open file dialog (only .txt due to format of decryption)

    if not extracted_file_path:
        return  

    with open(original_file_path, 'r') as f:
        original_message = f.read()
    with open(extracted_file_path, 'r') as f:
        extracted_message = f.read()

    metrics = calculate_steganography_metrics(original_message, extracted_message) # Computes metrics

    dialog = MetricsDialog(metrics)
    dialog.exec_()
