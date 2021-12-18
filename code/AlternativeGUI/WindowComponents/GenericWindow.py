from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton


class GenericWindow(QMainWindow):
    def __init__(self, gui_manager, message):
        super().__init__()
        self.gui_manager = gui_manager

        self.setWindowTitle("Serious Game Finder")
        self.left = 100
        self.top = 100
        self.width = 400
        self.height = 400
        self.setGeometry(self.left, self.top, self.width, self.height)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        center_widget = QWidget()
        vertical_layout = QVBoxLayout()

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("border-radius:20; border:2px solid black; font-size:20px; "
                                    "padding: 5px 5px 5px 5px; background-color: #48ff48;")
        vertical_layout.addWidget(message_label, alignment=Qt.AlignCenter)

        go_to_home_button = QPushButton()
        go_to_home_button.setIcon(QIcon('./resources/images/home.png'))
        go_to_home_button.setIconSize(QtCore.QSize(35, 35))
        go_to_home_button.setFixedSize(75, 50)  # width, height
        go_to_home_button.setStyleSheet(
            "QPushButton {border-radius:20; border:2px solid black; background-color: yellow; margin-top:2} "
            "QPushButton::hover"
            "{"
            "border:4px solid black"
            "}"
        )
        go_to_home_button.clicked.connect(self.on_click_home_button)
        vertical_layout.addWidget(go_to_home_button, alignment=Qt.AlignCenter)

        center_widget.setLayout(vertical_layout)
        main_layout.addWidget(center_widget, alignment=Qt.AlignVCenter)

        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #b5d8f8;")

        self.setCentralWidget(main_widget)

    def on_click_home_button(self):
        self.gui_manager.go_to_home_page()
