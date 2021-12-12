from AlternativeGUI.WindowComponents.GenericWindow import GenericWindow
from AlternativeGUI.WindowComponents.HomePageWindow import HomePageWindow
from AlternativeGUI.WindowComponents.ManualClassifierWindow import ManualClassifierWindow
from AlternativeGUI.WindowComponents.WaitingWindow import WaitingWindow


class GUIManager:
    def __init__(self, process_manager):
        self.window = None
        self.process_manager = process_manager
        self.go_to_home_page()

        self.page = 0
        self.params = None

        self.message = ''

    def go_to_home_page(self):
        if self.window:
            self.window.close()
        self.window = HomePageWindow(self)
        self.window.show()

    def go_to_manual_classifier_page(self):
        if self.window:
            self.window.close()
        self.window = ManualClassifierWindow(self)
        self.window.show()

    def go_to_waiting_page(self, message, go_back_button_text, number_labels):
        if self.window:
            self.window.close()
        self.window = WaitingWindow(self, message, go_back_button_text, number_labels)
        self.window.show()

    def go_to_generic_page(self, message):
        if self.window:
            self.window.close()
        self.window = GenericWindow(self, message)
        self.message = ''
        self.window.show()
