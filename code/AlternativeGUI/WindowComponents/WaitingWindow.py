from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie, QIcon
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout


def create_dictionary_data_retrieval_statistics(p_apps):
    dict_ = {'currently loaded': 0, 'checked': 0, 'taken from dataset': 0}
    for app in p_apps:
        check = app[0]
        from_dataset = app[1]
        if check:
            dict_.__setitem__('checked', dict_.get('checked') + 1)
        if from_dataset:
            dict_.__setitem__('taken from dataset', dict_.get('taken from dataset') + 1)
        dict_.__setitem__('currently loaded', dict_.get('currently loaded') + 1)

    return dict_


class WaitingWindow(QMainWindow):
    def __init__(self, gui_manager, message, go_back_button_text, number_labels):
        super().__init__()
        self.gui_manager = gui_manager
        self.apps_from_dataset = []

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
        bottom_layout = QHBoxLayout()
        bottom_widget = QWidget()

        message_label = QLabel(message)
        message_label.setStyleSheet("border-radius:20; border:2px solid black; font-size:20px; "
                                    "background-color: #48ff48;")
        vertical_layout.addWidget(message_label, alignment=Qt.AlignCenter)

        waiting_logo_label = QLabel()
        gif = QMovie('./resources/images/loading.gif')
        gif.setScaledSize(QtCore.QSize(64, 64))
        gif.start()
        waiting_logo_label.setAttribute(Qt.WA_NoSystemBackground)
        waiting_logo_label.setMovie(gif)
        waiting_logo_label.setStyleSheet("margin-top:15px")
        vertical_layout.addWidget(waiting_logo_label, alignment=Qt.AlignCenter)

        self.labels = []
        if number_labels == 1 or number_labels == 3:
            for i in range(number_labels):
                label = QLabel('')
                self.labels.append(label)
                label.setStyleSheet("border-radius:20; border:2px solid black; font-size:20px; "
                                    "background-color: #48ff48;")
            self.update_waiting_window(number_labels)
        if self.labels:
            for label in self.labels:
                vertical_layout.addWidget(label, alignment=Qt.AlignCenter)
                if not self.apps_from_dataset:
                    label.setHidden(True)

        go_to_home_button = QPushButton(go_back_button_text)
        go_to_home_button.setIcon(QIcon('./resources/images/home.png'))
        go_to_home_button.setIconSize(QtCore.QSize(35, 35))
        go_to_home_button.setStyleSheet(
            "QPushButton {border-radius:20; border:2px solid black; font-size:20px; "
            "padding: 5px 5px 5px 5px; background-color: yellow; display: inline-block;} "
            "QPushButton::hover"
            "{"
            "border:4px solid black"
            "}"
        )
        go_to_home_button.clicked.connect(self.on_click_home_button)
        bottom_layout.addWidget(go_to_home_button, alignment=Qt.AlignCenter)
        bottom_widget.setLayout(bottom_layout)

        center_widget.setLayout(vertical_layout)
        main_layout.addWidget(center_widget)
        main_layout.setAlignment(center_widget, Qt.AlignVCenter)
        main_layout.addWidget(bottom_widget)
        main_layout.setAlignment(bottom_widget, Qt.AlignBottom)

        main_widget.setLayout(main_layout)
        main_widget.setStyleSheet("background-color: #b5d8f8;")

        self.setCentralWidget(main_widget)

    def on_click_home_button(self):
        self.gui_manager.process_manager.close_application()
        self.gui_manager.go_to_home_page()

    def update_dynamic_labels(self, number_labels, apps_from_dataset):
        if number_labels == 1:
            label = self.labels[0]
            label.setHidden(False)
            n_apps_loaded = len(apps_from_dataset)

            label.setText('The number of currently loaded apps is :   ' + str(n_apps_loaded))
        elif number_labels == 3:

            dictionary = create_dictionary_data_retrieval_statistics(apps_from_dataset)

            self.labels[0].clear()
            self.labels[0].setHidden(False)
            self.labels[1].clear()
            self.labels[1].setHidden(False)
            self.labels[2].clear()
            self.labels[2].setHidden(False)
            self.labels[0].setText('The number of apps retrieved is :   ' +
                                   str(dictionary.get('currently loaded')))
            self.labels[1].setText('The number of apps retrieved only from dataset is :   ' +
                                   str(dictionary.get('taken from dataset')))
            self.labels[2].setText('The number of apps already checked and set into the database is :   ' +
                                   str(dictionary.get('checked')))

    def update_waiting_window(self, number_labels):
        if isinstance(self.gui_manager.window, WaitingWindow):
            if not self.apps_from_dataset:
                return
            self.gui_manager.window.update_dynamic_labels(number_labels, self.apps_from_dataset)
