from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow, QPushButton, QHBoxLayout, QWidget, QVBoxLayout
from AlternativeGUI.LogicComponents.ManualClassifierComponent import ManualClassifierComponent, persist_classification


class ManualClassifierWindow(QMainWindow):
    def __init__(self, gui_manager):
        super().__init__()
        self.gui_manager = gui_manager
        self.manual_classifier_component = ManualClassifierComponent()
        self.current_app_id = -1

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
        center_browser_widget.setUrl(QUrl('https://play.google.com/store/apps'))
        center_browser_widget.setStyleSheet("border-radius:20; border:2px solid black;")
        center_layout.addWidget(center_browser_widget)
        self.browser = center_browser_widget

        serious_button = QPushButton('Serious')
        serious_button.setStyleSheet(
            "QPushButton {"
            "border-radius:20; border:2px solid black; background-color: #11f523; font-size:20px; margin-bottom:2"
            "} "
            "QPushButton::hover { border:4px solid black}"
        )
        serious_button.setFixedSize(140, 50)
        serious_button.clicked.connect(self.on_click_serious_button)
        upper_layout.addWidget(serious_button, alignment=Qt.AlignLeft)

        start_button = QPushButton('Start')
        start_button.setStyleSheet(
            "QPushButton {"
            "border-radius:20; border:2px solid black; background-color: #4169e1; font-size:20px; margin-bottom:2"
            "} "
            "QPushButton::hover { border:4px solid black}"
        )
        start_button.setFixedSize(140, 50)
        start_button.clicked.connect(self.on_click_start_button)
        upper_layout.addWidget(start_button, alignment=Qt.AlignCenter)

        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet(
            "QPushButton {"
            "border-radius:20; border:2px solid black; background-color: #4169e1; font-size:20px; margin-bottom:2"
            "} "
            "QPushButton::hover { border:4px solid black}"
        )
        stop_button.setFixedSize(140, 50)
        stop_button.clicked.connect(self.on_click_stop_button)
        upper_layout.addWidget(stop_button, alignment=Qt.AlignCenter)

        non_serious_button = QPushButton('Non Serious')
        non_serious_button.setFixedSize(140, 50)
        non_serious_button.setStyleSheet(
            "QPushButton {"
            "border-radius:20; border:2px solid black; background-color: #ff0037; font-size:20px; margin-bottom:2"
            "} "
            "QPushButton::hover { border:4px solid black}"
        )
        non_serious_button.clicked.connect(self.on_click_non_serious_button)
        upper_layout.addWidget(non_serious_button, alignment=Qt.AlignRight)

        upper_widget.setLayout(upper_layout)

        go_to_home_button = QPushButton()
        go_to_home_button.setIcon(QIcon('./resources/images/home.png'))
        go_to_home_button.setIconSize(QtCore.QSize(35, 35))
        go_to_home_button.setFixedSize(75, 50)  # width, height
        go_to_home_button.setStyleSheet(
            "QPushButton {"
            "border-radius:20; border:2px solid black; background-color: yellow; margin-top:2"
            "} "
            "QPushButton::hover { border:4px solid black}"
        )
        go_to_home_button.clicked.connect(self.on_click_home_button)
        down_layout.addWidget(go_to_home_button, alignment=Qt.AlignCenter)

        down_widget.setLayout(down_layout)

        vertical_layout.addWidget(upper_widget, alignment=Qt.AlignTop)
        vertical_layout.addWidget(center_browser_widget, alignment=Qt.AlignCenter)
        vertical_layout.addWidget(down_widget, alignment=Qt.AlignBottom)
        main_widget.setLayout(vertical_layout)

        self.setCentralWidget(main_widget)

        main_widget.setStyleSheet("background-color: #34568b;")

    def on_click_serious_button(self):
        if self.current_app_id != -1:
            persist_classification(self.current_app_id, True)
            new_url, new_app_id = self.manual_classifier_component.get_app_to_classify()
            self.browser.setUrl(QUrl(new_url))
            self.current_app_id = new_app_id

    def on_click_non_serious_button(self):
        if self.current_app_id != -1:
            persist_classification(self.current_app_id, False)
            new_url, new_app_id = self.manual_classifier_component.get_app_to_classify()
            self.browser.setUrl(QUrl(new_url))
            self.current_app_id = new_app_id

    def on_click_start_button(self):
        if self.current_app_id == -1:
            url, app_id = self.manual_classifier_component.get_app_to_classify()
            self.current_app_id = app_id
            self.browser.setUrl(QUrl(url))

    def on_click_stop_button(self):
        self.current_app_id = -1
        self.browser.setUrl(QUrl('https://play.google.com/store/apps'))

    def on_click_home_button(self):
        self.current_app_id = -1
        self.gui_manager.go_to_home_page()
