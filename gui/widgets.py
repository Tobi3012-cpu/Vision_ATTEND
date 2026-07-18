from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class StatCard(QWidget):
    def __init__(self, title, value, color="#2ecc71", parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 120)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px;
            color: white;
            font-weight: bold;
        """)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 10))

        self.value_label = QLabel(str(value))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFont(QFont("Arial", 22, QFont.Bold))

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        # Subtle shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(Qt.gray)
        self.setGraphicsEffect(shadow)

    def set_value(self, new_value):
        self.value_label.setText(str(new_value))