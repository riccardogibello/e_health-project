from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QWidget, QVBoxLayout


class OverviewDashboardWindow(QMainWindow):
    def __init__(self, gui_manager, dash_process):
        super().__init__()
        self.gui_manager = gui_manager
        self.dash_process = dash_process

        self.setWindowTitle("Serious Game Finder - Manual Classifier")
        self.left = 100
        self.top = 100
        self.width = 1500
        self.height = 900
        self.setGeometry(self.left, self.top, self.width, self.height)
        main_widget = QWidget()
        vertical_layout = QVBoxLayout()

        upper_widget = QWidget()
        down_widget = QWidget()
        center_browser_widget = QWebEngineView()
        upper_layout = QHBoxLayout()
        down_layout = QHBoxLayout()
        center_layout = QHBoxLayout()

        center_browser_widget.setGeometry(100, 100, 1500, 800)
        center_browser_widget.setUrl(QUrl('http://127.0.0.1:8050/'))
        center_browser_widget.setStyleSheet("border-radius:20; border:2px solid black;")
        center_layout.addWidget(center_browser_widget)
        self.browser = center_browser_widget

        upper_widget.setLayout(upper_layout)

        go_to_home_button = QPushButton()
        go_to_home_button.setIcon(QIcon('./resources/images/home.png'))
        go_to_home_button.setIconSize(QtCore.QSize(35, 35))
        go_to_home_button.setFixedSize(75, 50)  # width, height
        go_to_home_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: yellow; margin-top:2")
        go_to_home_button.clicked.connect(self.on_click_home_button)
        down_layout.addWidget(go_to_home_button, alignment=Qt.AlignCenter)

        down_widget.setLayout(down_layout)

        vertical_layout.addWidget(upper_widget, alignment=Qt.AlignTop)
        vertical_layout.addWidget(center_browser_widget, alignment=Qt.AlignCenter)
        vertical_layout.addWidget(down_widget, alignment=Qt.AlignBottom)
        main_widget.setLayout(vertical_layout)

        self.setCentralWidget(main_widget)

        main_widget.setStyleSheet("background-color: #34568b;")

    def on_click_home_button(self):
        self.gui_manager.go_to_home_page()
