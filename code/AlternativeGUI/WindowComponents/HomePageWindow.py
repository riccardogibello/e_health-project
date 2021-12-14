import os
import signal
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout, QLabel
from AlternativeGUI.WindowComponents.WaitingWindow import WaitingWindow


class HomePageWindow(QMainWindow):
    def __init__(self, gui_manager):
        super().__init__()
        self.gui_manager = gui_manager

        self.setWindowTitle("Serious Game Finder")
        self.left = 100
        self.top = 100
        self.width = 600
        self.height = 800
        self.setGeometry(self.left, self.top, self.width, self.height)
        main_widget = QWidget()
        vertical_layout = QVBoxLayout()
        inner_layout = QVBoxLayout()
        inner_widget = QWidget()

        label_logo = QLabel()
        pixmap = QPixmap('./resources/images/Google_Play-Logo.wine.png')
        pixmap = pixmap.scaled(500, 500, Qt.KeepAspectRatio, Qt.FastTransformation)
        label_logo.setPixmap(pixmap)
        vertical_layout.addWidget(label_logo)

        load_datasets_button = QPushButton('Load Data from old dataset')
        load_datasets_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #48ff48; "
            "margin-top:2; font-size:25px; margin-top: 15px;")
        load_datasets_button.setFixedSize(500, 80)
        load_datasets_button.clicked.connect(self.on_click_load_datasets_button)
        inner_layout.addWidget(load_datasets_button, alignment=Qt.AlignCenter)

        retrieve_data_button = QPushButton('Retrieve Data from Google Play')
        retrieve_data_button.setFixedSize(500, 80)
        retrieve_data_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #ffd400; "
            "margin-top:2; font-size:25px; margin-top: 15px;")
        retrieve_data_button.clicked.connect(self.on_click_retrieve_data_button)
        inner_layout.addWidget(retrieve_data_button, alignment=Qt.AlignCenter)

        manual_classify_button = QPushButton('Classify manually some apps')
        manual_classify_button.setFixedSize(500, 80)  # width, height
        manual_classify_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #ff3333; "
            "margin-top:2; font-size:25px; margin-top: 15px;")
        manual_classify_button.clicked.connect(self.on_click_manual_classify_button)
        inner_layout.addWidget(manual_classify_button, alignment=Qt.AlignCenter)

        automatic_classify_button = QPushButton('Automatic Apps classification')
        automatic_classify_button.setFixedSize(500, 80)  # width, height
        automatic_classify_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #3bccff; "
            "margin-top:2; font-size:25px; margin-top: 15px;")
        automatic_classify_button.clicked.connect(self.on_click_automatic_classify_button)
        inner_layout.addWidget(automatic_classify_button, alignment=Qt.AlignCenter)

        show_dashboard_button = QPushButton('Show Dashboard')
        show_dashboard_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #3bccff; "
            "margin-top:2; font-size:25px; margin-top: 15px;")
        show_dashboard_button.setFixedSize(500, 80)
        show_dashboard_button.clicked.connect(self.on_click_show_dashboard_button)
        inner_layout.addWidget(show_dashboard_button, alignment=Qt.AlignCenter)

        exit_button = QPushButton('Exit')
        exit_button.setFixedSize(500, 90)  # width, height
        exit_button.setStyleSheet(
            "border-radius:20; border:2px solid black; background-color: #48ff48; margin-top:2; "
            "font-size:25px; margin-top: 15px;  margin-bottom: 15px;")
        exit_button.clicked.connect(self.on_click_exit_button)
        inner_layout.addWidget(exit_button, alignment=Qt.AlignCenter)
        inner_widget.setLayout(inner_layout)
        inner_widget.setStyleSheet("border-radius:20; border:2px solid black; background-color: #d5d5d7;")
        vertical_layout.addWidget(inner_widget)

        main_widget.setLayout(vertical_layout)

        self.setCentralWidget(main_widget)

        main_widget.setStyleSheet("background-color: #ffffff;")

    def on_click_load_datasets_button(self):
        self.gui_manager.go_to_waiting_page(message='The application is now loading data \nfrom the CSVs!',
                                            go_back_button_text='Save the results and go back to the homepage',
                                            number_labels=1)

        process_manager = self.gui_manager.process_manager
        thread = Thread(target=process_manager.load_datasets)
        thread.start()
        process_manager.signal.connect(lambda: self.gui_manager.go_to_generic_page(
            'The data loading has ended,\nnow you can go back to the homepage!'))

        second_thread = Thread(target=process_manager.update_load_data_page, args=(self.gui_manager, thread,))
        process_manager.update_signal.connect(
            lambda: self.update_waiting_window(1))
        second_thread.start()

    def update_waiting_window(self, number_labels):
        if isinstance(self.gui_manager.window, WaitingWindow):
            self.gui_manager.window.update_waiting_window(number_labels)

    def on_click_retrieve_data_button(self):
        self.gui_manager.go_to_waiting_page(message='The application is now retrieving data '
                                                    '\nfrom the Google Play Store!',
                                            go_back_button_text='Save the results and go back to the homepage',
                                            number_labels=3
                                            )

        # =================================================================================
        # The following code is used to start the process in the ProcessHandler on another thread (different from the
        # one of the GUI) and to callback the refresh of the page when it ends
        process_manager = self.gui_manager.process_manager
        thread = Thread(target=process_manager.launch_data_miner)
        thread.start()
        process_manager.signal.connect(lambda: self.gui_manager.go_to_generic_page(
            'The information retrieval has ended,\nnow you can go back to the homepage!'))

        second_thread = Thread(target=process_manager.update_data_retrieval_page, args=(self.gui_manager, thread))
        process_manager.update_signal.connect(
            lambda: self.update_waiting_window(3))
        second_thread.start()
        # =================================================================================

    def on_click_manual_classify_button(self):
        self.gui_manager.go_to_manual_classifier_page()

    def on_click_automatic_classify_button(self):
        self.gui_manager.go_to_waiting_page(message='The application is now automatically classifying the applications '
                                                    '\nstored into the database as possible serious games!',
                                            go_back_button_text='Go back to the homepage without saving',
                                            number_labels=-1)

        process_manager = self.gui_manager.process_manager
        thread = Thread(target=process_manager.do_classification_dataset)
        thread.start()
        process_manager.signal.connect(lambda: self.gui_manager.go_to_generic_page(
            'The classification task has ended,\nnow you can go back to the homepage!'))

    def on_click_exit_button(self):
        self.gui_manager.process_manager.close_application()
        self.gui_manager.window.close()
        os.kill(os.getpid(), signal.SIGTERM)  # this was forcefully added to stop also the dash app that is once started

    def on_click_show_dashboard_button(self):
        self.gui_manager.go_to_dashboard()
