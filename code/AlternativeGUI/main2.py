import sys
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QHBoxLayout, QWidget, QVBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
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

        serious_button = QPushButton('Serious')
        serious_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #11f523; font-size:20px; margin-bottom:2")
        serious_button.setFixedSize(140, 50)
        serious_button.clicked.connect(self.on_click_serious_button)
        upper_layout.addWidget(serious_button, alignment=Qt.AlignLeft)

        stop_button = QPushButton('Stop')
        stop_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #4169e1; font-size:20px; margin-bottom:2")
        stop_button.setFixedSize(140, 50)
        stop_button.clicked.connect(self.on_click_stop_button)
        upper_layout.addWidget(stop_button, alignment=Qt.AlignCenter)

        non_serious_button = QPushButton('Non Serious')
        non_serious_button.setFixedSize(140, 50)
        non_serious_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #ff0037; font-size:20px; margin-bottom:2")
        non_serious_button.clicked.connect(self.on_click_non_serious_button)
        upper_layout.addWidget(non_serious_button, alignment=Qt.AlignRight)

        upper_widget.setLayout(upper_layout)

        go_to_home_button = QPushButton()
        go_to_home_button.setIcon(QIcon('../../resources/images/home.png'))
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

    def on_click_serious_button(self):
        print('clicked')
        # TODO : serious

    def on_click_non_serious_button(self):
        print('clicked')
        # TODO : serious

    def on_click_stop_button(self):
        print('clicked')
        # TODO : serious

    def on_click_home_button(self):
        print('clicked')
        # TODO : serious


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
