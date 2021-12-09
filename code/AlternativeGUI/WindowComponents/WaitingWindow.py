from threading import Thread

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel


class WaitingWindow(QMainWindow):
    def __init__(self, gui_manager, message, image_path):
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

        waiting_logo_label = QLabel()
        gif = QMovie('./resources/images/loading.gif')
        gif.setScaledSize(QtCore.QSize(64, 64))
        gif.start()
        waiting_logo_label.setAttribute(Qt.WA_NoSystemBackground)
        waiting_logo_label.setMovie(gif)
        waiting_logo_label.setStyleSheet("margin-top:15px")
        vertical_layout.addWidget(waiting_logo_label, alignment=Qt.AlignCenter)

        self.statistic_image = QLabel()
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.statistic_image.setPixmap(pixmap)
        self.statistic_image.setStyleSheet("margin-top:20px")
        vertical_layout.addWidget(self.statistic_image, alignment=Qt.AlignCenter)

        center_widget.setLayout(vertical_layout)
        main_layout.addWidget(center_widget, alignment=Qt.AlignVCenter)

        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #b5d8f8;")

        self.setCentralWidget(main_widget)

    def update_statistic_image(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.statistic_image.setPixmap(pixmap)

        self.update()

