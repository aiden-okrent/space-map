from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget
from PyQt6.QtGui import QTextOption

class DisplayWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Disply Window")
        self.setGeometry(100, 100, 400, 600)

        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("background-color: black; color: white; font-family: Courier;")
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        #self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.FixedColumnWidth)
        
        ''' # calc max width of # of chars in the box via font metrics and display size
        font_metrics = self.text_edit.fontMetrics()
        char_width = font_metrics.averageCharWidth()
        display_width = self.text_edit.width()
        max_chars = display_width // char_width
        self.text_edit.setFixedWidth(max_chars * char_width)
        '''
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def write_text(self, text):
        self.text_edit.append(text)
        
    def clear_text(self):
        self.text_edit.clear()
