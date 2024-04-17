from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QRadioButton,
    QVBoxLayout,
)


class QualityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Quality")

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel("Select quality:")
        self.layout.addWidget(message)

        # Create radio buttons
        self.low_button = QRadioButton("Low")
        self.high_button = QRadioButton("High")

        self.quality = self.parent.centralDisplay.getMapQuality()
        if self.quality == 0:
            self.low_button.setChecked(True)
        elif self.quality == 1:
            self.high_button.setChecked(True)

        # connect all buttons to 1 method with a single arg of 0, 1
        self.low_button.clicked.connect(lambda: self.setQuality(0))
        self.high_button.clicked.connect(lambda: self.setQuality(1))

        # Add radio buttons to layout
        self.layout.addWidget(self.low_button)
        self.layout.addWidget(self.high_button)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        # Set dialog position
        self.move(200, 200)

    def setQuality(self, quality=0):
        self.quality = quality

    def accept(self) -> None:
        self.parent.centralDisplay.setMapQuality(self.quality)
        self.close()
        return super().accept()

    def reject(self) -> None:
        self.close()
        return super().reject()